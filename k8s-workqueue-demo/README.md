# Xử Lý Công Việc Song Song Trong Kubernetes Với Hàng Đợi Redis
## Tổng Quan
Dự án này minh họa cách sử dụng Kubernetes để xử lý công việc song song từ hàng đợi Redis. Mỗi công việc sẽ xử lý các nhiệm vụ được lấy từ hàng đợi Redis. Cấu hình này thể hiện cách Kubernetes có thể phân phối và xử lý các nhiệm vụ một cách hiệu quả trong một hệ thống phân tán.
### Tổng quan về luồng hoạt động 
Redis giữ danh sách công việc (hàng đợi công việc).
Worker pods trong Kubernetes kết nối đến Redis và lấy công việc.
Các worker pods xử lý các công việc song song (tuỳ thuộc vào số lượng pod bạn yêu cầu).
Sau khi các công việc được xử lý, bạn có thể kiểm tra kết quả hoặc dọn dẹp các tài nguyên đã sử dụng.
### Sơ đồ luồng hoạt động 
+-------------+       +-------------+       +-------------+
|             |       |             |       |             |
|   Redis     |<----->| Worker Pod  |<----->| Worker Pod  |
| (Queue)     |       | (Process)   |       | (Process)   |
|             |       |             |       |             |
+-------------+       +-------------+       +-------------+
### Giải thích ví dụ dễ hơn 
Giả sử bạn có một ứng dụng xử lý hình ảnh:

Các công việc trong Redis có thể là tên các tệp hình ảnh.

Worker pod sẽ lấy tên tệp từ Redis, tải hình ảnh và thực hiện một số xử lý (ví dụ: thay đổi kích thước, nhận dạng đối tượng, v.v.).

Sau khi hoàn thành, pod sẽ gửi lại kết quả hoặc lưu trữ kết quả đã xử lý.

Với parallelism: 2, hai worker pod sẽ cùng xử lý các tệp hình ảnh một cách song song, giúp tiết kiệm thời gian và tăng hiệu suất xử lý.
### Cơ chế chi tiết 
Cơ chế mà chúng ta đang nói đến sử dụng một hàng đợi công việc (work queue) lưu trữ các nhiệm vụ trong Redis. Các worker pods trong Kubernetes sẽ lấy công việc từ hàng đợi này và xử lý chúng một cách song song. Đây là một cách để phân chia công việc và tận dụng khả năng mở rộng của Kubernetes.
Cơ chế Chi Tiết
Redis là hàng đợi công việc: Redis được sử dụng như một nơi lưu trữ các nhiệm vụ cần xử lý. Nó hoạt động như một hàng đợi mà các worker (các pod trong Kubernetes) có thể push và pop các công việc vào và ra.

rpush: Lệnh này thêm các công việc vào cuối hàng đợi Redis.

lrange: Lệnh này dùng để xem các công việc trong hàng đợi, giúp kiểm tra xem công việc nào đã được thêm vào.

Các công việc có thể là bất kỳ tác vụ nào mà bạn muốn các worker xử lý. Ví dụ, bạn có thể thêm các tên công việc như "task1", "task2", v.v.

Worker Pods trong Kubernetes: Các worker pods là những pod trong Kubernetes sẽ lấy công việc từ Redis để xử lý. Mỗi worker pod chạy một instance của ứng dụng Python hoặc bất kỳ ứng dụng nào bạn tạo ra để xử lý công việc.

Worker Pod: Mỗi worker sẽ kết nối đến Redis và lấy công việc từ hàng đợi bằng cách sử dụng các lệnh Redis như lpop hoặc rpop (tùy vào cách bạn thiết kế). Sau đó, worker thực hiện công việc và có thể lưu kết quả hoặc thực hiện các hành động khác.

Parallelism: Bạn có thể điều chỉnh số lượng pod worker song song để tăng hiệu quả xử lý. Ví dụ, nếu bạn đặt parallelism: 2 trong cấu hình job của Kubernetes, hai pod worker sẽ chạy song song, xử lý hai công việc cùng một lúc.

Công việc được xử lý song song: Kubernetes sẽ khởi tạo nhiều worker pod dựa trên số lượng worker mà bạn chỉ định (thông qua tham số parallelism). Các worker pod này sẽ lấy các công việc từ Redis và bắt đầu xử lý chúng.

Giả sử bạn có 10 công việc trong Redis và parallelism: 2, thì 2 worker pods sẽ cùng nhau xử lý công việc, mỗi worker sẽ lấy 5 công việc từ Redis và xử lý chúng.

Nếu một worker pod hoàn thành một công việc, nó sẽ tiếp tục lấy công việc tiếp theo từ Redis và xử lý cho đến khi không còn công việc nào trong hàng đợi.

Giám sát và Quản lý công việc: Sau khi các worker pod xử lý xong công việc, Kubernetes sẽ tự động quản lý việc khởi động lại các pod nếu có sự cố. Bạn có thể theo dõi tiến trình công việc qua các logs của pod và kiểm tra xem công việc có được xử lý hoàn tất không.
## Yêu Cầu Trước Khi Bắt Đầu
Trước khi bạn bắt đầu, bạn cần có:

Một cụm Kubernetes (Bạn có thể sử dụng Minikube hoặc một dịch vụ Kubernetes được quản lý như Google Kubernetes Engine).
Công cụ dòng lệnh kubectl đã được cấu hình để giao tiếp với cụm của bạn.
Docker được cài đặt trên máy tính cục bộ của bạn để xây dựng và đẩy image Docker.
Quyền truy cập vào một Docker registry (như Docker Hub) nơi bạn có thể đẩy Docker image.
## Cài Đặt Môi Trường
### Bước 1: Khởi Động Redis
Trước tiên, bạn cần triển khai Redis trong cụm Kubernetes của mình, nơi sẽ được sử dụng làm hàng đợi nhiệm vụ:

```
kubectl apply -f https://k8s.io/examples/application/job/redis/redis-pod.yaml
kubectl apply -f https://k8s.io/examples/application/job/redis/redis-service.yaml
```
```
kubectl delete -f redis-pod.yaml
kubectl delete -f redis-service.yaml
```
```
```
Hai lệnh này sẽ triển khai một Pod Redis và một dịch vụ để các Pod khác có thể giao tiếp với Redis.
### Bước 2: Điền Hàng Đợi Redis
Bạn cần điền vào hàng đợi Redis với các nhiệm vụ. Khởi động một Pod tạm thời để truy cập Redis CLI:
```
kubectl run -i --tty temp --image redis --command "/bin/sh"

```
```
kubectl delete pod temp
```
Khi shell đã sẵn sàng, kết nối đến instance Redis và thêm các nhiệm vụ:
```
redis-cli -h redis
rpush job2 "task1"
rpush job2 "task2"
... (add more tasks as needed) ...
lrange job2 0 -1
```
Sau khi đã hoàn thành, thoát khỏi session tương tác bằng lệnh: (Exit hết đến thư mục chứa nó)
```
exit

### Bước 3: Xây Dựng Và Đẩy Docker Image
Bây giờ bạn cần xây dựng Docker image chứa ứng dụng công việc của mình. Đây là lệnh để thực hiện điều đó:

```
docker build -t yourusername/job-wq-2 .
docker push yourusername/job-wq-2
```
ví dụ của tôi la  huong1906

```
docker build -t huong1906/job-wq-2 .
docker push huong1906/job-wq-2
```
Bước 4: Định Nghĩa và Chạy Job
Tạo một tệp YAML mô tả job sử dụng Docker image bạn đã tạo. Dưới đây là ví dụ về tệp job.yaml:

```
apiVersion: batch/v1
kind: Job
metadata:
  name: job-wq-2
spec:
  parallelism: 2
  template:
    spec:
      containers:
      - name: worker
        image: yourusername/job-wq-2:latest
        env:
        - name: REDIS_HOST
          value: "redis"
      restartPolicy: Never

```
Sau khi tạo tệp job.yaml, áp dụng cấu hình này vào cụm Kubernetes:
```
kubectl apply -f job.yaml

```
### Bước 5: Giám Sát và Quản Lý Job
Bạn có thể kiểm tra trạng thái của job bằng cách sử dụng lệnh:

```
kubectl describe jobs/job-wq-2
```
Để xem logs của các Pod và theo dõi tiến độ, sử dụng lệnh sau:

```
kubectl logs -f job-wq-2...( điền theo đúng tên đã hiện )
```

### Bước 6: Dọn Dẹp
Để dọn dẹp các tài nguyên đã sử dụng trong demo này, bạn có thể xóa job và Redis deployment:
```
kubectl delete job job-wq-2
kubectl delete pod redis
kubectl delete svc redis
```
### Kết Luận
Demo này minh họa cách Kubernetes có thể được sử dụng để quản lý việc xử lý song song các nhiệm vụ bằng cách sử dụng một hàng đợi Redis. Cấu hình này có thể được điều chỉnh cho các trường hợp sử dụng khác nhau, nơi phân phối và quản lý nhiệm vụ là rất quan trọng.