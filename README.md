# QUIC-DoS-BAF-Measurement
一个用于测量QUIC(http3、doq)首包反射放大效果(放大倍率)的工具。
A tool for measuring the magnification of QUIC(http3、doq) initial-packet reflection amplification attacks.

### 简介
受启发于火山引擎云安全团队发表的一篇[关于QUIC反射放大攻击测量的博客](https://www.anquanke.com/post/id/289906)，博客中提到尽管QUIC协议在设计之初就考虑到了被用于反射放大攻击的威胁，并且引入了很多相关的安全机制，但是由于实际网络场景、特定配置等情况，导致现网中存在大量的具有反射放大效果的QUIC服务端。该篇博客只关注了基于首包（initial）的反射放大攻击，并且给出了测量结果但是测量代码并没有给出。此项目给出用于测量QUIC服务端init阶段反射放大倍数的代码。

实现原理相对简单，通过复用QUIC的python实现（[aioquic](https://github.com/aiortc/aioquic)）中的发包代码可以完成任务需求。注意，综合考虑带宽、准确率等因素，本项目并没有使用异步收发包的处理架构，而是采用串行发包+收发分离的架构来实现。可以对QUIC上层应用--http3以及dns over quic的服务端进行放大倍数的测量。

### 部署运行方式
1. 首先请确保你已经安装并且配置好了[aioquic](https://github.com/aiortc/aioquic)。安装完成aioquic后你需要根据readme提示执行examples文件夹下的http3_server.py和http3_client.py，以验证aioquic是否能正常运行。
2. 开启网络抓包工具（推荐wireshark）监听正确的网卡，用于收发分离架构下的数据包捕获。
3. 执行脚本向目标ip:port发送QUIC的init包，注意对于http3需要提供SNI。推荐将本项目下的代码放到aioquic/examples下。执行下面代码可开启测量。

测量http3服务端：

`python examples/QUIC_BAF_Measure.py --ca-certs tests/pycacert.pem  --host 1.2.3.4 --port 443 --server-name "www.example.com"`

测量doq服务端：

`python examples/QUIC_BAF_Measure.py --ca-certs tests/pycacert.pem  --host 1.2.3.4 --port 443`

4. (可选)使用QUIC_BAF_Measure_batch.py进行批量处理。
5. 结束发包测量。收集整理抓包工具中获得的相关数据包，按照ip、端口过滤。
6. 使用QUIC_BAF_Measure_Analysis.py进行数据分析。
