#!/usr/bin/env sh
# Google Fonts 에서 Manrope / Noto Sans KR / JetBrains Mono woff2 를 받아 self-host 용으로 정리한다.
# 인터넷이 되는 PC 에서 한 번 실행 → fonts/*.woff2 + fonts/fonts.css 생성 → 서비스 static 에 복사.
#   sh fonts/fetch-fonts.sh
# 폐쇄망에서 Google Fonts 가 막혀 있어도, 이 결과물을 쓰면 폰트가 항상 같은 모양으로 나온다.
#
# 결과: fonts.css 는 원본 @font-face 블록(font-family / font-style / font-weight / font-display / unicode-range)을
#       그대로 유지하고 src 만 로컬 파일로 바꾼다. 파일명은 NotoSansKR-400-korean-12.woff2 꼴.
# 테스트: GOOGLE_CSS=path/to/saved.css sh fetch-fonts.sh  (다운로드 없이 파싱만 검증. woff2 는 받지 않음)
set -e
cd "$(dirname "$0")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
URL="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"

if [ -n "$GOOGLE_CSS" ]; then cp "$GOOGLE_CSS" _google.css; DRY=1; else curl -sS -A "$UA" "$URL" -o _google.css; DRY=; fi
grep -q "@font-face" _google.css || { echo "Google Fonts CSS 를 받지 못했습니다 (프록시/네트워크 확인). 내용:"; head -c 300 _google.css; echo; rm -f _google.css; exit 1; }

# 1) @font-face 블록을 한 줄 하나로 펴서(awk, RS="}") 줄 단위 처리가 블록을 끊지 않게 한다.
#    각 줄: <subset>\t<block>   — subset 은 블록 바로 앞 주석 (/* korean */, /* [12] */, /* latin-ext */ …)
awk 'BEGIN{RS="}"} /@font-face/{
  sub(/^[ \t\r\n]+/,""); subset="";
  if (match($0,/\/\*[^*]*\*\//)) { subset=substr($0,RSTART+2,RLENGTH-4); gsub(/[ \[\]]/,"",subset); sub(/\/\*[^*]*\*\//,""); }
  gsub(/[\r\n]+/," "); gsub(/  +/," "); sub(/^ +/,""); sub(/ +$/,"");
  print subset "\t" $0 "}"
}' _google.css > _blocks.tsv

: > fonts.css
echo "/* Argus CSS Framework — self-hosted fonts. fetch-fonts.sh 가 생성. 서비스 static 의 /fonts/ 에 두고 argus.min.css 보다 먼저 로드 */" >> fonts.css
n=0; seq=0
while IFS="$(printf '\t')" read -r subset block; do
  fam=$(printf '%s' "$block" | sed -n "s/.*font-family: *'\([^']*\)'.*/\1/p" | tr -d ' ')
  wt=$(printf '%s' "$block" | sed -n 's/.*font-weight: *\([0-9]*\).*/\1/p')
  src=$(printf '%s' "$block" | sed -n 's/.*url(\([^)]*\)).*/\1/p')
  [ -z "$src" ] && continue
  seq=$((seq+1))
  file="${fam:-font}-${wt:-400}-${subset:-$seq}.woff2"
  [ -e "$file" ] && file="${fam:-font}-${wt:-400}-${subset:-x}-${seq}.woff2"
  if [ -z "$DRY" ]; then curl -sS -A "$UA" "$src" -o "$file"; fi
  # 2) 블록은 그대로, src 만 교체. 보기 좋게 선언마다 줄바꿈.
  printf '%s\n' "$block" | sed "s#url([^)]*)#url('./$file')#" \
    | awk '{ sub(/\{ */,"{\n  "); gsub(/; */,";\n  "); sub(/\n  *\}/,"\n}"); sub(/ *\}$/,"\n}"); print }' | sed '/^ *$/d' >> fonts.css   # BSD sed 호환: 줄바꿈은 awk 로
  echo "" >> fonts.css
  n=$((n+1))
done < _blocks.tsv
rm -f _google.css _blocks.tsv

# 3) 검증: 블록 수 == font-family 수 == unicode-range 수 == 로컬 url 수
b=$(grep -c "@font-face" fonts.css); f=$(grep -c "font-family" fonts.css); u=$(grep -c "unicode-range" fonts.css); s=$(grep -c "url('./" fonts.css)
if [ "$b" != "$f" ] || [ "$b" != "$s" ]; then echo "검증 실패: @font-face $b / font-family $f / unicode-range $u / src $s"; exit 1; fi
if [ -n "$DRY" ]; then echo "parse OK: $n blocks (dry run, woff2 미다운로드)"; else echo "done: $n blocks, $(ls *.woff2 | wc -l | tr -d ' ') woff2, fonts.css ($b @font-face, $u unicode-range)"; fi
