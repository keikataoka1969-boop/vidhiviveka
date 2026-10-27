#!/usr/bin/env python3
"""src/partN.html（hero〜footer の断片）に共通の head と目次ナビを付けて partN.html を書き出す。"""
import re, pathlib
here = pathlib.Path(__file__).parent
head = (here / 'src/head.html').read_text()
def fill_text(body, text):
    """data-to で終わり位置を指定した原文欄を、通しテキストから順に切り出して埋める。頁（ref=auto）も自動で付ける。"""
    state = {'cur': 0}
    def page_at(pos):
        ms = [m for m in re.finditer(r'\[p\.(\d+)\]', text[:pos + 1])]
        return ms[-1].group(1) if ms else '?'
    def rep(m):
        ref, mid, attrs = m.group(1), m.group(2), m.group(3)
        to = re.search(r'data-to="([^"]*)"', attrs).group(1)
        fm = re.search(r'data-from="([^"]*)"', attrs)
        frm = fm.group(1) if fm else None
        cur = state['cur']
        if frm:
            try:
                cur = text.index(frm, cur)
            except ValueError:
                raise SystemExit(f'data-from not found: {frm!r}')
        while True:
            sm = re.match(r'\s*(\[p\.\d+\])?\s*', text[cur:])
            if not sm.group(0):
                break
            cur += len(sm.group(0))
        try:
            end = text.index(to, cur) + len(to)
        except ValueError:
            raise SystemExit(f'not found after cursor: {to!r} (from {text[cur:cur+40]!r})')
        state['cur'] = end
        seg = text[cur:end]
        p0 = page_at(cur)
        pages = [p0] + re.findall(r'\[p\.(\d+)\]', seg)
        seg = re.sub(r'(?<=\S)\[p\.\d+\](?=\S)', '', seg)
        seg = re.sub(r'\s*\[p\.\d+\]\s*', ' ', seg)
        seg = re.sub(r'\s+', ' ', seg).strip()
        if ref == 'auto':
            ref = pages[0] if pages[0] == pages[-1] else f'{pages[0]}–{pages[-1]}'
        return f'<span class="ref">{ref}</span>{mid}<div class="src deva" lang="sa">{seg}</div>'
    pat = re.compile(r'<span class="ref">([^<]*)</span>(\s*)<div class="src deva" lang="sa"((?: data-(?:from|to)="[^"]*")+)></div>')
    return pat.sub(rep, body)

rows = []
for line in (here / 'parts.tsv').read_text().strip().split('\n'):
    n, deva, ja, pg, desc = (line.split('\t') + [''] * 5)[:5]
    f = here / f'part{int(n)}.html'
    srcf = here / 'src' / f'part{int(n)}.html'
    name = f'<a href="part{int(n)}.html">{ja}</a>' if srcf.exists() else ja
    rows.append(f'<tr><td class="num">{n}</td><td class="k">{name}<span class="sm" lang="sa" style="font-family:\'Noto Serif Devanagari\',serif">{deva}</span></td><td class="num">p.{pg}</td><td>{desc}</td></tr>')

for src in sorted((here / 'src').glob('*.html')):
    if src.name == 'head.html':
        continue
    body = src.read_text().replace('{{ROWS}}', '\n'.join(rows))
    tf = here / 'text' / src.name.replace('.html', '.txt')
    if tf.exists():
        body = fill_text(body, tf.read_text())
    title = re.search(r'<h1>(.*?)</h1>', body).group(1)
    m = re.search(r'<span class="sample">(.*?)</span>', body)
    links = [] if src.name == 'index.html' else ['<li><a href="index.html">一覧</a></li>']
    for sid, inner in re.findall(r'<section id="([^"]+)"[^>]*>\s*<div class="sec-head">(.*?)</div>', body, re.S):
        no = re.search(r'<span class="sec-no">(.*?)</span>', inner)
        h2 = re.sub(r'<.*?>', '', re.search(r'<h2[^>]*>(.*?)</h2>', inner).group(1))
        short = h2 if len(h2) <= 12 else h2[:11] + '…'
        links.append(f'<li><a href="#{sid}">' + (f'<b>{no.group(1)}</b>' if no else '') + f'{short}</a></li>')
    nav = '<nav class="toc" aria-label="目次">\n  <ol>\n    ' + '\n    '.join(links) + '\n  </ol>\n</nav>\n'
    page_title = re.sub(r'<.*?>', '', title) + ' 対訳'
    out = head.replace('{{TITLE}}', page_title) + '<body>\n' + nav + body + '\n</body>\n</html>\n'
    (here / src.name).write_text(out)
    print('wrote', src.name)
