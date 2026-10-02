#!/usr/bin/env sh
# Google Fonts 에서 Manrope / Noto Sans KR / JetBrains Mono woff2 를 받아 self-host 용으로 정리한다.
# 인터넷이 되는 PC 에서 한 번 실행 → fonts/*.woff2 + fonts/fonts.css 생성 → 서비스 static 에 복사.
#   sh fonts/fetch-fonts.sh
# 폐쇄망에서 Google Fonts 가 막혀 있어도, 이 결과물을 쓰면 폰트가 항상 같은 모양으로 나온다.
set -e
cd "$(dirname "$0")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
URL="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
curl -sS -A "$UA" "$URL" -o _google.css
# url(...) 을 로컬 파일로 바꾸고 다운로드
i=0
: > fonts.css
echo "/* Argus CSS Framework — self-hosted fonts. fetch-fonts.sh 가 생성. 서비스 static 의 /fonts/ 에 두고 argus.min.css 보다 먼저 로드 */" >> fonts.css
awk 'BEGIN{RS="}"} /@font-face/{print $0"}"}' _google.css | while IFS= read -r block; do
  [ -z "$block" ] && continue
  fam=$(echo "$block" | sed -n "s/.*font-family: *'\([^']*\)'.*/\1/p" | tr ' ' '-' )
  wt=$(echo "$block" | sed -n 's/.*font-weight: *\([0-9]*\).*/\1/p')
  src=$(echo "$block" | sed -n 's/.*url(\([^)]*\)).*/\1/p')
  ur=$(echo "$block" | sed -n 's/.*unicode-range: *\([^;]*\);.*/\1/p' | tr -d ' ' | cut -c1-12 | tr '+,' '__')
  [ -z "$src" ] && continue
  i=$((i+1))
  file="${fam}-${wt}-${i}.woff2"
  curl -sS -A "$UA" "$src" -o "$file"
  echo "$block" | sed "s#url([^)]*)#url('./$file')#" >> fonts.css
  echo "" >> fonts.css
done
rm -f _google.css
echo "done: $(ls *.woff2 | wc -l) files, fonts.css"
