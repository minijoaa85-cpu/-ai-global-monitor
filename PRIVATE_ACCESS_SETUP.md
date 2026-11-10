# 초대받은 사람만 보는 AI Observatory 설정 가이드

## 중요: GitHub Pages는 현재 공개
일반 개인 GitHub Pages는 이메일 기반 접근 허용목록을 제공하지 않습니다. URL을 다른 사람에게만 보내는 것으로는 접근이 제한되지 않습니다. GitHub Enterprise Cloud의 조직용 비공개 Pages 기능은 별개입니다.

## 먼저 현재 공개 사이트를 내려 주세요
1. GitHub 저장소 → Settings → Pages
2. 'Your site is live at...' 옆 점 3개 메뉴 → **Unpublish site**
3. GitHub의 **Settings → General → Danger Zone → Change repository visibility**에서 저장소를 **Private**으로 변경합니다. 과거 Artificial Analysis 데이터가 Git 기록에 남아 있으므로 비공개 전환을 권장합니다.
4. 공개 사이트에 접근제어가 설정되기 전까지 Public으로 되돌리지 마세요.
5. GitHub Actions의 `ENABLE_PUBLIC_PAGES` 변수는 **설정하지 마세요**. V4.1에서 이 변수가 `true`일 때만 기존 Pages 배포가 허용됩니다.

GitHub 공식 문서: https://docs.github.com/en/pages/getting-started-with-github-pages/unpublishing-a-github-pages-site

## 이메일 인증을 적용한 별도 사이트 (권장: Cloudflare Pages + Access)
1. https://dash.cloudflare.com/ 계정을 생성합니다.
2. Workers & Pages → Create → Pages → Connect to Git → GitHub에서 **Private** 저장소 `minijoaa85-cpu/-ai-global-monitor`를 연결합니다.
3. 프레임워크: None / 빌드 명령: 비워 둠 (필요 시 `echo ok`) / Build output directory: `site` / Root directory: 저장소 루트.
4. 배포 이후 Cloudflare Zero Trust → Access → Applications 에서 **Self-hosted application**을 만들고, 해당 **실제 프로덕션 `<project>.pages.dev` 호스트명 전체**에 정책을 설정합니다.
5. **Allow → Include → Emails**로 본인 이메일과 초대할 사람의 이메일만 추가합니다. 로그인 방식은 이메일 One-time PIN 등 원하는 인증 공급자를 선택합니다.
6. `Everyone` 또는 `Login methods: One-time PIN`만을 Allow 조건으로 넣지 마세요. 이것은 모든 이메일의 접근을 허용할 수 있습니다.
7. Cloudflare에서 preview deployment URL도 별도 차단합니다. Cloudflare Pages의 'Enable access policy' 옵션은 기본 설정으로는 **preview만 보호하고 production `*.pages.dev`는 보호하지 않을 수 있으니** production 호스트명 정책을 직접 검증해야 합니다.
8. 시크릿 브라우저에서 허용 목록에 없는 이메일로 로그인해 **차단됨**을 확인하고, 허용된 이메일로 로그인해 **정상 접속됨**을 확인합니다.
9. GitHub Pages 주소가 남아 있으면 Cloudflare Access를 우회하므로 GitHub Pages는 재게시하지 않습니다.

관련 공식 문서:
- https://developers.cloudflare.com/pages/platform/known-issues/
- https://developers.cloudflare.com/cloudflare-one/access-controls/policies/
- https://developers.cloudflare.com/cloudflare-one/access-controls/policies/common-policies/

## 파일/데이터 소유권
- GitHub에 배포 자동화 코드는 계속 보관합니다.
- Arena CC BY 4.0 데이터는 출처를 명시합니다.
- Artificial Analysis 무료 API는 공개 재배포하지 않습니다.
- 이전 Git 커밋에 남은 Artificial Analysis 데이터는 저장소 비공개 전환과 별도로 기록 삭제가 필요할 수 있습니다.

## Cloudflare 연결 전 알아둘 점
현재 연결된 GitHub 앱으로는 Cloudflare 프로젝트 계정 생성, 인증 앱 만들기, 실제 이메일 허용 목록 관리, GitHub 저장소 visibility 변경 또는 GitHub Pages unpublish 같은 관리자 작업을 수행할 수 없습니다. 본인 소유 계정에서 설정을 진행해야 합니다.
