---
date: 2024-09-07
mtime: 2024-10-15
---

# 八. StringTable 专题

**JVM 虚拟机**; **Java**

## 1. String 的基本特性

### 基本特性

![[附件/image/上篇08_StringTable(字符串常量表).jpg]]

### String 类在 jdk9 中的存储结构的变更

![[附件/image/上篇08_StringTable(字符串常量表)-1.jpg]]
![[附件/image/上篇08_StringTable(字符串常量表)-2.jpg]]
因为根据统计字符串中 latin 和 8859 的字符数较多, 而他们只占一个字节, 所以主张用 byte[] 替换了 char[]

- string: 代表不可变的字符序列。简称：不可变性。
    - 当对字符串重新赋值时，需要重写指定内存区域赋值，不能使用原有的 value 进行赋值。
    - 当对现有的字符串进行连接操作时，也需要重新指定内存区域赋值，不能使用原有的 value 进行赋值。
    - 当调用 string 的 replace() 方法修改指定字符或字符串时，也需要重新指定内存区域赋值，不能使用原有的 value 进行赋值。
- 通过字面量的方式（区别于 new) 给一个字符串赋值，此时的字符串值声明在字符串常量池中。

### StringTable 引入

字符串常量池的数据结构是 HashMap (数组 + 链表) 的结构 [[06_集合#6 Map接口]]

·字符串常量池中是不会存储相同内容的字符串的。

- String 的 string Pool 是一个固定大小的 Hashtable， 默认值大小长度是 1009。如果放进 string Pool 的 String 非常多， 就会造成 Hash 冲突严重，从而导致链表会很长，而链表长了后直接会造成的影响就是当调用 String.intern 时性能会大幅下降。
- 使用 -xx：StringTableSize 可设置 stringTable 的长度
- 在 jdk 6 中 String Table 是固定的， 就是 1009 的长度， 所以如果常量池中的字符串过多就会导致效率下降很快。String Table Size 设置没有要求
- 在 jdk 7 中， String Table 的长度默认值是 60013， String Table Size 设置没有要求
- Jdk 8 开始，设置 string Table 的长度的话， 1009 是可设置的最小值。

## 2. String 的内存分配

- 在 Java 语言中有 8 种基本数据类型和一种比较特殊的类型 string。这些类型为了使它们在运行过程中速度更快、更节省内存，都提供了一种常量池的概念。
- 常量池就类似一个 Java 系统级别提供的缓存。8 种基本数据类型的常量池都是系统协调的，String 类型的常量池比较特殊。它的主要使用方法有两种。
    - 直接使用双引号声明出来的 String 对象会直接存储在常量池中。

        √比如：string info="atguigu.com"；
    - 如果不是用双引号声明的 String 对象，可以使用 string 提供的 intern（）方法。这个后面重点谈

### jdk7 中的调整

- Java 6 及以前,字符串常量池存放在永久代。
- Java 7 中 oracle 的工程师对字符串池的逻辑做了很大的改变,即将字符串常量池的位置调整到 Java 堆内。
    - 所有的字符串都保存在堆 (Heap) 中,和其他普通对象一样,这样可以让你在进行调优应用时仅需要调整堆大小就可以了。
    - 字符串常量池概念原本使用得比较多,但是这个改动使得我们有足够的理由让我们重新考虑在 Java 7 中使用 string.intern().
- Java8 元空间,字符串常量在堆

![[附件/image/上篇08_StringTable(字符串常量表)-3.jpg]]
![[附件/image/上篇08_StringTable(字符串常量表)-4.jpg]]

### 为什么要调整

![[附件/image/上篇08_StringTable(字符串常量表)-5.jpg]]

1. 永久代默认比较小
2. 永久代中垃圾回收频次较低, 而字符串占用内存较高, 且需要垃圾回收, 所以移到堆中

## 3. String 的基本操作

![[附件/image/上篇08_StringTable(字符串常量表)-6.jpg]]
![[附件/image/上篇08_StringTable(字符串常量表)-7.jpg]]
![[附件/image/上篇08_StringTable(字符串常量表)-8.jpg]]

## 4. 字符串拼接操作

1. 常量与常量的拼接结果在常量池，原理是编译期优化中
2. 常量池中不会存在相同内容的常量。
3. 只要其中有一个是变量，结果就在堆中。变量拼接的原理是 stringBuilder
4. 如果拼接的结果调用 intern() 方法，则主动将常量池中还没有的字符串对象放入池中，并返回此对象地址

- 举例 1 常量与常量拼接

![[附件/image/上篇08_StringTable(字符串常量表)-9.jpg]]

- 举例 2 常量添加变量
![[附件/image/上篇08_StringTable(字符串常量表)-10.jpg]]
- 举例 3 final 修饰符修饰的字符串视为常量
![[附件/image/上篇08_StringTable(字符串常量表)-11.jpg]]

- 使用 StringBuider 的好处 注意改进空间

![[附件/image/上篇08_StringTable(字符串常量表)-12.jpg]]

## 5. intern() 的使用

![[附件/image/上篇08_StringTable(字符串常量表)-13.jpg]]

如果不是用双引号声明的 String 对象，可以使用 string 提供的 intern 方法：intern 方法会从字符申常量池中查询当前字符是否存在，若不存在就会将当前字符串放入常量池中。
- 比如：String myInfo=new String("I love atguigu").intern():
-
也就是说，如果在任意字符串上调用 String.

intern 方法，那么其返回结果所指向的那个类实例，必须和直接以常量形式出现的字符串实例完全相同。因此，下列表达式的值必定是 true:

("a"+"b"+"c").intern()= = "abc"

通俗点讲，Interned String 就是确保字符非在内存里只有一份拷贝，这样可以节约内存空间，加快字符串操作任务的执行速度。注意，这个值会被存放在字符串内部池 (String Intern Pool）

**面试题 JVM**

```java
public class StringIntern1 {
    public static void main(String[] args) {
        String s = new String("1");
        s.intern();

        String s2 = "1";
        System.out.println(s == s2); //

        String s3 = new String("1") + new String("1");
        s3.intern();

        String s4 = "11";
        System.out.println(s3 == s4); //
    }
}
```

![[附件/image/上篇08_StringTable(字符串常量表)-14.jpg]]

jdk6
![[附件/image/上篇08_StringTable(字符串常量表)-15.jpg]]
jdk7/8
![[附件/image/上篇08_StringTable(字符串常量表)-16.jpg]]
- 注意:

```java
/**
 * 题目：
 * new String("ab")会创建几个对象？看字节码，就知道是两个。
 *     一个对象是：new关键字在堆空间创建的
 *     另一个对象是：字符串常量池中的对象"ab"。 字节码指令：ldc
 *
 *
 * 思考：
 * new String("a") + new String("b")呢？
 *  对象1：new StringBuilder()
 *  对象2： new String("a")
 *  对象3： 常量池中的"a"
 *  对象4： new String("b")
 *  对象5： 常量池中的"b"
 *
 *  深入剖析： StringBuilder的toString():
 *      对象6 ：new String("ab")
 *       强调一下，toString()的调用，在字符串常量池中，没有生成"ab",没有ldc
 *
 */
public class StringNewTest {
    public static void main(String[] args) {
//        String str = new String("ab");

        String str = new String("a") + new String("b");
    }
}

```

```java

s = new String("a") + new String("b")

实际上是一个StringBuider调用一个toString方法, 即 

(1) StringBuider append "a" append "b"

(2) 调用to String()方法, 底层实现是, new String("ab"), 被 s 指向;

此时, 字符串常量池中是没有 "ab" 的


****再深入理解jdk6 和 jdk7 的区别****

jdk6 , 因为字符串常量池不在堆空间中(在运行时数据区里面), 所以相当于和对象不在同一个空间, new String("ab").intern 时, 实际上是在字符串常量池中创建了一个"ab"(实打实的)

jdk7, 因为字符串常量池移到了堆空间中,则与对象在同一片空间, 考虑空间节省的问题, new String("ab")时, 字符串常量池创建的"ab"的地址实际上是指向这个 new 对象的地址的.

```

区别

总结 String 的 intern() 方法的使用

- jdk1.6 中, 将这个字符串对象尝试放入串池.
    - 如果串池中有,则并不会放入。返回已有的串池中的对象的地址
    - 如果没有,会把此对象复制一份,放入串池,并返回串池中的对象地址
- Jdk1.7 起,将这个字符串对象尝试放入串池。
    - 如果串池中有,则并不会放入。返回已有的串池中的对象的地址
    - 如果没有,则会把对象的引用地址复制一份,放入串池,并返回串池中的引用地址

![[附件/image/上篇08_StringTable(字符串常量表)-17.jpg]]

**面试题 JVM**
![[附件/image/上篇08_StringTable(字符串常量表)-18.jpg]]
![[附件/image/上篇08_StringTable(字符串常量表)-19.jpg]]
因为是字符串的拼接, 所以会创建一个 StringBuider 来完成这个拼接 (只要涉及字符串变量的拼接, jvm 都会在底层新建一个 StringBuider 来完成这个工作)
StringBuider append 了 "a" 和 "b" 然后这个 StringBuider 再调用 to String() 方法, 这个方法底层是一个 new String("ab")
注意, 这个时候字符串常量池中仍然没有 "ab"

### intern 的效率测试

![[附件/image/上篇08_StringTable(字符串常量表)-20.jpg]]

使用 intern() 测试执行效率: 空间使用上

结论: 对于程序中大量存在的字符串,尤其其中存在很多重复字符串时,使用 intern() 可以节省内存空间

## 6. StringTable 的垃圾回收

![[附件/image/上篇08_StringTable(字符串常量表)-21.jpg]]

## 7.G1 的 String 去重操作

![[附件/image/上篇08_StringTable(字符串常量表)-22.jpg]]

- 背景: 对许多 Java 应用 (有大的也有小的) 做的测试得出以下结果:
    - 堆存活数据集合里面 string 对象占了 25%
    - 堆存活数据集合里面重复的 string 对象有 13.5%
    - String 对象的平均长度是 45
- 许多大规模的 Java 应用的瓶颈在于内存,测试表明,在这些类型的应用里面, Java 堆中存活的数据集合差不多 25% 是 String 对象。更进一步,这里面差不多一半 String 对象是重复的,重复的意思是说:`string1.equals (string2)=true`,堆上存在重复的 string 对象必然是一种内存的浪费。这个项目将在 G1 垃圾收集器中实现自动持续对重复的 string 对象进行去重,这样就能避免浪费内存.

实现
- 当垃圾收集器工作的时候,会访问堆上存活的对象。对每一个访问的对象都会检查是否是候选的要去重的 String 对象。
- 如果是,把这个对象的一个引用插入到队列中等待后续的处理。一个去重的线程在后台运行,处理这个队列,处理队列的一个元素意味着从队列删除这个元素,然后尝试去重它引的 String 对象。
- 使用一个 hashtable 来记录所有的被 String 对象使用的不重复的 char 数组当去重的时候,会查这个 hashtable,来看堆上是否已经存在一个一模一样的 char 数组.
- 如果存在, String 对象会被调整引用那个数组,释放对原来的数组的引用,最终会被垃圾收集器回收掉。
- 如果查找失败, char 数组会被插入到 hashtable,这样以后的时候就可以共享这个数组了.

命令行选项
- UseStringDeduplication(bool) ：开启 String 去重， 默认是不开启的， 需要手动开启。

- PrintStringDeduplicationStatistics(bool) ：打印详细的去重统计信息

- StringDeduplicationAgeThreshold(uint x) ：达到这个年龄的 String 对象被认为是去重的候选对象

新思路: 将堆空间中重复的字符串 GC
- 虚拟机指令: -XX:+PrintStringTableStatistics -XX:+PrintGCDetails
- 虚拟机指令: +UseStringDeduplication 开启 String 去重
————————————————
