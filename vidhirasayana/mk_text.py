#!/usr/bin/env python3
"""OCR テキストの行範囲から、ハイフン分綴を詰め、頁番号を [p.N] にした通しテキストを作る。
柱（頁番号の前後にある章名の繰り返し）は除く。
使い方: mk_text.py OCRファイル 開始行 終了行 > text/partNN.txt"""
import sys, re
L = open(sys.argv[1]).read().split('\n')
a, b = int(sys.argv[2]), int(sys.argv[3])
d = str.maketrans('०१२३४५६७८९', '0123456789')
noise = re.compile(r'Gemini|OCR|ページ|PAGE|Page|PDF|他 \d 件|ご提示|画像|省略|テキスト|^(विधिरसायनम्|चित्रपटः|P|1|4|•)$')
heads = {'अपूर्वविधिलक्षणाक्षेपः', 'परिसंख्याविध्युदाहरणाक्षेपः', 'परिसंख्याविधिलक्षणाक्षेपः', 'अपूर्वनियमविध्युदाहरणाक्षेपः',
         'नियमविधिलक्षणाक्षेपः', 'त्रिविधविधिलक्षणाक्षेपपरस्परातिदेशः', 'अपूर्वनियमपरिसंख्योदाहरणाक्षेपः',
         'अपूर्वनियमपरिसंख्याविध्युदाहरणाक्षेपसमाधानम्', 'अपूर्वनियमपरिसंख्योदाहरणाक्षेपसमाधानम्'}
pn = re.compile(r'^[०-९]{1,3}$')
drop = set()
for i in range(a - 1, b):
    if pn.match(L[i].strip()):
        for j in range(i - 3, i + 4):
            if L[j].strip() in heads:
                drop.add(j)
out = ''
glue = False
hp = re.compile(r'^(?:(\S+) ([०-९]{1,3})|([०-९]{1,3}) (\S+))$')
for i in range(a - 1, b):
    s = L[i].strip()
    m = hp.match(s)
    if m and (m.group(1) or m.group(4)) in heads | {'विधिरसायनम्'}:
        s = m.group(2) or m.group(3)
    if not s or noise.search(s) or i in drop:
        continue
    if pn.match(s):
        if re.search(r'[ऀ-ॿ]-$', out.rstrip()):
            out = out.rstrip()[:-1] + f'[p.{s.translate(d)}]'
            glue = True
        else:
            out = out.rstrip() + f' [p.{s.translate(d)}] '
            glue = False
        continue
    if glue:
        out += s
        glue = False
        continue
    if re.search(r'[ऀ-ॿ]-$', out.rstrip()) and not out.rstrip().endswith('--'):
        out = out.rstrip()[:-1] + s
    else:
        out = out.rstrip() + ' ' + s
out = out.replace('।।', '॥')
out = re.sub(r'[ \t]+', ' ', out)
print(out.strip())
