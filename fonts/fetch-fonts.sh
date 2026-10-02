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
  if (subset == "") subset = "s" (++k);     # 주석 없는 블록(Noto Sans KR 한글 서브셋 480개) — 빈 필드가 되지 않게 자리표시자
  print subset "\t" $0 "}"
}' _google.css > _blocks.tsv
SRC_BLOCKS=$(grep -c "@font-face" _google.css)

: > fonts.css
echo "/* Argus CSS Framework — self-hosted fonts. fetch-fonts.sh 가 생성. 서비스 static 의 /fonts/ 에 두고 argus.min.css 보다 먼저 로드 */" >> fonts.css
n=0; seq=0
TAB=$(printf '\t')
while IFS= read -r line; do
  subset=${line%%"$TAB"*}; block=${line#*"$TAB"}   # IFS 로 쪼개지 않는다: 탭은 공백류라 선행 탭을 read 가 먹어 필드가 밀린다
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

# 3) 검증: 원본 블록 수와 같아야 하고, 한글 '한'(U+D55C) 을 담는 블록이 Noto Sans KR 굵기 수(4)만큼 있어야 한다
b=$(grep -c "@font-face" fonts.css); s=$(grep -c "url('./" fonts.css)
han=$(awk 'function pad(h){ h=tolower(h); while (length(h)<6) h="0" h; return h }
  BEGIN{RS="}"; T=pad("d55c")} /Noto Sans KR/ && /unicode-range/ {
  ur=$0; sub(/.*unicode-range: */,"",ur); sub(/;.*/,"",ur); n=split(ur,a,",");
  for(i=1;i<=n;i++){ r=a[i]; gsub(/[ \t\r\n]/,"",r); sub(/^[Uu]\+/,"",r);
    if (index(r,"-")) { lo=pad(substr(r,1,index(r,"-")-1)); hi=pad(substr(r,index(r,"-")+1)) } else { lo=pad(r); hi=lo }
    if (lo <= T && T <= hi) { c++; break } } } END{print c+0}' fonts.css)   # 16진 문자열을 6자리로 맞춰 사전순 비교 — strtonum 없는 BSD awk 에서도 동작
if [ "$b" != "$SRC_BLOCKS" ] || [ "$b" != "$s" ]; then echo "검증 실패: 원본 @font-face $SRC_BLOCKS / 결과 $b / 로컬 src $s"; exit 1; fi
if [ "$han" -lt 4 ]; then echo "검증 실패: 한글(U+D55C) 담당 Noto Sans KR 블록이 $han 개 (굵기 4개 기대) — 한글 서브셋 누락"; exit 1; fi
if [ -n "$DRY" ]; then echo "parse OK: $n/$SRC_BLOCKS blocks, 한글 블록 $han (dry run, woff2 미다운로드)"; else echo "done: $n/$SRC_BLOCKS blocks, $(ls *.woff2 | wc -l | tr -d ' ') woff2, 한글 담당 블록 $han, fonts.css"; fi
