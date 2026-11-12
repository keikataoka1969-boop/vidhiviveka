#!/usr/bin/env python3
"""Build the Kumārasambhava I–VII bilingual HTML (Devanagari / IAST switchable)."""
import re, html as H, sys
from indic_transliteration import sanscript as S

import os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kumarasambhava_bilingual_sarga0%d.md')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'kumarasambhava-bilingual.html'
ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
DEV = re.compile(r'[ऀ-ॿ]')
JPN = re.compile(r'[぀-ヿ一-鿿]')

SARGAS = [
    (1, 'प्रथमः सर्गः', 'उमोत्पत्तिः', 'Umotpatti', '第一章', 'ウマーの誕生', 'upajāti', 59,
     'ヒマーラヤ山の威容と、その娘パールヴァティー（ウマー）の誕生・成長を描く。ナーラダがシヴァとの結婚を予言する。シヴァが苦行のためヒマーラヤに来ると、ヒマヴァットは娘をシヴァへの奉仕に遣わす。'),
    (2, 'द्वितीयः सर्गः', 'ब्रह्मसाक्षात्कारः', 'Brahmasākṣātkāra', '第二章', 'ブラフマーの教示', 'anuṣṭubh', 64,
     'ターラカが苦行で得た恩恵によって神々を苦しめる。神々はブラフマーに訴え、ブラフマーは「シヴァの息子だけがターラカを倒せる」と教える。インドラはカーマに、シヴァの心をパールヴァティーに向けさせる任務を与える。'),
    (3, 'तृतीयः सर्गः', 'मदनदहनम्', 'Madanadahana', '第三章', 'カーマの焼死', 'upajāti', 76,
     '時ならぬ春の到来とともに、カーマがシヴァの瞑想を破ろうと矢をつがえる。シヴァは第三の目の火でカーマを灰にする。ヒマヴァットは怯えた娘を抱いて立ち去る。'),
    (4, 'चतुर्थः सर्गः', 'रतिविलापः', 'Rativilāpa', '第四章', 'ラティの嘆き', 'vaitālīya', 46,
     'カーマの妻ラティが夫の灰の前で嘆く長大な独白。春の神ヴァサンタに火葬の薪を求め殉死しようとするが、天の声が「シヴァがパールヴァティーを娶るとき、カーマは再び身体を得る」と告げ、ラティは思いとどまる。'),
    (5, 'पञ्चमः सर्गः', 'तपःफलोदयः', 'Tapaḥphalodaya', '第五章', 'パールヴァティーの苦行', 'vaṃśastha', 85,
     'パールヴァティーは装身具を捨て、樹皮衣をまとって峻烈な苦行に入る。そこへバラモンの青年（変装したシヴァ）が現れ、シヴァを貶めて彼女の心を試す。彼女が怒って立ち去ろうとすると、シヴァは正体を現し「今日からあなたの僕だ」と告げる。'),
    (6, 'षष्ठः सर्गः', 'उमाप्रदानम्', 'Umāpradāna', '第六章', '七仙の使い', 'anuṣṭubh', 94,
     'シヴァに呼ばれた七仙がヒマヴァットの都オーシャディプラスタを訪れ、パールヴァティーとの婚姻を申し込む。ヒマヴァットは妻メーナーの同意を得て、娘をシヴァに与えることを約し、婚礼の日取りが定まる。'),
    (7, 'सप्तमः सर्गः', 'उमापरिणयः', 'Umāpariṇaya', '第七章', 'パールヴァティーの婚礼', 'upajāti', 95,
     '都をあげた婚礼の支度と花嫁の装い。シヴァは神々を従えて牡牛に乗り都へ向かう。窓辺に群がる都の女たち（第57–63偈）。手取りの儀、火の周りを巡る儀を経て婚礼が成り、二人は新婚の間に入る。'),
]

# ---------------------------------------------------------------- helpers
def iast(dev):
    t = S.transliterate(dev, S.DEVANAGARI, S.IAST)
    return t.replace("'", '’')

def md_inline(t):
    t = H.escape(t, quote=False)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', t)
    return t

def clean_skt(line):
    s = line.strip().strip('*').strip()
    s = s.rstrip('\\').strip()
    return s

def is_colophon_skt(s):
    x = s.strip('॥ ').strip()
    return x.startswith('इति') and ('सर्ग' in x)

def strip_num(s):
    # remove trailing verse numbers ॥१२॥ / ॥ ६४–६८ ॥ and dandas
    s = re.sub(r'\s*॥[^॥]*॥\s*$', '', s)
    s = re.sub(r'\s*[।॥]+\s*$', '', s)
    return s.strip()

COMM_START = [
    (lambda s: s.startswith('> **注') or s.startswith('> **〔注〕'), r'^>\s*\*\*〔?注〕?\*\*\s*[:：]?\s*'),
    (lambda s: s.startswith('> Vallabhadeva 注'), r'^>\s*Vallabhadeva\s*注\s*[:：]?\s*'),
    (lambda s: s.startswith('〔注〕'), r'^〔注〕\s*'),
]

def parse(sarga):
    text = open(BASE % sarga, encoding='utf-8').read()
    verses, colophon_skt, colophon_jp = [], [], []
    for sec in re.split(r'\n---+\n', text):
        sec = sec.strip()
        m = (re.match(r'###\s+' + ROMAN[sarga] + r'\.(\d+(?:[–\-]\d+)?)', sec)
             or re.match(r'##\s+第(\d+(?:[–\-]\d+)?)偈', sec))
        if not m:
            continue
        vid = m.group(1).replace('-', '–')
        kulaka = 'कुलकम्' in sec.split('\n', 1)[0]
        body = sec.split('\n', 1)[1] if '\n' in sec else ''
        lines = body.split('\n')
        skt, jp, comm = [], [], []
        state = 'skt'
        for i, raw in enumerate(lines):
            s = raw.strip()
            if not s:
                if state == 'skt' and skt:
                    nxt = next((l.strip() for l in lines[i + 1:] if l.strip()), '')
                    n2 = clean_skt(nxt)
                    if not (DEV.search(n2) and not JPN.search(n2) and not nxt.startswith('>') and not nxt.startswith('〔')):
                        state = 'jp'
                continue
            cs = None
            for test, rx in COMM_START:
                if test(s):
                    cs = re.sub(rx, '', s); break
            if cs is not None:
                state = 'comm'
                if cs.strip(): comm.append(cs.strip())
                continue
            if state == 'comm':
                comm.append(re.sub(r'^>\s*', '', s)); continue
            c = clean_skt(s)
            if state == 'skt' and DEV.search(c) and not JPN.search(c) and not s.startswith('>'):
                if is_colophon_skt(c):
                    colophon_skt.append(c.strip('॥ ').strip()); continue
                skt.append(c); continue
            if '॥' in s and JPN.search(s) and ('終' in s):
                colophon_jp.append(s.strip('॥ ').strip()); continue
            if DEV.search(c) and is_colophon_skt(c):
                colophon_skt.append(c.strip('॥ ').strip()); continue
            state = 'jp' if state == 'skt' else state
            if s.startswith('>'):
                s = re.sub(r'^>\s*', '', s)
            jp.append(s.rstrip())
        if skt or jp:
            verses.append(dict(id=vid, kulaka=kulaka, skt=skt, jp=jp, comm=comm))
    return verses, colophon_skt, colophon_jp

def render_skt(lines):
    out = []
    for ln in lines:
        d = strip_num(ln)
        if not d:
            continue
        out.append(
            '<span class="ln"><span class="dev" lang="sa-Deva">%s</span>'
            '<span class="iast" lang="sa-Latn">%s</span></span>' % (H.escape(d), H.escape(iast(d))))
    return '\n'.join(out)

def render_jp(lines):
    paras, cur = [], []
    for l in lines:
        cur.append(md_inline(l.strip()))
    if cur:
        paras.append('<br>'.join(cur))
    return ''.join('<p>%s</p>' % p for p in paras)

# ---------------------------------------------------------------- build
sections, total = [], 0
for (n, skt_title, skt_sub, sub_iast, jp_no, jp_title, metre, count, syn) in SARGAS:
    verses, col_skt, col_jp = parse(n)
    total += len(verses)
    blocks = []
    for v in verses:
        label = '%s.%s' % (ROMAN[n], v['id'])
        anchor = 'v%d-%s' % (n, v['id'].replace('–', '-'))
        extra = '<span class="tag">kulaka</span>' if v['kulaka'] else ''
        comm = ''
        if v['comm']:
            comm = ('<aside class="note"><span class="note-h">Vallabhadeva 注</span>%s</aside>'
                    % ''.join('<p>%s</p>' % md_inline(c) for c in [' '.join(v['comm'])]))
        blocks.append(
            '<article class="verse" id="%s">'
            '<a class="vno" href="#%s">%s</a>%s'
            '<div class="cols"><div class="skt">%s</div><div class="jp">%s</div></div>%s'
            '</article>' % (anchor, anchor, label, extra, render_skt(v['skt']), render_jp(v['jp']), comm))
    colo = ''
    if col_skt or col_jp:
        colo = '<div class="sarga-end">%s%s</div>' % (
            ''.join('<p class="dev-only"><span class="dev" lang="sa-Deva">॥ %s ॥</span><span class="iast">|| %s ||</span></p>' % (H.escape(c), H.escape(iast(c))) for c in col_skt[:1]),
            ''.join('<p class="jp-colo">%s</p>' % H.escape(c) for c in col_jp[:1]))
    sections.append(
        '<section class="sarga" id="sarga%d">'
        '<header class="sarga-h"><div class="sarga-no">%s</div>'
        '<h2><span class="dev" lang="sa-Deva">%s</span><span class="iast">%s</span></h2>'
        '<p class="sarga-jp">%s　%s</p>'
        '<p class="sarga-meta"><span class="dev" lang="sa-Deva">%s</span><span class="iast">%s</span> · 韻律 %s · 全%d偈</p>'
        '<p class="sarga-syn">%s</p></header>%s%s'
        '<a class="totop" href="#top">目次へ戻る</a></section>'
        % (n, ROMAN[n], skt_title, iast(skt_title), jp_no, jp_title, skt_sub, sub_iast, metre, count, syn,
           '\n'.join(blocks), colo))
    print('Sarga %d: %d verse blocks' % (n, len(verses)))

toc = ''.join(
    '<a class="card" href="#sarga%d"><span class="card-no">%s</span>'
    '<span class="card-skt"><span class="dev" lang="sa-Deva">%s</span><span class="iast">%s</span></span>'
    '<span class="card-jp">%s　%s</span><span class="card-n">%d偈 · %s</span>'
    '<span class="card-syn">%s</span></a>'
    % (n, ROMAN[n], skt_sub, sub_iast, jp_no, jp_title, c, m, syn)
    for (n, st, skt_sub, sub_iast, jp_no, jp_title, m, c, syn) in SARGAS)
jump = ''.join('<a href="#sarga%d">%s</a>' % (n, ROMAN[n]) for n in range(1, 8))

CSS = open(__file__.replace('build.py', 'style.css'), encoding='utf-8').read()
JS = open(__file__.replace('build.py', 'app.js'), encoding='utf-8').read()

page = '''<!doctype html>
<html lang="ja" data-script="dev" data-notes="on">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>クマーラサンバヴァ対訳</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+Devanagari:wght@400;600&family=Noto+Serif:ital,wght@0,400;0,600;1,400&family=Shippori+Mincho:wght@400;600&display=swap">
<style>%s</style>
</head>
<body>
<div id="top"></div>
<div class="bar" role="toolbar" aria-label="表示の設定">
  <a class="bar-title" href="#top">Kumārasambhava</a>
  <div class="seg" role="group" aria-label="サンスクリットの文字">
    <button type="button" data-set-script="dev" aria-pressed="true">देवनागरी</button>
    <button type="button" data-set-script="iast" aria-pressed="false">IAST</button>
    <button type="button" data-set-script="both" aria-pressed="false">併記</button>
  </div>
  <button type="button" class="notes-btn" data-toggle-notes aria-pressed="true">注</button>
  <nav class="jump" aria-label="章へ移動">%s</nav>
</div>

<header class="masthead">
  <p class="mh-dev"><span class="dev" lang="sa-Deva">कुमारसम्भवम्</span><span class="iast">Kumārasambhavam</span></p>
  <h1>クマーラサンバヴァ対訳</h1>
  <p class="mh-sub">カーリダーサ作・第一章〜第七章　ヴァッラバデーヴァ注（シャーラダー本）に基づく</p>
</header>

<section class="front">
  <h2 class="front-h">目次と内容梗概</h2>
  <div class="cards">%s</div>
</section>

<section class="front biblio">
  <h2 class="front-h">底本と凡例</h2>
  <p class="bib">M. S. Narayana Murti (ed.), unter Mitarbeit von Klaus L. Janert, <i>Vallabhadeva’s Kommentar (Śāradā-Version) zum Kumārasambhava des Kālidāsa</i>. Verzeichnis der orientalischen Handschriften in Deutschland, Supplementband 20,1. Wiesbaden: Franz Steiner, 1980.</p>
  <ul class="legend">
    <li>本文と偈番号は上記ヴァッラバデーヴァ本に従う。流布本（マッリナータ本）とは読み・偈の順序が異なる箇所がある。</li>
    <li>サンスクリットは上部の切替でデーヴァナーガリー・IAST（ローマ字転写）・併記を選べる。IAST は本文から機械的に転写したもの。</li>
    <li>各章のサンスクリット章題は流布本の慣用による。</li>
    <li>灰色の欄はヴァッラバデーヴァ注の要旨と訳者の補足。「注」ボタンで表示を切り替えられる。</li>
  </ul>
</section>

<main>%s</main>

<footer class="colophon">Kumārasambhava I–VII · Vallabhadeva’s Śāradā Version<br>『クマーラサンバヴァ』第一章〜第七章　対訳</footer>
<script>%s</script>
</body>
</html>
''' % (CSS, jump, toc, '\n'.join(sections), JS)

open(OUT, 'w', encoding='utf-8').write(page)
print('Total verse blocks:', total, '| bytes:', len(page.encode()))
