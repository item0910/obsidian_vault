---
date: 2024-08-24
mtime: 2024-12-10
---

# 二. 类加载子系统

**JVM 虚拟机**; **Java**

## 1. 类加载子系统的作用

![[附件/image/上篇02_类加载子系统.jpg]]
[[JVM宋红康_中篇01_.class文件结构]]

[[JVM宋红康_上篇05_方法区]]

[[JVM宋红康_上篇07_执行引擎]]

## 2. 类的加载过程

### 验证流程

![[附件/image/上篇02_类加载子系统-1.jpg]]

### 加载:

- 加载:
	1. 通过一个类的全限定名获取定义此类的二进制字节流
	2. 将这个字节流所代表的静态存储结构转化为方法区的运行时数据结构
	3. 在内存中生成一个代表这个类的 java.lang.Class 对象, 作为方法区这个类的各种数据的访问入口
> - 补充, 加载 .class 文件的方式
> 	- 从本地系统中直接加载
> 	- 通过网络获取，典型场景：Web Applet
> 	- 从 zip 压缩包中读取，成为日后 jar、war 格式的基础
> 	- 运行时计算生成，使用最多的是：动态代理技术
> 	- 由其他文件生成，典型场景：JSP 应用
> 	- 从专有数据库中提取.c1ass 文件，比较少见
> 	- 从加密文件中获取，典型的防 class 文件被反编译的保护措施

### 连接

>验证 (Verify) :

- 目的在子确保 Class 文件的字节流中包含信息符合当前虚拟机要求,保证被加载类的正确性,不会危害虚拟机自身安全。

- 主要包括四种验证,文件格式验证,元数据验证,宇节码验证,符号引用验证。

>准备 (Prepare) :

- 为类变量分配内存并且设置该类变量的默认初始值,即零值。

- 这里不包含用 final 修饰的 static,因为 final 在编译的时候就会分配了,准备阶段会显式初始化；

- 这里不会为实例变量分配初始化,类变量会分配在方法区中,而实例变量是会随着对象一起分配到 Java 堆中。

>解析 (Resolve):

- 将常量池内的符号引用转换为直接引用的过程。

- 事实上,解析操作往往会伴随着 JVM 在执行完初始化之后再执行。

- 符号引用就是一组符号来描述所引用的目标。符号引用的字面量形式明确定义在《java 虚拟机规范》的 Class 文件格式中。直接引用就是直接指向目标的指针、相对偏移量或一个间接定位到目标的句柄

- 解析动作主要针对类或接口、字段、类方法、接口方法、方法类型等。对应常量池中的 CONSTANT_Class_info, CONSTANT_Fieldref_info, CONSTANT_Methodref_info 等

### 初始化

初始化阶段就是执行类构造器方法`<clinit>()` 的过程。
- 此方法不需定义，是 javac 编译器自动收集类中的所有类变量的赋值动作和静态代码块中的语句合并而来。
- 构造器方法中指令按语句在源文件中出现的顺序执行。
- `<clinit>()` 不同于类的构造器。（关联：构造器是虚拟机视角下的< init>()
- 若该类具有父类，JVM 会保证子类的`<clinit>()` 执行前，父类的`<clinit>()` 已经执行完毕。
- 虚拟机必须保证一个类的`<clinit>()` 方法在多线程下被同步加锁。

[[JVM宋红康_中篇03_类的加载过程详解#2 1 加载完成的操作]]

## 3. 类加载器

### 如何理解类加载器

![[附件/image/上篇02_类加载子系统-2.jpg]]

### 类加载器的分类

总分类:

- JVM 支持两种类型的类加载器,分别为引导类加载器 (BootstrapClassLoader) 和自定义类加载器 (User-Defined ClassLoader)
- 从概念上来讲, 自定义类加载器一般指的是程序中由开发人员自定义的一类类加载器,但是 Java 虚拟机规范却没有这么定义,而是将所有派生于抽象类 ClassLoader 的类加载器都划分为自定义类加载器。
- 无论类加载器的类型如何划分,在程序中我们最常见的类加载器始终只有 3 个,如下所示:

![[附件/image/上篇02_类加载子系统-3.jpg]]

- 引导类加载器（启动类加载器，Bootstrap ClassLoader)
	- 这个类加载使用 C/C++ 语言实现的，嵌套在 JVM 内部。
	- 它用来加载 Java 的核心库 (JAVA_HOME/jre/lib/rt.jar、resources.jar 或 sun.boot.class,path 路径下的内容)，用于提供 JVM 自身需要的类
	- 并不继承自 java.lang.ClassLoader,没有父加载器。
	- 加载扩展类和应用程序类加载器，并指定为他们的父类加载器。
	- 出于安全考虑，Bootstrap 启动类加载器只加载包名为 java、javax、sun 等开头的类
---
- 扩展类加载器 (jxtension ClassLoader)
	- Java 语言编写, 由 sun.misc. Launcher$ExtclassLoader 实现。
    - 派生于 ClassLoader 类
    - 父类加载器为启动类加载器
    - 从 java .ext.dirs 系统属性所指定的目录中加载类库,或从 JDK 的安装目录的 jre/lib/ext 子目录 (扩展目录) 下加载类库。如果用户创建的 JAR 放在此目录下,也会自动由扩展类加载器加载。

---

- 应用程序类加载器 (系统类加载器, AppClassLoader)
	- java 语言编写,由 sun.misc. Launcher$AppClassLoader 实现
	- 派生于 ClassLoader 类
	- 父类加载器为扩展类加载器
	- 它负责加载环境变量 classpath 或系统属性 java.class.path 指定路径下的类库
	- 该类加载是程序中默认的类加载器,一般来说, Java 应用的类都是由它来完成加载
	- 通过 ClassLoader#getSystemClassLoader () 方法可以获取到该类加载器

### 用户自定义类加载器

- 在 Java 的日常应用程序开发中，类的加载几乎是由上述 3 种类加载器相互配合执行的，在必要时，我们还可以自定义类加载器，来定制类的加载方式。
- 为什么要自定义类加载器？
	- 隔离加载类
	- 修改类加载的方式
	- 扩展加载源
	- 防止源码泄漏

---

自定义类加载器实现步骤：
1. 开发人员可以通过继承抽象类 java.lang.ClassLoader 类的方式，实现自己的类加载器，以满足一些特殊的需求
2. 在 JDK1.2 之前，在自定义类加载器时，总会去继承 classLoader 类并重 ' 写 loadC1ass() 方法，从而实现自定义的类加载类，但是在 JDK1.2 之后已不再建议用户去覆盖 loadclass() 方法，而是建议把自定义的类加载逻辑写在 findclass() 方法中 [[JVM宋红康_中篇04_再谈类加载器#破坏双亲委派机制]]
3. 在编写自定义类加载器时，如果没有太过于复杂的需求，可以直接继承 URLClassLoader 类，这样就可以避免自己去编写 findclass() 方法及其获取字节码流的方式，使自定义类加载器编写更加简洁。

[[JVM宋红康_中篇04_再谈类加载器#2 4 用户自定义类加载器]]

### 关于 ClassLoader 类

ClassLoader 类,它是一个抽象类,其后所有的类加载器都继承自 ClassLoader (不包括启动类加载器

| 方法名称                                         | 描述                                                                  |
| ------------------------------------------------ |:--------------------------------------------------------------------- |
| getParent()                                      | 返回该类加载器的超类加载器                                            |
| loadClass(String name)                           | 加载名称为 name 的类,返回结果为 java.lang.Class 类的实例                  |
| findClass(String name)                           | 查找名称为 name 的类,返回结果为 java.lang.Class 类的实例                  |
| findLoadedClass(String name)                     | 查找名称为 name 的已经被加载过的类,返回结果为 java.lang.Class 类的实例    |
| defineClass(String name.byte[] b.int offint len) | 把字节数组 b 中的内容转换为一个 Java 类,返回结果为 java.lang.Class 类的实例 |
| resolveClass(Class< ?> c)                        | 连接指定的一个 Java 类                                                  |

#### 获取 ClassLoader 的途径

- 方式一: 获取当前类的 classLoader
	- clazz.getClassLoader ()
- 方式二: 获取当前线程上下文的 classLoader
	- Thread. currentThread ().getContextClassLoader()
- 方式三: 获取系统的 ClassLoader classLoader.
	- getSystemClassLoader ()
- 方式四: 获取调用者的 ClassLoader
	- DriverManager. getCallerClassLoader()

## 4. 双亲委派机制

- **面试题 JVM**

### 原理

![[附件/image/上篇02_类加载子系统-4.jpg]]

### 优势

- 优势
	- 避免类的重加载
	- 保护程序安全，防止核心 API 被随意篡改
		- 自定义类：java.lang.String
		- 自定义类：java.lang.ShkStart

>**java.lang.SecurityException:Prohibited package name:java.lang**

[[JVM宋红康_中篇04_再谈类加载器#破坏双亲委派机制]]

### 沙箱安全机制

自定义 String 类，但是在加载自定义 String 类的时候会率先使用引导类加载器加载，而引导类加载器在加载的过程中会先加载 dk 自带的文件 (rt.jar 包中 java\lang\String.class),报错信息说没有 main 方法，就是因为加载的是 rt.jar 包中的 String 类。这样可以保证对 java 核心源代码的保护，这就是沙箱安全机制。

## 5. 其它

### 两个 class 对象是否为同一个类?

在 JVM 中表示两个 class 对象是否为同一个类存在两个必要条件：

>1. 类的完整类名必须一致，包括包名。
>
>2. 加载这个类的 classLoader(指 classLoader 实例对象) 必须相同

- 换句话说，在 JVM 中，即使这两个类对象 (class 对象) 来源同一个 class 文件，被同一个虚拟机所加载，但只要加载它们的 ClassLoader 实例对象不同，那么这两个类对象也是不相等的。

### 对类加载器的引用

JVM 必须知道一个类型是由启动加载器加载的还是由用户类加载器加载的。如果一个类型是由用户类加载器加载的，那么 JVM 会将这个类加载器的一个引用作为类型信息的一部分保存在方法区中。当解析一个类型到另一个类型的引用的时候，JVM 需要保证这两个类型的类加载器是相同的。

[[JVM宋红康_上篇03_运行时数据区-程序计数器_虚拟机栈_本地方法#方法如何调用]]

### 类的主动使用和被动使用和初始化

>什么时候类会执行初始化 (clinit<>() 方法的调用)

- Java 虚拟机规范明确指出了有且只有以下六种情况, 会触发类进行初始化
1. 遇到 new , getstatic, putstatic 或 invokestatic 这四条字节码指令时, 如果类型没有进行过初始化, 则需要先触发其初始化阶段. 情景有:
	- 1. 使用 new 关键字实例化对象的时候
	- 2. 读取或设置一个类的静态字段 (final static 看情况除外, 因为已经在编译器将结果放入常量池 ([[JVM宋红康_中篇03_类的加载过程详解#4 3 类主动使用和被动使用]]))
	- 3. 调用一个类型的静态方法
2. 使用 java.lang.reflect 包的方法对类型进行反射调用的时候
3. 初始化子类时, 发现其父类还没有初始化, 则需要先触发其父类的初始化
4. 当虚拟机启动时, 用户需要指定一个要执行的主类, 包含 main() 方法的那个类, 虚拟机会先初始化这个类
5. 当使用 JDK7 新加入的动态语言支持时, 如果一个 java.lang.invoke.MethodHandle 示例最后的解析结果为 REF_getStatic, REF_putStatic, REF_invokeStatic, REF_newInvokeSpecial 四种类型的方法句柄, 并且这个方法句柄对应的类没有进行过初始化, 则需要先触发其初始化.
6. 当一个接口中定义了 JDK 8 新加入的默认方法 (default), 则如果有这个接口的实现类发生了初始化, 那该接口要在其之前被初始化.

主动和被动的区别在于会不会导致类的初始化 (字节码中 clinit 方法是否会被调用)
详细的初始化过程是否发生可以参照初始化章节
([[JVM宋红康_中篇03_类的加载过程详解#4 过程三 初始化 Initialization]])
————————————————
