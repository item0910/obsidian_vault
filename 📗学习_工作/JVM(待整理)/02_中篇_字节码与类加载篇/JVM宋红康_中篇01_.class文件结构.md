---
date: 2024-08-24
mtime: 2024-10-15
---

# 一. .class 文件结构

**JVM 虚拟机**; **Java**

## 1. 概述

### 字节码文件的跨平台性

![[附件/image/中篇01_.class文件结构.jpg]]
![[附件/image/中篇01_.class文件结构-1.jpg]]
![[附件/image/中篇01_.class文件结构-2.jpg]]

### Java 的前端编译器

![[附件/image/中篇01_.class文件结构-3.jpg]]
![[附件/image/中篇01_.class文件结构-4.jpg]]

### 透过字节码指令看代码细节

![[附件/image/中篇01_.class文件结构-5.jpg]]
- 程序 1
![[附件/image/中篇01_.class文件结构-6.jpg]]

程序 1 内部解答:

![[附件/image/中篇01_.class文件结构-7.jpg]]

![[附件/image/中篇01_.class文件结构-8.jpg]]
- 程序 1 分析:

	Integer 变量在赋值的时候, 内部执行了一个 valueof 方法, 该方法内有一个数组, 该数组存放着 [-128, 127] (内部是一个 cache 数组) 个数字的值, 然后判断需要赋值的数字的大小, 如果需要赋值的 Integer 在这个范围内, 则从这个 cache 数组中直接取出赋值.
	如果需要赋值的变量数值超过了这个范围, 则会 new 一个 Integer 来完成赋值. 所以该题结果为 true(Integer -> int 有一个拆箱的过程 ); true; false

程序 2 参考 StringTable 中的字符串拼接 ([[JVM宋红康_上篇08_StringTable(字符串常量表)#4 字符串拼接操作]])
![[附件/image/中篇01_.class文件结构-9.jpg]]

程序 3
![[附件/image/中篇01_.class文件结构-10.jpg]]

过程描述:
![[附件/image/中篇01_.class文件结构-11.jpg]]

附: 类中成员变量的赋值过程
![[附件/image/中篇01_.class文件结构-12.jpg]]

## 2. 虚拟机的基石: .class 文件

### 解读.class 文件

- 二进制解读
![[附件/image/中篇01_.class文件结构-13.jpg]]
- javap 反解析工具 (java 自带)
- 使用 IDEA 插件
![[附件/image/中篇01_.class文件结构-14.jpg]]

## 3. Class 文件结构 (按先后顺序)

![[附件/image/中篇01_.class文件结构-15.jpg]]
![[附件/image/中篇01_.class文件结构-16.jpg]]
![[附件/image/中篇01_.class文件结构-17.jpg]]
![[附件/image/中篇01_.class文件结构-18.jpg]]
![[附件/image/中篇01_.class文件结构-19.jpg]]
![[附件/image/中篇01_.class文件结构-20.jpg]]

### 3.1 魔数

![[附件/image/中篇01_.class文件结构-21.jpg]]

### 3.2 .class 文件的 JDK 版本号

![[附件/image/中篇01_.class文件结构-22.jpg]]
![[附件/image/中篇01_.class文件结构-23.jpg]]

### 3.3 常量池: 存放所有常量

![[附件/image/中篇01_.class文件结构-24.jpg]]
![[附件/image/中篇01_.class文件结构-25.jpg]]

#### 常量池计数器 -- 记录常量池常量的数量

![[附件/image/中篇01_.class文件结构-26.jpg]]

#### 常量池表

![[附件/image/中篇01_.class文件结构-27.jpg]]
![[附件/image/中篇01_.class文件结构-28.jpg]]

##### 字面量和符号引用

![[附件/image/中篇01_.class文件结构-29.jpg]]
![[附件/image/中篇01_.class文件结构-30.jpg]]
![[附件/image/中篇01_.class文件结构-31.jpg]]

##### 常量类型和结构

![[附件/image/中篇01_.class文件结构-32.jpg]]

![[附件/image/中篇01_.class文件结构-33.jpg]]
![[附件/image/中篇01_.class文件结构-34.jpg]]
![[附件/image/中篇01_.class文件结构-35.jpg]]
![[附件/image/中篇01_.class文件结构-36.jpg]]
![[附件/image/中篇01_.class文件结构-37.jpg]]
![[附件/image/中篇01_.class文件结构-38.jpg]]

### 3.4 访问标识

![[附件/image/中篇01_.class文件结构-39.jpg]]
![[附件/image/中篇01_.class文件结构-40.jpg]]

### 3.5 类索引 父类索引 接口索引集合

![[附件/image/中篇01_.class文件结构-41.jpg]]
![[附件/image/中篇01_.class文件结构-42.jpg]]

### 3.6 字段表集合

![[附件/image/中篇01_.class文件结构-43.jpg]]
![[附件/image/中篇01_.class文件结构-44.jpg]]
![[附件/image/中篇01_.class文件结构-45.jpg]]
![[附件/image/中篇01_.class文件结构-46.jpg]]
![[附件/image/中篇01_.class文件结构-47.jpg]]
![[附件/image/中篇01_.class文件结构-48.jpg]]
![[附件/image/中篇01_.class文件结构-49.jpg]]
![[附件/image/中篇01_.class文件结构-50.jpg]]

### 3.7 方法表集合

![[附件/image/中篇01_.class文件结构-51.jpg]]
![[附件/image/中篇01_.class文件结构-52.jpg]]
![[附件/image/中篇01_.class文件结构-53.jpg]]

### 3.8 属性表集合

![[附件/image/中篇01_.class文件结构-54.jpg]]
![[附件/image/中篇01_.class文件结构-55.jpg]]
![[附件/image/中篇01_.class文件结构-56.jpg]]
![[附件/image/中篇01_.class文件结构-57.jpg]]
![[附件/image/中篇01_.class文件结构-58.jpg]]
![[附件/image/中篇01_.class文件结构-59.jpg]]
![[附件/image/中篇01_.class文件结构-60.jpg]]
![[附件/image/中篇01_.class文件结构-61.jpg]]
![[附件/image/中篇01_.class文件结构-62.jpg]]
![[附件/image/中篇01_.class文件结构-63.jpg]]
![[附件/image/中篇01_.class文件结构-64.jpg]]
![[附件/image/中篇01_.class文件结构-65.jpg]]
![[附件/image/中篇01_.class文件结构-66.jpg]]

### 小结

![[附件/image/中篇01_.class文件结构-67.jpg]]

## 4. 使用 javap 指令解析.class 文件

![[附件/image/中篇01_.class文件结构-68.jpg]]

### 4.1 解析字节码的作用

![[附件/image/中篇01_.class文件结构-69.jpg]]

### 4.2 javac -g 操作

![[附件/image/中篇01_.class文件结构-70.jpg]]

### 4.3 javap 的用法

![[附件/image/中篇01_.class文件结构.jpeg]]
![[附件/image/中篇01_.class文件结构-1.jpeg]]
![[附件/image/中篇01_.class文件结构-2.jpeg]]
注意：①-v 相当于 -c -l ②-v 也不会输出私有的字段、方法等信息，所以如果想输出私有的信息，那需要在 -v 后面加上 -p 才行
所以常用 `javap -v -p` 指令

### 4.4 使用举例

1、代码：

```java
public class JavapTest {
    private int num;
    boolean flag;
    protected char gender;
    public String info;

    public static final int COUNTS = 1;
    static {
        String url = "www.atguigu.com";
    }
    {
        info = "java";
    }
    public JavapTest() {
    
    }
    private JavapTest(boolean falg) {
        this.flag = flag;
    }
    private void methodPrivate() {
    
    }
    int getNum(int i) {
        return num + i;
    }
    protected char showGender() {
        return gender;
    }
    public void showInfo() {
        int i = 100;
        System.out.println(info + i);
    }
}
```

2、字节码文件分析：

```console
Classfile /C:/Users/mingming/Desktop/JavapTest.class   // 字节码文件所属的路径
Last modified 2021-2-24; size 1393 bytes   // 最后修改时间，字节码文件的大小
MD5 checksum 2c764244fa3a95bfb346c9e416a7a3f6   // MD5散列值
Compiled from "JavapTest.java"   // 源文件的名称
public class io.renren.JavapTest
minor version: 0   // 副版本
major version: 52   // 主版本
flags: ACC_PUBLIC, ACC_SUPER   // 访问标识
```

---

**常量池**

---

```console
Constant pool:
   #1 = Methodref          #16.#48        // java/lang/Object."<init>":()V
   #2 = String             #49            // java
   #3 = Fieldref           #15.#50        // io/renren/JavapTest.info:Ljava/lang/String;
   #4 = Fieldref           #15.#51        // io/renren/JavapTest.flag:Z
   #5 = Fieldref           #15.#52        // io/renren/JavapTest.num:I
   #6 = Fieldref           #15.#53        // io/renren/JavapTest.gender:C
   #7 = Fieldref           #54.#55        // java/lang/System.out:Ljava/io/PrintStream;
   #8 = Class              #56            // java/lang/StringBuilder
   #9 = Methodref          #8.#48         // java/lang/StringBuilder."<init>":()V
  #10 = Methodref          #8.#57         // java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
  #11 = Methodref          #8.#58         // java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
  #12 = Methodref          #8.#59         // java/lang/StringBuilder.toString:()Ljava/lang/String;
  #13 = Methodref          #60.#61        // java/io/PrintStream.println:(Ljava/lang/String;)V
  #14 = String             #62            // www.atguigu.com
  #15 = Class              #63            // io/renren/JavapTest
  #16 = Class              #64            // java/lang/Object
  #17 = Utf8               num
  #18 = Utf8               I
  #19 = Utf8               flag
  #20 = Utf8               Z
  #21 = Utf8               gender
  #22 = Utf8               C
  #23 = Utf8               info
  #24 = Utf8               Ljava/lang/String;
  #25 = Utf8               COUNTS
  #26 = Utf8               ConstantValue
  #27 = Integer            1
  #28 = Utf8               <init>
  #29 = Utf8               ()V
  #30 = Utf8               Code
  #31 = Utf8               LineNumberTable
  #32 = Utf8               LocalVariableTable
  #33 = Utf8               this
  #34 = Utf8               Lio/renren/JavapTest;
  #35 = Utf8               (Z)V
  #36 = Utf8               falg
  #37 = Utf8               MethodParameters
  #38 = Utf8               methodPrivate
  #39 = Utf8               getNum
  #40 = Utf8               (I)I
  #41 = Utf8               i
  #42 = Utf8               showGender
  #43 = Utf8               ()C
  #44 = Utf8               showInfo
  #45 = Utf8               <clinit>
  #46 = Utf8               SourceFile
  #47 = Utf8               JavapTest.java
  #48 = NameAndType        #28:#29        // "<init>":()V
  #49 = Utf8               java
  #50 = NameAndType        #23:#24        // info:Ljava/lang/String;
  #51 = NameAndType        #19:#20        // flag:Z
  #52 = NameAndType        #17:#18        // num:I
  #53 = NameAndType        #21:#22        // gender:C
  #54 = Class              #65            // java/lang/System
  #55 = NameAndType        #66:#67        // out:Ljava/io/PrintStream;
  #56 = Utf8               java/lang/StringBuilder
  #57 = NameAndType        #68:#69        // append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
  #58 = NameAndType        #68:#70        // append:(I)Ljava/lang/StringBuilder;
  #59 = NameAndType        #71:#72        // toString:()Ljava/lang/String;
  #60 = Class              #73            // java/io/PrintStream
  #61 = NameAndType        #74:#75        // println:(Ljava/lang/String;)V
  #62 = Utf8               www.atguigu.com
  #63 = Utf8               io/renren/JavapTest
  #64 = Utf8               java/lang/Object
  #65 = Utf8               java/lang/System
  #66 = Utf8               out
  #67 = Utf8               Ljava/io/PrintStream;
  #68 = Utf8               append
  #69 = Utf8               (Ljava/lang/String;)Ljava/lang/StringBuilder;
  #70 = Utf8               (I)Ljava/lang/StringBuilder;
  #71 = Utf8               toString
  #72 = Utf8               ()Ljava/lang/String;
  #73 = Utf8               java/io/PrintStream
  #74 = Utf8               println
  #75 = Utf8               (Ljava/lang/String;)V
```

---

**字段表集合的信息**

---

```console
{
  private int num;   // 字段名
    descriptor: I   // 字段表集合的信息
    flags: ACC_PRIVATE   // 字段的访问标识

  boolean flag;
    descriptor: Z
    flags:

  protected char gender;
    descriptor: C
    flags: ACC_PROTECTED

  public java.lang.String info;
    descriptor: Ljava/lang/String;
    flags: ACC_PUBLIC

  public static final int COUNTS;
    descriptor: I
    flags: ACC_PUBLIC, ACC_STATIC, ACC_FINAL
    ConstantValue: int 1   // 常量字段的属性：ConstantValue
```

---

**方法表集合的信息**

---

```console
  public io.renren.JavapTest();   // 无参构造器方法信息
    descriptor: ()V
    flags: ACC_PUBLIC
    Code:
      stack=2, locals=1, args_size=1
         0: aload_0
         1: invokespecial #1                  // Method java/lang/Object."<init>":()V
         4: aload_0
         5: ldc           #2                  // String java
         7: putfield      #3                  // Field info:Ljava/lang/String;
        10: return
      LineNumberTable:
        line 16: 0
        line 14: 4
        line 18: 10
      LocalVariableTable:
        Start  Length  Slot  Name   Signature
            0      11     0  this   Lio/renren/JavapTest;

  private io.renren.JavapTest(boolean);   // 单个参数构造器方法信息
    descriptor: (Z)V
    flags: ACC_PRIVATE
    Code:
      stack=2, locals=2, args_size=2
         0: aload_0
         1: invokespecial #1                  // Method java/lang/Object."<init>":()V
         4: aload_0
         5: ldc           #2                  // String java
         7: putfield      #3                  // Field info:Ljava/lang/String;
        10: aload_0
        11: aload_0
        12: getfield      #4                  // Field flag:Z
        15: putfield      #4                  // Field flag:Z
        18: return
      LineNumberTable:
        line 19: 0
        line 14: 4
        line 20: 10
        line 21: 18
      LocalVariableTable:
        Start  Length  Slot  Name   Signature
            0      19     0  this   Lio/renren/JavapTest;
            0      19     1  falg   Z
    MethodParameters:
      Name                           Flags
      falg

  private void methodPrivate();
    descriptor: ()V
    flags: ACC_PRIVATE
    Code:
      stack=0, locals=1, args_size=1
         0: return
      LineNumberTable:
        line 24: 0
      LocalVariableTable:
        Start  Length  Slot  Name   Signature
            0       1     0  this   Lio/renren/JavapTest;

  int getNum(int);
    descriptor: (I)I
    flags:
    Code:
      stack=2, locals=2, args_size=2
         0: aload_0
         1: getfield      #5                  // Field num:I
         4: iload_1
         5: iadd
         6: ireturn
      LineNumberTable:
        line 26: 0
      LocalVariableTable:
        Start  Length  Slot  Name   Signature
            0       7     0  this   Lio/renren/JavapTest;
            0       7     1     i   I
    MethodParameters:
      Name                           Flags
      i

  protected char showGender();
    descriptor: ()C
    flags: ACC_PROTECTED
    Code:
      stack=1, locals=1, args_size=1
         0: aload_0
         1: getfield      #6                  // Field gender:C
         4: ireturn
      LineNumberTable:
        line 29: 0
      LocalVariableTable:
        Start  Length  Slot  Name   Signature
            0       5     0  this   Lio/renren/JavapTest;

  public void showInfo();
    descriptor: ()V   // 方法的描述符：方法的形参列表、返回值类型
    flags: ACC_PUBLIC   // 方法的访问标识
    Code:   // 方法的Code属性
      stack=3, locals=2, args_size=1   // stack：操作数栈的最大深度   locals：局部变量表的长度   args_size：方法接受参数的个数
// 偏移量  操作码   操作数
         0: bipush        100
         2: istore_1
         3: getstatic     #7                  // Field java/lang/System.out:Ljava/io/PrintStream;
         6: new           #8                  // class java/lang/StringBuilder
         9: dup
        10: invokespecial #9                  // Method java/lang/StringBuilder."<init>":()V
        13: aload_0
        14: getfield      #3                  // Field info:Ljava/lang/String;
        17: invokevirtual #10                 // Method java/lang/StringBuilder.append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
        20: iload_1
        21: invokevirtual #11                 // Method java/lang/StringBuilder.append:(I)Ljava/lang/StringBuilder;
        24: invokevirtual #12                 // Method java/lang/StringBuilder.toString:()Ljava/lang/String;
        27: invokevirtual #13                 // Method java/io/PrintStream.println:(Ljava/lang/String;)V
        30: return
     // 行号表：指明字节码指令的偏移量与java源代码中代码的行号的一一对应关系
      LineNumberTable:
        line 32: 0
        line 33: 3
        line 34: 30
     // 局部变量表：描述内部局部变量的相关信息
      LocalVariableTable:
        Start  Length  Slot  Name   Signature
            0      31     0  this   Lio/renren/JavapTest;
            3      28     1     i   I

  static {};
    descriptor: ()V
    flags: ACC_STATIC
    Code:
      stack=1, locals=1, args_size=0
         0: ldc           #14                 // String www.atguigu.com
         2: astore_0
         3: return
      LineNumberTable:
        line 11: 0
        line 12: 3
      LocalVariableTable:
        Start  Length  Slot  Name   Signature
}
SourceFile: "JavapTest.java"   //附加属性：指明当前字节码文件对应的源程序文件名
```

3、jclasslib 展示的内容：
![](附件/image/JVM宋红康_中篇01_.class文件结构-1695638317542.jpeg)

### 4.5 总结

![[附件/image/中篇01_.class文件结构-71.jpg]]

————————————————
