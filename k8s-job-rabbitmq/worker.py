#!/usr/bin/env python
# Script Python để tiêu thụ tin nhắn từ hàng đợi

import sys
import time

# Đọc dòng đầu tiên từ standard input (do amqp-consume chuyển tiếp)
message = sys.stdin.readlines()[0].strip()
print(f"Processing {message}") # In ra màn hình công việc đang xử lý
time.sleep(10)                 # Giả lập thời gian xử lý công việc
print(f"Finished processing {message}")