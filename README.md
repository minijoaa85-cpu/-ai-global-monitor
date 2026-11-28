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

## V4.1 — AI 신규 모델 및 글로벌 동향 보드 (2026-11-11)
- 대시보드의 **AI 신모델 · 업데이트 · 글로벌 동향** 섹션에서 기사 제목, 분류, 발표일, 한국어 한줄 안내, 공식 피드 소개문 일부, 원문 링크를 볼 수 있습니다.
- **주제/출처/최근 7·14·21일** 필터를 지원합니다. 원문 링크는 별도 창에서 열립니다.
- 수집 출처: **OpenAI News**, **Google AI Blog**, **GitHub Copilot Changelog**, **Hugging Face Blog**. Hugging Face Blog는 커뮤니티 게시물이 포함될 수 있으며 특정 공급업체의 공식 발표와 구분해야 합니다. Anthropic은 안정적인 공식 RSS가 없어 자동 수집에 포함하지 않고 공식 뉴스룸 바로가기를 제공합니다.
- **매일 오전 9:55 (KST)** `.github/workflows/news.yml`가 `src/news.py`를 실행해 `site/data/news.json`을 갱신하고 공개 Pages 배포까지 진행합니다. 매주 월요일 9:20 벤치마크 수집 일정은 그대로 유지됩니다.
- 한줄 한국어 안내는 **기사 제목 및 분류 기준 자동 템플릿**입니다. 기사 본문을 읽고 AI가 사실 검증한 상세 요약은 아닙니다. 공식 피드가 제공한 짧은 영어 소개문 일부를 함께 표시합니다.
- API 장애 시 수집 상태를 표시하며, 오래된 기사나 발표 날짜가 미래인 기사는 제외합니다. 신모델 소식은 향후 순위 변화를 가늠하는 참고 자료일 뿐, 성능 향상이나 미래 순위의 증거로 취급하지 않습니다.
- 기사 본문을 재배포하지 않고 제목·짧은 인용 및 원문 링크만 제공합니다. 원문 콘텐츠 권리는 각 출처에 있습니다.


## V4.2 — Development History / PDF / PPT (2026-11-28)

전력반도체 PSI Radar 프로젝트의 History 패턴을 AI Observatory에 적용했습니다.

- 상단 **History · V4.2** 및 오른쪽 하단 **History** 버튼을 누르면 우측 버전 이력 패널이 열립니다.
- 버전별 **한 줄 요약 → WHY · WHAT · VALUE 상세**와 해당 구현 근거 GitHub 링크를 제공합니다.
- 버전 그룹(V1.x, V2.x, V4.x) 필터, 모바일 접이식 패널, 닫기/ESC를 지원합니다.
- **전체 개발 이력 PDF 및 편집 가능한 PPTX** 다운로드 버튼이 제공됩니다.
- 유일한 원본: `site/version_history.json`. 웹 History와 PDF/PPT는 해당 파일에서 생성됩니다.
- 자동 생성 스크립트: `scripts/build_history_slides.py`. 배포 전에 `tests/test_version_history.py` 및 산출물 존재 여부를 검사합니다.
- History 전용 워크플로: `.github/workflows/history.yml`. 변경 시 PDF/PPT를 재생성하고 웹을 배포합니다.
- 주간 AI 평가 자동화, 일일 AI 뉴스 자동화에서도 PDF/PPT를 다시 생성해 다운로드 파일이 사라지지 않도록 합니다.

**향후 버전 출시 규칙:** 기능을 변경할 때마다 `version_history.json`에 새 버전, 날짜, 요약, WHY·WHAT·VALUE 및 GitHub 근거 링크를 추가하고 `latest_version`을 갱신합니다. 구현 테스트가 통과하기 전에는 새 기능을 완료됐다고 표시하지 않습니다. 개발 히스토리는 주간 평가 데이터 스냅샷과 독립적으로 유지합니다.

**운영 점검 (2026-11-28):** Arena 평가의 최근 성공 주차는 2026-11-23 (559건), 뉴스 갱신은 2026-11-27 (31건)입니다. 11/25, 11/26 뉴스 워크플로의 실패는 Pages artifact metadata 조회 장애에서 발생했으며, 수집 단계 자체는 성공했습니다. Pages 배포 단계에는 실패 시 한 번 재시도하도록 개선했습니다.


## V4.3 — Weekly AI Pulse / 이번 주 한줄 평 (2026-11-28)

대시보드 제목 바로 아래에 **Weekly AI Pulse** 요약 패널을 추가했습니다. 긴 순위표에 들어가기 전에 해당 주의 주요 흐름을 간단히 파악할 수 있습니다.

- **한줄 결론:** 최근 공식 발표의 주제 분포와 Arena에서 실제 수집된 평가 영역을 표시
- **주목 주제:** 수집한 공식 뉴스의 최근 7일 주제 분포(신모델·출시/업데이트/평가·성능/연구·동향)
- **벤치마크 인사이트:** 동일 평가·카테고리·버전·모델 조건에서 직전 주 대비 점수 상승/하락 건수와 실제 모델 순위 변화 사례
- **공식 발표:** 출처가 확인된 최근 모델/업데이트/평가 관련 기사 제목과 상세 원문 링크
- **신뢰성:** 원 데이터가 부족하거나 10일 이상 오래된 경우 요약 하단에 분석 제한 표시. 통계적 유의성이나 미래 순위는 추측하지 않음

원본 생성기: `src/weekly_brief.py`; 공개 데이터: `site/data/weekly_brief.json`; UI: `site/weekly-pulse.js`, `site/weekly-pulse.css`. 자동 테스트: `tests/test_weekly_brief.py`.

**자동 업데이트 연결:** 월요일 Arena 수집과 매일 공식 뉴스 수집이 완료되면 별도의 유료 LLM/API 호출 없이 규칙 기반 한국어 한줄 평을 재생성합니다. 최초 수동 배포를 위한 `.github/workflows/brief.yml`도 제공합니다. 공식 Arena 공개 자료는 최대 100행/분야의 부분 샘플이므로 산업 전체를 대표한다고 단정하지 않습니다.

