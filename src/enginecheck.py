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
import json
import pefile
from datetime import datetime

class GameAnalyzer:
    # 규칙 리스트 (Unreal Engine 제거됨)
    ENGINE_RULES = [
        # --- 1. RPG Maker (최우선 식별) ---
        {"name": "RPG Maker (MV/MZ / NW.js)", "pattern": lambda r, f, d: any(x.endswith('.rpgmvp') for x in f) or ('package.json' in f and 'nw.dll' in f), "deps": ["글로벌 런타임 불필요"]},
        {"name": "RPG Maker (XP/VX/VX Ace)", "pattern": lambda r, f, d: 'game.ini' in f, "deps": ["RPG Maker RTP", "DirectX 9.0c"]},

        # --- 2. PubCoder (언리얼보다 우선 검사) ---
        {"name": "PubCoder (Interactive Ebook/App)", "pattern": lambda r, f, d: any('pubcoder' in x for x in f) or any('pubreader' in x for x in f), "deps": ["글로벌 런타임 불필요"]},
      
        # 3. Unreal Engine (제안받은 통합 패턴 적용)
        {"name": "Unreal Engine", "pattern": lambda r, f, d: (
            not any('pubcoder' in x or 'pubreader' in x for x in f) and
            not any(x.endswith('.rpgmvp') for x in f) and
            ('binaries' in d and 'engine' in d or any('win64-shipping' in x for x in f))
        ), "deps": ["VC++ 2015-2022", "DirectX 11/12"]},

        # --- 3. 자체 엔진 ---
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
        {"name": "Clickteam Fusion", "pattern": lambda r, f, d: 'mmf2' in f or 'kcc' in f, "deps": ["글로벌 런타임 불필요"]},
        {"name": "Ogre3D Engine", "pattern": lambda r, f, d: any('ogre' in x for x in f), "deps": ["DirectX 9.0c", "VC++ 2010/2012/2015"]},
     #   {"name": "Unreal Engine", "pattern": lambda r, f, d: 'paks' in d and any(x.endswith(('.pak', '.ucas', '.utoc')) for x in f), "deps": ["VC++ 2015-2022", "DirectX 11/12"]},
    ]

    def __init__(self, target_dir):
        self.target_dir = os.path.abspath(target_dir.strip().strip('"'))
        self.detected_engine = "Unknown"
        self.required_programs = ["확인 불가"]

    def scan_files(self):
        if not os.path.exists(self.target_dir): return False

        walk_data = list(os.walk(self.target_dir))
        
        # 1차: 엔진 규칙 적용 (우선순위 순서대로)
        for rule in self.ENGINE_RULES:
            for root, dirs, files in walk_data:
                f_l, d_l = [f.lower() for f in files], [d.lower() for d in dirs]
                if rule["pattern"](root, f_l, d_l):
                    self.detected_engine = rule["name"]
                    self.required_programs = rule["deps"]
                    return True

        # 2차: PE 검사
        for root, _, files in walk_data:
            for f in files:
                if f.endswith('.exe') and self.verify_via_pe(os.path.join(root, f)):
                    return True
        return False

    def verify_via_pe(self, exe_path):
        try:
            pe = pefile.PE(exe_path, fast_load=False)
            imports = [entry.dll.decode().lower() for entry in pe.DIRECTORY_ENTRY_IMPORT]
            if b'unityplayer.dll' in [i.encode() for i in imports]:
                self.detected_engine = "Unity Engine (Detected via PE)"
                self.required_programs = ["VC++ 2015-2022"]
                return True
        except: pass
        return False

    def save_report(self):
        if not os.path.exists("results"): os.makedirs("results")
        filename = f"results/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "target_dir": self.target_dir, "engine": self.detected_engine, "required_programs": self.required_programs}, f, indent=4, ensure_ascii=False)
        print(f"\n[알림] 분석 보고서가 저장되었습니다: {filename}")

if __name__ == "__main__":
    path = input("분석할 경로를 입력하세요: ")
    analyzer = GameAnalyzer(path)
    if analyzer.scan_files():
        print(f"\n[분석 결과]\n■ 엔진: {analyzer.detected_engine}\n■ 필수 설치: {', '.join(analyzer.required_programs)}")
        analyzer.save_report()
    else: print("\n[알림] 엔진을 식별하지 못했습니다.")