# 第3回 解答

## 宿題

- 取り組んだレベル：基礎
- やったこと：search_glossaryのdocstringを変更
- 　　　　　　条件A：query には調べたい用語を1つだけ入れる（例: "LoRA"）。
- 　　　　　　条件B：query には調べたい用語をまとめて入れる（例: "LoRA, QLoRA"）。

- 結果：

- 条件A
@miiruW ➜ /workspaces/lecture-ai-engineering-2026 (lec03) $ uv run python -m app.agent --trace "LoRAとQLoRAの違いを教えて"
[model] gemini-3.5-flash-lite
LoRAとQLoRAの違いは、ベースモデルの重みをそのまま使うか、量子化してメモリを節約するかにあります。

* **LoRA**: 事前学習済みの重みは固定したまま、更新分（低ランク行列）だけを学習してパラメータ数や保存容量を削減する手法です。
* **QLoRA**: LoRAの仕組みに加え、ベースモデルの重みを4ビットなどに量子化（圧縮）することでメモリ使用量をさらに大幅に削減し、より小さなGPUでも大きなモデルを扱えるようにした手法です。

第2回

--- trace ---
[tool call]   search_glossary({'query': 'LoRA'})
[tool call]   search_glossary({'query': 'QLoRA'})
[tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラ…
[tool return] search_glossary -> [{"term": "QLoRA", "lecture": 2, "definition": "ベースモデルの重みを4ビットなどに量子化してメモリを節約したうえで、LoRAで学習する手法。より大きなモデルを小さなGPUで扱える。本講座の第2…
[usage] RunUsage(cost=Decimal('0.0008068'), details={'text_prompt_tokens': 1356}, input_text_tokens=1356, input_tokens=1356, output_tokens=160, requests=2, tool_calls=2)


-条件B
@miiruW ➜ /workspaces/lecture-ai-engineering-2026 (lec03) $ uv run python -m app.agent --trace "LoRAとQLoRAの違いを教えて"
[model] gemini-3.5-flash-lite
LoRAとQLoRAの違いは、**「ベースモデルの重みを量子化するかどうか」**にあります。それぞれの特徴は以下の通りです。

* **LoRA（Low-Rank Adaptation）**
  * **特徴**: 事前学習済みの重みをそのまま（通常は16ビットなどの高精度で）固定し、重みの更新分を表す小さな低ランク行列（アダプタ）だけを追加・学習するPEFT（Parameter-Efficient Fine-Tuning）手法です。
  * **メリット**: 学習パラメータ数を大幅に削減でき、効率的にファインチューニングが可能です。

* **QLoRA（Quantized LoRA）**
  * **特徴**: ベースモデルの重みを**4ビットなど極限まで量子化（軽量化）**した状態で固定し、その上でLoRAの仕組みを使って学習を行う手法です。
  * **メリット**: メモリ使用量を劇的に削減できるため、大きなモデルでもより小さなGPU環境で動かしてファインチューニングを行えるようになります。

このように、LoRAは「低ランク行列の追加による効率化」、QLoRAはそれに加えて「ベースモデルの4ビット量子化によるさらなるメモリ節約」を組み合わせた発展的な手法です。

（関係する回：第2回）

--- trace ---
[tool call]   search_glossary({'query': 'LoRA QLoRA'})
[tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラ…
[usage] RunUsage(cost=Decimal('0.0010559'), details={'text_prompt_tokens': 1053}, input_text_tokens=1053, input_tokens=1053, output_tokens=296, requests=2, tool_calls=1)


- 実行結果の比較

| 比較項目 | 条件A（用語を1つずつ） | 条件B（複数用語をまとめて） |
|---|---|---|
| docstringの指示 | 用語を1つだけ入れる | 用語をまとめて入れる |
| ツール呼び出し回数 | 2回 | 1回 |
| 入力トークン数 | 1,356 | 1,053 |
| 出力トークン数 | 160 | 296 |
| APIリクエスト数 | 2 | 2 |
| コスト | 0.0008068 | 0.0010559 |


- 気づき・疑問：
- 今回の実験から、docstringの記述を変更するだけで、エージェントのツール呼び出し方法が変化することが確認できた。
- 一方、ツール呼び出し回数の削減が必ずしもコスト削減につながるわけではないことも確認できた。
- したがって、docstringを設計する際には、単にツールの呼び出し回数を減らすだけでなく、検索結果の正確性や網羅性、回答品質、コストを総合的に考慮する必要があると考える。

- また条件A、条件Bともに複数回実行してみたがツールの呼び出し回数にブレはなく、今回のdocstringの指示は正しく認識されて動作しているものと推察される。

