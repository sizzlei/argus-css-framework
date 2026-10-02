# 컬러 테마

앱마다 메인 색(액센트)만 다르게 가져간다. 공통인 것은 표면·텍스트·간격·컴포넌트 모양·상태색·차트 범주색이고,
`--ag-accent` 계열과 브랜드 마크 그라데이션만 테마 파일이 덮어쓴다.

```html
<link rel="stylesheet" href="/static/argus.min.css">
<link rel="stylesheet" href="/static/themes/blue.min.css">   <!-- 이 한 줄이 앱의 색 -->
```

기본 제공 7종: `red` `orange` `yellow` `green` `blue` `indigo` `violet` (violet 은 프레임워크 기본값과 같다).
원색 그대로가 아니라 한 톤 눌러 자연스럽게 맞춘 값이고, 각 파일은 다크·라이트 두 블록을 모두 정의한다.
새 색은 `_template.css` 를 복사해 값만 채운다. `--ag-text-on-accent` 는 액센트 위 글자색 — 밝은 액센트(노랑·초록)는
어두운 글자가 필요하므로 꼭 확인한다 (대비 4.5:1).
