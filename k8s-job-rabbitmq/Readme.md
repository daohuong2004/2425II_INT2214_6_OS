# Demo Xử Lý Song Song Sử Dụng Hàng Đợi Công Việc trong Kubernetes

## Giới Thiệu

### Bài toán
 Bạn có một đống công việc nhỏ (ví dụ: xử lý ảnh, tính toán số liệu, thực hiện các tác vụ nhỏ...) → muốn chia ra nhiều worker làm song song cho nhanh.

### Thách thức:
- Làm sao phân phối công việc cho các worker?
- Làm sao quản lý worker?
- Làm sao tăng giảm số lượng worker tùy lúc?

### Giải pháp của demo:

Minh họa hoàn chỉnh cách Kubernetes hỗ trợ song song hóa (Parallel Processing) thông qua:
RabbitMQ = chia nhỏ công việc.
Job = quản lý số lượng Pod worker, tự động scale.
Pod worker = mỗi Pod độc lập xử lý 1 công việc.

### Các thành phần 
Thành Phần	
- RabbitMQ: Một cái "hàng đợi" để chứa danh sách công việc cần làm. Các worker sẽ bốc việc từ đây.
- Pod worker: Một worker cụ thể (chạy trong container). Mỗi Pod tự động lấy 1 việc từ RabbitMQ, làm, rồi tự chết (hoặc Kubernetes sẽ restart nếu lỗi).
- Kubernetes Job: Một bộ điều phối! Nó đảm bảo rằng sẽ có đủ số Pod worker được tạo ra để xử lý hết mọi công việc. Có thể quy định "cho chạy song song tối đa bao nhiêu worker" qua parallelism.
- Docker Image worker	Là chương trình xử lý thực tế, build sẵn vào một image. Các Pod worker chỉ việc tải về và chạy.
+------------+        +----------------+
| temp pod   |        | RabbitMQ        |
| (amqp-publish) ---> | job1 queue      |
+------------+        +----------------+
                             ↑
                             |
     +-----------------------+---------------------+
     |                       |                     |
+------------+        +------------+         +------------+
| Worker Pod |        | Worker Pod  |         | Worker Pod  |
| (worker.py)|        | (worker.py) |         | (worker.py) |
+------------+        +------------+         +------------+
### Mô hình hoạt động 
Ví dụ như sau :
1. Bạn có 8 cái task "Cần xử lý ảnh 1, 2, 3,...8".
2. Bạn nạp 8 cái task này vào RabbitMQ.

3. Bạn tạo 1 Kubernetes Job với:
completions: 8 (phải hoàn thành 8 Pod).
parallelism: 2 (cho phép chạy song song tối đa 2 Pod cùng lúc).
4. Kubernetes bắt đầu tạo 2 Pod cùng lúc:
Mỗi Pod khởi động → Kết nối RabbitMQ → Bốc 1 task → Làm xong → Thoát.
5. Khi một Pod xong, Job controller lại tạo thêm Pod khác (nếu chưa đủ 8).
6. Cứ thế, cho đến khi 8 task được xử lý hết, Job mới coi là hoàn thành.

## Yêu Cầu Hệ Thống

- Kubernetes Cluster với ít nhất hai node không phải là control plane hosts.
- `kubectl` đã cấu hình để giao tiếp với cluster của bạn.
- Docker, để xây dựng và quản lý các images container của bạn.
- Tài khoản trên Docker Hub hoặc một registry khác để lưu trữ các images.

## Cài Đặt và Cấu Hình
### Bước 1: Khởi Tạo RabbitMQ

Tạo Service và StatefulSet cho RabbitMQ bằng các lệnh sau:
```
kubectl create -f https://kubernetes.io/examples/application/job/rabbitmq/rabbitmq-service.yaml
kubectl create -f https://kubernetes.io/examples/application/job/rabbitmq/rabbitmq-statefulset.yaml
```
kubectl apply -f rabbitmq-service.yaml
kubectl apply -f rabbitmq-statefulset.yaml

### Bước 2: Tạo Pod Tạm Thời và Cài Đặt Công Cụ
```
kubectl run -i --tty temp --image ubuntu:22.04
```
Sau đó cài đặt các công cụ cần thiết:
```
apt-get update && apt-get install -y curl ca-certificates amqp-tools python3 dnsutils
```
### Bước 3: Chuẩn Bị và Đẩy Image
Tạo Dockerfile và script xử lý, sau đó build và đẩy image lên Docker Hub:
```
docker build -t <username>/job-wq-1 .
docker push <username>/job-wq-1
```
### Bước 4: Triển Khai Job
Tạo file job.yaml và áp dụng nó bằng lệnh:
```
kubectl apply -f job.yaml
```
## Sử Dụng
Sau khi triển khai Job, bạn có thể kiểm tra trạng thái và log của các Pods để đảm bảo rằng các tác vụ đang được xử lý một cách chính xác.

