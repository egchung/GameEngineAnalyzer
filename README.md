# GameEngineAnalyzer
GameEngineAnalyzer 
# GameEngineAnalyzer

게임 설치 폴더를 분석하여 사용된 **게임 엔진을 식별**하고, 해당 게임을 실행하기 위해 필요한 **필수 런타임 환경(VC++, DirectX 등)**을 안내하는 자동화 도구입니다.

## 🚀 주요 기능
- **다양한 엔진 식별**: Unreal, Unity, RPG Maker, PubCoder, Ren'Py 등 주요 게임 엔진 탐지.
- **필수 환경 가이드**: 식별된 엔진에 따라 필요한 런타임/라이브러리(DirectX, VC++ 등) 정보 출력.
- **보고서 생성**: 분석 결과를 JSON 파일로 저장하여 체계적인 기록 관리.
- **오탐 방지 로직**: 엔진별 고유 패턴 및 우선순위 알고리즘을 통한 높은 정확도.

## 🛠 사용 방법
1. **Python 설치**: Python 3.x 환경이 필요합니다.
2. **필수 라이브러리 설치**:
   ```bash
   pip install pefile