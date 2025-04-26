import time
import rediswq

# Định nghĩa máy chủ Redis mà hàng đợi sử dụng.
host = "redis"
# Uncomment (bỏ dấu comment) dòng dưới đây nếu Kube-DNS không hoạt động.
# import os
# host = os.getenv("REDIS_SERVICE_HOST")  # Lấy hostname từ biến môi trường

# Khởi tạo đối tượng RedisWQ để làm việc với hàng đợi Redis.
q = rediswq.RedisWQ(name="job2", host=host)
print("Worker with sessionID: " +  q.sessionID())  # In ra session ID của worker
print("Initial queue state: empty=" + str(q.empty()))  # Kiểm tra và in trạng thái ban đầu của hàng đợi

# Chạy vòng lặp cho đến khi hàng đợi trống.
while not q.empty():
  # Thuê (lease) một mục từ hàng đợi. Nếu không có mục, đợi 2 giây trước khi thử lại.
  item = q.lease(lease_secs=10, block=True, timeout=2)
  if item is not None:  # Nếu có mục được thuê thành công
    itemstr = item.decode("utf-8")  # Giải mã mục từ bytes sang chuỗi
    print("Working on " + itemstr)  # In ra mục đang được xử lý
    time.sleep(10)  # Thay thế bằng code xử lý thực tế. Đây chỉ là giả lập thời gian xử lý.
    q.complete(item)  # Đánh dấu hoàn thành xử lý mục
  else:  # Nếu không có mục nào được thuê trong lần này
    print("Waiting for work")  # In ra thông báo đang đợi công việc

# Khi hàng đợi trống, thông báo và thoát.
print("Queue empty, exiting")