# 使用素材

- 8×8ドット日本語フォント「美咲フォント」
- https://littlelimit.net/misaki.htm#download

# github用ブラウザ化
```bash
uv run pyxel package . main.py
uv run pyxel app2html 01_seven_wonders.pyxapp
```

- htmlをdocs/index.htmlとして移動
- githubで以下を実施
  - Setting/PagesでBranchをmasterにし/docsに変更してsave
  - https://{user_name}.github.io/01_seven_wonders/