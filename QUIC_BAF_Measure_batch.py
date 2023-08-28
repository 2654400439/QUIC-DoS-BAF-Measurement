import os
import time

# 批量执行，请准备包含待测试对象的文件。以doq测量为例
with open('doq_ip.txt', 'r') as f:
    data = f.read()

ip_list = data.split('\n')[:-1]

for ip in ip_list:
    os.system("python QUIC_BAF_Measure.py --ca-certs tests/pycacert.pem  --host " + ip +
              " --port 853")
    time.sleep(0.5)



