import os
import pefile

class GameAnalyzer:
    # 엔진 식별 규칙을 데이터로 분리 (유지보수 용이)
    ENGINE_RULES = [
        {"name": "Essence Engine 5.0", "pattern": lambda r, f: 'company of heroes' in r.lower() or 'relic' in r.lower(), "deps": ["DirectX 12", "VC++ 2019/2022"]},
        {"name": "Unity Engine", "pattern": lambda r, f: any(d.endswith('_data') for d in r.lower().split(os.sep)) or 'unityplayer.dll' in f, "deps": ["VC++ 2015-2022", "DirectX"]},
        {"name": "Godot Engine", "pattern": lambda r, f: any(file.endswith('.pck') for file in f) or 'godot' in r.lower(), "deps": ["글로벌 런타임 불필요"]},
        {"name": "RPG Maker (MV/MZ)", "pattern": lambda r, f: 'package.json' in f or 'www' in [d.lower() for d in r.split(os.sep)], "deps": ["글로벌 런타임 불필요"]},
    ]

    def __init__(self, target_dir):
        self.target_dir = os.path.abspath(target_dir.strip().strip('"'))
        self.detected_engine = "Unknown"
        self.required_programs = ["확인 불가"]

    def scan_files(self):
        if not os.path.exists(self.target_dir):
            return False

        for root, dirs, files in os.walk(self.target_dir):
            files_lower = [f.lower() for f in files]
            
            # 1. 규칙 기반 식별
            for rule in self.ENGINE_RULES:
                if rule["pattern"](root, files_lower):
                    self.detected_engine = rule["name"]
                    self.required_programs = rule["deps"]
                    return True
            
            # 2. 정적 PE 분석 (Import Table 검사 추가)
            for f in files_lower:
                if f.endswith('.exe'):
                    if self.verify_via_pe(os.path.join(root, f)):
                        return True
        return False

    def verify_via_pe(self, exe_path):
        try:
            pe = pefile.PE(exe_path, fast_load=False)
            # 임포트된 DLL 목록 확인으로 엔진 정밀 식별
            imports = [entry.dll.decode().lower() for entry in pe.DIRECTORY_ENTRY_IMPORT]
            if b'unityplayer.dll' in [i.encode() for i in imports]:
                self.detected_engine = "Unity Engine (Detected via PE)"
                self.required_programs = ["VC++ 2015-2022"]
                return True
        except:
            pass
        return False

if __name__ == "__main__":
    path = input("분석할 경로를 입력하세요: ")
    analyzer = GameAnalyzer(path)
    if analyzer.scan_files():
        print(f"\n[분석 결과]")
        print(f"■ 엔진: {analyzer.detected_engine}")
        print(f"■ 필수 설치: {', '.join(analyzer.required_programs)}")