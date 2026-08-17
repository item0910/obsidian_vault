---
date: 2024-09-07
mtime: 2024-09-25
---

# 二、三. JVM 监控及诊断工具

**JVM 虚拟机**; **Java**

## 二、命令行篇

### 1. 概述

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面).jpg]]
- 简单命令行工具
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-1.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-2.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-3.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-4.jpg]]

### 2. jps: 查看正在运行的 java 线程

#### 基本情况

#### 测试

#### 基本语法

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-6.jpg]]
可以通过 jps -help 来查看对应的参数信息

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-7.jpg]]
综合使用：
jps -l -m 等价于 jps -lm
如何将信息输出到同级文件中：
语法：命令 > 文件名称
例如：jps -l > a.txt

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-8.jpg]]

### 3. jstat: 查看 JVM 统计信息

#### 基本情况

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-9.jpg]]

#### 基本语法

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-10.jpg]]
其中 vmid 是进程 id 号，也就是 jps 之后看到的前面的号码，如下：

- option 参数
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-12.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-13.jpg]]
1、-class 举例：jstat -class -t -h3 13152 1000 10，其中 h3 中的 3 代表每隔 3 个分隔一次，13152 代表类的进程 id，1000 代表每隔 1000 毫秒打印一次，10 代表一共打印 10 次，如下所示：

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-14.jpg]]

其中 Timestamp 代表程序至今的运行时间，单位为秒；Loaded 代表加载的类的数目；Bytes 代表加载的类的总字节数；Unloaded 代表卸载的类的数目；Bytes 代表卸载的类的总字节数；Time 代表类装载所消耗的时间；

2、-gc 举例：jstat -gc 13152，其中 13152 代表类的进程 id，执行结果如下所示：

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-15.jpg]]

 其中 S0C 代表幸存者 0 区的总容量，S1C 代表幸存者 1 区的总容量，S0U 代表幸存者 0 区使用的容量，S1U 代表幸存者 1 区使用的容量，EC 代表伊甸园区的总容量，EU 代表伊甸园区使用的总容量，OC 代表老年代的总容量，OU 代表老年代已经使用的容量，MC 代表方法区的总容量，MU 代表方法区的总容量，CCSC 代表压缩类的总容量，CCSU 代表压缩类使用的容量，YGC 代表年轻代垃圾回收的次数，YGCT 年轻代进行垃圾回收需要的时间，FGC 代表代表 Full GC 的次数，FGCT 代表 Full GC 的时间，GCT 代表垃圾回收的总时间

 3、-gccapacity 举例：jstat -gccapacity 13152，其中 13152 代表类的进程 id，执行结果如下：

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-16.jpg]]

其中 S0C 代表幸存者 0 区的容量，S1C 代表幸存者 1 区的容量，EC 代表伊甸园区的容量，CCSC 代表压缩类的容量，YGC 代表年轻代垃圾回收的时间，FGC 代表 Full GC 垃圾回收的时间

 4、-gcutil 举例：jstat -gcutil 13152，其中 13152 代表类的进程 id，执行结果如下所示：

 以上是各区域占比以及垃圾回收的情况，S0 代表幸存者 0 区，S1 代表幸存者 1 区，E 代表伊甸园区，O 代表老年代，M 代表方法区，CCS 代表压缩类，以上这些值都是占比情况，YGC 代表年轻代垃圾回收的次数，YGCT 年轻代进行垃圾回收需要的时间，FGC 代表代表 Full GC 的次数，FGCT 代表 Full GC 的时间，GCT 代表垃圾回收的总时间

 5、-gccause 举例：jstat -gccause 13152，其中 13152 代表类的进程 id，执行结果如下：

 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-18.jpg]]

 以上是各区域占比以及垃圾回收的情况，还有触发垃圾回收的原因解释，S0 代表幸存者 0 区，S1 代表幸存者 1 区，E 代表伊甸园区，O 代表老年代，M 代表方法区，CCS 代表压缩类，以上这些值都是占比情况，YGC 代表年轻代垃圾回收的次数，YGCT 年轻代进行垃圾回收需要的时间，FGC 代表代表 Full GC 的次数，FGCT 代表 Full GC 的时间，GCT 代表垃圾回收的总时间，LGCC 和 GCC 代表垃圾回收的原因

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-19.jpg]]

- interval 参数
用于指定输出统计数据的周期，单位为毫秒。即：查询间隔

- count 参数
用于指定查询的总次数

- -t 参数

可以在输出信息前加上一个 Timestamp 列，显示程序的运行时间。单位：秒
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-20.jpg]]

我们执行 jstat -gc -t 13152 1000 10，这代表 1 秒打印出 1 行，一共 10 行，-t 代表打印出 Timestamp 总运行时间，结果如下所示：

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-21.jpg]]

上方红色框框中代表 Timestamp，而蓝色框框中代表垃圾回收时间，单位都是秒，如果让红色框框中的某两个值相减，假设这个值是 num1，然后让对应行的蓝色框框中的另外两个值相减，假设这个值是 num2，之后让 num2/num1，得出的差值就是上述所说的 GC 时间占运行时间的比例

虽然这种方式比较繁琐，但是在项目部署之后就需要使用命令行去看了，就没有可视化界面了，所以这种方式也要会

- -h 参数

#### 补充

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-22.jpg]]
第 1 步可以执行命令：jstat -gc -t 13152 1000 10

### 4. jinfo: 实时查看和修改 JVM 配置参数

#### 基本情况

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-23.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-24.jpg]]

#### 基本语法

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-25.jpg]]

##### 查看

- jinfo -sysprops 进程 id
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-26.jpg]]
可以查看由 System.getProperties() 取得的参数

- jinfo -flags 进程 id 查看设置的参数
查看曾经赋过值的一些参数
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-27.jpg]]

- jinfo -flag 参数名称 进程 id
查看某个 java 进程的具体参数信息
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面).jpeg]]

##### 修改

- jinfo -flag [+|-] 参数名称 进程 id
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-28.jpg]]

- jinfo -flag 参数名称=参数值 进程 id
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-29.jpg]]

#### 拓展

- java -XX:+PrintFlagsInitial
  查看所有 JVM 参数启动的初始值

- java -XX:+PrintFlagsFinal
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-30.jpg]]
值前面添加冒号: 的是修改之后的值，没有添加的都是没有发生改变的初始值

查看所有 JVM 参数的最终值

- java - 参数名称:+PrintCommandLineFlags
  查看那些已经被用户或者 JVM 设置过的详细的 XX 参数的名称和值

### 5. jmap: 导出 JVM 内存映像文件&内存使用情况

#### 基本情况

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-31.jpg]]

#### 基本语法

- -dump
  生成 Java 堆转储快照：dump 文件
  特别的：-dump:live 只保存堆中的存活对象
- -heap
  输出整个堆空间的详细信息，包括 GC 的使用、堆配置信息，以及内存的使用信息等
- -histo
  输出堆中对象的同级信息，包括类、实例数量和合计容量
  特别的：-histo:live 只统计堆中的存活对象
- -permstat
  以 ClassLoader 为统计口径输出永久代的内存状态信息
  仅 linux/solaris 平台有效
- -finalizerinfo
  显示在 F-Queue 中等待 Finalizer 线程执行 finalize 方法的对象
  仅 linux/solaris 平台有效
- -F
  当虚拟机进程对 -dump 选项没有任何响应时，可使用此选项强制执行生成 dump 文件
- -h | -help
  jamp 工具使用的帮助命令
- -J [flag]
  传递参数给 jmap 启动的 jvm

#### 使用 1: 导出内存映像文件

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-32.jpg]]

注意：
对于以上说明中的第 1 点是自动方式才会这样做，而手动不会在 Full GC 之后生成 Dump

使用手动方式生成 dump 文件，一般指令执行之后就会生成，不用等到快出现 OOM 的时候

使用自动方式生成 dump 文件，当出现 OOM 之前先生成 dump 文件

如果使用手动方式，一般使用第 2 种，毕竟生成堆中存活对象的 dump 文件是比较小的，便于传输和分析

##### 手动的方式

- jmap -dump:format=b,file=<filename.hprof> < pid>
- jmap -dump:live,format=b,file=<filename.hprof> < pid>

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-34.jpg]]

##### 自动的方式

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-35.jpg]]

具体使用如下：

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-36.jpg]]

自动的方式

  -XX:+HeapDumpOnOutOfMemoryError
  -XX:HeapDumpPath=<filename.hprof>


#### 使用 2: 显示堆内存相关信息

- jmap -heap

进程 id 只是时间点上的堆信息，而 jstat 后面可以添加参数，可以指定时间动态观察数据改变情况，而图形化界面工具，例如 jvisualvm 等，它们可以用图表的方式动态展示出相关信息，更加直观明了

例子如下：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-37.jpg]]
- jmap -histo 进程 id

输出堆中对象的同级信息，包括类、实例数量和合计容量，也是这一时刻的内存中的对象信息
例子如下：

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-38.jpg]]

#### 使用 3: 其他作用

这两个指令仅 linux/solaris 平台有效，所以无法在 windows 操作平台上演示，并且使用比较小众，不在多说
- jmap -permstat 进程 id
  查看系统的 ClassLoader 信息
- jmap -finalizerinfo
  查看堆积在 finalizer 队列中的对象

#### 小结

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-39.jpg]]

### 6. jhat: JDK 自带堆分析工具

#### 基本情况

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-40.jpg]]

#### 基本语法

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-41.jpg]]
其中 dumpfile 代表 dump 文件的地址以及名称，例如：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-42.jpg]]
- options 参数
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-43.jpg]]
举例:
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-44.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-45.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-46.jpg]]

### 7. jstack: 打印 JVM 中线程快照

#### 基本情况

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-47.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-48.jpg]]

#### 基本语法

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-49.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-50.jpg]]
举例:
1. ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-51.jpg]]
2. 加 -l 参数 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-52.jpg]]

总结:
如果程序出现等待问题，可以使用该指令去查看问题所在，结果中也会提示你问题所在

- option 参数：-F
  当正常输出的请求不被响应时，强制输出线程堆栈
- option 参数：-l
  除堆栈外，显示关于锁的附加信息
- option 参数：-m
  如果调用本地方法的话，可以显示 C/C++ 的堆栈
- option 参数：-h
  帮助操作


### 8. jcmd: 多功能命令行

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-53.jpg]]

#### 基本情况

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-54.jpg]]

#### 基本语法

- jcmd -l
  列出所有的 JVM 进程
- jcmd 进程号 help
  针对指定的进程，列出支持的所有具体命令
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-55.jpg]]
- jcmd 进程号 具体命令
  显示指定进程的指令命令的数据

### 9. jstatd: 远程主机信息收集

## 三、GUI(图形界面) 篇

### 1. 工具概述

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-56.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-57.jpg]]

### 2. JConsole

#### 基本概述

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-58.jpg]]

#### 启动

  - 在 jdk 安装目录中找到 jconsole.exe，双击该可执行文件就可以

  - 打开 DOS 窗口，直接输入 jconsole 就可以了

#### 三种连接方式

- Local

注意：本地连接要求 启动 jconsole 的用户 和 运行当前程序的用户 是同一个用户

具体操作如下：

1、在 DOS 窗口中输入 jconsole
    ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-59.jpg]]

2、在控制台上填写相关信息
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-60.jpg]]

3、选择“不安全的连接”

使用 JConsole 连接一个正在本地系统运行的 JVM，并且执行程序的和运行 JConsole 的需要是同一个用户。JConsole 使用文件系统的授权通过 RMI 连接起链接到平台的 MBean 的服务器上。这种从本地连接的监控能力只有 Sun 的 JDK 具有。

4、进入控制台页面
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-61.jpg]]

- Remote

使用下面的 URL 通过 RMI 连接器连接到一个 JMX 代理，service:jmx:rmi:///jndi/rmi://hostName:portNum/jmxrmi。JConsole 为建立连接，需要在环境变量中设置 mx.remote.credentials 来指定用户名和密码，从而进行授权。

- Advanced
使用一个特殊的 URL 连接 JMX 代理。一般情况使用自己定制的连接器而不是 RMI 提供的连接器来连接 JMX 代理，或者是一个使用 JDK1.4 的实现了 JMX 和 JMX Rmote 的应用

#### 主要作用

1、概览
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-62.jpg]]

2、内存
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-63.jpg]]

3、根据线程检测死锁
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-64.jpg]]

4、线程
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-65.jpg]]

5、VM 概要
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-66.jpg]]

### 3. VisualVM

jvisualvm 和 visual vm 的区别：

visual vm 是单独下载的工具，然后将 visual vm 结合到 jdk 中就变成了 jvisualvm，仅仅是添加了一个 j 而已，这个 j 应该是 java 的用处，所以说 jvisualvm 其实就是 visual vm

#### 基本概述

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-67.jpg]]
使用：

1. 在 jdk 安装目录中找到 jvisualvm.exe，然后双击执行即可
2. 打开 DOS 窗口，输入 jvisualvm 就可以打开该软件

#### 插件安装

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-68.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-69.jpg]]
1、首先在 IDEA 中搜索 VisualVM Launcher 插件并安装:
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-70.jpg]]
2、重启 IDEA，然后配置该插件
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-71.jpg]]

3、使用两种方式来运行程序
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-72.jpg]]

4、运行效果
还是打开 jvisualvm 界面，只是不需要我们手动打开 jvisualvm 而已

#### 连接方式

- 本地连接
	 监控本地 Java 进程的 CPU、类、线程等
- 远程连接
	 1- 确定远程服务器的 ip 地址
	 2- 添加 JMX（通过 JMX 技术具体监控远程服务器哪个 Java 进程）
	 3- 修改 bin/catalina.sh 文件，连接远程的 tomcat
	 4- 在…/conf 中添加 jmxremote.access 和 jmxremote.password 文件
	 5- 将服务器地址改成公网 ip 地址
	 6- 设置阿里云安全策略和防火墙策略
	 7- 启动 tomcat，查看 tomcat 启动日志和端口监听
	 8-JMX 中输入端口号、用户名、密码登录

#### 主要功能

主要功能
1. 生成/读取堆内存快照

一、生成堆内存快照

(1).方式 1：
	![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-73.jpg]]

(2).方式 2：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-74.jpg]]

注意：
		生成堆内存快照如下图：
		![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-75.jpg]]

这些快照存储在内存中，当线程停止的时候快照就会丢失，如果还想利用，可以将快照进行另存为操作，如下图：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-76.jpg]]

 二、装入堆内存快照
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-77.jpg]]

1. 查看 JVM 参数和系统属性
2. 查看运行中的虚拟机进程
3. 生成/读取线程快照
一、生成线程快照

(1) 方式 1：
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-78.jpg]]

(2) 方式 2：

注意：
生成线程快照如下图：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-79.jpg]]

这些快照存储在内存中，当线程停止的时候快照就会丢失，如果还想利用，可以将快照进行另存为操作，如下图：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-80.jpg]]

 二、装入线程快照
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-81.jpg]]

1. 程序资源的实时监控
2. 其他功能
- JMX 代理连接
- 远程环境监控
- CPU 分析和内存分析

### 4. Eclipse MAT

#### 基本概述

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-82.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-83.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-84.jpg]]
注意：如果单独使用，那么解压即可用，不需要安装即可

#### 获取堆 dump 文件

  - dump 文件内存
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-85.jpg]]

  - 两点说明
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-86.jpg]]

  - 获取 dump 文件
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-87.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-88.jpg]]

#### 分析堆 dump 文件

  - histogram
图标：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-89.jpg]]
具体内容：
	![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-90.jpg]]

展示了各个类的实例数目以及这些实例的 Shallow heap 或者 Retained heap 的总和

  - thread overview
  图标：
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-91.jpg]]
  具体信息:
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-92.jpg]]

查看系统中的 Java 线程
查看局部变量的信息
  - 获得对象互相引用的关系
    with outgoing references
    with incoming references
  - 浅堆与深堆
    shallow heap
	![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-93.jpg]]
	对象头代表根据类创建的对象的对象头，还有对象的大小不是可能向 8 字节对齐，而是就向 8 字节对齐

    retained heap
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-94.jpg]]
注意：
当前深堆大小 = 当前对象的浅堆大小 + 对象中所包含对象的深堆大小

补充：对象实际大小
   ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-95.jpg]]

练习
   ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-96.jpg]]
   ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-97.jpg]]

案例分析：StudentTrace

   ```java
   代码：
/**
 * 有一个学生浏览网页的记录程序，它将记录 每个学生访问过的网站地址。
 * 它由三个部分组成：Student、WebPage和StudentTrace三个类
 *
 *  -XX:+HeapDumpBeforeFullGC -XX:HeapDumpPath=c:\code\student.hprof
 * @author shkstart
 * @create 16:11
 */
public class StudentTrace {
    static List<WebPage> webpages = new ArrayList<WebPage>();

    public static void createWebPages() {
        for (int i = 0; i < 100; i++) {
            WebPage wp = new WebPage();
            wp.setUrl("http://www." + Integer.toString(i) + ".com");
            wp.setContent(Integer.toString(i));
            webpages.add(wp);
        }
    }

    public static void main(String[] args) {
        createWebPages();//创建了100个网页
        //创建3个学生对象
        Student st3 = new Student(3, "Tom");
        Student st5 = new Student(5, "Jerry");
        Student st7 = new Student(7, "Lily");

        for (int i = 0; i < webpages.size(); i++) {
            if (i % st3.getId() == 0)
                st3.visit(webpages.get(i));
            if (i % st5.getId() == 0)
                st5.visit(webpages.get(i));
            if (i % st7.getId() == 0)
                st7.visit(webpages.get(i));
        }
        webpages.clear();
        System.gc();
    }
}

class Student {
    private int id;
    private String name;
    private List<WebPage> history = new ArrayList<>();

    public Student(int id, String name) {
        super();
        this.id = id;
        this.name = name;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<WebPage> getHistory() {
        return history;
    }

    public void setHistory(List<WebPage> history) {
        this.history = history;
    }

    public void visit(WebPage wp) {
        if (wp != null) {
            history.add(wp);
        }
    }
}


class WebPage {
    private String url;
    private String content;

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }
}

   ```

   图片：
   ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-99.jpg]]
结论：

elementData 数组的浅堆是 80 个字节，而 elementData 数组中的所有 WebPage 对象的深堆之和是 1208 个字节，所以加在一起就是 elementData 数组的深堆之和，也就是 1288 个字节

解释：

我说“elementData 数组的浅堆是 80 个字节”，其中 15 个对象一共是 60 个字节，对象头 8 个字节，数组对象本身 4 个字节，这些的和是 72 个字节，然后总和要是 8 的倍数，所以“elementData 数组的浅堆是 80 个字节”

我说“WebPage 对象的深堆之和是 1208 个字节”，一共有 15 个对象，其中 0、21、42、63、84、35、70 不仅仅是 7 的倍数，还是 3 或者 5 的倍数，所以这几个数值对应的 i 不能计算在深堆之内，这 15 个对象中大多数的深堆是 152 个字节，但是 i 是 0 和 7 的那两个深堆是 144 个字节，所以 (13*152+144*2)-(6x152+144)=1208 ，所以这也印证了我上面的话，即“WebPage 对象的深堆之和是 1208 个字节”

因此“elementData 数组的浅堆 80 个字节”加上“WebPage 对象的深堆之和 1208 个字节”，正好是 1288 个字节，说明“elementData 数组的浅堆 1288 个字节”

  - 支配树
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-100.jpg]]
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-101.jpg]]
  注意：
跟随我一起来理解如何从“对象引用图 ---》支配树”，首先需要理解支配者（如果要到达对象 B，毕竟经过对象 A，那么对象 A 就是对象 B 的支配者，可以想到支配者大于等于 1），然后需要理解直接支配者（在支配者中距离对象 B 最近的对象 A 就是对象 B 的直接支配者，你要明白直接支配者不一定就是对象 B 的上一级，然后直接支配者只有一个），然后还需要理解支配树是怎么画的，其实支配树中的对象与对象之间的关系就是直接支配关系，也就是上一级是下一级的直接支配者，只要按照这样的方式来作图，肯定能从“对象引用图 ---》支配树”

在 Eclipse MAT 工具中如何查看支配树：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-102.jpg]]

#### 案例 Tomcat 堆溢出分析

##### 说明

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-103.jpg]]

##### 分析过程

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-104.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-105.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-106.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-107.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-108.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-109.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-110.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-111.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-112.jpg]]

#### 支持使用 OQL 语言查询对象信息

SELECT 子句

FROM 子句

WHERE 子句

内置对象与方法

### 补充 1: 再谈内存泄漏

#### 内存泄漏的理解与分析

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-113.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-114.jpg]]

#### Java 中内存泄漏的 8 种情况

##### 1. 静态集合类

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-115.jpg]]

##### 2. 单例模式

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-116.jpg]]

##### 3. 内部类持有外部类

##### 4. 各种连接, 如数据库连接, 网络连接和 IO 连接等

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-118.jpg]]

##### 5. 变量不合理的作用域

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-119.jpg]]

##### 6. 改变哈希值

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-120.jpg]]

```java
 例1：
/**
 * 演示内存泄漏
 *
 * @author shkstart
 * @create 14:43
 */
public class ChangeHashCode {
    public static void main(String[] args) {
        HashSet set = new HashSet();
        Person p1 = new Person(1001, "AA");
        Person p2 = new Person(1002, "BB");

        set.add(p1);
        set.add(p2);

        p1.name = "CC";//导致了内存的泄漏
        set.remove(p1); //删除失败

        System.out.println(set);

        set.add(new Person(1001, "CC"));
        System.out.println(set);

        set.add(new Person(1001, "AA"));
        System.out.println(set);

    }
}

class Person {
    int id;
    String name;

    public Person(int id, String name) {
        this.id = id;
        this.name = name;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Person)) return false;

        Person person = (Person) o;

        if (id != person.id) return false;
        return name != null ? name.equals(person.name) : person.name == null;
    }

    @Override
    public int hashCode() {
        int result = id;
        result = 31 * result + (name != null ? name.hashCode() : 0);
        return result;
    }

    @Override
    public String toString() {
        return "Person{" +
                "id=" + id +
                ", name='" + name + '\'' +
                '}';
    }
}

例2：
/**
 * 演示内存泄漏
 * @author shkstart
 * @create 14:47
 */
public class ChangeHashCode1 {
    public static void main(String[] args) {
        HashSet<Point> hs = new HashSet<Point>();
        Point cc = new Point();
        cc.setX(10);//hashCode = 41
        hs.add(cc);

        cc.setX(20);//hashCode = 51  此行为导致了内存的泄漏

        System.out.println("hs.remove = " + hs.remove(cc));//false
        hs.add(cc);
        System.out.println("hs.size = " + hs.size());//size = 2

        System.out.println(hs);
    }

}

class Point {
    int x;

    public int getX() {
        return x;
    }

    public void setX(int x) {
        this.x = x;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + x;
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null) return false;
        if (getClass() != obj.getClass()) return false;
        Point other = (Point) obj;
        if (x != other.x) return false;
        return true;
    }

    @Override
    public String toString() {
        return "Point{" +
                "x=" + x +
                '}';
    }
}
```

##### 7. 缓存泄漏

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-121.jpg]]

```java
例子：
/**
 * 演示内存泄漏
 *
 * @author shkstart
 * @create 14:53
 */
public class MapTest {
    static Map wMap = new WeakHashMap();
    static Map map = new HashMap();

    public static void main(String[] args) {
        init();
        testWeakHashMap();
        testHashMap();
    }

    public static void init() {
        String ref1 = new String("obejct1");
        String ref2 = new String("obejct2");
        String ref3 = new String("obejct3");
        String ref4 = new String("obejct4");
        wMap.put(ref1, "cacheObject1");
        wMap.put(ref2, "cacheObject2");
        map.put(ref3, "cacheObject3");
        map.put(ref4, "cacheObject4");
        System.out.println("String引用ref1，ref2，ref3，ref4 消失");

    }

    public static void testWeakHashMap() {

        System.out.println("WeakHashMap GC之前");
        for (Object o : wMap.entrySet()) {
            System.out.println(o);
        }
        try {
            System.gc();
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("WeakHashMap GC之后");
        for (Object o : wMap.entrySet()) {
            System.out.println(o);
        }
    }

    public static void testHashMap() {
        System.out.println("HashMap GC之前");
        for (Object o : map.entrySet()) {
            System.out.println(o);
        }
        try {
            System.gc();
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("HashMap GC之后");
        for (Object o : map.entrySet()) {
            System.out.println(o);
        }
    }

}
```

结果：
String 引用 ref1，ref2，ref3，ref4 消失
WeakHashMap GC 之前
obejct2=cacheObject2
obejct1=cacheObject1
WeakHashMap GC 之后
HashMap GC 之前
obejct4=cacheObject4
obejct3=cacheObject3
Disconnected from the target VM, address: '127.0.0.1:51628', transport: 'socket'
HashMap GC 之后
obejct4=cacheObject4
obejct3=cacheObject3

##### 8. 监听器和回调

#### 内存泄漏案例分析

##### 案例代码

```java
代码：
public class Stack {
    private Object[] elements;
    private int size = 0;
    private static final int DEFAULT_INITIAL_CAPACITY = 16;

    public Stack() {
        elements = new Object[DEFAULT_INITIAL_CAPACITY];
    }

    public void push(Object e) { //入栈
        ensureCapacity();
        elements[size++] = e;
    }

    public Object pop() {
        if (size == 0)
            throw new EmptyStackException();
        Object result = elements[--size];
        elements[size] = null;
        return result;
    }

    private void ensureCapacity() {
        if (elements.length == size)
            elements = Arrays.copyOf(elements, 2 * size + 1);
    }
}
```

##### 分析

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-123.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-124.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-125.jpg]]

##### 解决办法

```java
将代码中的pop()方法变成如下方法：
public Object pop() { //出栈
    if (size == 0)
        throw new EmptyStackException();
    return elements[--size];
}
```

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-126.jpg]]

### 补充 2: 支持使用 OQL 语言查询对象信息

#### SELECT 子句

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-127.jpg]]

#### FROM 子句

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-128.jpg]]

#### WHERE 子句

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-129.jpg]]

#### 内置对象与方法

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-130.jpg]]

### 5. JProfiler

#### 基本概述

##### 介绍

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-131.jpg]]

##### 特点

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-132.jpg]]

##### 主要功能

1- 方法调用
  对方法调用的分析可以帮助您了解应用程序正在做什么，并找到提高其性能的方法
2- 内存分配
  通过分析堆上对象、引用链和垃圾收集能帮您修复内存泄露问题，优化内存使用
3- 线程和锁
  JProfiler 提供多种针对线程和锁的分析视图助您发现多线程问题
4- 高级子系统
  许多性能问题都发生在更高的语义级别上。例如，对于 JDBC 调用，您可能希望找出执行最慢的 SQL 语句。JProfiler 支持对这些子系统进行集成分析

#### 安装与配置

- 下载与安装
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-133.jpg]]

- JProfiler 中配置 IDEA
1、IDE Integrations
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-134.jpg]]

2、选择合适的 IDE 版本
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-135.jpg]]

3、开始集成
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-136.jpg]]

4、正式集成
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-137.jpg]]
5、集成成功
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-138.jpg]]

6、点击 OK 即可

- IDEA 集成 JProfiler
一、安装 JProfiler 插件
方式 1：在线安装
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-139.jpg]]
方式 2、离线安装

首先下载插件：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-140.jpg]]
 准备离线安装：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-141.jpg]]

正式离线安装：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-142.jpg]]

注意：无论采用方式 1 还是方式 2 都需要重启 IDEA

二、将 JProfiler 配置到 IDEA 中
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-143.jpg]]

#### 具体使用

常见操作：
1、Starter Center
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-144.jpg]]

如果程序已经保存了 Quick Attach，那么即使下次程序运行的时候没有启动 JProfiler，而我们启动 JProfiler，然后找到该 Quick Attach 中的对应位置，点击就可以运行了
2、垃圾回收
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-145.jpg]]

3、 标记
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-146.jpg]]

4、手动刷新
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-147.jpg]]

5、Live memory 中的 Recorded Objects 可以查看对象信息，根据 View 中的 Change Liveness Mode 来更改查看的对象类型
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-148.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-149.jpg]]

如果通过 Telemetries 中的 Memory 看到垃圾回收之后内存占用还是越来越多，那就需要注意内存泄露问题了，这个时候我们可以查看 Live memory 中的 Recorded Objects 中的对象信息，可以先查看 Live Objects 中的，也就是存活的对象，然后在查看 Garbage Collected Objects，如果某对象只在 Live Objects 中出现，但是没有在 Garbage Collected Objects 中出现，那么说明该对象就没有进行垃圾回收，即该对象有可能造成内存泄露

6、保存堆快照 dump 文件
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-150.jpg]]

- 数据采集方式
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-151.jpg]]
推荐使用 Sampling 方式，足够用来分析 OOM 问题了

  instrumentation 重构模式

  Sampling 抽样模式

- 遥感监测 Telemetries
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-152.jpg]]
其中 Telemetries 就是遥感监测的意思
- 内存视图 Live Memory
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-153.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-154.jpg]]
分析：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-155.jpg]]

注意：
1. All Objects 后面的 Size 大小是浅堆大小
2. Record Objects 在判断内存泄露的时候使用，可以通过观察 Telemetries 中的 Memory，如果里面出现垃圾回收之后的内存占用逐步提高，这就有可能出现内存泄露问题，所以可以使用 Record Objects 查看，但是该分析默认不开启，毕竟占用 CPU 性能太多

- 堆遍历 heap walker

如果通过内存视图 Live Memory 已经分析出哪个类的对象不能进行垃圾回收，并且有可能导致内存溢出，如果想进一步分析，我们可以在该对象上点击右键，选择 Show Selection In Heap Walker，如下图：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-156.jpg]]
之后进行溯源，操作如下：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-157.jpg]]
查看结果，并根据结果去看对应的图表：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-158.jpg]]
以下是图表的展示情况：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-159.jpg]]

- cpu 视图 cpu views
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-1.jpeg]]

具体使用：
1、记录方法统计信息
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-160.jpg]]

2、方法统计
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-161.jpg]]

3、具体分析
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-162.jpg]]

- 线程视图 threads
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-163.jpg]]

具体使用：
1、查看线程运行情况
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-164.jpg]]

2、新建线程 dump 文件
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-165.jpg]]

- 监视器&锁 Monitors&locks
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-166.jpg]]

#### 案例分析

- 案例 1

```java
/**
 * 功能演示测试
 * @author shkstart
 * @create 12:19
 */
public class JProfilerTest {
    public static void main(String[] args) {
        while (true){
            ArrayList list = new ArrayList();
            for (int i = 0; i < 500; i++) {
                Data data = new Data();
                list.add(data);
            }
            try {
                TimeUnit.MILLISECONDS.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
class Data{
    private int size = 10;
    private byte[] buffer = new byte[1024 * 1024];//1mb
    private String info = "hello,atguigu";
}
```

- 案例 2
例子：

```java
public class MemoryLeak {

    public static void main(String[] args) {
        while (true) {
            ArrayList beanList = new ArrayList();
            for (int i = 0; i < 500; i++) {
                Bean data = new Bean();
                data.list.add(new byte[1024 * 10]);//10kb
                beanList.add(data);
            }
            try {
                TimeUnit.MILLISECONDS.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

}

class Bean {
    int size = 10;
    String info = "hello,atguigu";
    static ArrayList list = new ArrayList();
}
```

解释：
我们通过 JProfiler 来看一下，如下：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-167.jpg]]

你可以看到内存一个劲的往上涨，但是就是没有下降的趋势，说明这肯定有问题，过不了多久就会出现 OOM，我们来到 Live memory 中，先标记看一下到底是哪些对象在进行内存增长，等一小下看看会不会触发垃圾回收，如果不触发的话，我们自己来触发垃圾回收，之后观察哪些对象没有被回收掉，如下：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-168.jpg]]

我上面点击了 Mark Current，发现有些对象在持续增长，然后点击了一下 Run GC，结果如下所示：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-169.jpg]]

 可以看出 byte[] 没有被回收，说明它是有问题的，我们点击 Show Selection In Heap Walker，如下：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-170.jpg]]

然后看一下该对象被谁引用，如下：
 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-171.jpg]]

结果如下：
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-172.jpg]]

可以看出 byte[] 来自于 Bean 类是的 list 中，并且这个 list 是 ArrayList 类型的静态集合，所以找到了：static ArrayList list = new ArrayList();
发现 list 是静态的，这不妥，因为我们的目的是 while 结束之后 Bean 对象被回收，并且 Bena 对象中的所有字段都被回收，但是 list 是静态的，那就是类的，众所周知，类变量随类而生，随类而灭，因此每次我们往 list 中添加值，都是往同一个 list 中添加值，这会造成 list 不断增大，并且不能回收，所以最终会导致 OOM

### 6. Arthas

#### 基本概述

##### 背景

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-173.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-174.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-175.jpg]]

##### 概述

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-176.jpg]]

##### 基于哪些工具开发而来

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-177.jpg]]

##### 官方使用文档

  https://arthas.aliyun.com/doc/quick-start.html

#### 安装与使用

- 安装
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-178.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-179.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-180.jpg]]

- 工程目录
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-181.jpg]]

- 启动
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-182.jpg]]

- 查看进程
	jps
- 查看日志
	  cat ~/logs/arthas/arthas.log

- 查看帮助
	  java -jar arthas-boot.jar -h

- web console
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-183.jpg]]

- 退出
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-184.jpg]]

#### 相关诊断指令

##### 基础指令

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-185.jpg]]

##### jvm 相关

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-186.jpg]]
命令列表：(https://arthas.aliyun.com/doc/commands.html#id1)

  - dashboard
  链接：(https://arthas.aliyun.com/doc/dashboard.html)
  作用：当前系统的实时数据面板
  - thread
  链接：https://arthas.aliyun.com/doc/thread.html
  作用：查看当前线程信息，查看线程的堆栈

  - jvm
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-187.jpg]]

  - 其他
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-188.jpg]]


##### class/classloader 相关

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-189.jpg]]
  - sc
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-190.jpg]]

  - sm
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-191.jpg]]

  - jad
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-192.jpg]]
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-193.jpg]]

  - mc、redefine
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-194.jpg]]

  - classloader
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-195.jpg]]


##### monitor/watch/trace 相关

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-196.jpg]]

  - monitor
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-197.jpg]]

  - watch
  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-198.jpg]]

  - trace

  - stack

  - tt


##### 其他

  ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-201.jpg]]

  - profiler/火焰图
	profiler：
	https://arthas.aliyun.com/doc/profiler.html

  - options
	options：
	https://arthas.aliyun.com/doc/options.html

### 7. JMC(Java Mission COntrol)

#### 历史

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-202.jpg]]

#### 启动

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-203.jpg]]

#### 概述

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-204.jpg]]

#### 功能: 实时监控 JVM 运行时的状态

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-205.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-206.jpg]]

#### Java Flight Recorder

  事件类型
  启动方式
    方式 1：使用 -XX:StartFlightRecording=参数

	![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-207.jpg]]
    方式2：使用jcmd的JFR.* 子命令
	
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-208.jpg]]
    方式 3：JMC 的 JFR 插件
	![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-209.jpg]]
	 具体使用：

1、启动飞行记录仪
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-210.jpg]]

2、启动飞行记录
	 ![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-211.jpg]]

3、 正式启动
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-212.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-213.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-214.jpg]]

Java Flight Recorder 取样分析
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-215.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-216.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-217.jpg]]

代码

```java
/**
 * -Xms600m -Xmx600m -XX:SurvivorRatio=8
 * @author shkstart  shkstart@126.com
 * @create 2020  21:12
 */
public class OOMTest {
    public static void main(String[] args) {
        ArrayList<Picture> list = new ArrayList<>();
        while(true){
            try {
                Thread.sleep(5);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            list.add(new Picture(new Random().nextInt(100 * 50)));
        }
    }
}

class Picture{
    private byte[] pixels;

    public Picture(int length) {
        this.pixels = new byte[length];
    }

    public byte[] getPixels() {
        return pixels;
    }

    public void setPixels(byte[] pixels) {
        this.pixels = pixels;
    }
}
```

结果
1、一般信息
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-218.jpg]]

2、内存
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-219.jpg]]

3、代码
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-220.jpg]]

4、线程
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-221.jpg]]

5、I/O
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-222.jpg]]

6、系统
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-223.jpg]]

7、事件
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-224.jpg]]

### 8. 其它工具

#### Flame Graphs(火焰图)

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-2.jpeg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-3.jpeg]]

#### Tprofiler

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-225.jpg]]
![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-226.jpg]]

#### Btrace

![[附件/image/下篇02和03_JVM监控及诊断工具(命令行和图形界面)-227.jpg]]

#### YourKit

#### JProbe

#### Spring Insight

————————————————
