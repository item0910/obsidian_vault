---
date: 2024-09-07
mtime: 2024-09-25
---

# 四、JVM 运行时参数

**JVM 虚拟机**; **Java**

## 01-JVM 参数选项

### 类型一：标准参数选项

#### 特点

  比较稳定，后续版本基本不会变化
  以 - 开头

#### 各种选项

```java
-d32          使用 32 位数据模型 (如果可用)
-d64          使用 64 位数据模型 (如果可用)
-server       选择 "server" VM
               默认 VM 是 server.
 
-cp <目录和 zip/jar 文件的类搜索路径>
-classpath <目录和 zip/jar 文件的类搜索路径>
    用 ; 分隔的目录, JAR 档案
    和 ZIP 档案列表, 用于搜索类文件。
-D<名称>=<值>
    设置系统属性
-verbose:[class|gc|jni]
    启用详细输出
-version      
	输出产品版本并退出
-version:<值>
    警告: 此功能已过时, 将在未来发行版中删除。
    需要指定的版本才能运行
-showversion  
	输出产品版本并继续
-jre-restrict-search | -no-jre-restrict-search
    警告: 此功能已过时, 将在未来发行版中删除。
    在版本搜索中包括/排除用户专用 JRE
-? -help      
	输出此帮助消息
-X            
	输出非标准选项的帮助
-ea[:<packagename>...|:<classname>]
-enableassertions[:<packagename>...|:<classname>]
    按指定的粒度启用断言
-da[:<packagename>...|:<classname>]
-disableassertions[:<packagename>...|:<classname>]
    禁用具有指定粒度的断言
-esa | -enablesystemassertions
    启用系统断言
-dsa | -disablesystemassertions
    禁用系统断言
-agentlib:<libname>[=<选项>]
    加载本机代理库 <libname>, 例如 -agentlib:hprof
    另请参阅 -agentlib:jdwp=help 和 -agentlib:hprof=help
-agentpath:<pathname>[=<选项>]
    按完整路径名加载本机代理库
-javaagent:<jarpath>[=<选项>]
    加载 Java 编程语言代理, 请参阅 java.lang.instrument
-splash:<imagepath>
    使用指定的图像显示启动屏幕
```

直接在 DOS 窗口中运行 java 或者 java -help 可以看到所有的标准选项

#### 补充内容：

- -server 与 -client
![[附件/image/下篇04_JVM运行时参数.jpg]]
对于以上第 2 点，我们可以打开 DOS 窗口，输入 java -version 就可以看到 64 位机器上用的 server 模式，如下所示：
![[附件/image/下篇04_JVM运行时参数-1.jpg]]

### 类型二：-X 参数选项

#### 特点

- 非标准化参数
- 功能还是比较稳定的。但官方说后续版本可能会变更
        以 -X 开头

#### 各种选项

```java
-Xmixed        混合模式执行 (默认)
-Xint             仅解释模式执行
-Xcomp        仅采用即时编译器模式
-Xbootclasspath:<用 ; 分隔的目录和 zip/jar 文件>
                   设置搜索路径以引导类和资源
-Xbootclasspath/a:<用 ; 分隔的目录和 zip/jar 文件>
                   附加在引导类路径末尾
-Xbootclasspath/p:<用 ; 分隔的目录和 zip/jar 文件>
                   置于引导类路径之前
-Xdiag            显示附加诊断消息
-Xnoclassgc       禁用类垃圾收集
-Xincgc           启用增量垃圾收集
-Xloggc:<file>    将 GC 状态记录在文件中 (带时间戳)
-Xbatch           禁用后台编译
-Xms<size>        设置初始 Java 堆大小 重要
-Xmx<size>        设置最大 Java 堆大小 重要
-Xss<size>        设置 Java 线程堆栈大小 一般不更改
-Xprof            输出 cpu 配置文件数据
-Xfuture          启用最严格的检查, 预期将来的默认值
-Xrs              减少 Java/VM 对操作系统信号的使用 (请参阅文档)
-Xcheck:jni       对 JNI 函数执行其他检查
-Xshare:off       不尝试使用共享类数据
-Xshare:auto      在可能的情况下使用共享类数据 (默认)
-Xshare:on        要求使用共享类数据, 否则将失败。
-XshowSettings    显示所有设置并继续
-XshowSettings:all
                   显示所有设置并继续
-XshowSettings:vm 显示所有与 vm 相关的设置并继续
-XshowSettings:properties
                   显示所有属性设置并继续
-XshowSettings:locale
                   显示所有与区域设置相关的设置并继续
 
-X 选项是非标准选项，如有更改，恕不另行通知
```

直接在 DOS 窗口中运行 java -X 命令可以看到所有的 X 选项

#### JVM 的 JIT 编译模式相关的选项

- -Xint
          只使用解释器：所有字节码都被解释执行，这个模式的速度是很慢的
- -Xcomp
          只使用编译器：所有字节码第一次使用就被编译成本地代码，然后在执行
- -Xmixed
          混合模式：这是默认模式，刚开始的时候使用解释器慢慢解释执行，后来让 JIT 即时编译器根据程序运行的情况，有选择地将某些热点代码提前编译并缓存在本地，在执行的时候效率就非常高了

#### 特别地

-Xmx -Xms -Xss 属于 XX 参数

单位：k/K、m/M、g/G
设置：-Xmx、-Xms 最好设置成一样的值，避免扩容带来的损耗

- -Xms(size) 设置初始 Java 堆大小，等价于 -XX:InitialHeapSize

查看该参数值的时候，应该使用 InitialHeapSize，例如 jinfo flag InitialHeapSize 进程 id
等价证明：
![[附件/image/下篇04_JVM运行时参数-2.jpg]]
![[附件/image/下篇04_JVM运行时参数-3.jpg]]

- -Xmx(size) 设置最大 Java 堆大小，等价于 -XX:MaxHeapSize

查看该参数值的时候，应该使用 MaxHeapSize，例如 jinfo flag InitialHeapSize 进程 id
等价证明：
![[附件/image/下篇04_JVM运行时参数.jpeg]]

- -Xss(size) 设置 Java 线程堆栈大小，等价于 -XX:ThreadStackSize

查看该参数值的时候，应该使用 ThreadStackSize，例如 jinfo flag InitialHeapSize 进程 id

### 类型三：-XX 参数选项

#### 特点

- 非标准化参数
- 使用的最多的参数类型
- 这类选项属于实验性，不稳定
- 以 -XX 开头

#### 作用

用于开发和调试 JVM

#### 分类

- Boolean 类型格式
          -XX:+(option) 表示启用 option 属性
          -XX:-(option) 表示禁用 option 属性
          举例
		  ![[附件/image/下篇04_JVM运行时参数-4.jpg]]
          说明：因为有的指令默认是开启的，所以可以使用 - 关闭
        非 Boolean 类型格式（key-value 类型）
          子类型 1：数值型格式 -XX:(option)=(number)
		  ![[附件/image/下篇04_JVM运行时参数-5.jpg]]
          子类型 2：非数值型格式 -XX:(name)=(string)
		  ![[附件/image/下篇04_JVM运行时参数-6.jpg]]


#### 特别地

- -XX:+PrintFlagsFinal
输出所有参数的名称和默认值

默认不包括 Diagnostic 和 Experimental 的参数

可以配合 -XX:+UnlockDiagnosticVMOptions 和 -XX:UnlockExperimentalVMOptions 使用

## 02- 添加 JVM 参数选项

### Eclipse

1、在空白处单击右键，选择 Run As，在选择 Run Configurations……
![[附件/image/下篇04_JVM运行时参数-7.jpg]]

2、设置虚拟机参数
![[附件/image/下篇04_JVM运行时参数-8.jpg]]

### IDEA

1、Edit Configurations…
![[附件/image/下篇04_JVM运行时参数-9.jpg]]

2、设置虚拟机参数
![[附件/image/下篇04_JVM运行时参数-10.jpg]]

### 运行 jar 包

java -Xms50m -Xmx50m -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -jar demo.jar

### 通过 Tomcat 运行 war 包

Linux 系统下可以在 tomcat/bin/catalina.sh 中添加类似如下配置： JAVA_OPTS="-Xms512M -Xmx1024M"

Windows 系统下载 catalina.bat 中添加类似如下配置： set "JAVA_OPTS=-Xms512M -Xmx1024M"

### 程序运行过程中

![[附件/image/下篇04_JVM运行时参数-11.jpg]]

使用 jinfo -flag (name)>=(value) (pid) 设置非 Boolean 类型参数

使用 jinfo -flag [+|-] (name) (pid) 设置 Boolean 类型参数

## 03- 常用的 JVM 参数选项

### 打印设置的 XX 选项及值

- -XX:+PrintCommandLineFlags
        可以让程序运行前打印出用户手动设置或者 JVM 自动设置的 XX 选项

- -XX:+PrintFlagsInitial
        表示打印出所有 XX 选项的默认值

- -XX:+PrintFlagsFinal
        表示打印出 XX 选项在运行程序时生效的值
		如果值的前面加上了:=，说明该值不是初始值，该值可能被 jvm 自动改变了，也可能被我们设置的参数改变了，如下所示:

![[附件/image/下篇04_JVM运行时参数-12.jpg]]

- -XX:+PrintVMOptions
        打印 JVM 的参数

### 堆、栈、方法区等内存大小设置

#### 栈

- -Xss128k
          等价于 -XX:ThreadStackSize，设置每个线程的栈大小为 128k


#### 堆内存

```java
-Xms3550m
    等价于-XX:InitialHeapSize，设置JVM初始堆内存为3500M
-Xmx3550m
    等价于-XX:MaxHeapSize，设置JVM最大堆内存为3500M
-Xmn2g
    设置年轻代大小为2G，即等价于-XX:NewSize=2g -XX:MaxNewSize=2g，也就是设置年轻代初始值和年轻代最大值都是2G  官方推荐配置为整个堆大小的3/8
-XX:NewSize=1024m
    设置年轻代初始值为1024M
-XX:MaxNewSize=1024m
    设置年轻代最大值为1024M
-XX:SurvivorRatio=8
    设置年轻代中Eden区与一个Survivor区的比值，默认为8
```

注意: 只有显示使用 Eden 区和 Survivor 区的比例，才会让比例生效，否则比例都会自动设置，至于其中的原因，请看下面的 -XX:+UseAdaptiveSizePolicy 中的解释，最后推荐使用默认打开的 -XX:+UseAdaptiveSizePolicy 设置，并且不显示设置 -XX:SurvivorRatio

```java
-XX:+UseAdaptiveSizePolicy
    自动选择各区大小比例，默认开启
```

1、分析
默认开启，将会导致 Eden 区和 Survivor 区的比例自动分配，因此也会引起我们默认值 -XX:SurvivorRatio=8 失效，所以真实比例可能不是 8，比如可能是 6 等

2、如何设置 Eden 区和 Survivor 区的比例
-XX:SurvivorRatio=8
显示使用 Eden 区和 Survivor 区的比例，那就使用我自己的

没有显示使用 Eden 区和 Survivor 区的比例，无论打开或者关闭 -XX:+UseAdaptiveSizePolicy，都会自动设置 Eden 区和 Survivor 区的比例

结论：
只有显式使用 Eden 区和 Survivor 区的比例，才会让比例生效，否则比例都会自动设置，最后推荐使用默认打开的 -XX:+UseAdaptiveSizePolicy 设置，并且不显式设置 -XX:SurvivorRatio

```java
-XX:NewRatio=2
    设置老年代与年轻代（包括1个Eden区和2个Survivor区）的比值，默认为2
```

根据实际情况进行设置，主要根据对象生命周期来进行分配，如果对象生命周期很长，那么让老年代大一点，否则让新生代大一点

```java
-XX:PretenureSizeThreadshold=1024
    设置让大于此阈值的对象直接分配在老年代，单位为字节
    只对Serial、ParNew收集器有效
```

根据实际情况进行设置，主要根据对象生命周期来进行分配，如果对象生命周期很长，那么让老年代大一点，否则让新生代大一点

```java
-XX:MaxTenuringThreshold=15
    默认值为15
    新生代每次MinorGC后，还存活的对象年龄+1，当对象的年龄大于设置的这个值时就进入老年代
```

使用比较少，一般用默认值

```java
-XX:+PrintTenuringDistribution
    让JVM在每次MinorGC后打印出当前使用的Survivor中对象的年龄分布
-XX:TargetSurvivorRatio
    表示MinorGC结束后Survivor区域中占用空间的期望比例
```

#### 方法区

- 永久代

```java
java7之前
-XX:PermSize=256m
    设置永久代初始值为256M
-XX:MaxPermSize=256m
    设置永久代最大值为256M
```

- 元空间

```java
java8
-XX:MetaspaceSize
	初始空间大小
-XX:MaxMetaspaceSize
	最大空间，默认没有限制
-XX:+UseCompressedOops
	使用压缩对象指针
-XX:+UseCompressedClassPointers
	使用压缩类指针
-XX:CompressedClassSpaceSize
	设置Klass Metaspace的大小，默认1G
```

#### 直接内存

```java
-XX:MaxDirectMemorySize
    指定DirectMemory容量，若未指定，则默认与Java堆最大值一样
```

### OutOfMemory 相关的选项

-XX:+HeapDumpOnOutMemoryError(在出现 OOM 的时候
生成 dump 文件) 和 -XX:+HeapDumpBeforeFullGC(在出现 Full GC 的时候生成 dump 文件) 只能设置 1 个
，如果不设置 `-XX:HeapDumpPath=<path>`，那么将会在当前目录下生成 dump 文件，如果设置的话，将会在指定位置生成 dump 文件

```java
-XX:+HeapDumpOnOutMemoryError
    表示在内存出现OOM的时候，生成Heap转储文件，以便后续分析，-XX:+HeapDumpBeforeFullGC和-XX:+HeapDumpOnOutMemoryError只能设置1个
-XX:+HeapDumpBeforeFullGC
    表示在出现FullGC之前，生成Heap转储文件，以便后续分析，-XX:+HeapDumpBeforeFullGC和-XX:+HeapDumpOnOutMemoryError只能设置1个，请注意FullGC可能出现多次，那么dump文件也会生成多个
-XX:HeapDumpPath=(path)
	指定heap转存文件的存储路径，如果不指定，就会将dump文件放在当前目录中
```

```java
-XX:OnOutOfMemoryError
    指定一个可行性程序或者脚本的路径，当发生OOM的时候，去执行这个脚本
```

![[附件/image/下篇04_JVM运行时参数-13.jpg]]

### 垃圾收集器相关选项

![[附件/image/下篇04_JVM运行时参数-14.jpg]]
![[附件/image/下篇04_JVM运行时参数-15.jpg]]

#### 查看默认的垃圾回收器

![[附件/image/下篇04_JVM运行时参数-16.jpg]]

以上两种方式都可以查看默认使用的垃圾回收器，第一种方式更加准备，但是需要程序的支持；第二种方式需要去尝试，如果使用了，返回的值中有 + 号，否则就是 - 号

#### Serial 回收器

![[附件/image/下篇04_JVM运行时参数-17.jpg]]

#### Parnew 回收器

![[附件/image/下篇04_JVM运行时参数-18.jpg]]

根据下图可知，该回收器最终将会没有搭档，那就相当于被遗弃了

![[附件/image/下篇04_JVM运行时参数-1.jpeg]]

#### Parallel 回收器

- -XX:+UseParalle1GC 手动指定年轻代使用 Paralle1 并行收集器执行内存回收任务。
- -XX:+UseParalleloldG 手动指定老年代都是使用并行回收收集器。
	分别适用于新生代和老年代。默认 jdk8 是开启的。
	上面两个参数，默认开启一个，另一个也会被开启。( 互相激活)
- -XX:ParallelGCThreads 设置年轻代并行收集器的线程数。一般地，最好与 CPU 数量相等，以避免过多的线程数影响垃圾收集性能。
	在默认情况下，当 CPU 数量小于 8 个， ParallelGCThreads 的值等于 CPU 数量
	当 CPU 数量大于 8 个，ParallelGCThreads 的值等于 3+[5 * CPU Count]/8]
- -XX:MaxGCPauseMillis 设置垃圾收集器最大停顿时间 (即 STW 的时间)。单位是毫秒
	为了尽可能地把停顿时间控制在 MaxGCPauseMills 以内，收集器在工作时会调整 Java 堆大小或者其他一些参数。
	对于用户来讲，停顿时间越短体验越好。但是在服务器端，我们注重高并发，整体的吞吐量。所以服务器端适合 Parallel，进行控制。
		该参数使用需谨慎。
- -xx:GCTimeRatio 垃圾收集时间占总时间的比例 (= 1/(N + 1))。用于衡量吞吐量的大小。
	取值范围 (@.1@e)。默认值 99，也就是垃圾回收时间不超过 1%。
	与前一个 -XX:MaxGCPauseMillis 参数有一定矛盾性。暂停时间越长，Radio 参数就容易超过设定的比例。
- -XX:+UseAdaptiveSizePolicy 设置 Parallel scavenge 收集器具有自适应调节策略
	在这种模式下，年轻代的大小、Eden 和 Survivor 的比例、晋升老年代的对象年龄等参数会被自动调整，已达到在堆大小、吞吐量和停顿时间之间的平衡点。
	在手动调优比较困难的场合，可以直接使用这种自适应的方式，仅指定虚拟机的最大堆、目标的吞吐量 (GCTimeRatio) 和停顿时间 (MaxGCPauseMills)，让虚拟机自己完成调优工作。

注意：
1. Parallel 回收器主打吞吐量，而 CMS 和 G1 主打低延迟，如果主打吞吐量，那么就不应该限制最大停顿时间，所以 -XX:MaxGCPauseMills 不应该设置

2. -XX:MaxGCPauseMills 中的调整堆大小通过默认开启的 -XX:+UseAdaptiveSizePolicy 来实现

3. -XX:GCTimeRatio 用来衡量吞吐量，并且和 -XX:MaxGCPauseMills 矛盾，因此不会同时使用

#### CMS 回收器

- -XX:+UseConcMarkSweepGC 手动指定使用 CMS 收集器执行内存回收任务。
	- 开启该参数后会自动将 -Xx:+UseParNewGC 打开。即: ParNew(Young 区用)+CMS(0ld 区用)+Serial old 的组合。
- -XX:CMSInitiatingoccupanyFraction 设置堆内存使用率的阿值，一旦达到该网值，便开始进行回收。
	JDK5 及以前版本的默认值为 68,即当老年代的空间使用率达到 68% 时，会执行一次 CMS 回收 JDK6 及以上版本默认值为 92%
	如果内存增长缓慢，则可以设置一个稍大的值，大的阙值可以有效降低 CMS 的触发频率，减少老年代回收的次数可以较为明显地改善应用程序性能。反之，如果应用程序内存使用率增长很快，则应该降低这个阙值，以避免频繁触发老年代串行收集器。因此通过该选项使便可以有效降低 Fu11 GC 的执行次数
- -XX:+UseCMSCompactAtFullCollection 用于指定在执行完 Fu11 GC 后对内存空间进行压缩整理，以此避免内存碎片的产生。不过由于内存压缩整理过程无法并发执行，所带来的问题就是停顿时间变得更长了。
- -XX:CMSFul1GCsBeforeCompaction 设置在执行多少次 Ful] GC 后对内存空间进行压缩整理。
- -XX:ParallelCMSThreads 设置 CMS 的线程数量。
	CMS 默认启动的线程数是 (ParallelGCThreads3)/4，ParallelGCThreads 是年轻代并行收集器的线程数。当 CPU 资源比较紧张时，受到 CMS 收集器线程的影响，应用程序的性能在垃圾回收阶段可能会非常糟糕。

-XX:ParallelCMSThreads 和 ParallelGCThreads 有关系，ParallelGCThreads 在上面 Parnew 回收器中有提到

- 补充参数
	另外，CMS 收集器还有如下常用参数:
	- -xx:ConcGCThreads: 设置并发垃圾收集的线程数，默认该值是基于 ParallelGCThreads 计算出来的;
	- -XX:+UseCMSInitiatingOccupancyonly: 是否动态可调，用这个参数可以使 CMS 一直按 CMSInitiatingOccupancyFraction 设定的值启动
	- -Xx:+CMSScavengeBeforeRemark: 强 hotspot 虚拟机在 ms remark 阶段之前做一次 minorgc，用于提高 remark 阶段的速 L:
	- -XX:+CMSClassUnloadingEnable: 如果有的话，启用回收 Perm 区 (JDK8 之前)
	- -XX:+CMSParallelInitialEnabled: 用于开启 CMS initial-mark 阶段采用多线程的方式进行标记，用于提高标记速度，在 Java8 开始已经默认开启;
	- -XX:+CMSParallelRemarkEnabled: 用户开启 CMS remark 阶段采用多线程的方式进行重新标记默认开启;
	- -XX:+ExplicitGCInvokesConcurrent
	- -XX:+ExplicitGCInvokesConcurrentAndUnloadsClasses 这两个参数用户指定 hotspot 虚拟在执行 System.gc() 时使用 CMS 周期;
	- -XX:+CMSPrecleaningEnabled: 指定 CMS 是否需要进行 Pre cleaning 这个阶段

- 特别说明
![[附件/image/下篇04_JVM运行时参数-23.jpg]]

#### G1 回收器

![[附件/image/下篇04_JVM运行时参数-24.jpg]]

如果使用 G1 垃圾收集器，不建议设置 -Xmn 和 -XX:NewRatio，毕竟可能影响 G1 的自动调节

Mixed GC 调优参数

![[附件/image/下篇04_JVM运行时参数-25.jpg]]

#### 怎么选择垃圾收集器

![[附件/image/下篇04_JVM运行时参数-26.jpg]]

### GC 日志相关选项

#### 常用参数

```java
-verbose:gc
  输出日志信息，默认输出的标准输出
  可以独立使用

-XX:+PrintGC
  等同于-verbose:gc 表示打开简化的日志
  可以独立使用
```

![[附件/image/下篇04_JVM运行时参数-2.jpeg]]

```java
-XX:+PrintGCDetails
  在发生垃圾回收时打印内存回收详细的日志， 并在进程退出时输出当前内存各区域的分配情况
  可以独立使用
```

![[附件/image/下篇04_JVM运行时参数-3.jpeg]]

```java
-XX:+PrintGCTimeStamps
  程序启动到GC发生的时间秒数
  不可以独立使用，需要配合-XX:+PrintGCDetails使用
```

![[附件/image/下篇04_JVM运行时参数-27.jpg]]

```java
-XX:+PrintGCDateStamps
  输出GC发生时的时间戳（以日期的形式，例如：2013-05-04T21:53:59.234+0800）
  不可以独立使用，可以配合-XX:+PrintGCDetails使用
```

![[附件/image/下篇04_JVM运行时参数-28.jpg]]

```java
-XX:+PrintHeapAtGC
  每一次GC前和GC后，都打印堆信息
  可以独立使用
```

![[附件/image/下篇04_JVM运行时参数-29.jpg]]

```java
-XIoggc:<file>
  把GC日志写入到一个文件中去，而不是打印到标准输出中
```

![[附件/image/下篇04_JVM运行时参数-30.jpg]]

#### 其他参数

```java
-XX:TraceClassLoading
  监控类的加载
-XX:PrintGCApplicationStoppedTime
  打印GC时线程的停顿时间
-XX:+PrintGCApplicationConcurrentTime
  垃圾收集之前打印出应用未中断的执行时间
-XX:+PrintReferenceGC
  记录回收了多少种不同引用类型的引用
-XX:+PrintTenuringDistribution
  让JVM在每次MinorGC后打印出当前使用的Survivor中对象的年龄分布
-XX:+UseGCLogFileRotation
  启用GC日志文件的自动转储
-XX:NumberOfGCLogFiles=1
  GC日志文件的循环数目
-XX:GCLogFileSize=1M
  控制GC日志文件的大小
```

### 其他参数

```java
-XX:+DisableExplicitGC
  禁用hotspot执行System.gc()，默认禁用
-XX:ReservedCodeCacheSize=<n>[g|m|k]、-XX:InitialCodeCacheSize=<n>[g|m|k]
  指定代码缓存的大小
-XX:+UseCodeCacheFlushing
  使用该参数让jvm放弃一些被编译的代码， 避免代码缓存被占满时JVM切换到interpreted-only的情况
-XX:+DoEscapeAnalysis
  开启逃逸分析
-XX:+UseBiasedLocking
  开启偏向锁
-XX:+UseLargePages
  开启使用大页面
-XX:+PrintTLAB
  打印TLAB的使用情况
-XX:TLABSize
  设置TLAB大小
```

## 04- 通过 Java 代码获取 JVM 参数

![[附件/image/下篇04_JVM运行时参数-31.jpg]]

```java
/**
 *
 * 监控我们的应用服务器的堆内存使用情况，设置一些阈值进行报警等处理
 *
 * @author shkstart
 * @create 15:23
 */
public class MemoryMonitor {
    public static void main(String[] args) {
        MemoryMXBean memorymbean = ManagementFactory.getMemoryMXBean();
        MemoryUsage usage = memorymbean.getHeapMemoryUsage();
        System.out.println("INIT HEAP: " + usage.getInit() / 1024 / 1024 + "m");
        System.out.println("MAX HEAP: " + usage.getMax() / 1024 / 1024 + "m");
        System.out.println("USE HEAP: " + usage.getUsed() / 1024 / 1024 + "m");
        System.out.println("\nFull Information:");
        System.out.println("Heap Memory Usage: " + memorymbean.getHeapMemoryUsage());
        System.out.println("Non-Heap Memory Usage: " + memorymbean.getNonHeapMemoryUsage());

        System.out.println("=======================通过java来获取相关系统状态============================ ");
        System.out.println("当前堆内存大小totalMemory " + (int) Runtime.getRuntime().totalMemory() / 1024 / 1024 + "m");// 当前堆内存大小
        System.out.println("空闲堆内存大小freeMemory " + (int) Runtime.getRuntime().freeMemory() / 1024 / 1024 + "m");// 空闲堆内存大小
        System.out.println("最大可用总堆内存maxMemory " + Runtime.getRuntime().maxMemory() / 1024 / 1024 + "m");// 最大可用总堆内存大小

    }
} 
```

![[附件/image/下篇04_JVM运行时参数-32.jpg]]
