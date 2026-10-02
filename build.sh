#!/usr/bin/env sh
# css/*.css 를 순서대로 합쳐 dist/ 를 만든다. 빌드 도구 의존 없음 (lightningcss 있으면 minify 품질↑).
# dist/ 는 배포 전용 — 전부 minified, 소스는 css/ js/.
#   dist/argus.min.css              전체 (가장 단순한 선택)
#   dist/argus.core.min.css         tokens+base+layout+components+utilities — 최소 세트
#   dist/argus.patterns.min.css     인증·사이드바·로그·Slack·배너·알림… 도메인 패턴 (core 뒤에 로드)
#   dist/argus.charts.min.css       CSS 차트 + Apex/Chart.js 보정 (차트 있는 페이지만)
#   dist/argus.auth-landing.min.css 랜딩형 인증 변형 (선택, 거의 안 씀)
#   dist/themes/<color>.min.css           컬러 테마 (red orange yellow green blue indigo violet)
#   dist/argus.js / .charts.js      선택 JS 헬퍼 (minified)
#   dist/VERSION
# 사람이 읽는 합본이 필요하면 `sh build.sh --readable` → dist/argus.css 추가 생성.
set -e
cd "$(dirname "$0")"
VERSION="1.1.0"
CORE="tokens base layout components utilities"
ORDER="tokens base layout components charts patterns utilities"

# 린트: tokens.css 와 themes/ 밖의 hex 리터럴은 허용 목록(흰/검 글자, 마스크, Slack·Google 버튼, @media print 회색)만
BAD=$(grep -nE "#[0-9a-fA-F]{3,8}\b" css/base.css css/layout.css css/components.css css/charts.css css/patterns.css css/utilities.css css/extras/*.css \
  | grep -vE "#fff\b|#ffffff|#000\b|#0b1a14|#1a1400|#04111a|#04110b|#2eb67d|#259e6b|#e01e5a|#c01b4f|#1f1f1f|#dadce0|#f8f9fa|#c6c6c6|#131314|#e3e3e3|#8e918f|#1b1b1c|#6ee7b7|#fda4af|#111\b|#333\b|#555\b|#999\b|#bbb\b|#ddd\b|#eee\b|#f3f3f3|data:image" || true)
if [ -n "$BAD" ]; then echo "리터럴 색상 발견 — 토큰으로 바꾸거나 build.sh 허용 목록에 추가:"; echo "$BAD"; exit 1; fi

rm -rf dist && mkdir -p dist/themes
BANNER="/*! Argus CSS Framework v$VERSION — 어드민 페이지용 디자인 시스템 | 다크 기본 / data-theme=\"light\" */"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

LCSS=""; for c in ./node_modules/.bin/lightningcss lightningcss; do command -v "$c" >/dev/null 2>&1 && { LCSS="$c"; break; }; done
[ -z "$LCSS" ] && npx --no-install lightningcss --version >/dev/null 2>&1 && LCSS="npx --no-install lightningcss"
if [ -n "$LCSS" ]; then MIN="lightningcss"; else MIN="sed"; fi
minify() { # $1 in, $2 out
  if [ "$MIN" = lightningcss ]; then
    $LCSS --minify --targets ">= 0.5%, last 2 versions, not dead" "$1" -o "$2"
  else
    { echo "$BANNER"; sed -e 's,/\*[^!][^*]*\*\+\([^/*][^*]*\*\+\)*/,,g' "$1" | tr -s ' \n\t' ' ' | sed -e 's/ *\([{};:,>]\) */\1/g' -e 's/;}/}/g'; } > "$2"
  fi
}
concat() { # $1 out, rest = module names
  out="$1"; shift
  { echo "$BANNER"; for f in "$@"; do echo; cat "css/$f.css"; done; } > "$out"
}

concat "$TMP/full.css" $ORDER
concat "$TMP/core.css" $CORE
concat "$TMP/patterns.css" patterns
concat "$TMP/charts.css" charts
minify "$TMP/full.css"     dist/argus.min.css
minify "$TMP/core.css"     dist/argus.core.min.css
minify "$TMP/patterns.css" dist/argus.patterns.min.css
minify "$TMP/charts.css"   dist/argus.charts.min.css
minify css/extras/auth-landing.css dist/argus.auth-landing.min.css
for t in css/themes/*.css; do n=$(basename "$t" .css); case "$n" in _*) continue;; esac; minify "$t" "dist/themes/$n.min.css"; done
[ "$1" = "--readable" ] && cp "$TMP/full.css" dist/argus.css

printf "%s\n" "$VERSION" > dist/VERSION

# JS: 모듈 합본 → 가능하면 minify (esbuild/terser 가 있을 때), 없으면 주석·공백만 정리
{ echo "/*! Argus CSS Framework v$VERSION — 선택 JS 헬퍼 (js/modules 합본, 각 IIFE 독립) */"; for m in js/modules/*.js; do echo; cat "$m"; done; } > "$TMP/ag.js"
# JS minifier 탐색 순서: 저장소 node_modules/.bin (npm i 로 설치) → PATH → npx 캐시. 없으면 주석·공백 제거만
ESBUILD=""; for c in ./node_modules/.bin/esbuild esbuild; do command -v "$c" >/dev/null 2>&1 && { ESBUILD="$c"; break; }; done
[ -z "$ESBUILD" ] && npx --no-install esbuild --version >/dev/null 2>&1 && ESBUILD="npx --no-install esbuild"
jsmin() { # $1 in, $2 out
  if [ -n "$ESBUILD" ]; then $ESBUILD --minify --log-level=error "$1" > "$2"
  elif npx --no-install terser --version >/dev/null 2>&1; then npx --no-install terser -c -m -o "$2" "$1"
  else sed -E -e 's,^[[:space:]]*//.*$,,' -e 's,/\*[^!][^*]*\*/,,g' -e 's/^[[:space:]]+//' "$1" | grep -v '^$' > "$2"; fi
}
jsmin "$TMP/ag.js" dist/argus.js
jsmin js/argus.charts.js dist/argus.charts.js

echo "minifier: css=$MIN js=${ESBUILD:-sed}"
for f in dist/*.min.css dist/*.js; do printf "%-42s %7d bytes  gzip %6d\n" "$f" "$(wc -c < "$f")" "$(gzip -9c "$f" | wc -c)"; done
