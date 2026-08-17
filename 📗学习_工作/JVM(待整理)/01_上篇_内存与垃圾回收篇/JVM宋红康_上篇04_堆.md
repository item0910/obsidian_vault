---
date: 2024-09-07
mtime: 2024-10-15
---

# 四. 堆

**JVM 虚拟机**; **Java**

## 1. 堆的概述

### 堆的位置

![[附件/image/上篇04_堆.jpg]]

### 堆的核心概述

查阅<深>p44
- 是什么
	- 一个 JVM 实例堆内存, 堆也是 Java 内存管理的核心区域
	- Java 堆在 JVM 启动的时候就被创建 , 其空间大小可由参数 -Xmx -Xms 设定 (一般设为相等)
	- 堆在物理上可以存在于不连续的空间, 但在逻辑上应该是连续的
	- 所有线程共享 Java 堆, 在这里还可以划分线程私有的缓冲区 (TLAB)

- 特性:
	- Java 所有数组和对象 " 几乎 " 都是在堆上创建的 [[#8 栈上分配和逃逸分析]]
	- 堆上的对象需要通过垃圾回收才会消亡, 而堆即是垃圾回收的重点区域

- 为什么
	- 因为大量的对象在创建之后生命周期很短, 储存在垃圾回收的重点区域堆当中可以有效的管理内存

- 怎么做
	- -Xmx600m -Xms600m 设置堆空间的大小
	- -XX:NewRatio=2(默认值) 设置新生代和老年代的空间比例
	- -XX:SurvivorRatio=8(默认值) 设置 eden 区与 survivor 区的比例 (需要配合自适应参数使用)
	- -Xmn 设置新生代最大内存大小, 这个值一般采用默认
- 栈堆方法区结构示意图:

![[附件/image/上篇04_堆-1.jpg]]

### 堆空间的细分

| Java 版本 |     |     |     |
|---------|-----|-----|-----|
| Java7   |新生代 (Young Generation Space(eden & survivor))|老年代 (Old)|永久代 (Perm)|
| Java8   |新生代 (Young Generation Space(eden & survivor))|老年代 (Old)|元空间 (Meta)|

![[附件/image/上篇04_堆-2.jpg]]

### 堆的内部空间结构

- 堆空间内部图:

![[附件/image/上篇04_堆-3.jpg]]

### 设置堆内存大小与 OOM(out of memory)

#### 堆空间大小的设置与默认初始值

- 通过参数设定堆大小 (通常设定相等, 目的在于为了能够在 GC 之后不需要重新计算堆的大小, 便于管理和提高性能)
	- -Xmx 等价于 -XX:MaxHeapSize;
	- -Xms 等价于 -XX:InitialHeapSize;
- 默认情况下初始内存大小: 物理电脑内存大小 / 64; 最大内存大小: 物理电脑内存大小 / 4;

#### OOM

```java
/**
 * @author Item
 */
class Picture {
    int size = 0;

    public Picture(int size) {
        this.size = size;
    }
}


public class OOMTest {
    public static void main(String[] args) {
        ArrayList<Picture> pictures = new ArrayList<Picture>();
        int count = 0;

        while (true) {
            pictures.add(new Picture(new Random().nextInt(1024 * 1024)));
            System.out.println("新建了" + ++count + "副画");
        }
    }
}

```

## 2. 年轻代与老年代

### 堆空间的分代思想

#### 为什么要分代

- 经研究, 不同对象的生命周期不同, 70% - 90% 的对象是临时对象

- 为了优化性能, 很多朝生夕死的对象需要进行集中进行回收.

 ### 年轻代和老年代概述和进一步细分
- 对于 Java 对象来说, 按照生命周期可以划分为两类对象
	- 一种是生命周期较短的对象, 他们的创建和消亡都非常迅速
	- 一种是生命周期较长的对象, 有时他们的生命周期甚至可以和 JVM 生命周期保持一致

- 对于堆区来说, 可以划分为年轻代 (YoungGen) 和 老年代 (Old)
	- 其中年轻代又分为 Eden(伊甸园区), Survivor0 区和 Survivor1 区 (也称 From 和 To 区) ,其中 To 区是永远为空的.

### 分布和默认比例

- 默认分布

	- -Xmx600m -Xms600m 设置堆空间的大小
	- -XX:NewRatio=2(默认值) 设置新生代和老年代的空间比例
	- -XX:SurvivorRatio=8(默认值) 设置 eden 区与 survivor 区的比例 (需要配合自适应参数使用)
	- -Xmn 设置新生代最大内存大小, 这个值一般采用默认

## 3. 对象的分配过程

### 对象内存分配过程概述与图解

<深> p129
为新对象分配内存是一件非常严谨和复杂的任务，JVM 的设计者们不仅需要考虑内存如何分配、在哪里分配等问题，并且由于内存分配算法与内存回收算法密切相关，所以还需要考虑 GC 执行完内存回收后是否会在内存空间中产生内存碎片。
1. new 的对象先放伊甸园区。此区有大小限制。
2. 当伊甸园的空间填满时，程序又需要创建对象，JVM 的垃圾回收器将对伊甸园区进行垃圾回收 (Minor GC)，将伊甸园区中的不再被其他对象所引用的对象进行销毁。再加载新的对象放到伊甸园区
3. 然后将伊甸园中的剩余对象移动到幸存者 0 区。
4. 如果再次触发垃圾回收，此时上次幸存下来的放到幸存者 0 区的，如果没有回收，就会放到幸存者 1 区。
5. 如果再次经历垃圾回收，此时会重新放回幸存者 0 区，接着再去幸存者 1 区
6. 啥时候能去养老区呢?可以设置次数。默认是 15 次。
	- 可以设置参数:-xx:MaxTenuringThreshold=< N >进行设置
7. 在养老区，相对悠闲。当养老区内存不足时，再次触发 GC:Major GC，进行养老区的内存清理。
8. 若养老区执行了 Major GC 之后发现依然无法进行对象的保存，就会产生 OOM 异常

	>java.lang.OutOfMemoryError: Java heap space

![[附件/image/上篇04_堆-6.jpg]]

### 总结和流程图

![[附件/image/上篇04_堆-7.jpg]]
![[附件/image/上篇04_堆-8.jpg]]

![[附件/image/上篇04_堆-9.jpg]]

### 常用的调优工具

- JDK 命令行
- Eclipse:MemoryAnalyzer Tool
- Jconsole
- VisualVM
- Jprofiler
- Java Flight Recorder
- GCViewer
- GC Easy

## 4. GC

### GC 的分类

![[附件/image/上篇04_堆-11.jpg]]
STW: stop the world

### Minor GC 的触发机制

![[附件/image/上篇04_堆-12.jpg]]

### Major GC 触发机制

![[附件/image/上篇04_堆-13.jpg]]

### Full GC 触发机制

![[附件/image/上篇04_堆-14.jpg]]

## 5. 对象晋升策略 (Promotion 规则)

![[附件/image/上篇04_堆-15.jpg]]

## 6. 对象分配内存过程 TLAB(Thread Local Allocation Buffer)

- 对象的创建
[[JVM宋红康_上篇06_Java对象和直接内存#创建对象的步骤 6步]]
![[附件/image/上篇04_堆-16.jpg]]

### 为什么要有 TLAB

![[附件/image/上篇04_堆-17.jpg]]

### 什么是 TLAB

![[附件/image/上篇04_堆-18.jpg]]

### 图解和说明

![[附件/image/上篇04_堆-19.jpg]]
![[附件/image/上篇04_堆-20.jpg]]
![[附件/image/上篇04_堆-21.jpg]]

## 7. 小结堆空间的参数设置

![[附件/image/上篇04_堆-22.jpg]]
![[附件/image/上篇04_堆-23.jpg]]
![[附件/image/上篇04_堆-24.jpg]]

## 8. 栈上分配和逃逸分析

### 什么是逃逸分析和举例

#### 逃逸分析概述

![[附件/image/上篇04_堆-25.jpg]]
![[附件/image/上篇04_堆-26.jpg]]

#### 举例

![[附件/image/上篇04_堆-27.jpg]]
![[附件/image/上篇04_堆-28.jpg]]
![[附件/image/上篇04_堆-29.jpg]]

### 逃逸分析的参数设置

![[附件/image/上篇04_堆-30.jpg]]

### 逃逸分析结论

![[附件/image/上篇04_堆-31.jpg]]

### 编译器基于逃逸分析的代码优化

![[附件/image/上篇04_堆-32.jpg]]

#### 栈上分配

![[附件/image/上篇04_堆-33.jpg]]

#### 同步省略

![[附件/image/上篇04_堆-34.jpg]]
![[附件/image/上篇04_堆-35.jpg]]

#### 分离对象或标量替换

![[附件/image/上篇04_堆-36.jpg]]
![[附件/image/上篇04_堆-37.jpg]]
![[附件/image/上篇04_堆-38.jpg]]

#### 逃逸分析的参数

![[附件/image/上篇04_堆-39.jpg]]

#### 逃逸分析小结

![[附件/image/上篇04_堆-40.jpg]]

## 9. 堆小结

![[附件/image/上篇04_堆-41.jpg]]

————————————————
