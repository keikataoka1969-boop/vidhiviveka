# Mach, Erkenntnis und Irrtum (1906) — 独日対訳 作業メモ

公開先: https://keikataoka1969-boop.github.io/vidhiviveka/erkenntnis/ （gh-pages ブランチの erkenntnis/）

## 構成
- data/ocr_raw.txt            元のOCR（END_OF_PDF_PAGE 区切り。印刷頁 = 通し番号 - 2）
- data/draft/de_XX.tsv        tools/prep.py が作る自動整形版（下書き）
- data/de/de_XX.tsv           校訂済みドイツ語（正本）。行: "id<TAB>頁[c]<TAB>本文"、注: "nK<TAB><TAB>本文"
- data/ja/ja_XX.tsv           和訳。行: "id<TAB>訳文"、注: "nK<TAB>訳文"。// で始まる行はコメント
- data/corr/corr_XX.html      校訂注（各章末の折りたたみ欄）
- data/meta.json              書名・章名（和）
- tools/render.py             site/erkenntnis/ に HTML を生成（参考: mach/ 『感覚の分析』と同じレイアウト）
- tools/publish.sh "msg"      生成→gh-pages にコピー→トップ index.html の章リスト更新→push、ソースも開発ブランチへ

## 記法
⟦pb:N⟧ 底本の改頁、⟦fn:K⟧ 注参照（章内通し番号）、⟦br⟧ 注内の段落、⟦fig:…⟧ 図版位置、*…* 斜体（隔字体）

## 手順（1章ごと）
1. cp data/draft/de_XX.tsv data/de/de_XX.tsv
2. 脚注の混入・番号ずれ・行脱落・OCR誤字を直す（id は節ごとに連番）
3. data/ja/ja_XX.tsv を作成（注番号を独文と一致させる。render.py が不一致を警告）
4. data/corr/corr_XX.html を書く
5. tools/publish.sh "Erkenntnis und Irrtum: Kapitel N"

## 訳語
Befund 所見 / Vorstellung 表象 / Vorstellungsleben 表象生活 / vulgär 通俗的 / Leib 身体 / Körper 物体 /
Ich 自我 / Empfindung 感覚 / Element 要素 / Abhängigkeit 依存関係 / Anpassung 適応 / Naturforscher 自然研究者 /
Spezialforscher 専門研究者 / Orientierung 方向づけ / Association 連合 / Reproduktion 再生 / Nachdenken 熟考 /
Reflex 反射 / Instinkthandlung 本能行為 / Wille 意志 / Aufmerksamkeit 注意 / Organempfindung 器官感覚

## 進捗
第Ⅰ〜Ⅸ章 公開済み（以降も同手順で継続）。序文（Vorwort）はOCRに含まれていない。

## 校訂で頻出するパターン（下書きTSVでの典型的な誤り）
- 頁下の脚注（"1) Morgan, l. c. p. 339." 等）が次節の本文中に混入 → 抜き出して注を新設し、番号を繰り下げ
- 本文中の未リンク注記号 ¹) ²) ³) 2) *) → 対応する注へ ⟦fn:K⟧
- "16. Jahrhundert" 等が節番号と誤認 → 前段落に連結
- 図版脇の短い行で段落が細切れ → 連結し ⟦fig:Fig. N (S. x)⟧
- 長い一行に組まれた頁（OCR の段落復元頁）で節・注が連結 → 手で分割
- 数式・分数（1/108 → 1/10⁸ など）、ダッシュ（— … —）の脱落
