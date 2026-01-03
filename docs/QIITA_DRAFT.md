# 宇都宮市のオープンデータをAIで爆速活用！自作MCPサーバー「utsunomiya-open-data」を作って公開しました

こんにちは、[あなたの名前]です。
今回は、宇都宮市のオープンデータをLLM（Claudeなど）から直接検索・分析できるようにする **MCP (Model Context Protocol) サーバー** を開発し、PyPIで公開しました。

「避難場所どこだっけ？」「人口推移を知りたい」といった質問をAIに投げるだけで、最新のオープンデータを自動で取得して回答してくれるようになります。

## 何を作ったの？

**utsunomiya-mcp-server** というPythonパッケージです。
GitHub: [takurot/utsunomiya-mcp-server](https://github.com/takurot/utsunomiya-mcp-server)
PyPI: [utsunomiya-mcp-server](https://pypi.org/project/utsunomiya-mcp-server/)

このMCPサーバーをClaude Desktopなどのクライアントに登録すると、以下の機能が使えるようになります。

1.  **データセットの検索**: 宇都宮市オープンデータポータル (CKAN) から、キーワードで欲しいデータを検索。
2.  **データの取得**: CSVデータを自動でダウンロード・解析。
3.  **分析**: Pandasを使ってデータの集計や抽出を実行。

これら全てを、自然言語の指示だけで自律的にやってくれます。

## インストール方法

`uv` や `pip` を使って簡単にインストールできます。

### おすすめ: Claude Desktop で使う場合

Claude Desktop アプリの設定ファイル (`~/Library/Application Support/Claude/claude_desktop_config.json` など) に以下を追記するだけです。
`uvx` を使うと、事前インストール不要で常に最新版を実行できて便利です。

```json
{
  "mcpServers": {
    "utsunomiya-open-data": {
      "command": "uvx",
      "args": [
        "utsunomiya-mcp-server"
      ]
    }
  }
}
```

Python環境に直接インストールして使う場合はこちら：

```bash
pip install utsunomiya-mcp-server
```

```json
{
  "mcpServers": {
    "utsunomiya-open-data": {
      "command": "utsunomiya-mcp",
      "args": []
    }
  }
}
```

## 実用例：どんなことができる？

実際にClaude Desktopで使ってみた例を紹介します。

### 1. 避難場所の検索

**プロンプト**:
> 「豊郷台周辺の避難場所を教えて。どのような災害に対応しているかも知りたいです。」

**AIの挙動**:
1. ツールが `evacuation_sites` データセットなどを検索・ロード。
2. 住所フィルターなどで「豊郷台」を含むデータを抽出。
3. 該当する施設名と、対応する災害種別（洪水、土砂災害など）を回答。

### 2. 人口データの分析

**プロンプト**:
> 「宇都宮市の最新の人口データを取得して、人口が多い地区トップ5を教えてください。」

**AIの挙動**:
1. `search_datasets("人口")` を実行し、最新の町丁別人口データを検索。
2. 見つかったCSVデータをロード。
3. `世帯数` や `合計(人)` カラムでソートし、分析結果を提示。

### 3. 未知のデータの探索

**プロンプト**:
> 「宇都宮市にAEDはどれくらい設置されていますか？データがあれば分析してください。」

**AIの挙動**:
1. `search_datasets("AED")` を実行。
2. 「AED設置施設一覧」などのデータセットを発見。
3. データをロードし、施設数や設置場所の傾向などを分析して回答。

## 仕組み（技術的な話）

このサーバーは [FastMCP](https://github.com/jlowin/fastmcp) を使用して実装されています。
また、宇都宮市オープンデータポータルサイトは [CKAN](https://ckan.org/) APIを採用しているため、`package_search` などのAPIを叩くことで動的に新しいデータセットを発見できるようにしています。

### 工夫した点

*   **動的なデータセット探索**: 事前に定義したデータだけでなく、API検索で見つかった任意のCSVデータをロードできるようにしました。
*   **SSL問題への対処**: 一部のデータソースで発生するSSL証明書エラーに対処しつつ、安全にデータ取得できるよう調整しました。
*   **エンコーディング自動判定**: 日本のオープンデータによくある `Shift-JIS` と `UTF-8` の混在に対応するため、`chardet` で自動判定しています。

## まとめ

オープンデータは「公開されているけど使いにくい」ことが多かったですが、MCP × LLM の組み合わせによって、**「会話するだけで活用できるデータ」** に変わりました。

ぜひインストールして、宇都宮市のデータをハックしてみてください！

---
**Links**
*   [PyPI - utsunomiya-mcp-server](https://pypi.org/project/utsunomiya-mcp-server/)
*   [GitHub Repository](https://github.com/takurot/utsunomiya-mcp-server)
*   [宇都宮市オープンデータポータルサイト](https://data.city.utsunomiya.tochigi.jp/)
