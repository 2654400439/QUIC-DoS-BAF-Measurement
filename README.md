# QUIC-DoS-BAF-Measurement
一个用于测量QUIC(http3、doq)首包反射放大效果(放大倍率)的工具。
A tool for measuring the magnification of QUIC(http3、doq) initial-packet reflection amplification attacks.

### 简介
受启发于火山引擎云安全团队发表的一篇[关于QUIC反射放大攻击测量的博客](https://www.anquanke.com/post/id/289906)，博客中提到尽管QUIC协议在设计之初就考虑到了被用于反射放大攻击的威胁，并且引入了很多相关的安全机制，但是由于实际网络场景、特定配置等情况，导致现网中存在大量的具有反射放大效果的QUIC服务端。该篇博客只关注了基于首包（initial）的反射放大攻击，并且给出了测量结果但是测量代码并没有给出。此项目给出用于测量QUIC服务端init阶段反射放大倍数的代码。

实现原理相对简单，通过复用QUIC的python实现（[aioquic](https://github.com/aiortc/aioquic)）中的发包代码可以完成任务需求。注意，综合考虑带宽、准确率等因素，本项目并没有使用异步收发包的处理架构，而是采用串行发包+收发分离的架构来实现。可以对QUIC上层应用--http3以及dns over quic的服务端进行放大倍数的测量。
