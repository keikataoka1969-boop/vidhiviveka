#!/usr/bin/env python3
"""OCR -> per-chapter JSON for Mach, Erkenntnis und Irrtum (2. Aufl. 1906).

Output data/ch_XX.json:
  {num, title_de, page_start, page_end,
   paras: [{id, sec, pages:[..], de}],   # de contains ⟦pb:N⟧ and ⟦fn:K⟧ tokens
   notes: {K: text}}                      # K = chapter-continuous footnote number
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'ocr_raw.txt')

CHAPTERS = [  # (title, printed start page) from the Inhaltsverzeichnis
 ("Philosophisches und naturwissenschaftliches Denken", 1),
 ("Eine psycho-physiologische Betrachtung", 20),
 ("Gedächtnis. Reproduktion und Association", 31),
 ("Reflex, Instinkt, Wille, Ich", 50),
 ("Die Entwicklung der Individualität in der natürlichen und kulturellen Umgebung", 70),
 ("Die Wucherung des Vorstellungslebens", 88),
 ("Erkenntnis und Irrtum", 108),
 ("Der Begriff", 126),
 ("Empfindung, Anschauung, Phantasie", 144),
 ("Anpassung der Gedanken an die Tatsachen und aneinander", 164),
 ("Über Gedankenexperimente", 183),
 ("Das physische Experiment und dessen Leitmotive", 201),
 ("Ähnlichkeit und Analogie als Leitmotive der Forschung", 220),
 ("Die Hypothese", 232),
 ("Das Problem", 251),
 ("Die Voraussetzungen der Forschung", 275),
 ("Beispiele von Forschungswegen", 287),
 ("Deduktion und Induktion in psychologischer Beleuchtung", 304),
 ("Zahl und Maß", 320),
 ("Der physiologische Raum im Gegensatz zum metrischen", 337),
 ("Zur Psychologie und natürlichen Entwicklung der Geometrie", 353),
 ("Raum und Geometrie vom Standpunkt der Naturforschung", 389),
 ("Die physiologische Zeit im Gegensatz zur metrischen", 423),
 ("Zeit und Raum physikalisch betrachtet", 434),
 ("Sinn und Wert der Naturgesetze", 449),
]
LAST_PAGE = 463  # Sachregister begins at 464

SUP = str.maketrans('¹²³⁴⁵⁶⁷⁸⁹⁰', '1234567890')
CYR = str.maketrans({'О': 'O', 'К': 'K', 'а': 'a', 'р': 'p', 'п': 'n', 'и': 'u', 'Я': 'R'})
SUSPENDED = {'und', 'oder', 'bis', 'als', 'wie', 'sowie', 'noch', 'resp', 'bzw', 'u', 'zu', 'nebst', 'statt'}


def norm(s):
    return re.sub(r'[^a-zäöüß]', '', s.lower().replace('mαβ', 'maß').replace('maβ', 'maß'))


def load_pages():
    txt = open(RAW, encoding='utf-8').read()
    parts = re.split(r'\n?END_OF_PDF_PAGE_\d+\n?', txt)
    # ordinal 1,2 = title + TOC ; printed page = ordinal - 2
    pages = {}
    for i, p in enumerate(parts):
        printed = i - 1  # parts[0] is ordinal 1
        if printed >= 1:
            pages[printed] = p
    return pages


def chapter_of(page):
    c = 0
    for i, (_, st) in enumerate(CHAPTERS):
        if page >= st:
            c = i
    return c


def strip_head(lines, page, chap):
    """Remove running head / page number / chapter title lines at top of page."""
    title = norm(CHAPTERS[chap][0])
    out = list(lines)
    removed = 0
    while out and removed < 4:
        l = out[0].strip()
        if not l:
            out.pop(0); continue
        n = norm(l)
        if re.fullmatch(r'\d{1,3}', l):
            out.pop(0); removed += 1; continue
        if n and (n == title or (len(n) > 4 and title.startswith(n)) or (len(n) > 4 and n in title and len(l) < 90)):
            out.pop(0); removed += 1; continue
        # head glued to paragraph in reflowed pages: "462 Sinn und Wert der Naturgesetze. geeignet ..."
        m = re.match(r'^(\d{1,3}\s+)?([^.]{3,90}\.)(\s+\d{1,3})?\s+(.*)$', l)
        if m and norm(m.group(2)) == title:
            out[0] = m.group(4); removed += 1; continue
        break
    # chapter title on first page may be split across two lines ("Philosophisches" / "und ...")
    return out


FN_START = re.compile(r'^(?:([¹²³⁴⁵⁶⁷⁸⁹]|\d{1,2}|\*)\))\s*(.*)$')


def classify(lines):
    """Mark lines that are in footnote (petit) type by width: body ~55-65, notes ~66-80."""
    L = [len(x.strip()) for x in lines]
    kind = []
    for n in L:
        if n == 0: kind.append('e')
        elif n > 110: kind.append('L')
        elif n >= 68: kind.append('f')
        elif n <= 63: kind.append('b')
        else: kind.append('?')
    isf = [False] * len(lines)
    i = 0
    while i < len(lines):
        if kind[i] == 'f':
            j = i
            while j < len(lines) and kind[j] in 'f?':
                j += 1
            nf = sum(1 for k in range(i, j) if kind[k] == 'f')
            if nf >= 2 or (j >= len(lines) - 1 and nf >= 1):
                for k in range(i, j): isf[k] = True
                # a short paragraph-final line right after the block, or an indented first line
                # of the next note paragraph (followed by f) belongs to the note too
                while j < len(lines):
                    if kind[j] in 'b?' and j + 1 < len(lines) and kind[j+1] == 'f':
                        isf[j] = True; j += 1
                        while j < len(lines) and kind[j] in 'f?':
                            isf[j] = True; j += 1
                    elif kind[j] == 'b' and re.search(r'[.!?:)]$', lines[j].strip()) and len(lines[j].strip()) < 55 and isf[j-1] and (j + 1 >= len(lines) or kind[j+1] in 'f?' or FN_START.match(lines[j+1].strip()) or (j+1 < len(lines) and kind[j+1]=='b' and len(lines[j+1].strip())<=63 and j+2 < len(lines) and kind[j+2]=='f')):
                        isf[j] = True; j += 1
                    else:
                        break
            i = max(j, i + 1)
        else:
            i += 1
    return isf


def split_page(text, page, chap, prev_note_open=False):
    lines = text.split('\n')
    lines = strip_head(lines, page, chap)
    # remove sheet signatures like "2*" or "Mach, Erkenntnis und Irrtum. 3"
    while lines and (not lines[-1].strip() or re.fullmatch(r'\d{1,2}\*?|\S*\s*\d+\*', lines[-1].strip())
                     or re.match(r'^Mach,\s*Erkenntnis', lines[-1].strip())):
        lines.pop()
    isf = classify(lines)
    body, notes, cont = [], [], []
    in_notes = False
    for idx, l in enumerate(lines):
        s = l.strip()
        m = FN_START.match(s)
        if m and (isf[idx] or in_notes or len(s) >= 40 or idx >= len(lines) - 3):
            num = m.group(1).translate(SUP)
            in_notes = True
            notes.append([num, m.group(2)])
            continue
        if in_notes or isf[idx]:
            if not s:
                continue
            if notes:
                notes[-1][1] = join_lines(notes[-1][1], s)
            else:
                cont.append(s)
            continue
        body.append(l)
    return body, notes, cont


def join_lines(a, b):
    if not a:
        return b
    if re.search(r'[A-Za-zäöüß]-$', a):
        if b[:1].islower() or b[:1] in 'äöüß':
            return a[:-1] + b
        return a + b
    return a + ' ' + b


def fix_inline(s):
    s = s.translate(CYR)
    s = s.replace('Mαβ', 'Maß').replace('Maβ', 'Maß')
    def rep(m):
        w2 = m.group(2)
        if w2.rstrip('.,;') in SUSPENDED:
            return m.group(0)
        return m.group(1) + w2
    s = re.sub(r'([a-zäöüß])- ([a-zäöüß][a-zäöüß]*)', rep, s)
    s = re.sub(r'(?<=\S)"', '“', s)
    s = s.replace('"', '„')
    s = re.sub(r' {2,}', ' ', s)
    s = s.replace(' ⟦pb', ' ⟦pb')
    return s.strip()


SENT_END = re.compile(r'(?<=[a-zäöüß]{3}[.!?])(?:⟦fn:\d+⟧)?\s+(?=[A-ZÄÖÜ„])|(?<=[a-zäöüß]{3}[.!?]“)\s+(?=[A-ZÄÖÜ„])')


def split_long(text, maxlen=1300):
    if len(text) <= maxlen:
        return [text]
    cuts = [m.end() for m in SENT_END.finditer(text)]
    # fix: keep footnote token attached to previous sentence
    n = -(-len(text) // 1000)  # number of chunks, ~1000 chars each
    target = len(text) / n
    parts, last = [], 0
    for i in range(1, n):
        goal = target * i
        best = min((c for c in cuts if c > last + 300 and c < len(text) - 300), key=lambda c: abs(c - goal), default=None)
        if best is None:
            continue
        parts.append(text[last:best].strip()); last = best
    parts.append(text[last:].strip())
    return [x for x in parts if x]


def is_par_end(line):
    s = line.rstrip()
    return len(s) < 50 and re.search(r'[.!?:;"“”»)]$', s) is not None


SEC_START = re.compile(r'^(\d{1,2})\.\s+(?=[A-ZÄÖÜ„"(])')


def build():
    pages = load_pages()
    chapters = []
    for ci, (title, start) in enumerate(CHAPTERS):
        end = (CHAPTERS[ci + 1][1] - 1) if ci + 1 < len(CHAPTERS) else LAST_PAGE
        paras = []           # list of dict(sec, pages, de)
        cur = None
        sec = 0
        notes = {}
        fn_counter = 0
        prev_open = False
        for pg in range(start, end + 1):
            body, pnotes, cont = split_page(pages.get(pg, ''), pg, ci, prev_open)
            if cont and fn_counter:
                t = notes[fn_counter]
                for cl in cont:
                    t = join_lines(t, cl)
                notes[fn_counter] = fix_inline(t)
            if pg == start:
                # drop the chapter title lines
                t = norm(title); acc = ''
                while body and body[0].strip() and (t.startswith(norm(acc + body[0])) or not body[0].strip()):
                    acc += body[0]; body.pop(0)
                    if norm(acc) == t: break
            # footnote renumbering map for this page
            fmap = {}
            for num, ntext in pnotes:
                fn_counter += 1
                key = num if num != '*' else '*'
                fmap.setdefault(key, []).append(fn_counter)
                notes[fn_counter] = fix_inline(ntext)
            used = {k: 0 for k in fmap}
            prev_open = bool(pnotes) and not re.search(r'[.!?)]$', notes[fn_counter].strip())

            def fnrep(m):
                k = m.group(2).translate(SUP)
                if k in fmap and used[k] < len(fmap[k]):
                    n = fmap[k][used[k]]; used[k] += 1
                    return m.group(1) + '⟦fn:%d⟧' % n
                return m.group(0)

            first_line_of_page = True
            for l in body:
                s = l.strip()
                if not s:
                    continue
                s = re.sub(r'(\S?)\s?((?:[¹²³⁴⁵⁶⁷⁸⁹])|(?<=[\s.,;:!?"“a-zäöü])\d)\)', fnrep, s)
                msec = SEC_START.match(s)
                newpar = (cur is None or cur.get('closed') or msec is not None)
                if newpar:
                    if msec:
                        sec = int(msec.group(1))
                    cur = {'sec': sec, 'pages': [pg], 'de': '', 'closed': False}
                    paras.append(cur)
                    if first_line_of_page and pg != start and len(paras) > 1:
                        pass
                else:
                    if first_line_of_page:
                        if not re.search(r'[A-Za-zäöüß]-$', cur['de']):
                            cur['de'] += ' '
                        cur['de'] += '⟦pb:%d⟧' % pg
                        if pg not in cur['pages']:
                            cur['pages'].append(pg)
                cur['de'] = join_lines(cur['de'], s) if not cur['de'].endswith('⟧') else (
                    cur['de'] + s if not re.search(r'[A-Za-zäöüß]-⟦pb:\d+⟧$', cur['de']) else
                    re.sub(r'-(⟦pb:\d+⟧)$', r'\1', cur['de']) + s)
                first_line_of_page = False
                long = len(s) > 110
                cur['long'] = long
                if long:
                    cur['closed'] = re.search(r'[.!?:"“”»)]$', s) is not None
                    if not cur['closed']:
                        pass
                elif is_par_end(s):
                    cur['closed'] = True
                else:
                    cur['closed'] = False
            # fix "-⟦pb" hyphen joins where next page starts lowercase
        for p in paras:
            p['de'] = re.sub(r'([A-Za-zäöüß])-⟦pb:(\d+)⟧([a-zäöüß])', r'\1⟦pb:\2⟧\3', p['de'])
            p['de'] = fix_inline(p['de'])
            p.pop('closed', None); p.pop('long', None)
        # split very long paragraphs into reading units at sentence boundaries
        out = []
        for p in paras:
            for k, chunk in enumerate(split_long(p['de'])):
                q = dict(p); q['de'] = chunk; q['cont'] = k > 0
                if k > 0:
                    m = re.findall(r'⟦pb:(\d+)⟧', ''.join(split_long(p['de'])[:k]))
                    q['pages'] = [int(m[-1])] if m else p['pages'][:1]
                out.append(q)
        paras = out
        # ids: sec.n
        cnt = {}
        for p in paras:
            cnt[p['sec']] = cnt.get(p['sec'], 0) + 1
            p['id'] = '%d.%d' % (p['sec'], cnt[p['sec']])
        chapters.append({'num': ci + 1, 'title_de': title, 'page_start': start, 'page_end': end,
                         'paras': paras, 'notes': {str(k): v for k, v in notes.items()}})
    return chapters


def write_tsv(c, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('#\t%d\t%s\t%d-%d\n' % (c['num'], c['title_de'], c['page_start'], c['page_end']))
        for p in c['paras']:
            f.write('%s\t%d%s\t%s\n' % (p['id'], p['pages'][0], 'c' if p.get('cont') else '', p['de']))
        for k, v in c['notes'].items():
            f.write('n%s\t\t%s\n' % (k, v))


if __name__ == '__main__':
    chs = build()
    os.makedirs(os.path.join(ROOT, 'data', 'draft'), exist_ok=True)
    for c in chs:
        write_tsv(c, os.path.join(ROOT, 'data', 'draft', 'de_%02d.tsv' % c['num']))
        nfr = sum(p['de'].count('⟦fn:') for p in c['paras'])
        print(c['num'], 'paras', len(c['paras']), 'secs', max(p['sec'] for p in c['paras']),
              'notes', len(c['notes']), 'linked', nfr)
