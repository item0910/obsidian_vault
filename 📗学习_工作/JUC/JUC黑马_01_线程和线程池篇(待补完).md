---
date: 2024-09-07
mtime: 2024-11-20
---

# 并发编程要解决什么问题?

链接: [https://www.bilibili.com/video/BV16J411h7Rd](https://www.bilibili.com/video/BV16J411h7Rd)

- 问题: Java 并发编程处理什么问题?

> 多线程如何处理共享资源的问题.

围绕以上这个问题引出如下两个问题:
1. 线程相关的问题
2. 线程怎样处理共享资源的问题 (共享资源的读写)

由此, 将并发编程分为两个篇章, 分别是
1. 线程和线程池篇: 解决线程的创建, 管理和调度的问题
2. 共享模型篇: 解决如何处理共享资源的问题

# 一. 多线程问题导入

几个基本概念:

## 1.1 进程和线程

### 进程

- 进程：程序是静止的，进程实体的运行过程就是进程，是系统进行**资源分配的基本单位**
- 进程拥有共享的资源，如内存空间等，供其**内部的线程共享**
- 程序由指令和数据组成，但这些指令要运行，数据要读写，就必须将指令加载至 CPU，数据加载至内存。在 指令运行过程中还需要用到磁盘、网络等设备。进程就是用来加载指令、管理内存、管理 IO 的当一个程序被运行，从磁盘加载这个程序的代码至内存，这时就开启了一个进程。进程就可以视为程序的一个实例。大部分程序可以同时运行多个实例进程（例如记事本、画图、浏览器等），也有的程序只能启动一个实例进程（例如网易云音乐、360 安全卫士等）
- 进程的特征：并发性、异步性、动态性、独立性、结构性
- 进程间通信较为复杂
	同一台计算机的进程通信称为 IPC（Inter-process communication）
	- 信号量：信号量是一个计数器，用于多进程对共享数据的访问，解决同步相关的问题并避免竞争条件
	- 共享存储：多个进程可以访问同一块内存空间，需要使用信号量用来同步对共享存储的访问
	- 管道通信：管道是用于连接一个读进程和一个写进程以实现它们之间通信的一个共享文件，pipe 文件
		- 匿名管道（Pipes）：用于具有亲缘关系的父子进程间或者兄弟进程之间的通信，只支持**半双工通信**
		- 命名管道（Names Pipes）：以磁盘文件的方式存在，可以实现本机任意两个进程通信，遵循 FIFO
	- 消息队列：内核中存储消息的链表，由消息队列标识符标识，能在不同进程之间提供**全双工通信**，对比管道：
		- 匿名管道存在于内存中的文件；命名管道存在于实际的磁盘介质或者文件系统；消息队列存放在内核中，只有在内核重启（操作系统重启）或者显示地删除一个消息队列时，该消息队列才被真正删除
		- 读进程可以根据消息类型有选择地接收消息，而不像 FIFO 那样只能默认地接收

	不同计算机之间的**进程通信**，需要通过网络，并遵守共同的协议，例如 HTTP
	- 套接字：与其它通信机制不同的是，它可用于不同机器间的互相通信

### 线程

- **线程**：线程是属于进程的，是一个基本的 CPU 执行单元，是程序执行流的最小单元。线程是进程中的一个实体，是系统**独立调度的基本单位**，线程本身不拥有系统资源，只拥有一点在运行中必不可少的资源，但它可与同属一个进程的其他线程共享进程所拥有的全部资源
- 一个线程就是一个指令流，将指令流中的一条条指令以一定的顺序交给 CPU 执行
- Java 中，线程作为最小调度单位，进程作为资源分配的最小单位。 在 windows 中进程是不活动的，只是作为线程的容器

关系：一个进程可以包含多个线程，这就是多线程，比如看视频是进程，图画、声音、广告等就是多个线程

线程的作用：使多道程序更好的并发执行，提高资源利用率和系统吞吐量，增强操作系统的并发性能

## 1.2 并行和并发

- 并行：在同一时刻，有多个指令在多个 CPU 上同时执行
- 并发：在同一时刻，有多个指令在单个 CPU 上交替执行

### 【应用】多核 CPU 并发

- **结论**
1. **单核 cpu** 下，多线程不能实际提高程序运行效率，只是为了能够在不同的任务之间切换，不同线程轮流使用 cpu ，不至于一个线程总占用 cpu，别的线程没法干活
2. 多核 cpu 可以并行跑多个线程，但能否提高程序运行效率还是要分情况的有些任务，经过精心设计，将任务拆分，并行执行，当然可以提高程序的运行效率。但不是所有计算任务都能拆分（参考后文的【阿姆达尔定律】）也不是所有任务都需要拆分，任务的目的如果不同，谈拆分和效率没啥意义
3. IO 操作不占用 cpu，只是我们一般拷贝文件使用的是【**阻塞 IO**】，这时相当于线程虽然不用 cpu，**但需要一直等待 IO 结束**，没能充分利用线程。所以才有后面的【非阻塞 IO】和【异步 IO】优化

## 1.3 同步和异步

- 需要等待结果返回，才能继续运行就是同步
- 不需要等待结果返回，就能继续运行就是异步
	- 比如: 视频转换, Tomcat3.0 提供异步线程, 用户界面相关的 UI 线程

### 总结: 进程和线程的对比

线程进程对比：
- 进程基本上相互独立的，而线程存在于进程内，是进程的一个子集
- 进程拥有共享的资源，如内存空间等，供其内部的线程共享
- 进程间通信较为复杂
	- 同一台计算机的进程通信称为 IPC（Inter-process communication）
	- 不同计算机之间的进程通信，需要通过网络，并遵守共同的协议，例如 HTTP
- 线程通信相对简单，因为它们共享进程内的内存，一个例子是多个线程可以访问同一个共享变量
- 线程更轻量，线程上下文切换成本一般上要比进程上下文切换低

# 二. 线程

## 2.1 Java 线程的几个核心概念

### 2.1.1 线程在 JVM 中

- 每个线程启动后，虚拟机就会为其分配一块栈内存
	- 每个栈由多个栈帧（Frame）组成，对应着每次方法调用时所占用的内存
	- 每个线程只能有一个活动栈帧，对应着当前正在执行的那个方法
	- 程序计数器（Program Counter Register）记录下一条 JVM 指令的执行地址，是线程私有的
- **线程的上下文切换**
	- 线程上下文切换（Thread Context Switch）：一些原因导致 CPU 不再执行当前线程，转而执行另一个线程

		- 线程的 CPU 时间片用完
		- 垃圾回收
		- 有更高优先级的线程需要运行
		- 线程自己调用了 sleep、yield、wait、join、park 等方法

	- 当 Context Switch 发生时，需要由操作系统保存当前线程的状态，并恢复另一个线程的状态，包括程序计数器、虚拟机栈中每个栈帧的信息，如局部变量、操作数栈、返回地址等

## 2.2 线程的创建

```
Thread t = new Thread(){
	public void run(){
		//...
	}
}
t.setName("t1");
```

#### 创建线程类的四种方法

##### 一. 继承 Thread 类

##### 二. 实现 Runnable 接口, 并将其实现类的实例作为参数传入 Thread 的构造方法中

```java
//Thread 类本身也是实现了 Runnable 接口，Thread 类中持有 Runnable 的属性，执行线程 run 方法底层是调用 Runnable#run：
public class Thread implements Runnable {
    private Runnable target;
    
    public void run() {
        if (target != null) {
          	// 底层调用的是 Runnable 的 run 方法
            target.run();
        }
    }
}
```

- 分析 Thread 的源码，理清它与 Runnable 的关系
	小结:
	方法 1 是把线程和任务合并在了一起，方法 2 是把线程和任务分开了
	1. 线程任务类只是实现了 Runnable 接口，可以继续继承其他类，避免了单继承的局限性
	2. 同一个线程任务对象可以被包装成多个线程对象
	3. 实现解耦操作,线程任务代码可以被多个线程共享，并独立于线程
	4. 适合多个线程去共享同一个资源
	5. **线程池**可以放入实现 Runnable 或 Callable 线程任务对象

##### 三. 实现 Callable 接口, 并将其实现类的实例作为参数传入 FutureTask 的构造方法中, 并将生成的实例传入 Thread 的构造方法之中

- 步骤
	1. 定义一个线程任务类实现 Callable 接口，申明线程执行的结果类型
	2. 重写线程任务类的 call 方法，这个方法可以直接返回执行的结果
	3. 创建一个 Callable 的线程任务对象
	4. 把 Callable 的线程任务对象**包装成一个未来任务对象**
	5. 把未来任务对象包装成线程对象
	6. 调用线程的 start() 方法启动线程
- 原理:

	`FutureTask<V>` 的继承结构如下:

	```
	public class FutureTask<V> implements RunnableFuture<V> extends Runnable Future<V>
	```

- FutureTask 就是 Runnable 对象，因为 **Thread 类只能执行 Runnable 实例的任务对象**，所以把 Callable 包装成未来任务对象
- run() 执行完后会把结果设置到 FutureTask 的一个成员变量，get() 线程可以获取到该变量的值
- get() 线程会阻塞等待任务执行完成

```java
@Slf4j(topic = "c.CreatedThreadTest")
public class CreatedThreadTest {
    public static void main(String[] args) throws ExecutionException, InterruptedException {
		
        MyThread my1 = new MyThread("继承");
        my1.start();







		//推荐
		Thread my2 = new Thread(new MyRunnable(),"Runnable实现");
        my2.start();

		//lambda表示:
        Thread my3 = new Thread(()->{
			//本质是实现了一个runnable函数式接口
            log.debug("函数式接口实现");
        },"函数式接口");
        my3.start();






		//方式三: 通过实现Callnable接口
        FutureTask<String> futureTask = new FutureTask<String>(()->{
			//本质是实现了一个带返回值的callnable函数式接口
            TimeUnit.SECONDS.sleep(5);
            return "futureTask线程运行结束后的返回值";
        });

        long now = System.currentTimeMillis();
        Thread my4 = new Thread(futureTask,"futuretask");
        my4.start();
		//该方法需要等到futureTask创建的线程执行完毕后才能获取值,否则将主线程进入阻塞状态
		System.out.println("主线程启动");
        log.debug("返回值:{}",futureTask.get());
        log.debug("花费时间:{}",System.currentTimeMillis() - now);
    }
}

@Slf4j(topic = "c.MyThread")
//方式一, 继承Thread类(间接实现Runnable接口)
class MyThread extends Thread {

    public MyThread(String name) {
        super(name);
    }

    @Override
    public void run() {
        log.debug("继承方式实现");
    }
}


@Slf4j(topic = "c.MyRunnable")
//方式二, 通过实现Runnable接口
class MyRunnable implements Runnable {
    @Override
    public void run() {
        log.debug("实现runnable方式实现");
    }
}
```

- FutureTask 类详解
	- 简述: 将一个 runnable 接口封装成一个 Callable 接口, 并执行 run 方法, run() 方法会唤醒等待的 get() 方法, 从而使其获得结果
	FutureTask 未来任务对象，继承 Runnable、Future 接口，用于包装 Callable 对象，实现任务的提交

```java
public static void main(String[] args) throws ExecutionException, InterruptedException {
    FutureTask<String> task = new FutureTask<>(new Callable<String>() {
        @Override
        public String call() throws Exception {
            return "Hello World";
        }
    });
    new Thread(task).start();	//启动线程
    String msg = task.get();	//获取返回任务数据
    System.out.println(msg);
}
```

- 构造方法：

```java
public FutureTask(Callable<V> callable){
	this.callable = callable;	// 属性注入
    this.state = NEW; 			// 任务状态设置为 new
}
```

```java
public FutureTask(Runnable runnable, V result) {
    // 适配器模式
    this.callable = Executors.callable(runnable, result);
    this.state = NEW;       
}
public static <T> Callable<T> callable(Runnable task, T result) {
    if (task == null) throw new NullPointerException();
    // 使用装饰者模式将 runnable 转换成 callable 接口，外部线程通过 get 获取
    // 当前任务执行结果时，结果可能为 null 也可能为【传进来】的值，传进来什么返回什么
    return new RunnableAdapter<T>(task, result);
}
static final class RunnableAdapter<T> implements Callable<T> {
    final Runnable task;
    final T result;
    // 构造方法
    RunnableAdapter(Runnable task, T result) {
        this.task = task;
        this.result = result;
    }
    public T call() {
        // 实则调用 Runnable#run 方法
        task.run();
        // 返回值为构造 FutureTask 对象时传入的返回值或者是 null
        return result;
    }
}
```

- 成员属性

FutureTask 类的成员属性：

* 任务状态：

  ```java
  // 表示当前task状态
  private volatile int state;
  // 当前任务尚未执行
  private static final int NEW          = 0;
  // 当前任务正在结束，尚未完全结束，一种临界状态
  private static final int COMPLETING   = 1;
  // 当前任务正常结束
  private static final int NORMAL       = 2;
  // 当前任务执行过程中发生了异常，内部封装的 callable.run() 向上抛出异常了
  private static final int EXCEPTIONAL  = 3;
  // 当前任务被取消
  private static final int CANCELLED    = 4;
  // 当前任务中断中
  private static final int INTERRUPTING = 5;
  // 当前任务已中断
  private static final int INTERRUPTED  = 6;
  ```

* 任务对象：

  ```java
  private Callable<V> callable;	// Runnable 使用装饰者模式伪装成 Callable
  ```

* **存储任务执行的结果**，这是 run 方法返回值是 void 也可以获取到执行结果的原因：

  ```java
  // 正常情况下：任务正常执行结束，outcome 保存执行结果，callable 返回值
  // 非正常情况：callable 向上抛出异常，outcome 保存异常
  private Object outcome; 
  ```

* 执行当前任务的线程对象：

  ```java
  private volatile Thread runner;	// 当前任务被线程执行期间，保存当前执行任务的线程对象引用
  ```

* 线程阻塞队列的头节点：

  ```java
  // 会有很多线程去 get 当前任务的结果，这里使用了一种数据结构头插头取（类似栈）的一个队列来保存所有的 get 线程
  private volatile WaitNode waiters;
  ```

* 内部类：

  ```java
  static final class WaitNode {
      // 单向链表
      volatile Thread thread;
      volatile WaitNode next;
      WaitNode() { thread = Thread.currentThread(); }
  }
  ```

- 成员方法

FutureTask 类的成员方法：
* **FutureTask#run**：任务执行入口

  ```java
  public void run() {
      //条件一：成立说明当前 task 已经被执行过了或者被 cancel 了，非 NEW 状态的任务，线程就不需要处理了
      //条件二：线程是 NEW 状态，尝试设置当前任务对象的线程是当前线程，设置失败说明其他线程抢占了该任务，直接返回
      if (state != NEW ||
          !UNSAFE.compareAndSwapObject(this, runnerOffset, null, Thread.currentThread()))
          return;
      try {
          // 执行到这里，当前 task 一定是 NEW 状态，而且【当前线程也抢占 task 成功】
          Callable<V> c = callable;
          // 判断任务是否为空，防止空指针异常；判断 state 状态，防止外部线程在此期间 cancel 掉当前任务
          // 【因为 task 的执行者已经设置为当前线程，所以这里是线程安全的】
          if (c != null && state == NEW) {
              V result;
              // true 表示 callable.run 代码块执行成功 未抛出异常
              // false 表示 callable.run 代码块执行失败 抛出异常
              boolean ran;
              try {
  				// 【调用自定义的方法，执行结果赋值给 result】
                  result = c.call();
                  // 没有出现异常
                  ran = true;
              } catch (Throwable ex) {
                  // 出现异常，返回值置空，ran 置为 false
                  result = null;
                  ran = false;
                  // 设置返回的异常
                  setException(ex);
              }
              // 代码块执行正常
              if (ran)
                  // 设置返回的结果
                  set(result);
          }
      } finally {
          // 任务执行完成，取消线程的引用，help GC
          runner = null;
          int s = state;
          // 判断任务是不是被中断
          if (s >= INTERRUPTING)
              // 执行中断处理方法
              handlePossibleCancellationInterrupt(s);
      }
  }
  ```

>run()->set(result)

- FutureTask#set：设置正常返回值，首先将任务状态设置为 COMPLETING 状态代表完成中，逻辑执行完设置为 NORMAL 状态代表任务正常执行完成，最后唤醒 get() 阻塞线程

  ```java
  protected void set(V v) {
      // CAS 方式设置当前任务状态为完成中，设置失败说明其他线程取消了该任务
      if (UNSAFE.compareAndSwapInt(this, stateOffset, NEW, COMPLETING)) {
          // 【将结果赋值给 outcome】
          outcome = v;
          // 将当前任务状态修改为 NORMAL 正常结束状态。
          UNSAFE.putOrderedInt(this, stateOffset, NORMAL);
          finishCompletion();
      }
  }
  ```

>run()->set(result)-- 将结果赋值给 outcome-->finishCompletion();

- FutureTask#setException：设置异常返回值

  ```java
  protected void setException(Throwable t) {
      if (UNSAFE.compareAndSwapInt(this, stateOffset, NEW, COMPLETING)) {
          // 赋值给返回结果，用来向上层抛出来的异常
          outcome = t;
          // 将当前任务的状态 修改为 EXCEPTIONAL
          UNSAFE.putOrderedInt(this, stateOffset, EXCEPTIONAL);
          finishCompletion();
      }
  }
  ```

- FutureTask#finishCompletion：**唤醒 get() 阻塞线程**

  ```java
  private void finishCompletion() {
      // 遍历所有的等待的节点，q 指向头节点
      for (WaitNode q; (q = waiters) != null;) {
          // 使用cas设置 waiters 为 null，防止外部线程使用cancel取消当前任务，触发finishCompletion方法重复执行
          if (UNSAFE.compareAndSwapObject(this, waitersOffset, q, null)) {
              // 自旋
              for (;;) {
                  // 获取当前 WaitNode 节点封装的 thread
                  Thread t = q.thread;
                  // 当前线程不为 null，唤醒当前 get() 等待获取数据的线程
                  if (t != null) {
                      q.thread = null;
                      LockSupport.unpark(t);
                  }
                  // 获取当前节点的下一个节点
                  WaitNode next = q.next;
                  // 当前节点是最后一个节点了
                  if (next == null)
                      break;
                  // 断开链表
                  q.next = null; // help gc
                  q = next;
              }
              break;
          }
      }
      done();
      callable = null;	// help GC
  }
  ```

>run()->set(result)-- 将结果赋值给 outcome-->finishCompletion()-->唤醒 get()

- FutureTask#handlePossibleCancellationInterrupt：任务中断处理

  ```java
  private void handlePossibleCancellationInterrupt(int s) {
      if (s == INTERRUPTING)
          // 中断状态中
          while (state == INTERRUPTING)
              // 等待中断完成
              Thread.yield();
  }
  ```

>run()->set(result)-- 将结果赋值给 outcome-->finishCompletion()-->唤醒 get()

* **FutureTask#get**：获取任务执行的返回值，执行 run 和 get 的不是同一个线程，一般有多个线程 get，只有一个线程 run

  ```java
  public V get() throws InterruptedException, ExecutionException {
      // 获取当前任务状态
      int s = state;
      // 条件成立说明任务还没执行完成
      if (s <= COMPLETING)
          // 返回 task 当前状态，可能当前线程在里面已经睡了一会
          s = awaitDone(false, 0L);
      return report(s);
  }
  ```

- FutureTask#awaitDone：**get 线程封装成 WaitNode 对象进入阻塞队列阻塞等待**

  ```java
  private int awaitDone(boolean timed, long nanos) throws InterruptedException {
      // 0 不带超时
      final long deadline = timed ? System.nanoTime() + nanos : 0L;
      // 引用当前线程，封装成 WaitNode 对象
      WaitNode q = null;
      // 表示当前线程 waitNode 对象，是否进入阻塞队列
      boolean queued = false;
      // 【三次自旋开始休眠】
      for (;;) {
          // 判断当前 get() 线程是否被打断，打断返回 true，清除打断标记
          if (Thread.interrupted()) {
              // 当前线程对应的等待 node 出队，
              removeWaiter(q);
              throw new InterruptedException();
          }
  		// 获取任务状态
          int s = state;
          // 条件成立说明当前任务执行完成已经有结果了
          if (s > COMPLETING) {
              // 条件成立说明已经为当前线程创建了 WaitNode，置空 help GC
              if (q != null)
                  q.thread = null;
              // 返回当前的状态
              return s;
          }
          // 条件成立说明当前任务接近完成状态，这里让当前线程释放一下 cpu ，等待进行下一次抢占 cpu
          else if (s == COMPLETING) 
              Thread.yield();
          // 【第一次自旋】，当前线程还未创建 WaitNode 对象，此时为当前线程创建 WaitNode对象
          else if (q == null)
              q = new WaitNode();
          // 【第二次自旋】，当前线程已经创建 WaitNode 对象了，但是node对象还未入队
          else if (!queued)
              // waiters 指向队首，让当前 WaitNode 成为新的队首，【头插法】，失败说明其他线程修改了新的队首
              queued = UNSAFE.compareAndSwapObject(this, waitersOffset, q.next = waiters, q);
          // 【第三次自旋】，会到这里，或者 else 内
          else if (timed) {
              nanos = deadline - System.nanoTime();
              if (nanos <= 0L) {
                  removeWaiter(q);
                  return state;
              }
              // 阻塞指定的时间
              LockSupport.parkNanos(this, nanos);
          }
          // 条件成立：说明需要阻塞
          else
              // 【当前 get 操作的线程被 park 阻塞】，除非有其它线程将唤醒或者将当前线程中断
              LockSupport.park(this);
      }
  }
  ```

- FutureTask#report：封装运行结果，可以获取 run() 方法中设置的成员变量 outcome，**这是 run 方法的返回值是 void 也可以获取到任务执行的结果的原因**

  ```java
  private V report(int s) throws ExecutionException {
      // 获取执行结果，是在一个 futuretask 对象中的属性，可以直接获取
      Object x = outcome;
      // 当前任务状态正常结束
      if (s == NORMAL)
          return (V)x;	// 直接返回 callable 的逻辑结果
      // 当前任务被取消或者中断
      if (s >= CANCELLED)
          throw new CancellationException();		// 抛出异常
      // 执行到这里说明自定义的 callable 中的方法有异常，使用 outcome 上层抛出异常
      throw new ExecutionException((Throwable)x);	
  }
  ```

>run()->set(result)-- 将结果赋值给 outcome-->finishCompletion()-->唤醒 get()-->return x=outcome;

* FutureTask#cancel：任务取消，打断正在执行该任务的线程

  ```java
  public boolean cancel(boolean mayInterruptIfRunning) {
      // 条件一：表示当前任务处于运行中或者处于线程池任务队列中
      // 条件二：表示修改状态，成功可以去执行下面逻辑，否则返回 false 表示 cancel 失败
      if (!(state == NEW &&
            UNSAFE.compareAndSwapInt(this, stateOffset, NEW,
                                     mayInterruptIfRunning ? INTERRUPTING : CANCELLED)))
          return false;
      try {
          // 如果任务已经被执行，是否允许打断
          if (mayInterruptIfRunning) {
              try {
                  // 获取执行当前 FutureTask 的线程
                  Thread t = runner;
                  if (t != null)
                      // 打断执行的线程
                      t.interrupt();
              } finally {
                  // 设置任务状态为【中断完成】
                  UNSAFE.putOrderedInt(this, stateOffset, INTERRUPTED);
              }
          }
      } finally {
          // 唤醒所有 get() 阻塞的线程
          finishCompletion();
      }
      return true;
  }
  ```

##### 四. 通过线程池获取 (将在线程池相关的章节介绍)

#### 查看线程的方法

```sh
windows：

-   任务管理器可以查看进程和线程数，也可以用来杀死进程
    
-   tasklist 查看进程
    
-   taskkill 杀死进程
    

linux：

-   ps -fe | grep java 从所有进程中筛选
    
-   ps -fT -p <PID> 查看某个进程（PID）的所有线程
    
-   kill 杀死进程
    
-   top 按大写 H 切换是否显示线程
    
-   top -H -p <PID> 查看某个进程（PID）的所有线程
    

Java：

-   jps 命令查看所有 Java 进程
    
-   jstack <PID> 查看某个 Java 进程（PID）的所有线程状态
    
-   jconsole 来查看某个 Java 进程中线程的运行情况（图形界面）

1. 先开启某个线程并做设置:
java -Djava.rmi.server.hostname=`ip地址` -Dcom.sun.management.jmxremote -  
Dcom.sun.management.jmxremote.port=`连接端口` -Dcom.sun.management.jmxremote.ssl=是否安全连接 -  
Dcom.sun.management.jmxremote.authenticate=是否认证 java类名称

2. jconsole中填写相关参数即可
```

#### 线程的内部构造

Java Virtual Machine Stacks（Java 虚拟机栈）：每个线程启动后，虚拟机就会为其分配一块栈内存
- 每个栈由多个栈帧（Frame）组成，对应着每次方法调用时所占用的内存
- 每个线程只能有一个活动栈帧，对应着当前正在执行的那个方法
- 可以用线程 Debug 模式来观察

线程上下文切换（Thread Context Switch）：一些原因导致 CPU 不再执行当前线程，转而执行另一个线程 (使用 CPU 到不使用 CPU)
- 线程的 CPU 时间片用完
- 垃圾回收
- 有更高优先级的线程需要运行
- 线程自己调用了 sleep、yield、wait、join、park 等方法

程序计数器（Program Counter Register）：记住下一条 JVM 指令的执行地址，是线程私有的

当 Context Switch 发生时，需要由操作系统保存当前线程的状态，并恢复另一个线程的状态，包括程序计数器、虚拟机栈中每个栈帧的信息，如局部变量、操作数栈、返回地址等

Java 创建的线程是内核级线程，**线程的调度是在内核态运行的，而线程中的代码是在用户态运行**，所以线程切换（状态改变）会导致用户与内核态转换，这是非常消耗性能

Java 中 main 方法启动的是一个进程也是一个主线程，main 方法里面的其他线程均为子线程，main 线程是这些线程的父线程

#### 主线程与守护线程

默认情况下，Java 进程需要等待所有线程都运行结束，才会结束。有一种特殊的线程叫做守护线程，只要其它非守护线程运行结束了，即使守护线程的代码没有执行完，也会强制结束。

```java
@Slf4j(topic = "c.TestDaemon")
public class TestDaemon {
    public static void main(String[] args) {
        log.debug("开始运行...");
        Thread t1 = new Thread(() -> {
            log.debug("开始运行...");
            sleep(2);
            log.debug("运行结束...");
        }, "daemon");
        // 设置该线程为守护线程
        t1.setDaemon(true);
        t1.start();

        sleep(1);
        log.debug("运行结束...");
    }
}
```

说明：当运行的线程都是守护线程，Java 虚拟机将退出，因为普通线程执行完后，JVM 是守护线程，不会继续运行下去

常见的守护线程：

- 垃圾回收器线程就是一种守护线程
- Tomcat 中的 Acceptor 和 Poller 线程都是守护线程，所以 Tomcat 接收到 shutdown 命令后，不会等待它们处理完当前请求

## 2.3 线程的常见方法

- Thread 类所包含的方法

| 方法                                        | 说明                                                         |
| ------------------------------------------- | ------------------------------------------------------------ |
| public void start()                         | 启动一个新线程；Java 虚拟机调用此线程的 run 方法                |
| public void run()                           | 线程启动后调用该方法                                         |
| public void setName(String name)            | 给当前线程取名字                                             |
| public void getName()                       | 获取当前线程的名字<br />线程存在默认名称：子线程是 Thread- 索引，主线程是 main |
| public static Thread currentThread()        | 获取当前线程对象，代码在哪个线程中执行                       |
| public static void sleep(long time)         | 让当前线程休眠多少毫秒再继续执行<br />**Thread.sleep(0)** : 让操作系统立刻重新进行一次 cpu 竞争 |
| public static native void yield()           | 提示线程调度器让出当前线程对 CPU 的使用                        |
| public final int getPriority()              | 返回此线程的优先级                                           |
| public final void setPriority(int priority) | 更改此线程的优先级，常用 1 5 10                               |
| public void interrupt()                     | 中断这个线程，异常处理机制                                   |
| public static boolean interrupted()         | 判断当前线程是否被打断，清除打断标记                         |
| public boolean isInterrupted()              | 判断当前线程是否被打断，不清除打断标记                       |
| public final void join()                    | 等待这个线程结束                                             |
| public final void join(long millis)         | 等待这个线程死亡 millis 毫秒，0 意味着永远等待                  |
| public final native boolean isAlive()       | 线程是否存活（还没有运行完毕）                               |
| public final void setDaemon(boolean on)     | 将此线程标记为守护线程或用户线程                             |

下面将从**作用, 用法, 原理, 注意点**四个角度阐述

### 2.3.1 run, start

#### run

称为线程体，包含了要执行的这个线程的内容，方法运行结束，此线程随即终止。直接调用 run 是在主线程中执行了 run，没有启动新的线程，需要顺序执行;

#### start

使用 start 是启动新的线程，此线程处于就绪（可运行）状态，通过新的线程间接执行 run 中的代码, **每个线程对象只可以调用一次**

简单来说: start 才叫多线程
说明：**线程控制资源类**

**面试题多线程**

**面试问题**：run() 方法中的异常不能抛出，只能 try/catch

- 因为父类中没有抛出任何异常，子类不能比父类抛出更多的异常
- **异常不能跨线程传播回 main() 中**，因此必须在本地进行处理

### 2.3.2 sleep, yield

#### sleep：

	-   调用 sleep 会让当前线程**从 `Running` 进入 `Timed Waiting` 状态**（阻塞）
	-   sleep() 方法的过程中，线程**不会释放对象锁**
	-   其它线程可以使用 interrupt 方法**打断**正在睡眠的线程，这时 sleep 方法会抛出 InterruptedException
	-   睡眠结束后的线程未必会立刻得到执行，需要抢占 CPU
	-   建议用 TimeUnit 的 sleep 代替 Thread 的 sleep 来获得更好的可读性

##### 【应用】sleep 的应用之限制对 CPU 的使用

在没有利用 cpu 来计算时，不要让 while(true) 空转浪费 cpu，这时可以使用 yield 或 sleep 来让出 cpu 的使用权
给其他程序

```java
while(true) {  
	try {  
		Thread.sleep(50);  
	} catch (InterruptedException e) {  
		e.printStackTrace();  
	}  
}
```

1. 可以用 **wait** 或 **条件变量**达到类似的效果
2. 不同的是，后两种都需要加锁，并且需要相应的唤醒操作，一般适用于**要进行同步的场景**
3. sleep 适用于无需锁同步的场景

#### yield(让出, 终止)：

	-   调用 yield 会让提示线程调度器让出当前线程对 CPU 的使用
	-   具体的实现依赖于操作系统的任务调度器, 会出现想让没有让出去的情况
	-   **会放弃 CPU 资源，锁资源不会释放**

### 2.3.3 setPriority

线程优先级会提示（hint）调度器优先调度该线程，但这仅仅是一个提示，调度器可以忽略它

如果 CPU 比较忙，那么优先级高的线程会获得更多的时间片，但 CPU 闲时，优先级几乎没作用

```java
Thread t1 = new Thread(task1, "t1");  
Thread t2 = new Thread(task2, "t2");  
// t1.setPriority(Thread.MIN_PRIORITY);  
// t2.setPriority(Thread.MAX_PRIORITY);  
t1.start();  
t2.start();
```

### 2.3.5 join

#### 用法

- 作用: 用来等待调用线程的完成
- 用法: t1.join() / t1.join(3000);

```java
/**
 * @author Item
 */
@Slf4j(topic = "c.testJoin")
public class testJoin {
	public static void main(String[] args) {
		Thread t1 = new Thread(() -> {
			try {
				log.debug("{}", "t1开始执行");
				TimeUnit.SECONDS.sleep(3);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			log.debug("{}", "睡醒了");
		}, "t1");
		t1.start();

		try {
			t1.join();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		log.debug("{}", "t1执行完毕主线程开始执行");
	}
}
```

#### 【应用】join 的应用之同步:

```java
    static int r1 = 0;
    static int r2 = 0;
    public static void main(String[] args) throws InterruptedException {
        test2();
    }
    private static void test2() throws InterruptedException {
        Thread t1 = new Thread(() -> {
            sleep(1);
            r1 = 10;
        });
        Thread t2 = new Thread(() -> {
            sleep(2);
            r2 = 20;});
        long start = System.currentTimeMillis();
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        long end = System.currentTimeMillis();
        log.debug("r1: {} r2: {} cost: {}", r1, r2, end - start);
    }
```

- 分析:
	- 第一个 join：等待 t1 时, t2 并没有停止, 而在运行
	- 第二个 join：1s 后, 执行到此, t2 也运行了 1s, 因此也只需再等待 1s

- 添加等待时间
	- 等够时间:

```java
public class Test {
    static int r1 = 0;
    static int r2 = 0;
    public static void main(String[] args) throws InterruptedException {
        test3();
    }
    public static void test3() throws InterruptedException {
        Thread t1 = new Thread(() -> {
            sleep(1);
            r1 = 10;
        });
        long start = System.currentTimeMillis();
        t1.start();
        // 线程执行结束会导致 join 结束
        t1.join(1500);
        long end = System.currentTimeMillis();
        log.debug("r1: {} r2: {} cost: {}", r1, r2, end - start);
    }
}
结果: 20:52:15.623 [main] c.TestJoin - r1: 10 r2: 0 cost: 1502
```

- 没等够时间

```java
public class Test {
    static int r1 = 0;
    static int r2 = 0;
    public static void main(String[] args) throws InterruptedException {
        test3();
    }
    public static void test3() throws InterruptedException {
        Thread t1 = new Thread(() -> {
            sleep(2);
            r1 = 10;
        });
        long start = System.currentTimeMillis();
        t1.start();
        // 线程执行结束会导致 join 结束
        t1.join(1500);
        long end = System.currentTimeMillis();
        log.debug("r1: {} r2: {} cost: {}", r1, r2, end - start);
    }
}

结果: 20:52:15.623 [main] c.TestJoin - r1: 0 r2: 0 cost: 1502
```

- 原理
	- join 方法是被 synchronized 修饰的，本质上是一个对象锁，其内部的 wait 方法调用也是释放锁的，但是**释放的是调用该方法的当前的线程对象，而不是外面的锁**
	- 当某个线程调用他的 join 方法后, 他就不再是释放, 直到线程完毕

	```java
	public final synchronized void join(long millis) throws InterruptedException {
		// 调用者线程进入 thread 的 waitSet 等待, 直到当前线程运行结束
		while (isAlive()) {
			wait(0);
		}
	}
	23:44:37.068 c.testJoin [t1] - t1开始执行
	23:44:40.072 c.testJoin [t1] - 睡醒了
	23:44:40.072 c.testJoin [main] - t1执行完毕主线程开始执行
	Process finished with exit code 0
	```

### 2.3.4 interrupt 系列

`public void interrupt()`：打断这个线程，异常处理机制, 正常运行的线程被打断,打断标记会置为 true;

`public static boolean interrupted()`：判断当前线程是否被打断，打断返回 true 并**清除打断标记**(置为 false)，连续调用两次一定返回 false

`public boolean isInterrupted()`：判断当前线程是否被打断，**不清除打断标记**

打断的线程会发生上下文切换，操作系统会保存线程信息，抢占到 CPU 后会从中断的地方接着运行（打断不是停止）

-

```java
/**
 * @author Item
 */
@Slf4j(topic="c.IsInterruppetedTest")
public class IsInterruppetedTest {
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            //t1处于阻塞状态, sleep, wait, join
            log.debug("sleep");
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        },"t1");
        t1.start();
        Thread.sleep(500);
        log.debug("打断t1");
        t1.interrupt();
        log.debug("t1的打断标记为:{}",t1.isInterrupted());
    }
}
```

- 结果:t1 的打断标记被置为 false(意为: 未在运行中被打断)

```shell
23:50:47.068 c.IsInterruppetedTest [t1] - sleep
23:50:47.567 c.IsInterruppetedTest [main] - 打断t1
23:50:47.567 c.IsInterruppetedTest [main] - t1的打断标记为:false
java.lang.InterruptedException: sleep interrupted
	at java.lang.Thread.sleep(Native Method)
	at cn.itcast.myown.IsInterruppetedTest.lambda$main$0(IsInterruppetedTest.java:18)
	at java.lang.Thread.run(Thread.java:748)
```

- 打断正在正常运行中的线程

```java
Thread t2 = new Thread(()->{
            log.debug("正常运行");
            while(true){
                boolean interrupted = Thread.currentThread().isInterrupted();
                if(interrupted){
                    log.debug("被打断了");
                    break;
                }
            }
        },"t2");

        t2.start();
        Thread.sleep(500);
        log.debug("打断t2");
        t2.interrupt();
        log.debug("t2的打断标记为:{}",t2.isInterrupted());
```

- 结果, 打断标记被置为 true.

```shell
00:06:41.574 c.IsInterruppetedTest [t2] - 正常运行
00:06:42.080 c.IsInterruppetedTest [main] - 打断t2
00:06:42.080 c.IsInterruppetedTest [main] - t2的打断标记为:true
00:06:42.080 c.IsInterruppetedTest [t2] - 被打断了
```

- 注意⚠️:
	- **park 状态的线程被打断:** 不会清空打断状态

```java
/**
 * @author Item
 */
@Slf4j(topic = "c.InterruptParkTest")
public class InterruptParkTest {
    public static void main(String[] args) throws InterruptedException {
        Thread t3 = new Thread(() -> {
            log.debug("park..");
            LockSupport.park();
            log.debug("t3被打断");
            log.debug("t3的打断标记为:{}",Thread.currentThread().isInterrupted());
			LockSupport.park();//打断标记为true时不会执行, 需要在前面再执行interrupted, 将打断标记清除;
        }, "t3");
	
        t3.start();

        log.debug("主线程在打断t3前睡眠");
        Thread.sleep(2000);
        log.debug("打断t3");
        t3.interrupt();
    }
}
```

- 结果: park 的线程被打断不会清除打断标记

```shell
01:25:24.157 c.InterruptParkTest [t3] - park..
01:25:24.157 c.InterruptParkTest [main] - 主线程在打断t3前睡眠
01:25:26.163 c.InterruptParkTest [main] - 打断t3
01:25:26.163 c.InterruptParkTest [t3] - t3被打断
01:25:26.163 c.InterruptParkTest [t3] - t3的打断标记为:true
```

#### 【模式】两阶段终止模式 (用 Interrupted 实现)

终止模式之两阶段终止模式：Two Phase Termination
- 目标：
	- 在一个线程 T1 中如何优雅终止线程 T2？**优雅指的是给 T2 一个后置处理器**

- 错误思想：
	- 1. 使用线程对象的 stop() 方法停止线程：stop 方法会真正杀死线程，如果这时线程锁住了共享资源，当它被杀死后就再也没有机会释放锁，其它线程将永远无法获取锁
	- 2. 使用 System.exit(int) 方法停止线程：目的仅是停止一个线程，但这种做法会让整个程序都停止

流程图示:

![[附件/image/01_线程和线程池篇(待补完).jpg]]

- 设计思路:
	- 共享的状态: 监视器的打断标记
	- 线程的方法: 监视器启动和线程和监视器线程停止.
	- 设计一个类, 作为监视器, 其中以打断标记为共享资源 (或者监视器线程为共享资源, 因为监视器线程就已经包含了监视器的打断标记)
	- 正常被打断, 打断标记不会变; 线程间隔中被打断 (wait 或 sleep 中), 打断标记会被清空, 此时需要重置打断标记, 用来停止线程.
- 代码:

```java
/**
 * @author Item
 */
@Slf4j(topic="c.TwoPhraseInterruptTest")
public class TwoPhraseInterruptTest {
    public static void main(String[] args) throws InterruptedException {
        TwoPhraseStop tps = new TwoPhraseStop();
        log.debug("监控线程启动");
        tps.start();
        sleep(5);
        log.debug("停止监控线程");
        tps.stop();
    }
}
//两阶段终止类
@Slf4j(topic="c.TwoPhraseStop")
class TwoPhraseStop{
    //懒汉式调用, 只有使用方法时, 才对属性赋值.
    private Thread monitor = null;

    public void start(){
        monitor = new Thread(()->{
            while(true){
                //检测打断标记, 如果被打断了, 则停止监控线程
                if(monitor.isInterrupted()){
                    log.debug("线程被打断:做善后处理");
                    break;
                }
                //监视器进程正常执行
                log.debug("执行监控任务");
                //sleep一下
                try {
                    log.debug("sleep一下");
                    sleep(3);
                } catch (InterruptedException e) {
                    //sleep中被打断, 会造成打断标记被清空, 不能正常退出循环
                    //重置打断标记为true
                    log.debug("在sleep时被打断");
                    monitor.interrupt();
                    e.printStackTrace();
                }
            }
        });
        monitor.start();
    }

    public void stop(){
        //打断线程
        monitor.interrupt();
    }
}
```

- 后面会陆续更新新的优雅方法

### 2.3.5 setDeamon

设置为守护线程
[[#主线程与守护线程]]

### 2.3.6 特别: wait/notify

>这里的特别方法只提及, 将在共享模型之有锁 (管程) 篇重新重点介绍

- Object 方法
	- 当一个线程在 wait 时, 会释放锁并处于可被其他线程唤醒的 notify 的状态
	- notify 是没有指向性的
[[JUC黑马_02_共享模型篇(待补完)#wait notify]]

### 2.3.7 特别: park/unpark

- LockSupport 的方法
	- 当一个线程在 park 时, 也会释放锁并处于可被 unpark 的状态
	- unpark 是可以指向的
	- park 状态中的线程, 如果被打断, 不会清空打断状态.
	- 线程打断标记为 true 时, park() 不会生效
[[JUC黑马_02_共享模型篇(待补完)#park unpark]]

### 2.3.8 特别: lock 之 await, condition, signal

- lock 的 condition 对象的方法
	- 与 wait 不同的是, 可以根据不同的 condition, 来进行指向性的唤醒
[[JUC黑马_02_共享模型篇(待补完)#4 2 Reentrantlock]]

### 2.3.9 已经被不推荐的方法

不推荐使用的方法，这些方法已过时，容易破坏同步代码块，造成线程死锁：
- stop
- resume
- suspend

## 2.4 线程的状态及其切换

### 2.4.1 进程的五种状态 (操作系统层面)

进程的状态参考操作系统：创建态、就绪态、运行态、阻塞态、终止态

![[附件/image/01_线程和线程池篇(待补完)-1.jpg]]

- 【初始状态】仅是在语言层面创建了线程对象，还未与操作系统线程关联
- 【可运行状态】（就绪状态）指该线程已经被创建（与操作系统线程关联），可以由 CPU 调度执行
- 【运行状态】指获取了 CPU 时间片运行中的状态
	- 当 CPU 时间片用完，会从【运行状态】转换至【可运行状态】，会导致线程的上下文切换
- 【阻塞状态】
	- 如果调用了阻塞 API，如 BIO 读写文件，这时该线程实际不会用到 CPU，会导致线程上下文切换，进入【阻塞状态】
	- 等 BIO 操作完毕，会由操作系统唤醒阻塞的线程，转换至【可运行状态】
	- 与【可运行状态】的区别是，对【阻塞状态】的线程来说只要它们一直不唤醒，调度器就一直不会考虑调度它们
- 【终止状态】表示线程已经执行完毕，生命周期已经结束，不会再转换为其它状态

### 2.4.2 六种状态 (Java 层面)

线程由生到死的完整过程（生命周期）：当线程被创建并启动以后，既不是一启动就进入了执行状态，也不是一直处于执行状态，在 API 中 `java.lang.Thread.State` 这个枚举中给出了六种线程状态：

| 线程状态                   | 导致状态发生条件                                             |
| -------------------------- | ------------------------------------------------------------ |
| NEW（新建）                | 线程刚被创建，但是并未启动，还没调用 start 方法，只有线程对象，没有线程特征 |
| Runnable（可运行）         | 线程可以在 Java 虚拟机中运行的状态，可能正在运行自己代码，也可能没有，这取决于操作系统处理器，调用了 t.start() 方法：就绪（经典叫法） |
| Blocked（锁阻塞）          | 当一个线程试图获取一个对象锁，而该对象锁被其他的线程持有，则该线程进入 Blocked 状态；当该线程持有锁时，该线程将变成 Runnable 状态 |
| Waiting（无限等待）        | 一个线程在等待另一个线程执行一个（唤醒）动作时，该线程进入 Waiting 状态，进入这个状态后不能自动唤醒，必须等待另一个线程调用 notify 或者 notifyAll 方法才能唤醒 |
| Timed Waiting （计时等待） | 有几个方法有超时参数，调用将进入 Timed Waiting 状态，这一状态将一直保持到超时期满或者接收到唤醒通知。带有超时参数的常用方法有 Thread.sleep 、Object.wait |
| Teminated（被终止）        | run 方法正常退出而死亡，或者因为没有捕获的异常终止了 run 方法而死亡 |

![[附件/image/01_线程和线程池篇(待补完)-2.jpg]]

- NEW → RUNNABLE：当调用 t.start() 方法时，由 NEW → RUNNABLE

- RUNNABLE <--> WAITING：
    - 调用 obj.wait() 方法时
        调用 obj.notify()、obj.notifyAll()、t.interrupt()：
        - 竞争锁成功，t 线程从 WAITING → RUNNABLE
        - 竞争锁失败，t 线程从 WAITING → BLOCKED

    - 当前线程调用 t.join() 方法，注意是当前线程在 t 线程对象的监视器上等待
    - 当前线程调用 LockSupport.park() 方法

- RUNNABLE <--> TIMED_WAITING：调用 obj.wait(long n) 方法、当前线程调用 t.join(long n) 方法、当前线程调用 Thread.sleep(long n)

- RUNNABLE <--> BLOCKED：t 线程用 synchronized(obj) 获取了对象锁时竞争失败

演示:

```java
package cn.itcast.n3;

import lombok.extern.slf4j.Slf4j;

import java.io.IOException;

@Slf4j(topic = "c.TestState")
public class TestState {
    public static void main(String[] args) throws IOException {
        Thread t1 = new Thread("t1") {
            @Override
            public void run() {
                log.debug("running...");
            }
        };

        Thread t2 = new Thread("t2") {
            @Override
            public void run() {
                while(true) { // runnable

                }
            }
        };
        t2.start();

        Thread t3 = new Thread("t3") {
            @Override
            public void run() {
                log.debug("running...");
            }
        };
        t3.start();

        Thread t4 = new Thread("t4") {
            @Override
            public void run() {
                synchronized (TestState.class) {
                    try {
                        Thread.sleep(1000000); // timed_waiting
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        };
        t4.start();

        Thread t5 = new Thread("t5") {
            @Override
            public void run() {
                try {
                    t2.join(); // waiting
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        };
        t5.start();

        Thread t6 = new Thread("t6") {
            @Override
            public void run() {
                synchronized (TestState.class) { // blocked
                    try {
                        Thread.sleep(1000000);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        };
        t6.start();

        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        log.debug("t1 state {}", t1.getState());
        log.debug("t2 state {}", t2.getState());
        log.debug("t3 state {}", t3.getState());
        log.debug("t4 state {}", t4.getState());
        log.debug("t5 state {}", t5.getState());
        log.debug("t6 state {}", t6.getState());
        System.in.read();
    }
}
- 结果:
05:30:10.488 c.TestState [t3] - running...
05:30:10.994 c.TestState [main] - t1 state NEW
05:30:10.995 c.TestState [main] - t2 state RUNNABLE
05:30:10.995 c.TestState [main] - t3 state TERMINATED
05:30:10.995 c.TestState [main] - t4 state TIMED_WAITING
05:30:10.995 c.TestState [main] - t5 state WAITING
05:30:10.995 c.TestState [main] - t6 state BLOCKED
```

### 2.4.3 【应用】应用之统筹 (泡茶方案一 Join 解决)

```java
    private static void s1() {
        Thread t1 = new Thread(() -> {
            log.debug("洗水壶");
            sleep(1);
            log.debug("烧开水");
            sleep(15);
        }, "老王");

        Thread t2 = new Thread(() -> {
            log.debug("洗茶壶");
            sleep(1);
            log.debug("洗茶杯");
            sleep(2);
            log.debug("拿茶叶");
            sleep(1);
            try {
                t1.join()；//等待t1完成
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            log.debug("泡茶");
        }, "小王");

        t1.start();
        t2.start();
    }
```

- 缺点：
	- 现在只能是 t2 等待 t1，如果需要 t1 等待 t2 则该代码需要改写
	- 如果需要互相传递返回结果，则该代码无法完成。

# 三. 线程池

## 3.1 自定义线程池实现

### 任务队列 (queue)

- 阻塞获取 (take->poll)
- 阻塞添加 (put->offer)
- 大小 (size)
- 判断是否满 (tryPut)

### 线程池 (pool)

- 成员
	- 任务队列
	- 线程 workers
	- 线程数 poolsize
	- 任务超时时间 timeout
	- 拒绝策略
- 内部类 (线程 worker)
	- 内部类的 run 方法
- 方法 (execute)
	- 通过内部类 worker 执行 (获取池中的线程对象)

## 3.2 ThreadPoolExecutor(结构)

### 3.2.1 线程池状态

### 3.2.2 构造方法及工作方式

### 3.2.3 几种常用的线程池

构造, 特点, 场景

#### newFixedThreadPool

#### newCachedThreadPool

#### newSingleThreadExecutor

### 3.2.4 使用线程池 (线程池方法)(prog)

### 3.2.5 关闭线程池 (两种方法)

### 并发模式之工作线程 (Work Thread)

## 3.3 线程任务的执行调度

### 3.3.1 调度

#### Timer

#### ScheduledExcutorService

#### FixRate

#### Fixdelay

#### 应用之定期执行

- 延迟队列 (prog)

### 3.3.2 异常处理

### 3.3.3 Tomcat 线程池 (prog)

### 3.3.4 Fork/join 线程池

作用, 用法, 原理, 注意点
- 分治思想
