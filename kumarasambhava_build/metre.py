import re,sys
from indic_transliteration import sanscript as S
VOW=['ai','au','ā','ī','ū','ṝ','e','o','a','i','u','ṛ','ḷ']
LONG={'ai','au','ā','ī','ū','ṝ','e','o'}
CONS2=['kh','gh','ch','jh','ṭh','ḍh','th','dh','ph','bh']
def tokens(iast):
    s=iast.lower()
    s=re.sub(r"[^a-zāīūṛṝḷēōṃḥṅñṭḍṇśṣ]","",s)
    out=[];i=0
    while i<len(s):
        m=None
        for v in VOW:
            if s.startswith(v,i): m=('V',v);break
        if not m:
            for c in CONS2:
                if s.startswith(c,i): m=('C',c);break
        if not m: m=('M' if s[i] in 'ṃḥ' else 'C', s[i])
        out.append(m); i+=len(m[1])
    return out
def scan(dev):
    iast=S.transliterate(dev,S.DEVANAGARI,S.IAST)
    t=[]
    for w in re.split(r'[\s\-]+',iast):
        t+=tokens(w)
    res=[]
    for k,(typ,v) in enumerate(t):
        if typ!='V': continue
        h = v in LONG
        j=k+1; nc=0
        while j<len(t) and t[j][0]!='V':
            if t[j][0]=='M': h=True
            else: nc+=1
            j+=1
        if nc>=2 or (nc>=1 and j>=len(t)): h=True
        res.append('–' if h else '⏑')
    return ''.join(res)
if __name__=='__main__':
    for a in sys.argv[1:]:
        w=scan(a); print(len(w),w)
