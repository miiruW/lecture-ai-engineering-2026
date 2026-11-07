"""第3回: エージェントに持たせるツール。

ここに書いた関数の docstring と型ヒントが、そのままモデルへの「ツールの説明文」になる。
説明文を書き換えると、モデルがツールを使うかどうか・どんな引数で呼ぶかが変わる。
"""

import json
from functools import cache
from pathlib import Path
import random

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3


@cache
def load_glossary() -> list[dict]:
    with open(DATA_DIR / "glossary.json", encoding="utf-8") as f:
        return json.load(f)["terms"]


def make_quiz(lecture: int) -> str:
    """指定した講義回の用語から確認問題を1問作る。

    復習問題を求められたときに使う。
    """
    entries = [entry for entry in load_glossary() if entry["lecture"] == lecture]
    if not entries:
        return json.dumps({"error": f"第{lecture}回の用語がありません。"}, ensure_ascii=False)

    entry = random.choice(entries)
    return json.dumps(
        {
            "question": f"{entry['term']}の意味は？",
            "definition": entry["definition"],
        },
        ensure_ascii=False,
    )


def _normalize(text: str) -> str:
    # 検索時の表記ゆれを吸収するため、文字列を正規化する
    # casefold() : 大文字・小文字の違いを吸収する（lower()より強力）
    # replace(" ", "") : 半角スペースを削除
    # replace("　", "") : 全角スペースを削除
    # 例：「 LoRA 」と「lora」を同じ文字列として比較できる
    return text.casefold().replace(" ", "").replace("　", "")


def _names(entry: dict) -> list[str]:
    # 用語の検索対象となる名前をリストにまとめる
    # term : 用語名
    # id : 用語の識別ID
    # aliases : 別名のリスト
    # すべて正規化して、表記ゆれを吸収する
    return [_normalize(entry["term"]), _normalize(entry["id"])] + [
        _normalize(a) for a in entry["aliases"]
    ]


def search_glossary(query: str) -> str:
    #"""講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。
    
    #AIエンジニアリングの用語や、この講座（AIE2026）に固有の言葉について
    #答える前に使うこと。query には調べたい用語を1つだけ入れる（例: "LoRA"）。
    #講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。
    #"""
    
    """講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。

    AIエンジニアリングの用語や、この講座（AIE2026）に固有の言葉について
    答える前に使うこと。query には調べたい用語をまとめて入れる（例: "LoRA, QLoRA"）。
    講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。
    """

    q = _normalize(query)
    if not q:
        return "検索語が空です。調べたい用語を1つ指定してください。"
    glossary = load_glossary()

    # 【検索優先順位1：完全一致】
    # 用語名・ID・別名のいずれかが検索キーワードと完全一致するものを抽出
    exact = [e for e in glossary if q in _names(e)]
    # 「r」のような短い別名が何にでも当たらないよう、名前側が短いものは除く
    
    # 【検索優先順位2：部分一致】
    # 完全一致したものを除き、次のいずれかに該当する用語を抽出
    # ① 検索キーワードが用語名などに含まれる
    # ② 用語名などが3文字以上で、検索キーワードに含まれる
    # 「r」のような短い別名が何にでも当たらないよう、名前側が短いものは除く
    partial = [
        e for e in glossary
        if e not in exact and any(q in n or (len(n) >= 3 and n in q) for n in _names(e))
    ]
    # 【検索優先順位3：定義文内の一致】
    # 完全一致・部分一致の対象にならなかった用語について、
    # 定義文に検索キーワードが含まれるか確認する
    in_definition = [
        e for e in glossary
        if e not in exact and e not in partial and q in _normalize(e["definition"])
    ]

    # 検索結果を優先順位順に結合する
    # exact → partial → in_definition
    # 最初のMAX_RESULTS件（3件）だけ取得する
    hits = (exact + partial + in_definition)[:MAX_RESULTS]

    # 検索結果が見つからなかった場合の処理
    if not hits:
        return f"用語集に「{query}」は見つかりませんでした。"
    
    # 検索結果をJSON形式に変換して返す
    # 各用語について、用語名・講義回・定義・関連用語を含める
    return json.dumps(
        [
            {
                "term": e["term"],
                "lecture": e["lecture"],
                "definition": e["definition"],
                "related": e["related"],
            }
            for e in hits
        ],
        ensure_ascii=False,
    )


def get_lecture_summary(lecture: int) -> str:
    """指定した回（1始まりの整数）の講義の要点を返す。

    「第3回では何を学ぶ？」のように、回の内容や関係を聞かれたときに使う。
    """

    # 指定された講義回に対応するMarkdownファイルのパスを作成する
    # :02d は整数を2桁のゼロ埋め形式にする指定
    # 例：lecture=3 → "03.md"
    path = DATA_DIR / "lectures" / f"{lecture:02d}.md"
    if not path.exists():
        available = sorted(p.stem for p in (DATA_DIR / "lectures").glob("*.md"))
        return f"第{lecture}回の要点はまだありません。用意されている回: {', '.join(available)}"
    return path.read_text(encoding="utf-8")
