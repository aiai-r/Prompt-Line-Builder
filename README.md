# Prompt Line Builder

Stable Diffusion WebUI reForge 向けの拡張です。プロンプト・パラメータを行ごとに追加し、「Prompts from file or textbox」で読み込めるテキストを作成できます。モデルやサンプラー、各種生成パラメータを GUI 上から直接指定し、1 行ずつ組み立てて保存できます。

## 主な機能
- プロンプト/ネガティブプロンプトを行単位で追加
- モデル・サンプラー・スタイルの選択と各種パラメータ指定（任意入力のみを引数化）
- 行リストのテキスト保存（UTF-8）および貼り付け・ドラッグ＆ドロップでの読み込み
- txt2img / img2img 両方に対応

## インストール
- 拡張タブから Install from URL  
  1. WebUI の「Extensions」タブを開く  
  2. 「Install from URL」にリポジトリの URL を入力し、「Install」を押す  
  3. 完了後に「Installed」タブから「Apply and restart UI」を実行
- 手動クローン  
  1. WebUI の `extensions` フォルダへ移動  
  2. `git clone <このリポジトリのURL> Prompt-Line-Builder`  
  3. WebUI を再起動

## 使い方
1. WebUI を起動し、txt2img または img2img タブを開くと「Prompt Line Builder」が表示されます。
2. 各行のプロンプト/ネガティブプロンプトと必要なパラメータを入力し、「行を追加」でコマンド形式の行を組み立てます。
3. 「txt に保存」で `prompt_lists` 配下に UTF-8 で保存できます。ドラッグ＆ドロップでテキストを読み込むことも可能です。
4. 何も入力していないパラメータは引数に含まれません。入力したものだけが `--seed` などのフラグとして付与されます。

## ライセンス
本リポジトリは Stable Diffusion WebUI（AGPL-3.0）に依存しています。公開時は AGPL-3.0 での配布を推奨します。MIT など別ライセンスで公開する場合は依存関係とライセンス適合性をご確認ください。
