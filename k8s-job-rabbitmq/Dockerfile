# # Tạo Docker Image cho worker

# # Dockerfile
# # Specify BROKER_URL and QUEUE when running
# FROM ubuntu:20.04

# # Cài đặt các gói cần thiết
# RUN apt-get update && \
#     DEBIAN_FRONTEND=noninteractive apt-get install -y curl ca-certificates amqp-tools python2 dnsutils \
#     --no-install-recommends && \
#     rm -rf /var/lib/apt/lists/*

# # Copy script worker vào image và đặt quyền thực thi (mặc dù đã chmod trước đó)
# COPY ./worker.py /worker.py
# RUN chmod +x /worker.py

# # Lệnh mặc định khi container chạy
# # Lấy 1 (-c 1) tin nhắn từ hàng đợi $QUEUE tại $BROKER_URL
# # và chạy script /worker.py với tin nhắn đó làm input
# CMD ["/usr/bin/amqp-consume", "--url=${BROKER_URL}", "-q", "${QUEUE}", "-c", "1", "/worker.py"]
# FROM python:3.8-slim

# RUN apt-get update && apt-get install -y curl ca-certificates dnsutils --no-install-recommends && \
#     pip install pika && \
#     rm -rf /var/lib/apt/lists/*

# COPY ./worker.py /worker.py
# RUN chmod +x /worker.py

# CMD ["python", "/worker.py"]
# FROM ubuntu:20.04

# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt-get update && \
#     apt-get install -y curl ca-certificates python2-minimal dnsutils && \
#     apt-get install -y --no-install-recommends \
#     amqp-tools || true && \
#     rm -rf /var/lib/apt/lists/*

# COPY ./worker.py /worker.py
# RUN chmod +x /worker.py

# CMD ["/usr/bin/amqp-consume", "--url=${BROKER_URL}", "-q", "${QUEUE}", "-c", "1", "/worker.py"]
FROM ubuntu:20.04

# Fix không hỏi interactive khi cài gói
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y curl ca-certificates python2 dnsutils && \
    apt-get install -y --no-install-recommends amqp-tools && \
    rm -rf /var/lib/apt/lists/*

COPY ./worker.py /worker.py
RUN chmod +x /worker.py

CMD ["sh", "-c", "/usr/bin/amqp-consume --url=\"$BROKER_URL\" -q \"$QUEUE\" -c 1 /worker.py"]
