#!/bin/bash
# Render, copy to gh-pages worktree, update root index, commit & push; sync sources to dev branch.
set -e
SRC=/home/user/erkenntnis; PAGES=/home/user/vv-pages; DEV=/home/user/vidhiviveka
MSG="$1"
python3 -I $SRC/tools/render.py
cp $SRC/site/iast-fonts.css $SRC/site/erkenntnis/; touch $SRC/site/erkenntnis/.nojekyll
cd $PAGES && git fetch -q origin gh-pages && git reset -q --hard FETCH_HEAD
rm -rf $PAGES/erkenntnis && cp -r $SRC/site/erkenntnis $PAGES/erkenntnis
python3 -I - <<'PY'
import re,json,os
meta=json.load(open('/home/user/erkenntnis/data/meta.json',encoding='utf-8'))
R=['','Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ','Ⅵ','Ⅶ','Ⅷ','Ⅸ','Ⅹ','ⅩⅠ','ⅩⅡ','ⅩⅢ','ⅩⅣ','ⅩⅤ','ⅩⅥ','ⅩⅦ','ⅩⅧ','ⅩⅨ','ⅩⅩ','ⅩⅩⅠ','ⅩⅩⅡ','ⅩⅩⅢ','ⅩⅩⅣ','ⅩⅩⅤ']
done=[n for n in range(1,26) if os.path.exists('/home/user/vv-pages/erkenntnis/kapitel_%02d.html'%n)]
lis=''.join('<li><a href="erkenntnis/kapitel_%02d.html">第%s章 %s</a></li>\n'%(n,R[n],meta['chapters_jp'][n-1]) for n in done)
p='/home/user/vv-pages/index.html'; s=open(p,encoding='utf-8').read()
s=re.sub(r'(<!-- erkenntnis-chapters -->\n)(.*?)(</ul>)',lambda m:m.group(1)+lis+m.group(3),s,count=1,flags=re.S)
open(p,'w',encoding='utf-8').write(s)
PY
git add -A erkenntnis index.html
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01CRhRi1YqMjsVSu8MvJ585s"
for i in 1 2 3 4; do git push -q origin HEAD:gh-pages && break; sleep $((2**i)); done
cd $DEV && rm -rf erkenntnis-src/tools erkenntnis-src/data && mkdir -p erkenntnis-src && cp -r $SRC/tools $SRC/data $SRC/README.md erkenntnis-src/ && rm -rf erkenntnis-src/tools/__pycache__
git add -A erkenntnis-src
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "$MSG (sources)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01CRhRi1YqMjsVSu8MvJ585s" || true
for i in 1 2 3 4; do git push -q origin claude/relaxed-cori-9lrpau && break; sleep $((2**i)); done
echo PUBLISHED
