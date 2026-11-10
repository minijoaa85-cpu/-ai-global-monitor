# Global AI Observatory V4.0

실제 글로벌 생성형 AI 성능 리더보드를 주간 수집하고, 모바일 웹사이트 및 한국어 HTML 보고서로 발행하는 개인 관리형 플랫폼입니다.

## 실제 웹사이트
https://minijoaa85-cpu.github.io/-ai-global-monitor/

## V4 기능
- [x] 공식 Arena 리더보드 (text, text_style_control, webdev, search, vision, document, agent) — 공개 데이터셋 CC BY 4.0
- [x] 공식 순위, 95% 신뢰구간, 표본 수, 발표 날짜 보존
- [x] 분야별 모델 TOP 10, 검색, 모델 최대 3종 직접 비교
- [x] 같은 평가 방식의 주간 점수 변동과 장기 추세
- [x] 한국어 주간 보고서 `site/weekly-report.html`, CSV 다운로드
- [x] GitHub Actions 매주 월요일 오전 9:20 (KST) 자동 수집+데이터 커밋+Pages 배포
- [x] Python 단위 테스트 및 Node JavaScript 문법 검사
- [x] 공개할 수 없는 라이선스 데이터 자동 게시 차단 및 장애 상태 표시

## 출처/라이선스
**Arena 공식 리더보드 데이터**: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset — Creative Commons Attribution 4.0 (CC BY 4.0). 공개 화면과 보고서에 출처를 표시합니다. 각 leaderboard의 점수 척도·평가 방식·신뢰구간이 달라 결합 점수는 제공하지 않습니다.

**Artificial Analysis**: https://artificialanalysis.ai/data-api — Free API는 내부 사용 전용으로, 외부 재배포에 대한 권리가 포함되지 않습니다. 기존에 등록한 `AA_API_KEY`는 GitHub Secrets에 그대로 보관되지만 V4 공개 수집기는 의도적으로 이 키를 호출하지 않으며 해당 데이터의 신규 공개 게시도 중단했습니다.

**중요: 이전 버전이 공개 저장소에 남긴 Artificial Analysis 데이터는 현재 브랜치의 최신 파일에서는 제거되지만, 기존 Git 커밋 기록에는 남아 있을 수 있습니다. 완전히 제거하려면 별도의 히스토리 정리/재작성 또는 저장소 재생성이 필요합니다.** 정리 전에는 저장소의 과거 공개 커밋을 제3자에게 배포하지 마세요.

**LiveBench**: https://livebench.github.io/ — 공개 자료의 실제 버전·파일 구조와 재배포 조건을 추가 확인할 때까지 수집을 활성화하지 않았습니다. 미구현을 성공으로 표시하지 않습니다.

## 수집 데이터의 한계
- Hugging Face Dataset Viewer `latest` split에서 분야별 **최대 100행만** 조회합니다. 전체 글로벌 모델 리더보드를 완전하게 수집한 것은 아니며, 데이터에 없는 모델이나 순위는 누락될 수 있습니다.
- API 트래픽 제한(HTTP 429)으로 일부 분야가 누락될 수 있습니다. 이때 해당 분야는 `ERROR` 상태로 표시하고 오류를 숨기지 않습니다.
- 동일한 평가 영역 안에서도 category별 비교만 허용하며 다른 방법론/지표를 합산하지 않습니다.
- 매주 월요일 00:20 UTC 자동 수집. GitHub Actions 스케줄은 혼잡/비활성 상태에 따라 지연 또는 중단될 수 있습니다.
- 일주일 내 재실행은 동일 주차 스냅샷을 최신 값으로 교체합니다. 주간 추세는 서로 다른 주차가 누적될 때 의미가 있습니다.
- 불완전하거나 오래된 데이터는 임의로 보간하거나 0점으로 표시하지 않습니다.

## 운영 방법
1. GitHub 저장소 **Actions → Weekly AI benchmark collection → Run workflow** (수동 테스트).
2. 녹색 체크를 확인한 뒤 **Actions 로그**에서 source 상태와 수집된 레코드를 검토합니다.
3. 대시보드에 접속해 새로고침합니다. `site/data/status.json`에서 최신 상태 확인.
4. **Settings → Pages → Build and deployment: GitHub Actions** 설정을 유지합니다.
5. `Publish AI benchmark dashboard`는 필요할 때 수동 실행하는 복구용 워크플로입니다.
6. API 키를 이 저장소의 코드나 공개 댓글에 올리지 마세요.

## 로컬 테스트
Python 3.12 이상과 Node 20 이상:
```bash
python -m unittest discover -s tests -v
node --check site/v4.js
python src/monitor.py
python src/report.py
python -m http.server 8000 -d site
```
서버 실행 뒤 http://localhost:8000 에서 테스트합니다.

## 구조
- `src/monitor.py`: 공식 허용 라이선스 데이터만 공개 수집
- `src/report.py`: 주간 한국어 HTML 보고서
- `site/index.html`, `site/v4.css`, `site/v4.js`: 모바일 관측소 대시보드
- `site/data/`: 공개 가능한 정규화 데이터
- `.github/workflows/weekly.yml`: 검증·주간 수집·커밋·웹 배포
- `.github/workflows/pages.yml`: 수동 배포 복구용
- `tests/`: 수집 파서 단위 테스트

## 후속 확장
LiveBench의 공개/재배포 조건 확인 후 공식 파일 기반 커넥터, 실제 평가 방법 버전 변경 감지, 주간 보고서 이메일 전송을 추가할 수 있습니다. 이메일 전송은 별도의 메일 인증 설정이 필요합니다.
