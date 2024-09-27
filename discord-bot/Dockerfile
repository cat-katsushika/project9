# ベースイメージとしてPythonを指定
FROM python:3.11.10-slim-bullseye

# 作業ディレクトリを指定
WORKDIR /discord-bot

# 必要な依存関係があれば、ここでインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコンテナにコピー
COPY bot.py ./

# コンテナ内でPythonスクリプトを実行する
CMD [ "python", "./bot.py" ]
