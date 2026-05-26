# GameEngineAnalyzer

게임 설치 폴더를 분석하여 사용된 **게임 엔진을 식별**하고, 해당 게임을 실행하기 위해 필요한 **필수 런타임 환경(VC++, DirectX 등)**을 안내하는 자동화 도구입니다.

## 🚀 주요 기능
- **다양한 엔진 식별**: Unreal, Unity, RPG Maker, Ren'Py 등 주요 게임 엔진 탐지.
- **필수 환경 가이드**: 식별된 엔진에 따라 필요한 런타임/라이브러리(DirectX, VC++ 등) 정보 출력.
- **보고서 생성**: 분석 결과를 Markdown 파일로 저장하여 사람이 읽기 쉬운 기록 관리.
- **오탐 방지 로직**: 엔진별 고유 패턴 및 우선순위 알고리즘을 통한 높은 정확도.

## 🛠 사용 방법


### 방법 1: 소스코드 직접 실행
파이썬 환경이 설치되어 있다면 소스코드를 통해 직접 실행할 수 있습니다.
1. **Python 설치**: Python 3.x 환경이 필요합니다.
2. **필수 라이브러리 설치**:
   `pip install pefile` 명령어로 필수 라이브러리를 설치합니다.
3. `python src/enginecheck.py` 명령어로 실행합니다.

#### 단일 게임 / 설치 라이브러리 일괄 분석

```bash
# 게임 1개 폴더
python src/enginecheck.py "D:\Games\Peglin"

# STOVE Games처럼 하위에 게임 폴더가 여러 개인 최상위 경로 (자동 일괄 분석)
python src/enginecheck.py "D:\EG_ProgramFiles\STOVE_v3\Games"

# 일괄 분석 강제
python src/enginecheck.py "D:\Games" --batch
```

- 콘솔에 폴더명·엔진·필수 프로그램을 출력하고, JSON도 함께 표시합니다.
- 단일 분석 결과는 `results/report_YYYYMMDD_HHMMSS.md`에 저장됩니다.
- 일괄 분석 결과는 `results/batch_YYYYMMDD_HHMMSS.md`에 저장됩니다.

### 방법 2: 실행 파일(.exe) 사용 (권장)
별도의 설치 과정 없이 즉시 실행 가능합니다.
1. [Releases](https://github.com/egchung/GameEngineAnalyzer/releases) 페이지에서 최신 `GameEngineAnalyzer.exe` 파일을 다운로드합니다.
2. 다운로드한 파일을 실행합니다.
3. 분석할 게임의 루트 폴더 경로를 입력하면 분석이 시작됩니다.

> **⚠️ 주의사항 (백신 경고)**
> 본 실행 파일은 직접 빌드(PyInstaller)된 파일이므로, Windows Defender나 일부 백신 프로그램에서 "알 수 없는 게시자"로 인식하여 경고창을 띄울 수 있습니다.
> 1. 경고창에서 **[추가 정보]** 클릭
> 2. **[실행]** 버튼 클릭
> 개발자(본인)가 직접 빌드한 신뢰할 수 있는 파일이니 안심하고 실행하셔도 됩니다.
