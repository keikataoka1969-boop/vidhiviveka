#!/usr/bin/env python3
"""OCR テキストの行範囲から、ハイフン分綴を詰め、頁番号を [p.N] にした通しテキストを作る（ディーピカー用）。
柱「पूर्वमीमांसाविषयसङ्ग्रहदीपिका」は除く。頁番号の行はその頁の始まりとみなす。
使い方: mk_text.py OCRファイル 開始行 終了行 > text/partN.txt"""
import sys, re
L = [s.strip().replace('‌', '') for s in open(sys.argv[1]).read().split('\n')]
a, b = int(sys.argv[2]), int(sys.argv[3])
d = str.maketrans('०१२३४५६७८९', '0123456789')
noise = re.compile(r'Gemini|OCR|ページ|PAGE|Page|PDF|他 \d 件|ご提示|画像|省略|テキスト|ファイル|^(P|1|4|•|श्रीः)$')
head = 'पूर्वमीमांसाविषयसङ्ग्रहदीपिका'
pn = re.compile(r'^[०-९]{3}$')
out = ''
for i in range(a - 1, b):
    s = L[i].lstrip('• ').strip()
    if not s or noise.search(s) or s == head:
        continue
    if pn.match(s):
        out = out.rstrip() + f' [p.{int(s.translate(d))}] '
        continue
    if re.search(r'[ऀ-ॿ]-$', out.rstrip()) and not out.rstrip().endswith('--'):
        out = out.rstrip()[:-1] + s
    else:
        out = out.rstrip() + ' ' + s
out = out.replace('।।', '॥')
out = re.sub(r'[ \t]+', ' ', out)
print(out.strip())
