# 使用素材

- 8×8ドット日本語フォント「美咲フォント」
- https://littlelimit.net/misaki.htm#download

# github用ブラウザ化

```
.\build.ps1
```

```bash
uv run pyxel package . main.py
uv run pyxel app2html 01_seven_wonders.pyxapp
New-Item -ItemType Directory -Force docs | Out-Null
Move-Item -Force 01_seven_wonders.html docs/index.html
```

- htmlをdocs/index.htmlとして移動
- githubで以下を実施
  - Setting/PagesでBranchをmasterにし/docsに変更してsavehttps://{user_name}.github.io/01_seven_wonders/
