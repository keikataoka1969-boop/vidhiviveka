#!/usr/bin/env python3
"""OCR テキストの行範囲から、ハイフン分綴を詰め、頁番号を [p.N] にした通しテキストを作る（チトラパタ用）。
見開き一枚の OCR では、左頁の頁番号が上に、右頁の頁番号が下にあり、右頁の始まりは柱「चित्रपटः」だけで示される。
そこで、頁番号の直後の柱は捨て、頁番号のない柱を次の頁の始まりとみなす。下の頁番号は、すでに出した頁なら捨てる。
使い方: mk_text.py OCRファイル 開始行 終了行 > text/partNN.txt"""
import sys, re
L = [s.strip() for s in open(sys.argv[1]).read().split('\n')]
a, b = int(sys.argv[2]), int(sys.argv[3])
d = str.maketrans('०१२३४५६७८९', '0123456789')
noise = re.compile(r'Gemini|OCR|ページ|PAGE|Page|PDF|他 \d 件|ご提示|画像|省略|テキスト|^(P|1|4|•|श्रीः)$')
pn = re.compile(r'^[०-९]{3}$')
out = ''
cur = None
prev = ''
def mark(n):
    global out, cur
    cur = n
    out = out.rstrip() + f' [p.{n}] '
for i in range(a - 1, b):
    s = L[i]
    if not s or noise.search(s):
        continue
    if pn.match(s):
        n = int(s.translate(d))
        if n != cur:
            mark(n)
        prev = 'num'
        continue
    if s == 'चित्रपटः':
        if prev != 'num' and cur is not None:
            mark(cur + 1)
        prev = 'head'
        continue
    prev = 'text'
    if re.search(r'[ऀ-ॿ]-$', out.rstrip()) and not out.rstrip().endswith('--'):
        out = out.rstrip()[:-1] + s
    else:
        out = out.rstrip() + ' ' + s
out = out.replace('।।', '॥')
out = re.sub(r'[ \t]+', ' ', out)
print(out.strip())
