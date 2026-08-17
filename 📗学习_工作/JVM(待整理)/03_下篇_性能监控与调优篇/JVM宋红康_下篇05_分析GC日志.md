---
date: 2024-09-07
mtime: 2024-09-25
---

# 五、分析 GC 日志

**JVM 虚拟机**; **Java**

## 01-GC 日志参数

```java
-verbose:gc

	输出gc日志信息，默认输出到标准输出

-XX:+PrintGC

	输出GC日志。类似：-verbose:gc

-XX:+PrintGCDetails

	在发生垃圾回收时打印内存回收相处的日志， 并在进程退出时输出当前内存各区域分配情况

-XX:+PrintGCTimeStamps

	输出GC发生时的时间戳

-XX:+PrintGCDateStamps

	输出GC发生时的时间戳（以日期的形式，例如：2013-05-04T21:53:59.234+0800）

-XX:+PrintHeapAtGC

	每一次GC前和GC后，都打印堆信息

-Xloggc:<file>

	表示把GC日志写入到一个文件中去，而不是打印到标准输出中
```

## 02-GC 日志格式

### 复习：GC 分类

![[附件/image/下篇05_分析GC日志.jpg]]

- 新生代收集：当 Eden 区满的时候就会进行新生代收集，所以新生代收集和 S0 区域和 S1 区域无关

- 老年代收集和新生代收集的关系：进行老年代收集之前会先进行一次年轻代的垃圾收集，原因如下：一个比较大的对象无法放入新生代，那它自然会往老年代去放，如果老年代也放不下，那会先进行一次新生代的垃圾收集，之后尝试往新生代放，如果还是放不下，才会进行老年代的垃圾收集，之后在往老年代去放，这是一个过程，我来说明一下为什么需要往老年代放，但是放不下，而进行新生代垃圾收集的原因，这是因为新生代垃圾收集比老年代垃圾收集更加简单，这样做可以节省性能

- 进行垃圾收集的时候，堆包含新生代、老年代、元空间/永久代：可以看出 Heap 后面包含着新生代、老年代、元空间，但是我们设置堆空间大小的时候设置的只是新生代、老年代而已，元空间是分开设置的

### 不同 GC 分类的 GC 细节

```java
/**
 *  -XX:+PrintCommandLineFlags
 *
 *  -XX:+UseSerialGC:表明新生代使用Serial GC ，同时老年代使用Serial Old GC
 *
 *  -XX:+UseParNewGC：标明新生代使用ParNew GC
 *
 *  -XX:+UseParallelGC:表明新生代使用Parallel GC
 *  -XX:+UseParallelOldGC : 表明老年代使用 Parallel Old GC
 *  说明：二者可以相互激活
 *
 *  -XX:+UseConcMarkSweepGC：表明老年代使用CMS GC。同时，年轻代会触发对ParNew 的使用
 * @author shkstart
 * @create 17:19
 */
public class GCUseTest {
    public static void main(String[] args) {
        ArrayList<byte[]> list = new ArrayList<>();

        while(true){
            byte[] arr = new byte[1024 * 10];//10kb
            list.add(arr);
//            try {
//                Thread.sleep(5);
//            } catch (InterruptedException e) {
//                e.printStackTrace();
//            }
        }
    }
} 
****
```

#### 老年代使用 CMS GC

GC 设置方法：参数中使用 -XX:+UseConcMarkSweepGC，说明老年代使用 CMS GC，同时年轻代也会触发对 ParNew 的使用，因此添加该参数之后，新生代使用 ParNew GC，而老年代使用 CMS GC，整体是并发垃圾收集，主打低延迟

![[附件/image/下篇05_分析GC日志-1.jpg]]

打印出来的 GC 细节：

![[附件/image/下篇05_分析GC日志-2.jpg]]

#### 新生代使用 Serial GC

GC 设置方法：参数中使用 -XX:+UseSerialGC，说明新生代使用 Serial GC，同时老年代也会触发对 Serial Old GC 的使用，因此添加该参数之后，新生代使用 Serial GC，而老年代使用 Serial Old GC，整体是串行垃圾收集

![[附件/image/下篇05_分析GC日志-3.jpg]]

打印出来的 GC 细节：

![[附件/image/下篇05_分析GC日志-4.jpg]]

DefNew 代表新生代使用 Serial GC，然后 Tenured 代表老年代使用 Serial Old GC

### GC 日志分类

- MinorGC

![[附件/image/下篇05_分析GC日志-5.jpg]]

- FullGC

![[附件/image/下篇05_分析GC日志-6.jpg]]

### GC 日志结构剖析

- 垃圾收集器

![[附件/image/下篇05_分析GC日志-7.jpg]]

- GC 前后情况

![[附件/image/下篇05_分析GC日志-8.jpg]]

- GC 时间

![[附件/image/下篇05_分析GC日志-9.jpg]]

### Minor GC 日志解析

添加 -XX:+PrintGCDateStamps 参数

```java
2020-11-20T17:19:43.265-0800

  日志打印时间 日期格式 如 2013-05-04T21:53:59.234+0800
```

添加 -XX:+PrintGCTimeStamps 参数

```java
0.822:

  gc发生时，Java虚拟机启动以来经过的秒数
```

```java
[GC(Allocation Failure)

  发生了一次垃圾回收，这是一次Minior GC。它不区分新生代还是老年代GC，括号里的内容是gc发生的原因，这里的Allocation Failure的原因是新生代中没有足够区域能够存放需要分配的数据而失败
  
[PSYoungGen:76800K->8433K(89600K)
 
	PSYoungGen：
	
		表示GC发生的区域，区域名称与使用的GC收集器是密切相关的
			Serial收集器：Default New Generation 显示Defnew
			ParNew收集器：ParNew
			Parallel Scanvenge收集器：PSYoung
			老年代和新生代同理，也是和收集器名称相关

	76800K->8433K(89600K)：
		GC前该内存区域已使用容量->GC后盖区域容量(该区域总容量)
			如果是新生代，总容量则会显示整个新生代内存的9/10，即eden+from/to区	
			如果是老年代，总容量则是全身内存大小，无变化
```

虽然本次是 Minor GC，只会进行新生代的垃圾收集，但是也肯定会打印堆中总容量相关信息

```java
76800K->8449K(294400K)
 
	在显示完区域容量GC的情况之后，会接着显示整个堆内存区域的GC情况：GC前堆内存已使用容量->GC后堆内存容量（堆内存总容量），并且堆内存总容量 = 9/10 新生代 + 老年代，然后堆内存总容量肯定小于初始化的内存大小
	
,0.0088371
 
	整个GC所花费的时间，单位是秒
	
[Times：user=0.02 sys=0.01,real=0.01 secs]

	user：指CPU工作在用户态所花费的时间
	sys：指CPU工作在内核态所花费的时间
	real：指在此次事件中所花费的总时间
```

### Full GC 日志解析

添加 -XX:+PrintGCDateStamps 参数

```java
2020-11-20T17:19:43.794-0800

	日志打印时间 日期格式 如 2013-05-04T21:53:59.234+0800
```

添加 -XX:+PrintGCTimeStamps 参数

```java
1.351

	gc发生时，Java虚拟机启动以来经过的秒数

Full GC(Metadata GCThreshold)

	括号中是gc发生的原因，原因：Metaspace区不够用了。 除此之外，还有另外两种情况会引起Full GC，如下： 1、Full GC(FErgonomics) 原因：JVM自适应调整导致的GC 2、Full GC（System） 原因：调用了System.gc()方法

[PSYoungGen: 100082K->0K(89600K)]

	PSYoungGen：
	
		表示GC发生的区域，区域名称与使用的GC收集器是密切相关的
			Serial收集器：Default New Generation 显示DefNew
			ParNew收集器：ParNew
			Parallel Scanvenge收集器：PSYoungGen
			老年代和新生代同理，也是和收集器名称相关
		
	10082K->0K(89600K)：
	
		GC前该内存区域已使用容量->GC该区域容量(该区域总容量)
			如果是新生代，总容量会显示整个新生代内存的9/10，即eden+from/to区
			如果是老年代，总容量则是全部内存大小，无变化

ParOldGen：32K->9638K(204800K)

	老年代区域没有发生GC，因此本次GC是metaspace引起的

10114K->9638K(294400K),

	在显示完区域容量GC的情况之后，会接着显示整个堆内存区域的GC情况：GC前堆内存已使用容量->GC后堆内存容量（堆内存总容量），并且堆内存总容量 = 9/10 新生代 + 老年代，然后堆内存总容量肯定小于初始化的内存大小

[Meatspace:20158K->20156K(1067008K)],

	metaspace GC 回收2K空间

```

## 03-GC 日志分析工具

### GCEasy

#### 基本概述

![[附件/image/下篇05_分析GC日志.jpeg]]

### GCViewer

#### 基本概述

![[附件/image/下篇05_分析GC日志-1.jpeg]]

#### 安装

![[附件/image/下篇05_分析GC日志-10.jpg]]

### 其他工具

#### GChisto

![[附件/image/下篇05_分析GC日志-11.jpg]]

官网上没有下载的地方，需要自己从 SVN 上拉下来编译
不过这个工具似乎没怎么维护了，存在不少 bug

#### HPjmeter

工具很强大，但是只能打开由以下参数生成的 GC log，-verbose:gc -Xloggc:gc.log。添加其他参数生成的 gc.log 无法打开

HPjmeter 集成了以前的 HPjtune 功能，可以分析在 HP 机器上产生的垃圾回收日志文件
