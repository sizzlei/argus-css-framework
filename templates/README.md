# Go html/template 적용 예시

프레임워크를 실제 서버 템플릿(Go `html/template` + Alpine.js)에 적용한 예. 원본 서비스의 Alpine 바인딩·템플릿 변수·JS 는 손대지 않고 class 만 `ag-` 로 바꾼 상태라, 같은 구조의 서비스라면 그대로 복사해 쓸 수 있다.

| 경로 | 내용 |
|---|---|
| `go-html-template/layouts/auth.html` | 인증 레이아웃. Tailwind CDN·인라인 style 대신 `argus.min.css` + 테마 한 장 로드 |
| `go-html-template/login.html` | 이메일 → OTP → QR 등록 3단계 로그인. 표준 `.ag-auth` (examples/login.html 과 같은 디자인). 잠금 해제 모달은 `.ag-modal-overlay`. 그라데이션 패널을 원하면 `ag-auth--landing` 클래스만 추가 (+ `argus.auth-landing.min.css`) |

적용: `dist/argus.min.css`, `dist/themes/<color>.min.css` 를 서비스 static 에 복사한 뒤 두 파일을 참고해 템플릿을 고친다. `{{asset}}` 헬퍼와 `.Version .Env .Commit` 변수는 예시용 — 서비스의 것으로 바꾼다.

정적 미리보기: `examples/login.html` (컬러 셀렉터로 blue 선택).
