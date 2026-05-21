"""
Version: v1.0.1
Date: 2026-05-21
Release Note: 
- 에센스 엔진(Essence Engine 5.0) 식별 규칙 추가
- 렐릭 엔터테인먼트 게임군(Company of Heroes 3 등) 지원
"""

import os
import sys
import pefile

class GameAnalyzer:
    def __init__(self, target_dir):
        self.target_dir = os.path.abspath(target_dir.strip().strip('"'))
        self.detected_engine = "Unknown"
        self.required_programs = ["확인 불가 (일반 실행 파일 구조)"]
        self.found_files_summary = []

    def scan_files(self):
        print(f"\n[디버그] 1. 대상 경로 변환 완료: {self.target_dir}")
        if not os.path.exists(self.target_dir):
            print("[오류] 입력하신 경로가 존재하지 않습니다.")
            return False

        print("[디버그] 2. 폴더 내부 깊은 탐색을 시작합니다...")
        
        for root, dirs, files in os.walk(self.target_dir):
            dirs_lower = [d.lower() for d in dirs]
            files_lower = [f.lower() for f in files]
            root_lower = root.lower()

            # 1. 커스텀/특수 엔진 규칙
            if 'company of heroes' in root_lower or 'relic' in root_lower:
                self.detected_engine, self.required_programs = "Essence Engine 5.0 (Relic)", ["DirectX 12", "VC++ 2019/2022"]
                return True
            if 'shotgunking' in root_lower or 'punkcake' in root_lower:
                self.detected_engine, self.required_programs = "PUNKCAKE Custom Engine", ["글로벌 런타임 불필요"]
                return True
            if 'cats hidden' in root_lower or 'travellincats' in root_lower:
                self.detected_engine, self.required_programs = "Clickteam Fusion", ["글로벌 런타임 불필요"]
                return True
            if 'troubleshooter' in root_lower or any('ogre' in f for f in files_lower):
                self.detected_engine, self.required_programs = "Ogre3D Engine", ["DirectX 9.0c", "VC++ 2010/2012/2015"]
                return True
            if 'fs2' in root_lower or 'card_default.pak' in files_lower:
                self.detected_engine, self.required_programs = "Joycity Custom Online Engine", ["DirectX 9.0c", "VC++ Redistributable"]
                return True
            if any(f.endswith('.isa') for f in files_lower) or 'ism.dll' in files_lower:
                self.detected_engine, self.required_programs = "ISM Engine", ["DirectX 9.0c (d3dx9_43.dll)", "VC++ Redistributable"]
                return True
            if any(f.endswith('.npk') for f in files_lower) or 'mware.dll' in files_lower:
                self.detected_engine, self.required_programs = "Nitroplus Engine", ["글로벌 런타임 불필요"]
                return True
            if any('tyrano' in f for f in files_lower) or 'tyrano' in dirs_lower:
                self.detected_engine, self.required_programs = "TyranoBuilder", ["글로벌 런타임 불필요"]
                return True
            if 'nw_100_percent.pak' in files_lower or 'pubcoder' in files_lower:
                self.detected_engine, self.required_programs = "PubCoder", ["글로벌 런타임 불필요"]
                return True

            # 2. 범용 엔진 규칙
            if 'package.json' in files_lower or 'www' in dirs_lower:
                self.detected_engine, self.required_programs = "RPG Maker (MV/MZ)", ["글로벌 런타임 불필요"]
                return True
            if 'game.ini' in files_lower:
                self.detected_engine, self.required_programs = "RPG Maker (XP/VX/VX Ace)", ["RPG Maker RTP", "DirectX 9.0c"]
                return True
            if any(f.endswith('.pck') for f in files_lower) or 'godot' in root_lower:
                self.detected_engine, self.required_programs = "Godot Engine", ["글로벌 런타임 불필요"]
                return True
            if any(f.endswith('.oppc') for f in files_lower):
                self.detected_engine, self.required_programs = "Phoenix Engine", ["DirectX 9.0c", "VC++ 2008/2010"]
                return True
            if any(f.endswith('.fbq') for f in files_lower):
                self.detected_engine, self.required_programs = "Frozenbyte Engine", ["PhysX", "VC++ 2010-2022"]
                return True
            if 'data.win' in files_lower or 'game.win' in files_lower:
                self.detected_engine, self.required_programs = "GameMaker Studio", ["VC++ 2015-2022", "DirectX"]
                return True
            if any(f.endswith('.xp3') for f in files_lower):
                self.detected_engine, self.required_programs = "KiriKiri Engine", ["VC++ 2010/2015-2022", "DirectX 9.0c"]
                return True
            if any(d.endswith('_data') for d in dirs_lower) or 'unityplayer.dll' in files_lower:
                self.detected_engine, self.required_programs = "Unity Engine", ["VC++ 2015-2022", "DirectX"]
                return True
            if 'paks' in dirs_lower or any(f.endswith('.pak') for f in files_lower):
                self.detected_engine, self.required_programs = "Unreal Engine", ["VC++ 2015-2022", "DirectX 11/12"]
                return True
            if 'game' in dirs_lower and 'renpy' in dirs_lower:
                self.detected_engine, self.required_programs = "Ren'Py", ["VC++ 2015", "DirectX"]
                return True

            # 3. 바이너리 정적 검증
            for f in files:
                if f.lower().endswith('.exe'):
                    if self.verify_via_pe(os.path.join(root, f)): return True

        return False

    def verify_via_pe(self, exe_path):
        try:
            pe = pefile.PE(exe_path, fast_load=True)
            return False
        except: return False

if __name__ == "__main__":
    print("="*60 + "\n                게임 엔진 및 런타임 분석기 (v1.0.1)\n" + "="*60)
    analyzer = GameAnalyzer(input("분석할 경로: "))
    analyzer.scan_files()
    print("-" * 60 + f"\n■ 검출 엔진: {analyzer.detected_engine}\n■ 필수 설치: {', '.join(analyzer.required_programs)}\n" + "=" * 60)
    input("종료하려면 엔터...")