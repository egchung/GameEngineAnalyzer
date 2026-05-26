"""

GameEngineAnalyzer

==================

이 도구는 지정된 경로의 게임 파일을 분석하여 사용된 게임 엔진을 식별하고,

해당 엔진 구동에 필요한 필수 런타임 환경(VC++, DirectX 등)을 제안합니다.



Version: 1.0.0

Description: 자동 게임 엔진 식별 및 필수 런타임 환경 분석기

Dependencies: pefile (pip install pefile)

Copyright (c) 2026 egchung

GitHub: https://github.com/egchung/GameEngineAnalyzer

MIT License - https://opensource.org/licenses/MIT



"""



import os

import re

import sys

import json

import argparse

import pefile

from datetime import datetime



class GameAnalyzer:

    # 규칙 리스트 (Unreal Engine 제거됨, PubCoder는 scan_files에서 선검사)

    ENGINE_RULES = [

        # --- 1. RPG Maker ---

        {"name": "RPG Maker (MV/MZ / NW.js)", "pattern": lambda r, f, d: any(x.endswith('.rpgmvp') for x in f) or ('package.json' in f and 'nw.dll' in f), "deps": ["글로벌 런타임 불필요"]},

        {"name": "RPG Maker (XP/VX/VX Ace)", "pattern": lambda r, f, d: 'game.ini' in f, "deps": ["RPG Maker RTP", "DirectX 9.0c"]},



        # --- 2. 자체 엔진 ---

        {"name": "Joycity Custom Engine", "pattern": lambda r, f, d: 'card_default.pak' in f or 'fs2' in r.lower(), "deps": ["DirectX 9.0c", "VC++ Redistributable"]},

        {"name": "Essence Engine 5.0 (Relic)", "pattern": lambda r, f, d: any(x.endswith('.sga') for x in f) or 'relic' in r.lower() or 'coh3' in r.lower(), "deps": ["DirectX 12", "VC++ 2019/2022"]},

        {"name": "PUNKCAKE Custom Engine", "pattern": lambda r, f, d: 'shotgunking' in r.lower() or 'punkcake' in r.lower(), "deps": ["글로벌 런타임 불필요"]},

        {"name": "Phoenix Engine (Relic Custom)", "pattern": lambda r, f, d: any(x.endswith('.oppc') for x in f), "deps": ["DirectX 9.0c", "VC++ 2008/2010"]},

        {"name": "Frozenbyte Engine", "pattern": lambda r, f, d: any(x.endswith('.fbq') for x in f), "deps": ["NVIDIA PhysX", "VC++ 2010/2012/2015-2022"]},

        

        # --- 4. 비주얼 노벨 ---

        {"name": "KiriKiri (Z / TVP) Engine", "pattern": lambda r, f, d: any(x.endswith(('.xp3', '.cf')) for x in f), "deps": ["VC++ 2010/2015-2022", "DirectX 9.0c"]},

        {"name": "Ren'Py", "pattern": lambda r, f, d: 'renpy' in r.lower() or 'librenpy.dll' in f, "deps": ["VC++ 2015", "DirectX"]},

        {"name": "TyranoBuilder", "pattern": lambda r, f, d: 'tyrano' in r.lower() or 'tyrano' in f, "deps": ["글로벌 런타임 불필요"]},

        {"name": "Nitroplus Engine", "pattern": lambda r, f, d: any(file.endswith('.npk') for file in f) or 'mware.dll' in f, "deps": ["글로벌 런타임 불필요"]},

        {"name": "ISM Engine", "pattern": lambda r, f, d: any(file.endswith('.isa') for file in f) or 'ism.dll' in f, "deps": ["DirectX 9.0c", "VC++ Redistributable"]},

        

        # --- 5. 메이저 엔진 ---

        {"name": "Unity Engine", "pattern": lambda r, f, d: any(x.endswith('_data') for x in d) or 'unityplayer.dll' in f or 'gameassembly.dll' in f, "deps": ["VC++ 2015-2022", "DirectX"]},

        {"name": "Godot Engine", "pattern": lambda r, f, d: any(x.endswith('.pck') for x in f) or any('godot' in x for x in f), "deps": ["글로벌 런타임 불필요"]},

        {"name": "GameMaker Studio", "pattern": lambda r, f, d: 'data.win' in f or 'game.win' in f or any(x.startswith('audiogroup') for x in f), "deps": ["VC++ 2015-2022", "DirectX"]},

        {"name": "Clickteam Fusion", "pattern": lambda r, f, d: any(

            'mmf2' in x or x.startswith('mmf') or (x.startswith('kc') and x.endswith('.mfx')) or x.endswith('.mfx')

            for x in f

        ), "deps": ["글로벌 런타임 불필요"]},

        {"name": "Ogre3D Engine", "pattern": lambda r, f, d: any('ogre' in x for x in f), "deps": ["DirectX 9.0c", "VC++ 2010/2012/2015"]},

    ]



    def __init__(self, target_dir):

        self.target_dir = os.path.abspath(target_dir.strip().strip('"'))

        self.detected_engine = "Unknown"

        self.required_programs = ["확인 불가"]



    def _binary_contains(self, path, keyword):

        try:

            with open(path, "rb") as handle:

                while True:

                    chunk = handle.read(1024 * 1024)

                    if not chunk:

                        return False

                    if keyword in chunk:

                        return True

        except OSError:

            return False

        return False



    def _is_pubcoder(self, root, files, files_lower, dirs):

        """PubCoder는 NW.js 런타임을 쓰지만 파일명에 pubcoder가 없을 수 있음 (exe 내장 문자열)."""

        names_lower = files_lower + [d.lower() for d in dirs]

        if any("pubcoder" in name or "pubreader" in name for name in names_lower):

            return True

        if "pubcoder" in root.lower() or "pubreader" in root.lower():

            return True



        if not ("nw.dll" in files_lower and any(

            pak in files_lower for pak in ("nw_100_percent.pak", "nw_200_percent.pak", "resources.pak")

        )):

            return False

        if "package.json" in files_lower or any(name.endswith(".rpgmvp") for name in files_lower):

            return False



        skip_exes = {"notification_helper.exe", "uninstall.exe"}

        for raw_name, lower_name in zip(files, files_lower):

            if not lower_name.endswith(".exe") or lower_name in skip_exes:

                continue

            exe_path = os.path.join(root, raw_name)

            if self._binary_contains(exe_path, b"pubcoder") or self._binary_contains(exe_path, b"pubreader"):

                return True

        return False



    def _is_chromium_locale_pak(self, filename):

        """Electron/Chromium locales 폴더의 언어 팩 (en-us.pak, ko.pak 등)."""

        return bool(re.match(r"^[a-z]{2}(-[a-z0-9]+)?\.pak$", filename))



    def _is_electron(self, root, files_lower, dirs_lower):

        """Electron(Chromium) 래퍼 — STOVE HTML5/비주얼노벨 런처 등."""

        if "app.asar" in files_lower:

            return True

        if "chrome_100_percent.pak" in files_lower and "chrome_200_percent.pak" in files_lower:

            return True

        if "resources" in dirs_lower and "locales" in dirs_lower:

            if "chrome_100_percent.pak" in files_lower or "resources.pak" in files_lower:

                return True

        return False



    def _is_unreal(self, root, files, dirs):

        # PubCoder/RPG Maker/Electron 오탐 차단

        if any('pubcoder' in f or 'pubreader' in f for f in files):

            return False

        if any(f.endswith('.rpgmvp') for f in files):

            return False

        if 'nw.dll' in files:

            return False

        if os.path.basename(root).lower() == 'locales':

            return False



        webview_paks = {'resources.pak', 'chrome_100_percent.pak', 'nw_100_percent.pak', 'chrome_200_percent.pak', 'nw_200_percent.pak'}

        if 'binaries' in dirs and 'engine' in dirs:

            return True

        if any('win64-shipping' in f for f in files):

            return True

        if any(f.endswith(('.ucas', '.utoc')) for f in files):

            return True

        return any(

            f.endswith('.pak')

            and f not in webview_paks

            and not (f.startswith('nw_') and f.endswith('.pak'))

            and not self._is_chromium_locale_pak(f)

            for f in files

        )



    def scan_files(self):

        if not os.path.exists(self.target_dir):

            return False



        for root, dirs, files in os.walk(self.target_dir):

            f_l = [f.lower() for f in files]

            d_l = [d.lower() for d in dirs]



            if self._is_pubcoder(root, files, f_l, dirs):

                self.detected_engine = "PubCoder (Interactive Ebook/App)"

                self.required_programs = ["글로벌 런타임 불필요"]

                return True



            if self._is_electron(root, f_l, d_l):

                self.detected_engine = "Electron (Chromium App)"

                self.required_programs = ["글로벌 런타임 불필요"]

                return True



            for rule in self.ENGINE_RULES:

                if rule["pattern"](root, f_l, d_l):

                    self.detected_engine = rule["name"]

                    self.required_programs = rule["deps"]

                    return True



            if self._is_unreal(root, f_l, d_l):

                self.detected_engine = "Unreal Engine"

                self.required_programs = ["VC++ 2015-2022", "DirectX 11/12"]

                return True



            for f in f_l:

                if f.endswith('.exe') and self.verify_via_pe(os.path.join(root, f)):

                    return True

        return False



    def verify_via_pe(self, exe_path):

        try:

            pe = pefile.PE(exe_path, fast_load=False)

            imports = [entry.dll.decode().lower() for entry in pe.DIRECTORY_ENTRY_IMPORT]

            if 'unityplayer.dll' in imports:

                self.detected_engine = "Unity Engine (Detected via PE)"

                self.required_programs = ["VC++ 2015-2022"]

                return True

        except: pass

        return False



    def to_result(self):

        return {

            "folder": os.path.basename(self.target_dir),

            "path": self.target_dir,

            "engine": self.detected_engine,

            "required_programs": self.required_programs,

            "detected": self.detected_engine != "Unknown",

        }



    def save_report(self, results_dir="results"):

        os.makedirs(results_dir, exist_ok=True)

        filename = os.path.join(results_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

        payload = self.to_result()

        lines = [

            "# 분석 보고서",

            "",

            f"- 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",

            f"- 폴더: {payload['folder']}",

            f"- 경로: {payload['path']}",

            f"- 엔진: {payload['engine']}",

            f"- 감지 여부: {'예' if payload['detected'] else '아니오'}",

            "",

            "## 필수 설치",

        ]

        if payload["required_programs"]:

            lines.extend(f"- {dep}" for dep in payload["required_programs"])

        else:

            lines.append("- 없음")

        with open(filename, "w", encoding="utf-8") as handle:

            handle.write("\n".join(lines))

        print(f"\n[알림] 분석 보고서가 저장되었습니다: {filename}")

        return filename





def is_batch_root(path):

    """설치 라이브러리 루트(예: STOVE Games) — 하위 폴더마다 게임이 있는 구조."""

    if not os.path.isdir(path):

        return False

    try:

        entries = os.listdir(path)

    except OSError:

        return False

    subdirs = [name for name in entries if os.path.isdir(os.path.join(path, name))]

    if len(subdirs) < 2:

        return False

    has_root_exe = any(

        name.lower().endswith(".exe") and os.path.isfile(os.path.join(path, name))

        for name in entries

    )

    return not has_root_exe





def analyze_folder(path):

    analyzer = GameAnalyzer(path)

    analyzer.scan_files()

    return analyzer.to_result()





def scan_install_root(root_dir, results_dir="results"):

    root = os.path.abspath(root_dir.strip().strip('"'))

    if not os.path.isdir(root):

        raise FileNotFoundError(f"경로를 찾을 수 없습니다: {root}")



    folder_names = sorted(

        name for name in os.listdir(root)

        if os.path.isdir(os.path.join(root, name))

    )



    games = []

    total = len(folder_names)

    for index, name in enumerate(folder_names, 1):

        game_path = os.path.join(root, name)

        print(f"[{index}/{total}] {name} ...", flush=True)

        games.append(analyze_folder(game_path))



    report = {

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "root_dir": root,

        "total": len(games),

        "games": games,

    }

    return report





def save_batch_report(report, results_dir="results"):

    os.makedirs(results_dir, exist_ok=True)

    filename = os.path.join(

        results_dir,

        f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",

    )

    lines = [

        "# 일괄 분석 보고서",

        "",

        f"- 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",

        f"- 루트: {report['root_dir']}",

        f"- 총 폴더: {report['total']}",

        "",

        "## 게임 목록",

    ]

    for game in report["games"]:

        lines.extend([

            f"### {game['folder']}",

            f"- 경로: {game['path']}",

            f"- 엔진: {game['engine']}",

            f"- 필수 설치: {', '.join(game['required_programs']) if game['required_programs'] else '없음'}",

            f"- 감지됨: {'예' if game['detected'] else '아니오'}",

            "",

        ])

    with open(filename, "w", encoding="utf-8") as handle:

        handle.write("\n".join(lines))

    return filename





def print_batch_summary(report):

    print(f"\n[일괄 분석 결과] 루트: {report['root_dir']}")

    print(f"총 {report['total']}개 폴더\n")

    for game in report["games"]:

        deps = ", ".join(game["required_programs"])

        print(f"  · {game['folder']}")

        print(f"    엔진: {game['engine']}")

        print(f"    필수: {deps}\n")





def print_single_result(result):

    print(f"\n[분석 결과] {result['folder']}")

    print(f"■ 경로: {result['path']}")

    print(f"■ 엔진: {result['engine']}")

    print(f"■ 필수 설치: {', '.join(result['required_programs'])}")





def run_single(path, results_dir="results", emit_json=True):

    analyzer = GameAnalyzer(path)

    analyzer.scan_files()

    result = analyzer.to_result()

    print_single_result(result)

    saved = analyzer.save_report(results_dir)

    if emit_json:

        print("\n[JSON]")

        print(json.dumps(result, indent=4, ensure_ascii=False))

    return result, saved





def run_batch(path, results_dir="results", emit_json=True):

    report = scan_install_root(path, results_dir)

    print_batch_summary(report)

    saved = save_batch_report(report, results_dir)

    print(f"\n[알림] 일괄 분석 보고서가 저장되었습니다: {saved}")

    if emit_json:

        print("\n[JSON]")

        print(json.dumps(report, indent=4, ensure_ascii=False))

    return report, saved





def main(argv=None):

    parser = argparse.ArgumentParser(

        description="게임 설치 폴더의 엔진 및 필수 런타임을 분석합니다.",

    )

    parser.add_argument(

        "path",

        nargs="?",

        help="분석할 경로 (게임 1개 폴더 또는 설치 라이브러리 최상위 폴더)",

    )

    parser.add_argument(

        "--batch",

        action="store_true",

        help="하위 폴더를 게임 단위로 일괄 분석",

    )

    parser.add_argument(

        "--single",

        action="store_true",

        help="입력 경로 하나만 단일 게임으로 분석",

    )

    parser.add_argument(

        "--output-dir",

        default="results",

        help="JSON 저장 폴더 (기본: results)",

    )

    parser.add_argument(

        "--no-json-print",

        action="store_true",

        help="콘솔 JSON 출력 생략",

    )

    args = parser.parse_args(argv)



    path = args.path or input("분석할 경로를 입력하세요: ").strip()

    if not path:

        print("[오류] 경로가 비어 있습니다.")

        sys.exit(1)



    path = os.path.abspath(path.strip().strip('"'))

    emit_json = not args.no_json_print



    try:

        if args.batch or (not args.single and is_batch_root(path)):

            run_batch(path, args.output_dir, emit_json)

        else:

            result, saved = run_single(path, args.output_dir, emit_json)

            if not result["detected"]:

                print("\n[알림] 엔진을 식별하지 못했습니다.")

                sys.exit(1)

    except FileNotFoundError as exc:

        print(f"[오류] {exc}")

        sys.exit(1)





if __name__ == "__main__":

    try:

        main()

    finally:

        # When running as a bundled executable (PyInstaller) on Windows,

        # pause and wait for any key so the console window doesn't close immediately.

        if os.name == "nt" and getattr(sys, "frozen", False):

            try:

                import msvcrt

                print("\nPress any key to exit...")

                msvcrt.getch()

            except Exception:

                pass

