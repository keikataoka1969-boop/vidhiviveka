#!/usr/bin/env python3
"""デーヴァナーガリーを Kyoto-Harvard 方式に転写する。
使い方: deva2kh.py 入力ファイル... > 出力"""
import sys, re
V = {'अ':'a','आ':'A','इ':'i','ई':'I','उ':'u','ऊ':'U','ऋ':'R','ॠ':'RR','ऌ':'lR','ॡ':'lRR','ए':'e','ऐ':'ai','ओ':'o','औ':'au'}
M = {'ा':'A','ि':'i','ी':'I','ु':'u','ू':'U','ृ':'R','ॄ':'RR','ॢ':'lR','ॣ':'lRR','े':'e','ै':'ai','ो':'o','ौ':'au'}
C = {'क':'k','ख':'kh','ग':'g','घ':'gh','ङ':'G','च':'c','छ':'ch','ज':'j','झ':'jh','ञ':'J','ट':'T','ठ':'Th','ड':'D','ढ':'Dh','ण':'N',
     'त':'t','थ':'th','द':'d','ध':'dh','न':'n','प':'p','फ':'ph','ब':'b','भ':'bh','म':'m','य':'y','र':'r','ल':'l','व':'v',
     'श':'z','ष':'S','स':'s','ह':'h','ळ':'L'}
O = {'ं':'M','ः':'H','ँ':'~','ऽ':"'",'।':'|','॥':'||','ॐ':'oM','॰':'.'}
D = {chr(0x966+i): str(i) for i in range(10)}
def kh(s):
    s = s.replace('‌', '').replace('‍', '').replace('़', '')
    out = []; i = 0
    while i < len(s):
        ch = s[i]
        if ch in C:
            out.append(C[ch]); nx = s[i+1] if i+1 < len(s) else ''
            if nx in M: out.append(M[nx]); i += 2; continue
            if nx == '्': i += 2; continue
            out.append('a'); i += 1; continue
        if ch in V: out.append(V[ch])
        elif ch in M: out.append(M[ch])
        elif ch in O: out.append(O[ch])
        elif ch in D: out.append(D[ch])
        elif ch == '्': pass
        else: out.append(ch)
        i += 1
    return ''.join(out)
if __name__ == '__main__':
    for f in sys.argv[1:]:
        sys.stdout.write(kh(open(f).read()))
