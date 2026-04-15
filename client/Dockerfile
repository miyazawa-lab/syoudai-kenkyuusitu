# ベースイメージ
FROM debian:bookworm-slim

# gcc など開発ツールをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential gcc make \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# client.txt を追加
COPY client.txt /app/client.txt

# client.txt → client.c に変換してコンパイル
RUN mv client.txt client.c && \
    gcc client.c -o client -lpthread

# コンテナ起動時に実行
CMD ["./client"]
