from scapy.all import rdpcap

# 读取 PCAP 文件
pcap_file = "test.pcapng"
packets = rdpcap(pcap_file)

srcip_len_tuple = []

for packet in packets:
    srcip_len_tuple.append([packet[0][1].src, len(packet)])

# print(srcip_len_tuple)

ip_sum_dict = {}

# 遍历每个子列表
for item in srcip_len_tuple:
    ip = item[0]  # 获取 IP 地址
    num = item[1]  # 获取数字

    # 将数字累加到对应的 IP 地址的和上
    ip_sum_dict[ip] = ip_sum_dict.get(ip, 0) + num

# 将字典转换为列表，每个元素是一个元组 (IP, 数字之和)
result = [(ip, total) for ip, total in ip_sum_dict.items()]

sorted_result = sorted(result, key=lambda x: x[1], reverse=True)

print(sorted_result)

ip_list = []
BAF_list = []

for item in sorted_result:
    ip_list.append(item[0])
    BAF_list.append(item[1])

print(len(ip_list))


BAF_list = [item / 1322 for item in BAF_list]

print(BAF_list)

flag_none_BAF = 0
flag_1_3_BAF = 0
flag_over_3_BAF = 0

for BAF in BAF_list:
    if BAF < 1:
        flag_none_BAF += 1
    elif 1 < BAF <= 3:
        flag_1_3_BAF += 1
    elif BAF > 3:
        flag_over_3_BAF += 1

print(flag_none_BAF, flag_1_3_BAF, flag_over_3_BAF)