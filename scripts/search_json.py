import json
import sys
from pathlib import Path

# JSONの場所
JSON_PATH = Path("data/rag_data/lectures.json")

# コマンドライン引数があれば、それを検索語として使う
# 例: python scripts/search_json.py コンパクション セッション
keywords = sys.argv[1:]

if not keywords:
    keywords = ["コンパクション", "セッション", "メモリ"]

if not JSON_PATH.exists():
    print(f"JSONファイルが見つかりません: {JSON_PATH}")
    print("findコマンドで実際の場所を確認してください。")
    sys.exit(1)

with JSON_PATH.open(encoding="utf-8") as f:
    data = json.load(f)


def search_pages(obj):
    """JSONの中から、ページ単位の辞書を再帰的に探す"""
    if isinstance(obj, dict):
        # page_idやcontentを持つ辞書をページとして扱う
        if "content" in obj and isinstance(obj["content"], str):
            yield obj

        for value in obj.values():
            yield from search_pages(value)

    elif isinstance(obj, list):
        for value in obj:
            yield from search_pages(value)


pages = list(search_pages(data))

print(f"JSON: {JSON_PATH}")
print(f"ページ候補数: {len(pages)}")
print(f"検索語: {', '.join(keywords)}")
print("=" * 70)

found_count = 0

for page in pages:
    text = page.get("content", "")

    # いずれかのキーワードを含むページを表示
    matched = [keyword for keyword in keywords if keyword in text]

    if not matched:
        continue

    found_count += 1

    page_id = page.get("id") or page.get("page_id") or "(ページIDなし)"
    page_number = page.get("page", "(ページ番号なし)")
    title = page.get("title", "(タイトルなし)")

    print(f"[{found_count}]")
    print(f"一致した語: {', '.join(matched)}")
    print(f"ID: {page_id}")
    print(f"ページ: {page_number}")
    print(f"タイトル: {title}")
    print("-" * 70)
    print(text[:1500])
    print("=" * 70)

print(f"見つかったページ数: {found_count}")
