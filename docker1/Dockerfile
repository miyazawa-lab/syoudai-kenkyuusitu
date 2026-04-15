FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc make \
        libjansson-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# server.txt をコピー
COPY server.txt /app/server.txt

# server.txt → server.c に変更してコンパイル
RUN mv server.txt server.c && \
    gcc server.c -o server -lpthread -ljansson

CMD ["./server"]


