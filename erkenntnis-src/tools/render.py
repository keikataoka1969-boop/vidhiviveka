#!/usr/bin/env python3
"""Render the German/Japanese parallel edition (same layout as the reference Mach site).

Inputs
  data/meta.json
  data/de/de_XX.tsv   lines: "#\tN\ttitle\tpages" | "id\tpage[c]\tGerman" | "nK\t\tnote"
  data/ja/ja_XX.tsv   lines: "id\tJapanese" | "nK\tnote"   (same ids)
  data/corr/corr_XX.html  optional inner HTML for the 校訂注 box
Output
  site/erkenntnis/index.html, kapitel_XX.html
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, 'tools', 'tpl')
OUT = os.path.join(ROOT, 'site', 'erkenntnis')
ROMAN = ['', 'Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ', 'ⅩⅠ', 'ⅩⅡ', 'ⅩⅢ', 'ⅩⅣ', 'ⅩⅤ',
         'ⅩⅥ', 'ⅩⅦ', 'ⅩⅧ', 'ⅩⅨ', 'ⅩⅩ', 'ⅩⅩⅠ', 'ⅩⅩⅡ', 'ⅩⅩⅢ', 'ⅩⅩⅣ', 'ⅩⅩⅤ']
LATIN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV',
         'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV']


def read(p):
    return open(p, encoding='utf-8').read()


def load_de(n):
    p = os.path.join(ROOT, 'data', 'de', 'de_%02d.tsv' % n)
    if not os.path.exists(p):
        return None
    head, rows, notes = None, [], {}
    for line in read(p).splitlines():
        if not line.strip():
            continue
        f = line.split('\t')
        if f[0] == '#':
            head = {'num': int(f[1]), 'title': f[2], 'pages': f[3]}
        elif f[0].startswith('n'):
            notes[f[0][1:]] = f[2]
        else:
            rows.append({'id': f[0], 'page': int(re.match(r'\d+', f[1]).group()), 'cont': f[1].endswith('c'), 'de': f[2]})
    return head, rows, notes


def load_ja(n):
    p = os.path.join(ROOT, 'data', 'ja', 'ja_%02d.tsv' % n)
    if not os.path.exists(p):
        return None
    d = {}
    for line in read(p).splitlines():
        if line.strip() and not line.startswith('//'):
            k, _, v = line.partition('\t')
            d[k.strip()] = v.strip()
    return d


def inline(text, lang, pb=True):
    """Escape and convert ⟦pb:N⟧ ⟦fn:K⟧ ⟦br⟧ tokens; *x* -> <i>x</i>."""
    parts = re.split(r'(⟦[^⟧]+⟧)', text)
    out = []
    for p in parts:
        m = re.fullmatch(r'⟦(\w+)(?::([^⟧]+))?⟧', p)
        if not m:
            e = html.escape(p, quote=False)
            e = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', e)
            out.append(e)
            continue
        kind, arg = m.group(1), m.group(2)
        if kind == 'pb':
            if pb:
                out.append('<span class="pb" title="Leipzig 1906, S. %s">%s</span>' % (arg, arg))
        elif kind == 'fn':
            out.append('<a class="fr" href="#n%s">%s</a>' % (arg, arg))
        elif kind == 'br':
            out.append('<br>')
        elif kind == 'fig':
            out.append('')
    return ''.join(out)


def pages_of(row):
    ps = [row['page']] + [int(x) for x in re.findall(r'⟦pb:(\d+)⟧', row['de'])]
    seen = []
    for p in ps:
        if p not in seen:
            seen.append(p)
    return seen


def chapter_html(n, meta, de, ja, prev_link, next_link):
    head, rows, notes = de
    title_jp = meta['chapters_jp'][n - 1]
    secs = []
    for r in rows:
        s = r['id'].split('.')[0]
        if s not in secs:
            secs.append(s)
    css = read(os.path.join(TPL, 'chapter.css'))
    js = read(os.path.join(TPL, 'chapter.js'))
    missing = [r['id'] for r in rows if r['id'] not in ja] + ['n' + k for k in notes if 'n' + k not in ja]
    for r in rows:
        a = re.findall(r'⟦fn:(\d+)⟧', r['de']); b = re.findall(r'⟦fn:(\d+)⟧', ja.get(r['id'], ''))
        if a != b:
            print('  WARNING ch%d %s footnote refs differ: de=%s ja=%s' % (n, r['id'], a, b), file=sys.stderr)
    if missing:
        print('  WARNING ch%d missing ja for: %s' % (n, ', '.join(missing)), file=sys.stderr)
    o = []
    o.append('<!DOCTYPE html>\n<html lang="ja">\n<head>\n<link rel="stylesheet" href="iast-fonts.css">\n'
             '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    o.append('<title>第%s章 %s</title>\n' % (ROMAN[n], html.escape(title_jp)))
    o.append('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Noto+Serif+JP:wght@400;600&display=swap">\n')
    o.append('<style>' + css + '</style>\n</head>\n<body>\n')
    o.append('<div class="bar"><div class="bar-in">\n  <a class="ch" href="index.html" title="目次">第%s章</a>\n' % ROMAN[n])
    o.append('  <span class="seg" role="group" aria-label="表示言語">\n'
             '    <button type="button" data-v="both" aria-pressed="true">対訳</button>\n'
             '    <button type="button" data-v="only-de" aria-pressed="false">独</button>\n'
             '    <button type="button" data-v="only-jp" aria-pressed="false">日</button>\n  </span>\n'
             '  <span class="seg" role="group" aria-label="注">\n'
             '    <button type="button" data-n="show" aria-pressed="true">注あり</button>\n'
             '    <button type="button" data-n="no-notes" aria-pressed="false">注なし</button>\n  </span>\n')
    o.append('  <nav class="secnav" aria-label="節">' + ''.join('<a href="#s%s">§%s</a>' % (s, s) for s in secs if s != '0') + '</nav>\n</div></div>\n\n')
    pfirst, plast = head['pages'].split('-')
    o.append('<header class="title">\n  <div class="kicker">KAPITEL %s · 第%s章</div>\n' % (LATIN[n], ROMAN[n]))
    o.append('  <h1>%s</h1>\n  <div class="de-title" lang="de">%s</div>\n' % (html.escape(title_jp), html.escape(head['title'])))
    o.append('  <div class="source">底本：%s, S. %s–%s　｜　本文中の <span class="pb">201</span> は底本の改頁位置</div>\n</header>\n\n<main>\n'
             % (meta['source'], pfirst, plast))
    cur = None
    for r in rows:
        s = r['id'].split('.')[0]
        if s != cur:
            cur = s
            if s != '0':
                o.append('<h2 class="sec" id="s%s"><a href="#s%s">§ %s</a></h2>\n' % (s, s, s))
        pid = r['id']
        pg = ''.join('<span>S.&nbsp;%d</span>' % p for p in pages_of(r))
        o.append('<article class="row" id="p%s">\n  <aside class="mg"><a class="pid" href="#p%s">%s</a><span class="pg">%s</span></aside>\n'
                 % (pid, pid, pid, pg))
        o.append('  <p class="de" lang="de">%s</p>\n' % inline(r['de'], 'de'))
        o.append('  <p class="jp" lang="ja">%s</p>\n' % inline(ja.get(pid, '<span class="missing">（未訳）</span>'), 'ja', pb=False))
        refs = re.findall(r'⟦fn:(\d+)⟧', r['de'])
        if refs:
            o.append('  <ol class="notes">')
            for k in refs:
                o.append('<li id="n%s"><span class="nn">%s</span><p class="de" lang="de">%s</p><p class="jp" lang="ja">%s</p></li>'
                         % (k, k, inline(notes.get(k, ''), 'de'), inline(ja.get('n' + k, '（未訳）'), 'ja')))
            o.append('</ol>\n')
        o.append('</article>\n')
        for fig in re.findall(r'⟦fig:([^⟧]+)⟧', r['de']):
            o.append('<figure class="fig"><span lang="de">%s</span><em>図版は原書を参照</em></figure>\n' % html.escape(fig))
    o.append('</main>\n\n')
    corr = os.path.join(ROOT, 'data', 'corr', 'corr_%02d.html' % n)
    if os.path.exists(corr):
        o.append('<details class="corr">\n  <summary>校訂注（底本との照合）</summary>\n' + read(corr) + '\n</details>\n\n')
    o.append('<nav class="pager">%s<a href="index.html">目次</a>%s</nav>\n\n' % (prev_link or '<span></span>', next_link or '<span></span>'))
    o.append('<script>' + js + '</script>\n</body>\n</html>\n')
    return ''.join(o)


def index_html(meta, done):
    css = read(os.path.join(TPL, 'index.css'))
    o = ['<!DOCTYPE html>\n<html lang="ja">\n<head>\n<link rel="stylesheet" href="iast-fonts.css">\n<meta charset="UTF-8">\n'
         '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Mach 認識と誤謬 目次</title>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600&display=swap">\n'
         '<style>' + css + '\n.ch.pending { color: var(--muted); pointer-events: none; }\n.ch.pending .ch-jp::after { content: "（準備中）"; font-size: .8em; margin-left: .4em; }\n</style>\n</head>\n<body>\n']
    o.append('<header>\n  <div class="book-title-jp">%s</div>\n  <div class="book-title-de">%s</div>\n'
             '  <div class="book-subtitle">%s</div>\n  <div class="book-meta">Ernst Mach &#x7C; %s &#x7C; 独日対訳</div>\n</header>\n\n'
             % (meta['book_jp'], meta['book_de'], meta['subtitle_de'], meta['edition']))
    o.append('<div class="toc-label">目次 INHALTSVERZEICHNIS</div>\n\n<nav class="toc">\n')
    titles_de = []
    for n in range(1, 26):
        de = load_de(n)
        titles_de.append(de[0]['title'] if de else '')
    import importlib.util
    spec = importlib.util.spec_from_file_location('prep', os.path.join(ROOT, 'tools', 'prep.py'))
    prep = importlib.util.module_from_spec(spec); spec.loader.exec_module(prep)
    for n in range(1, 26):
        tde = prep.CHAPTERS[n - 1][0]
        cls = 'ch' if n in done else 'ch pending'
        o.append('  <a class="%s" href="kapitel_%02d.html">\n    <span class="ch-num">%s</span>\n    <span class="ch-titles">\n'
                 '      <span class="ch-jp">%s</span>\n      <span class="ch-de">%s</span>\n    </span>\n  </a>\n'
                 % (cls, n, ROMAN[n], meta['chapters_jp'][n - 1], html.escape(tde)))
    o.append('</nav>\n\n<footer>\n  <p>エルンスト・マッハ『認識と誤謬——研究の心理学についての素描』第2版（ライプツィヒ：J. A. バルト、1906年）全25章の独日対訳。'
             'ドイツ語本文はOCRテキストを底本の版面に即して校訂した。</p>\n'
             '  <p>Ernst Mach, Erkenntnis und Irrtum. Skizzen zur Psychologie der Forschung, 2. Aufl., Leipzig: Johann Ambrosius Barth, 1906.</p>\n'
             '</footer>\n</body>\n</html>\n')
    return ''.join(o)


def main():
    meta = json.load(open(os.path.join(ROOT, 'data', 'meta.json'), encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    done = [n for n in range(1, 26) if load_de(n) and load_ja(n)]
    for n in done:
        prev_link = next_link = None
        if n - 1 in done:
            prev_link = '<a href="kapitel_%02d.html">← 第%s章</a>' % (n - 1, ROMAN[n - 1])
        if n + 1 in done:
            next_link = '<a href="kapitel_%02d.html">第%s章 →</a>' % (n + 1, ROMAN[n + 1])
        h = chapter_html(n, meta, load_de(n), load_ja(n), prev_link, next_link)
        open(os.path.join(OUT, 'kapitel_%02d.html' % n), 'w', encoding='utf-8').write(h)
        print('wrote kapitel_%02d.html' % n)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index_html(meta, done))
    print('wrote index.html; chapters done:', done)


if __name__ == '__main__':
    main()
