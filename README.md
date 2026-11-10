# Global AI Benchmark Monitor

공식 출처별 생성형 AI 모델 벤치마크 점수를 주간 수집하여 모델 순위와 장기 추세를 비교하는 개인용 웹 대시보드입니다.

## 배포
1. GitHub 저장소 **Settings → Pages → Build and deployment → Source** 에서 **GitHub Actions**를 선택하세요.
2. **Actions → Publish AI benchmark dashboard → Run workflow** 에서 초기 배포를 실행할 수 있습니다. main에 site 폴더 변경이 발생하면 다시 배포됩니다.
3. 배포 주소: https://minijoaa85-cpu.github.io/-ai-global-monitor/
4. **Actions → Weekly AI benchmark collection → Run workflow** 를 눌러 최초 수집을 실행하세요.
5. Actions의 녹색 체크 표시와 대시보드의 "평가기관 연결 상태"를 확인하세요.

## API 설정 (중요)
- Artificial Analysis: Settings → Secrets and variables → Actions → Secrets → New repository secret. 이름 `AA_API_KEY`로 API 키를 등록하세요. **비밀 키를 코드/채팅에 넣지 마세요.**
- Hugging Face: Actions Variables에 `HF_BENCHMARK_DATASETS` 를 추가할 수 있으나, 실제 데이터셋이 leaderboard endpoint를 제공하는지 별도 확인이 필요합니다.
- LiveBench: 현재 어댑터는 공식 자료 구조 확인을 위한 탐색 단계로 실제 점수 수집은 **미구현**입니다. 실패나 미구현을 성공으로 표시하지 않습니다.

## 매주 자동화
매주 **월요일 오전 9시 20분 KST** (00:20 UTC) GitHub Actions에서 `src/monitor.py`를 실행합니다. `src/report.py`는 `site/weekly-report.html`을 생성하고 data JSON을 함께 커밋합니다. 공개 사이트에 이 파일들이 자동 반영됩니다.

## 데이터 해석
- 비어 있는 데이터는 0점이 아니며, 실제 인증/수집이 필요합니다.
- 서로 다른 지표를 합쳐 근거 없는 종합 순위를 만들지 않습니다.
- 지표 버전이 달라지면 점수를 직접 비교하지 않습니다.
- 공개 사이트에 데이터 게시 시 각 제공기관의 라이선스와 데이터 재배포 조건을 준수하세요. Artificial Analysis 무료 API의 공개 재배포는 별도 확인이 필요할 수 있습니다.
- API 스키마/엔드포인트가 바뀌면 해당 수집기를 수정해야 합니다.

## 로컬 확인
```bash
python src/monitor.py
python src/report.py
python -m http.server 8000 -d site
```
http://localhost:8000 에서 확인할 수 있습니다.

**중요:** 프로젝트 설치와 실제 외부 API 데이터 수집 성공은 별개의 단계입니다. 데이터 수집 성공 여부는 Actions 로그 및 site/data/status.json으로 확인하세요.
