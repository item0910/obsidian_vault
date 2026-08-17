---
date: 2024-08-24
mtime: 2024-10-15
---

多线程下并发面临的问题:
1. 充分利用 CPU(共享资源)
2. 结果冲突 (同时 +1, -1)

# 一. 共享模型之内存 (JMM)

## JMM 介绍 (prog)

## 1.1 三大特性之可见性

### 原理之 CPU 缓存

### 解决方法

## 1.2 三大特性之原子性 (prog)

## 1.3 三大特性之有序性

### 底层原理: 指令重排

### 解决 DCL

## 1.4 happens-before 原则

## 模式之两阶段终止

## 模式之 Balking(犹豫)

# 二. 共享模型之有锁 (管程)

两个线程对初始值为 0 的静态变量一个做自增，一个做自减，各做 5000 次，结果是 0 吗？

```java
public class Test {
    static int counter = 0;
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 5000; i++) {
                counter++;
            }
        }, "t1");
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 5000; i++) {
                counter--;
            }
        }, "t2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        log.debug("{}",counter);
    }
}
```

从字节码分析:
- i++:

```java
getstatic i // 获取静态变量i的值  
iconst_1    // 准备常量1  
iadd        // 自增  
putstatic i // 将修改后的值存入静态变量i
```

- i--

```java
getstatic i // 获取静态变量i的值  
iconst_1    // 准备常量1  
isub        // 自减  
putstatic i // 将修改后的值存入静态变
```

![[附件/image/02_共享模型篇(待补完).jpg]]

![[附件/image/02_共享模型篇(待补完)-1.jpg]]

## 2.1 基本概念之临界区与竞态条件

### 临界区

- 一个程序运行多个线程本身是没有问题的
- 问题出在**多个线程访问共享资源**
	- 多个线程**读**共享资源其实也没有问题
	- 在多个线程对共享资源**读写操作时发生指令交错**，就会出现问题

- 一段代码块内如果存在对共享资源的多线程读写操作，称这段代码块为临界区

```java
static int counter = 0;  
static void increment()  
	// 临界区  
	{  
		counter++;  
	}  
	static void decrement()  
	// 临界区  
	{  
		counter--;  
	}
```

### 竞态条件

多个线程在临界区内执行，由于代码的执行序列不同而导致结果无法预测，称之为发生了**竞态条件**

为了避免临界区的竞态条件发生，有多种手段可以达到目的。
- 阻塞式的解决方案：synchronized，Lock
- 非阻塞式的解决方案：原子变量

### 面向对象 (共享资源) 的多线程

- 写多线程的步骤 (套路)

## 2.2 synchronized

synchronized 实际是用对象锁保证了**临界区内代码的原子性**，临界区内的代码对外是不可分割的，不会被线程切换所打断。

```java
synchronized(对象) // 线程1， 线程2(blocked)  
	{  
		临界区  
	}
```

### 2.2.1 synchronized 关键字的使用和分析

- 房子和学生的理解, 带锁进入.进门反锁

#### syn 加在代码块上: 括号里面的就是加的锁

```java
    static int counter = 0;
    static final Object room = new Object();
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 5000; i++) {
                synchronized (room) {
                    counter++;
                }
            }
        }, "t1");
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 5000; i++) {
                synchronized (room) {
                    counter--;
                }
            }
        }, "t2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        log.debug("{}",counter);
    }
```

![[附件/image/02_共享模型篇(待补完)-2.jpg]]

synchronized 实际是用对象锁保证了临界区内代码的原子性，临界区内的代码对外是不可分割的，不会被线程切换所打断。
- 思考
	- 如果把 synchronized(obj) 放在 for 循环的外面，如何理解？
		- 原子性扩大, 但同样可以保证原子性
	- 如果 t1 synchronized(obj1) 而 t2 synchronized(obj2) 会怎样运作？
		- 不能保证原子性, 锁对象不同
	- 如果 t1 synchronized(obj) 而 t2 没有加会怎么样？如何理解？
		- 不能保证原子性, t2 不需要尝试获取对象锁

##### 面向对象的改造

```java
class Room {
    int value = 0;
    public void increment() {
        synchronized (this) {
            value++;
        }
    }
    public void decrement() {
        synchronized (this) {
            value--;
        }
    }
    public int get() {
        synchronized (this) {
            return value;
        }
    }
}
@Slf4j
public class Test1 {
    public static void main(String[] args) throws InterruptedException {
        Room room = new Room();
        Thread t1 = new Thread(() -> {
            for (int j = 0; j < 5000; j++) {
                room.increment();
            }
        }, "t1");
        Thread t2 = new Thread(() -> {
            for (int j = 0; j < 5000; j++) {
                room.decrement();
            }
        }, "t2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        log.debug("count: {}" , room.get());
    }
}
```

#### syn 加在一般方法上: 等价与 syn(this), 相当于谁调用就用谁锁

```java
class Test{
	public synchronized void test() {
	}
}

等价于 - 锁住的是this
class Test{
	public void test() {
		synchronized(this) {
		}
	}
}
```

#### syn 加在静态方法上, 等价于 syn(this.class), 加的类锁.

```java
class Test{
	public synchronized static void test() {
	}
}

等价于- 锁住的是类
class Test{
	public static void test() {
		synchronized(Test.class) {
		}
	}
}
```

#### 八锁问题

1. `12` 或者 `21`

```java
class Number{
    public synchronized void a() {
        log.debug("1");
    }
    public synchronized void b() {
        log.debug("2");
    }
}
    public static void main(String[] args) {
        Number n1 = new Number();
        new Thread(()->{ n1.a(); }).start();
        new Thread(()->{ n1.b(); }).start();
    }
}
```

1. 一秒后 12, 2 一秒后 1

```java
public class Test8Locks {
    public static void main(String[] args) {
        Number n1 = new Number();
        new Thread(() -> {
            log.debug("begin");
            n1.a();
        }).start();
        new Thread(() -> {
            log.debug("begin");
            n1.b();
        }).start();
    }
}
@Slf4j(topic = "c.Number")
class Number{
    public synchronized void a() {
        sleep(1);
        log.debug("1");
    }
    public synchronized void b() {
        log.debug("2");
    }
}
```

1. 3 一定会在某一时刻被打印, 12 不能被同时调度 (互斥)

```java
class Number{
    public synchronized void a() {
        sleep(1);
        log.debug("1");
    }
    public synchronized void b() {
        log.debug("2");
    }
    public void c() {
        log.debug("3");
    }
}
    public static void main(String[] args) {
        Number n1 = new Number();
        new Thread(()->{ n1.a(); }).start();
        new Thread(()->{ n1.b(); }).start();
        new Thread(()->{ n1.c(); }).start();
    }
}
```

1. 2 1s 后 1, 两个锁对象不同

```java
@Slf4j(topic = "c.Number")
class Number{
    public synchronized void a() {
        sleep(1);
        log.debug("1");
    }
    public synchronized void b() {
        log.debug("2");
    }
}
    public static void main(String[] args) {
        Number n1 = new Number();
        Number n2 = new Number();
        new Thread(()->{ n1.a(); }).start();
        new Thread(()->{ n2.b(); }).start();
    }
}
```

1. 2 1s 后 1, 一个所著的是类对象, 一个锁住的是 this, 两个对象也不同.

```java
class Number{
    public static synchronized void a() {
        sleep(1);
        log.debug("1");
    }
    public synchronized void b() {
        log.debug("2");
    }
}
    public static void main(String[] args) {
        Number n1 = new Number();
        new Thread(()->{ n1.a(); }).start();
        new Thread(()->{ n1.b(); }).start();
    }
}
```

1. 1s 后 12， 或 2 1s 后 1, 锁对象相同

```java
public class Test8Locks {
    public static void main(String[] args) {
        Number n1 = new Number();
        new Thread(() -> {
            log.debug("begin");
            n1.a();
        }).start();
        new Thread(() -> {
            log.debug("begin");
            n1.b();
        }).start();
    }
}
@Slf4j(topic = "c.Number")
class Number{
    public static synchronized void a() {
        sleep(1);
        log.debug("1");
    }
    public static synchronized void b() {
        log.debug("2");
    }
}
```

1. 2 1s 后 1, 锁对象不同

```java
class Number{
    public static synchronized void a() {
        sleep(1);
        log.debug("1");
    }
    public synchronized void b() {
        log.debug("2");
    }
}
    public static void main(String[] args) {
        Number n1 = new Number();
        Number n2 = new Number();
        new Thread(()->{ n1.a(); }).start();
        new Thread(()->{ n2.b(); }).start();
    }
}
```

1. 1s 后 12， 或 2 1s 后 1, 锁对象相同

```java
class Number{
    public static synchronized void a() {
        sleep(1);
        log.debug("1");
    }
    public static synchronized void b() {
        log.debug("2");
    }
}
    public static void main(String[] args) {
        Number n1 = new Number();
        Number n2 = new Number();
        new Thread(()->{ n1.a(); }).start();
        new Thread(()->{ n2.b(); }).start();
    }
}
```

### 2.2.2 线程安全的分析

#### 成员变量和静态变量是否线程安全？

- 如果它们没有共享，则线程安全
- 如果它们被共享了，根据它们的状态是否能够改变，又分两种情况
	- 如果只有读操作，则线程安全
	- 如果有读写操作，则这段代码是临界区，需要考虑线程安全

#### 局部变量是否线程安全？

- 局部变量是线程安全的
- 但局部变量引用的对象则未必
	- 如果该对象没有逃离方法的作用访问，它是线程安全的
	- 如果该对象逃离方法的作用范围，需要考虑线程安全

```java
public static void test1() {  
	int i = 10;  
	i++;  
}

stack=1, locals=1, args_size=0  

0: bipush  10
2: istore_0  
3: iinc    0,1
6: return
```

下面将几种情况一一进行分析:
- 主方法: 创建两个线程, 然后

```java
public class TestThreadSafe {

    static final int THREAD_NUMBER = 2;
    static final int LOOP_NUMBER = 200;
    public static void main(String[] args) {
        ThreadUnSafe test = new ThreadSafeSubClass();//这个类会更改
		
        for (int i = 0; i < THREAD_NUMBER; i++) {
            new Thread(() -> {
                test.method1(LOOP_NUMBER);
            }, "Thread" + (i+1)).start();
        }
    }
}
```

- 情况 1 : 先分析一个成员变量的例子: 使用成员变量, 此时两个线程共同修改这个成员变量, 会造成资源共享的问题, 从而引发线程安全

```java
class ThreadUnsafe {
    ArrayList<String> list = new ArrayList<>();
    public void method1(int loopNumber) {
        for (int i = 0; i < loopNumber; i++) {
            method2();
            method3();
        }
    }

    private void method2() {
        list.add("1");
    }

    private void method3() {
        list.remove(0);
    }
}
```

- 把成员变量改为局部变量, 此时两个线程各用各的局部变量, 不会引发资源共享的问题

```java
public class TestThreadSafe {

    static final int THREAD_NUMBER = 2;
    static final int LOOP_NUMBER = 200;
    public static void main(String[] args) {
        ThreadSafe test = new ThreadSafeSubClass();
		
        for (int i = 0; i < THREAD_NUMBER; i++) {
            new Thread(() -> {
                test.method1(LOOP_NUMBER);
            }, "Thread" + (i+1)).start();
        }
    }
}
class ThreadSafe {
    public final void method1(int loopNumber) {
        ArrayList<String> list = new ArrayList<>();
        for (int i = 0; i < loopNumber; i++) {
            method2(list);
            method3(list);
        }
    }

    public void method2(ArrayList<String> list) {
        list.add("1");
    }

    private void method3(ArrayList<String> list) {
        System.out.println(1);
        list.remove(0);
    }
}
```

- 如果方法 3 是 public, 子类可以进行改写, 此时的 method3 又会新建一个线程与其他线程竞争 list 这个局部变量, 造成线程安全问题.

```java
public class TestThreadSafe {

    static final int THREAD_NUMBER = 2;
    static final int LOOP_NUMBER = 200;
    public static void main(String[] args) {
        ThreadSafeSubClass test = new ThreadSafeSubClass();
		
        for (int i = 0; i < THREAD_NUMBER; i++) {
            new Thread(() -> {
                test.method1(LOOP_NUMBER);
            }, "Thread" + (i+1)).start();
        }
    }
}

class ThreadSafe {
    public void method1(int loopNumber) {
        ArrayList<String> list = new ArrayList<>();
        for (int i = 0; i < loopNumber; i++) {
            method2(list);
            method3(list);
        }
    }

    public void method2(ArrayList<String> list) {
        list.add("1");
    }

    public void method3(ArrayList<String> list) {
        System.out.println(1);
        list.remove(0);
    }
}

class ThreadSafeSubClass extends ThreadSafe{
//    @Override
    public void method3(ArrayList<String> list) {
        System.out.println(2);
        new Thread(() -> {
            list.remove(0);
        }).start();
    }
}
```

更改:

```java
public class TestThreadSafe {

    static final int THREAD_NUMBER = 2;
    static final int LOOP_NUMBER = 200;
    public static void main(String[] args) {
        ThreadSafeSubClass test = new ThreadSafeSubClass();
		
        for (int i = 0; i < THREAD_NUMBER; i++) {
            new Thread(() -> {
                test.method1(LOOP_NUMBER);
            }, "Thread" + (i+1)).start();
        }
    }
}

class ThreadSafe {
	//改成final方法, 不支持改写
    public final void method1(int loopNumber) {
        ArrayList<String> list = new ArrayList<>();
        for (int i = 0; i < loopNumber; i++) {
            method2(list);
            method3(list);
        }
    }

    public void method2(ArrayList<String> list) {
        list.add("1");
    }
	//改成private, 不能被重写
    private void method3(ArrayList<String> list) {
        System.out.println(1);
        list.remove(0);
    }
}

class ThreadSafeSubClass extends ThreadSafe{
//    @Override
    public void method3(ArrayList<String> list) {
        System.out.println(2);
        new Thread(() -> {
            list.remove(0);
        }).start();
    }
}
```

- 从这个例子可以看出 private 或 final 提供【安全】的意义所在，请体会开闭原则中的【闭】: 加强线程安全

#### 常见线程安全类

HashTable 的 put 是有 syconized 修饰的

> 指: 多个线程调用他们同一个实例的方法时, 是线程安全的, 也可以理解为**他们的每个方法是原子的**, 但注意, **他们的多个方法的组合不是原子的**

比如:

```java
Hashtable table = new Hashtable();
// 线程1，线程2 同时得到null, 都put了, 结果两个结果覆盖了.
if( table.get("key") == null) {
	table.put("key", value);
}
```

- String
- Integer
- StringBuffer
- Random
- Vector
- Hashtable
- java.util.concurrent 包下的类 JUC

##### 不可变线程安全类

String、Integer 等都是不可变类，因为其内部的状态不可以改变，因此它们的方法都是线程安全的
String 有 replace，substring 又是如何保证线程安全
- replace, substring: 创建了一个新的对象 (没有共享), 没有改动对象的属性.

#### 例子判断

- 例 1

```java
public class MyServlet extends HttpServlet {  
	// 是否安全？  否, table是
	Map<String,Object> map = new HashMap<>();  
	// 是否安全？  是
	String S1 = "...";  
	// 是否安全？  是
	final String S2 = "...";  
	// 是否安全？  否
	Date D1 = new Date();  
	// 是否安全？  是
	final Date D2 = new Date();
```

- 例 2

```java
public class MyServlet extends HttpServlet {
    // 是否安全？ 否
    private UserService userService = new UserServiceImpl();
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        userService.update(...);
    }
}
public class UserServiceImpl implements UserService {
    // 记录调用次数
    private int count = 0;
    public void update() {
        // ...
        count++;
    }
}
```

- 例 3

```java
@Slf4j
@Aspect
@Component
public class MyAspect {
    // 是否安全？ 否, 单例会发生共享: 解决方法, 处理成环绕通知, 把开始时间和结束时间都处理成环绕通知中的局部变量, 就能保证线程安全.
    private long start = 0L;
    @Before("execution(* *(..))")
    public void before() {
        start = System.nanoTime();
    }
    @After("execution(* *(..))")
    public void after() {
        long end = System.nanoTime();
        System.out.println("cost time:" + (end-start));
    }
}
```

- 例 4

```java
public class MyServlet extends HttpServlet {
    // 是否安全 没有可以修改的东西
    private UserService userService = new UserServiceImpl();
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        userService.update(...);
    }
}
public class UserServiceImpl implements UserService {
    // 是否安全 里面没有可更改的东西
    private UserDao userDao = new UserDaoImpl();
    public void update() {
        userDao.update();
    }
}
public class UserDaoImpl implements UserDao {
    public void update() {
        String sql = "update user set password = ? where username = ?";
        // 是否安全 安全, 没有成员变量
        try (Connection conn = DriverManager.getConnection("","","")){
            // ...
        } catch (Exception e) {
            // ...
        }
    }
}
```

- 例 5

```java
public class MyServlet extends HttpServlet {
    // 是否安全 不是
    private UserService userService = new UserServiceImpl();
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        userService.update(...);
    }
}
public class UserServiceImpl implements UserService {
    // 是否安全 不是
    private UserDao userDao = new UserDaoImpl();
    public void update() {
        userDao.update();
    }
}
public class UserDaoImpl implements UserDao {
    // 是否安全 会被共享, 但是不是线程安全
    private Connection conn = null;
    public void update() throws SQLException {
        String sql = "update user set password = ? where username = ?";
        conn = DriverManager.getConnection("","","");
        // ...
        conn.close();
    }
}
```

- 例 6

```java
public class MyServlet extends HttpServlet {
    // 是否安全
    private UserService userService = new UserServiceImpl();
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        userService.update(...);
    }
}
public class UserServiceImpl implements UserService {
    ⚠️安全, 每次都会新创建一个
	public void update() {
        UserDao userDao = new UserDaoImpl();
        userDao.update();
    }
}
public class UserDaoImpl implements UserDao {
    // 是否安全
    private Connection = null;
    public void update() throws SQLException {
        String sql = "update user set password = ? where username = ?";
        conn = DriverManager.getConnection("","","");
        // ...
        conn.close();
    }
}
```

- 例 7

```java
public abstract class Test {
    public void bar() {
        // 是否安全 不安全, 带入到里面开了新线程产生了共享
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        foo(sdf);
    }
	//抽象类的方法行为不确定
    public abstract foo(SimpleDateFormat sdf);

    public static void main(String[] args) {
        new Test().bar();
    }

    public void foo(SimpleDateFormat sdf) {
        String dateStr = "1999-10-11 00:00:00";
        for (int i = 0; i < 20; i++) {
            new Thread(() -> {
                try {
                    sdf.parse(dateStr);
                } catch (ParseException e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }
}
```

- 思考:String 类为什么要设计成 final 的? 如果不设计成 final, 那么他的子类就有可能覆盖掉 String 的一些行为, 从而使其失去线程安全性.

- 例 8

```java
public abstract class Test {
    private static Integer i = 0;
    public static void main(String[] args) throws InterruptedException {
        List<Thread> list = new ArrayList<>();
        for (int j = 0; j < 2; j++) {
            Thread thread = new Thread(() -> {
                for (int k = 0; k < 5000; k++) {
                    synchronized (i) {
                        i++;
                    }
                }
            }, "" + j);
            list.add(thread);
        }
        list.stream().forEach(t -> t.start());
        list.stream().forEach(t -> {
            try {
                t.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        log.debug("{}", i);
    }
}
```

### 2.2.3 应用之互斥

- 悲观锁
- 乐观锁 (CAS)

### 2.2.4 两个练习

#### 买票

- 下面的代码会出现线程安全问题吗?

```java
@Slf4j(topic = "c.ExerciseSell")
public class ExerciseSell {
    public static void main(String[] args) throws InterruptedException {
        // 模拟多人买票
        TicketWindow window = new TicketWindow(1000);

        // 所有线程的集合
        List<Thread> threadList = new ArrayList<>();
        // 卖出的票数统计
        List<Integer> amountList = new Vector<>();
        for (int i = 0; i < 2000; i++) {
            Thread thread = new Thread(() -> {
                // 买票⚠️操作共享变量, 需要保护
                int amount = window.sell(random(5));
                // 统计买票数⚠️这里如果是ArrayList就需要考虑共享变量线程安全问题
                amountList.add(amount);
            });
            threadList.add(thread);
            thread.start();
        }

        for (Thread thread : threadList) {
            thread.join();
        }

        // 统计卖出的票数和剩余票数
        log.debug("余票：{}",window.getCount());
        log.debug("卖出的票数：{}", amountList.stream().mapToInt(i-> i).sum());
    }

    // Random 为线程安全
    static Random random = new Random();

    // 随机 1~5
    public static int random(int amount) {
        return random.nextInt(amount) + 1;
    }
}

// 售票窗口
class TicketWindow {
    private int count;

    public TicketWindow(int count) {
        this.count = count;
    }

    // 获取余票数量
    public int getCount() {
        return count;
    }

    // 售票
    public int sell(int amount) {
        if (this.count >= amount) {
            this.count -= amount;
            return amount;
        } else {
            return 0;
        }
    }
}
```

- 对 window 这个共享变量有读有写, 所以需要线程安全保护
	- sell 方法要用 sychonized 修饰
	- amountList 要用 Vector

#### 银行转账

```java
public class ExerciseTransfer {
    public static void main(String[] args) throws InterruptedException {
        Account a = new Account(1000);
        Account b = new Account(1000);
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                a.transfer(b, randomAmount());
            }
        }, "t1");
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                b.transfer(a, randomAmount());
            }
        }, "t2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        // 查看转账2000次后的总金额
        log.debug("total:{}", (a.getMoney() + b.getMoney()));
    }

    // Random 为线程安全
    static Random random = new Random();

    // 随机 1~100
    public static int randomAmount() {
        return random.nextInt(100) + 1;
    }
}

// 账户
class Account {
    private int money;

    public Account(int money) {
        this.money = money;
    }

    public int getMoney() {
        return money;
    }

    public void setMoney(int money) {
        this.money = money;
    }

    // 转账⚠️这里显然不对
	public void transfer(Account target, int amount) {
		if (this.money > amount) {
			this.setMoney(this.getMoney() - amount);
			target.setMoney(target.getMoney() + amount);
		}
	}
	//⚠️这样是不行地, 这样等于各加了自己的对象锁, 起不到保护的作用
	public synchronized void transfer(Account target, int amount) {
		if (this.money > amount) {
			this.setMoney(this.getMoney() - amount);
			target.setMoney(target.getMoney() + amount);
		}
	}
	//✅正确方式1:
	public void transfer(Account target, int amount) {
        synchronized(Account.class) {
            if (this.money >= amount) {
                this.setMoney(this.getMoney() - amount);
                target.setMoney(target.getMoney() + amount);
            }
        }
    }
	//✅正确方式2:但并不是一个高效的方法, 当许多账户都要使用共享对象时
	public static synchronized void transfer(Account target, int amount) {
		if (this.money >= amount) {
			this.setMoney(this.getMoney() - amount);
			target.setMoney(target.getMoney() + amount);
		}
    }
}

```

## 2.3 对象锁细节

### 2.3.1 Monitor

#### Monitor 原理

- 对象头介绍包含两部分 [[JVM宋红康_上篇06_Java对象和直接内存#问 对象头信息里面有哪些东西]]

	1. 运行时元数据 (Mark Word): 哈希值, GC 分代年龄, 锁状态标志, 线程持有的锁, 偏向线程 ID, 偏向时间戳
	2. 类型指针 (元数据指针 Klass Word): 指向类元数据 InstanceKlass, 确定该对象所属的类型, 如果是数组类型, 还需要记录数组的长度
    对象在内存中除对象头外的剩余内容
- 以 32 位虚拟机为例

![[附件/image/02_共享模型篇(待补完)-3.jpg]]

https://stackoverflow.com/questions/26357186/what-is-in-java-object-header

![[附件/image/02_共享模型篇(待补完)-4.jpg]]
- 原理: 从操作系统层面
   1. Monitor 被翻译为监视器或管程, 相当与一个**操作系统对象**
   2. 每个 Java 对象都可以关联一个 Monitor 对象，如果使用 synchronized 给对象上锁（重量级）之后，该对象头的 Mark Word 中就被设置指向 Monitor 对象的指针
   3. 过程:
	    1. 刚开始 Monitor 中 Owner 为 null
		1. 当 Thread-2 执行 synchronized(obj) 就会将 Monitor 的所有者 Owner 置为 Thread-2，Monitor 中只能有一个 **Owner**
		2. 在 Thread-2 上锁的过程中，如果 Thread-3，Thread-4，Thread-5 也来执行 synchronized(obj)，就会进入**EntryList BLOCKED**
		3. Thread-2 执行完同步代码块的内容，然后唤醒 EntryList 中等待的线程来竞争锁，竞争的时是非公平的
		4. 图中 WaitSet 中的 Thread-0，Thread-1 是之前获得过锁，但条件不满足进入 **WAITING** 状态的线程，后面讲 wait-notify 时会分析

- 注意:
	- synchronized 必须是进入同一个对象的 monitor 才有上述的效果
	- 不加 synchronized 的对象不会关联监视器，不遵从以上规则

#### wait/notify

##### 原理和使用

- 与 sleep 的区别
- 使用 wait/notify 的正确姿势

##### 模式之保护性暂停

##### 模式之生产者和消费者

#### park/unpark

- 深入理解线程状态

### 2.3.2 字节码解析 synchronized

先看一段简单代码:

```java
    static final Object lock = new Object();
    static int counter = 0;
    public static void main(String[] args) {
        synchronized (lock) {
            counter++;
        }
    }
```

对应的字节码:

```sh
0: getstatic #2 // <- lock引用 （synchronized开始）
3: dup
4: astore_1     // lock引用 -> slot 1
5: monitorenter // 将 lock对象 MarkWord 置为 Monitor 指针
6: getstatic #3 // <- i
9: iconst_1     // 准备常数 1
10: iadd        // +1
11: putstatic #3// -> i
14: aload_1     // <- lock引用
15: monitorexit // 将 lock对象 MarkWord 重置, 唤醒 EntryList
16: goto 24
19: astore_2    // e -> slot 2
20: aload_1     // <- lock引用
21: monitorexit // 将 lock对象 MarkWord 重置, 唤醒 EntryList
22: aload_2     // <- slot 2 (e)
23: athrow      // throw e
24: return

Exception table:
	from to target type
	6    16   19    any
	19   22   19    any
```

- 注意
	- 方法级别的 synchronized 不会在字节码指令中有所体现

### 2.3.3 sychronized 进阶原理

Monitor 是操作系统层面的锁, 如果一段竞争代码每次需要用到 Monitor 级别的锁对我们代码的性能影响很大

竞争的各种情况优化

#### 轻量锁

轻量级锁的使用场景：如果一个对象虽然有多线程要加锁，但加锁的时间是错开的（也就是没有竞争），那么可以使用轻量级锁来优化。

轻量级锁对使用者是透明的，即语法仍然是 synchronized

假设有两个方法同步块，利用同一个对象加锁

```java
    static final Object obj = new Object();
    public static void method1() {
        synchronized( obj ) {
            // 同步块 A
            method2();
        }
    }
    public static void method2() {
        synchronized( obj ) {
            // 同步块 B
        }
    }
```

- 过程
	- 创建锁记录（Lock Record）对象，每个线程都的栈帧都会包含一个锁记录的结构，内部可以存储锁定对象的 Mark Word

		![[附件/image/02_共享模型篇(待补完)-5.jpg]]

	- 让锁记录中 Object reference 指向锁对象，并尝试用 cas 替换 Object 的 Mark Word，将 Mark Word 的值存入锁记录
	- 如果 cas 替换成功，对象头中存储了 锁记录地址和状态 00 ，表示由该线程给对象加锁，这时图示如下

	- 如果 **cas 失败**，有两种情况
		- 如果是其它线程已经持有了该 Object 的轻量级锁，这时表明有竞争，进入锁膨胀过程
		- 如果是自己执行了 synchronized 锁重入，那么再添加一条 Lock Record 作为重入的计数

	![[附件/image/02_共享模型篇(待补完)-8.jpg]]
	- 当退出 synchronized 代码块（解锁时）如果**有取值为 null 的锁记录，表示有重入**，这时重置锁记录，表示重入计数减一

	- 当退出 synchronized 代码块（解锁时）锁记录的值不为 null，这时使用 cas 将 Mark Word 的值恢复给对象头
		- 成功，则解锁成功
		- 失败，说明轻量级锁进行了锁膨胀或已经升级为重量级锁，进入重量级锁解锁流程

#### 重量锁: 竞争产生锁膨胀

如果在尝试加轻量级锁的过程中，CAS 操作无法成功，这时一种情况就是有其它线程为此对象加上了轻量级锁（有竞争），这时需要进行锁膨胀，将轻量级锁变为重量级锁。

例:

```java
static Object obj = new Object();  
	public static void method1() {  
		synchronized( obj ) {  
		// 同步块  
	}  
}
```

- 当 Thread-1 进行轻量级加锁时，Thread-0 已经对该对象加了轻量级锁, 后两位 00

![[附件/image/02_共享模型篇(待补完)-10.jpg]]

- 这时 Thread-1 加轻量级锁失败，进入锁膨胀流程
	- 即为 Object 对象申请 Monitor 锁，让 Object 指向重量级锁地址, 后两位变为 10
	- 然后自己进入 Monitor 的 EntryList BLOCKED

![[附件/image/02_共享模型篇(待补完)-11.jpg]]

- 当 Thread-0 退出同步块解锁时，根据 Monitor 的地址使用 cas 将 Mark Word 的值恢复给对象头，失败。这时会进入重量级解锁流程，即按照 Monitor 地址找到 Monitor 对象，设置 Owner 为 null，唤醒 EntryList 中 BLOCKED 线程

#### 自旋优化

#### 偏向锁

#### 锁粗化 (prog)

- 锁粒度和粒度细分

#### 锁消除 (JIT)

#### 活跃性

- 死锁
	- 发生条件
	- 定位
- 活锁
- 锁饥饿

### 2.3.4 Reentranlock

#### 原理

- AQS() 原理 (sync 同步器)
- Reentranlock 原理

#### 可重入

#### 可打断

#### 锁超时

#### 公平锁

#### 条件变量

#### 模式之顺序控制

# 三. 共享模型之无锁 (CAS 和不可变)

## 3.1 CAS

- 问题: 取款
	- 解决方法 1: 加锁
	- 解决方法 2: CAS

### 3.1.1 CAS 与 volatile

#### Unsafe 类

- 底层方法
- CAS 操作

#### 慢动作分析

#### volatile

#### 为什么无锁的无锁效率高

#### CAS 特点

### 3.1.2 原子类

#### (1) 原子整数

- 1
- 2
- 3

#### (2) 原子引用

- 1
- 2
- 3
- ABA 问题
- 解决方法 (stampedReentranlock)

#### (3) 原子数组

- 1
- 2
- 3

### 3.1.3 字段更新器

### 3.1.4 原子累加器

#### 性能比较

#### 原理

- 原理之伪共享
- CAS 锁
- 应用之分治

## 3.2 不可变与无状态

- 日期转换的问题

### 3.2.1 不可变的思路

### 3.2.2 不可变的设计

#### final

- 原理

#### 保护性拷贝

### 模式之享元模式

## 3.3 Local

# 四. JUC 工具类

## 4.1 AQS->原子类

## 4.2 Reentrantlock

## 4.3 读写锁

### 4.3.1 作用用法

### 4.3.2 注意点

- 应用之缓存

### 4.3.3 读写锁原理

### 4.3.4 stampedLock

- 用法
- 缺点
	- 不支持条件变量
	- 不可重入

## 4.4 Semaphore(拦车杆)

### 作用

### 用法

### 应用

- 改进数据库连接池
- 限流 (guava)

## 4.5 Exchanger(prog)

## 4.6 CountDownLatch

- 作用
- 应用
	- 等待多人游戏
	- 等待多个线程远程调用完毕 (结合 Future)

## 4.7 CyclicBarrier

- 用法
- 与 CountDownLatch 的区别
- 注意点

## 4.8 线程安全集合类

总的来说, Java 的线程安全的集合类可以分为三类
- 遗留类
	- Vector
	- HashTable
- Collections 修饰的
- JUC 中线程安全的
	- ConCurrent 类
		- CAS 优化的
			- 弱一致性
				- 查询
				- 遍历
				- size
	- Blocking 类
		- 阻塞队列: LinkedBlockingQueue
		- 非阻塞队列: ConcurrentLinkedQueue
	- CopyOnWrite 类
		- 拷贝方式 (读多写少的情况)

### 4.8.1 Concurrent 类

#### (1) 应用之数单词

#### (2)JDK7 中 Hashmap 原理

- 原理
- JDK7 中扩容会引发的问题
- JDK8 中扩容会引发的问题

#### (3)ConcurrentHashMap

- JDK8
- JDK7

### 4.8.2 LinkedBlockingQueue 阻塞队列

- 阻塞原理

### 4.8.3 ConcurrentLinkedQueue 非阻塞队列

- 非阻塞原理
- 模仿写一个非阻塞队列

#### 4.8.4 CopyOnWriteArrayList

- 并发读, 读写分离
- 弱一致性
	- get 弱一致
	- 迭代弱一致
	- 并发度和一致性不可兼得

#### 4.8.5 SkipListMap(prog)
