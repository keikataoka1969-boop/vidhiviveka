#!/usr/bin/env python3
"""OCR テキストの行範囲から、ハイフン分綴を詰め、頁番号を [p.N] にした通しテキストを作る。
使い方: mk_text.py OCRファイル 開始行 終了行 > text/vadaNN.txt"""
import sys, re
L = open(sys.argv[1]).read().split('\n')
a, b = int(sys.argv[2]), int(sys.argv[3])
d = str.maketrans('०१२३४५६७८९', '0123456789')
noise = re.compile(r'Gemini|OCR|ページ|PAGE|Page|PDF|他 \d 件|ご提示|画像|省略|テキスト|^(पूर्वोत्तरमीमांसा|वादनक्षत्रमाला|उपक्रमपराक्रमः|विधिरसायनम्|चित्रपटः|P|1|•)$')
out = ''
for i in range(a - 1, b):
    s = L[i].strip()
    if not s or noise.search(s):
        continue
    if re.fullmatch(r'[०-९]{3}', s):
        out = out.rstrip() + f' [p.{s.translate(d)}] '
        continue
    if re.search(r'[ऀ-ॿ]-$', out.rstrip()) and not out.rstrip().endswith('--'):
        out = out.rstrip()[:-1] + s
    else:
        out = out.rstrip() + ' ' + s
    out += ' '
out = re.sub(r'(?<=[ऀ-ॿ])- (?=[ऀ-ॿ])', '', out)
out = re.sub(r'(?<=[\u0900-\u097F])- (\[p\.\d+\]) ', r'\1', out)
out = out.replace('।।', '॥')
out = re.sub(r'[ \t]+', ' ', out)
# 各段の見出しと論の区切りで改行して読みやすくする（スライスには影響しない）
out = re.sub(r' (?=अथ [^ ]* ?[^ ]* ?[^ ]*कक्ष्या)', '\n', out)
print(out.strip())
