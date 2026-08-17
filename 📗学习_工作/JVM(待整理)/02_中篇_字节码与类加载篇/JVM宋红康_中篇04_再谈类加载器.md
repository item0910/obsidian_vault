---
date: 2024-09-07
mtime: 2024-10-15
---

# 四. 再谈类加载器

**JVM 虚拟机**; **Java**

## 1. 再谈之概述 ClassLoader

![[附件/image/中篇04_再谈类加载器.jpg]]
![[附件/image/中篇04_再谈类加载器-1.jpg]]
![[附件/image/中篇04_再谈类加载器-2.jpg]]

**面试题 JVM**
![[附件/image/中篇04_再谈类加载器-3.jpg]]
![[附件/image/中篇04_再谈类加载器-4.jpg]]

### 1.1 类加载的分类

![[附件/image/中篇04_再谈类加载器-5.jpg]]

### 1.2 类加载器的必要性

![[附件/image/中篇04_再谈类加载器-6.jpg]]

### 1.3 命名空间

![[附件/image/中篇04_再谈类加载器-7.jpg]]
![[附件/image/中篇04_再谈类加载器-8.jpg]]
![[附件/image/中篇04_再谈类加载器-9.jpg]]
通过不同加载器加载的类对象是不相等的 (class 对象内部 ClassLoader 属性 会记录自己是哪一个类加载的自己)

### 1.4 类加载机制的基本特征

![[附件/image/中篇04_再谈类加载器-10.jpg]]

### 1.5 类加载器之间的关系和验证

Launcher.java 类：

```java
public class Launcher {
    ……

    public Launcher() {
        Launcher.ExtClassLoader var1;
        try {
            var1 = Launcher.ExtClassLoader.getExtClassLoader();
        } catch (IOException var10) {
            throw new InternalError("Could not create extension class loader", var10);
        }

        try {
            this.loader = Launcher.AppClassLoader.getAppClassLoader(var1);
        } catch (IOException var9) {
            throw new InternalError("Could not create application class loader", var9);
        }

        Thread.currentThread().setContextClassLoader(this.loader);
                ……
}
```

分析：
1、验证扩展类加载器的父类是 null
先看：

```java
 var1 = Launcher.ExtClassLoader.getExtClassLoader();
```

获取到扩展类加载器，点击该方法往里面追溯，在找到：

```java
return new Launcher.ExtClassLoader(var0);
```

我们在点击该方法往里面追溯，在找到：

```java
super(getExtURLs(var1), (ClassLoader)null, Launcher.factory);
```

然后点击 super，往里面追溯，在找到：

```java
public URLClassLoader(URL[] urls, ClassLoader parent,
                      URLStreamHandlerFactory factory) {
    super(parent);
```

点击其中的 parent 就是 null，我们点击 super，往里面追溯，在找到：

```java
protected SecureClassLoader(ClassLoader parent) {
    super(parent);
```

点击其中的 parent 就是 null，我们点击 super，往里面追溯，在找到：

```java
protected ClassLoader(ClassLoader parent) {
    this(checkCreateClassLoader(), parent);
}
```

点击其中的 parent 就是 null，我们点击 this，往里面追溯，在找到：

```java
private ClassLoader(Void unused, ClassLoader parent) {
    this.parent = parent;
```

由于 parent 就是 null，所以扩展类加载器的父类是 null，也就是引导类加载器，因此我们调用获取扩展类加载器父类的方法获得的结果是 null

 2、验证系统类加载器的父类是扩展类加载器
先看：

```java
this.loader = Launcher.AppClassLoader.getAppClassLoader(var1);
```

获取到系统类加载器，点击该方法往里面追溯，在找到：

```java
return new Launcher.AppClassLoader(var1x, var0);
``` 

其中 var0 就是扩展类加载器，点击 AppClassLoader，往里面追溯，在找到：

```java
AppClassLoader(URL[] var1, ClassLoader var2) {
    super(var1, var2, Launcher.factory);
    this.ucp.initLookupCache(this);
}
```

其中 var2 就是扩展类加载器，我们点击 super，往里面追溯，在找到：

```java
public URLClassLoader(URL[] urls, ClassLoader parent, URLStreamHandlerFactory factory) {
    super(parent);
```

里面的 parent 就是扩展类加载器，我们点击 super，往里面追溯，在找到：

```java
protected SecureClassLoader(ClassLoader parent) {
    super(parent);
```

里面的 parent 就是扩展类加载器，我们点击 super，往里面追溯，在找到：

```java
protected ClassLoader(ClassLoader parent) {
    this(checkCreateClassLoader(), parent);
}
```

里面的 parent 就是扩展类加载器，我们点击 this，往里面追溯，在找到：

```java
private ClassLoader(Void unused, ClassLoader parent) {
    this.parent = parent;
```

由于 parent 就是扩展类加载器，所以系统类加载器的父类是扩展类加载器，因此我们调用获取系统类加载器父类的方法获得的结果是扩展类加载器
3、当前线程上下文的 ClassLoader 就是系统类加载器

```java
Thread.currentThread().setContextClassLoader(this.loader)
```

就是将系统类加载器设置为当前线程的上下文加载器，所以

```java
Thread.currentThread().getContextClassLoader()
```

获取到的就是系统类加载器

## 2. 复习: 类的加载器分类

- 复习:

![[附件/image/中篇04_再谈类加载器-11.jpg]]
![[附件/image/中篇04_再谈类加载器-12.jpg]]
![[附件/image/中篇04_再谈类加载器-13.jpg]]
注意, 这里的 getParent , 就像类的 get 方法, Parent 是作为一个属性或者说是 field 存在, 而不是真正的父类

### 2.1 引导类加载器

![[附件/image/中篇04_再谈类加载器-14.jpg]]
![[附件/image/中篇04_再谈类加载器-15.jpg]]
![[附件/image/中篇04_再谈类加载器-16.jpg]]
![[附件/image/中篇04_再谈类加载器-17.jpg]]

### 2.2 扩展类加载器

![[附件/image/中篇04_再谈类加载器-18.jpg]]
![[附件/image/中篇04_再谈类加载器-19.jpg]]

### 2.3 系统类加载器

![[附件/image/中篇04_再谈类加载器-20.jpg]]

### 2.4 用户自定义类加载器

![[附件/image/中篇04_再谈类加载器-21.jpg]]

## 3. 测试不同的类的加载器

![[附件/image/中篇04_再谈类加载器-22.jpg]]
![[附件/image/中篇04_再谈类加载器-23.jpg]]

## 4. ClassLoader 源码解析

![[附件/image/中篇04_再谈类加载器-24.jpg]]

### ClassLoader 的主要方法

![[附件/image/中篇04_再谈类加载器-25.jpg]]
![[附件/image/中篇04_再谈类加载器-26.jpg]]
![[附件/image/中篇04_再谈类加载器-27.jpg]]
三者关系
loadClass(双亲委派的体现 (递归寻找父类的 loadClass 方法)) 引用了 findClass 方法 , findClass 方法 (实际在 URLClassLoader 中是空方法体) 又引用了 defineClass 方法, defineClass 是真正完成二进制流到生成 Class 对象的方法

#### LoadClass 的剖析

![[附件/image/中篇04_再谈类加载器-28.jpg]]
![[附件/image/中篇04_再谈类加载器-29.jpg]]

### SecureClassLoader 与 URLClassLoader

![[附件/image/中篇04_再谈类加载器-30.jpg]]
![[附件/image/中篇04_再谈类加载器-31.jpg]]

### ExtClassLoader 与 AppClassLoader

![[附件/image/中篇04_再谈类加载器-32.jpg]]
![[附件/image/中篇04_再谈类加载器-33.jpg]]

### Class.forName() 与 ClassLoader.loadClass 的区别

![[附件/image/中篇04_再谈类加载器-34.jpg]]
- 区别 1: Class.forName 是静态方法, classLoader.loadClass 是实例方法
- 区别 2: Class.forName 调用时, 会进行类的初始化, 而 classLoader.loadClass 不会 (方法中 resolve 参数都为 false, 表示类不进行解析 ([[JVM宋红康_中篇03_类的加载过程详解#3 3 解析Resolution]])
([[JVM宋红康_中篇03_类的加载过程详解#4 3 类主动使用和被动使用]])

## 5. 双亲委派模型

### 定义与本质

![[附件/image/中篇04_再谈类加载器-35.jpg]]
![[附件/image/中篇04_再谈类加载器-36.jpg]]

### 优势与劣势

![[附件/image/中篇04_再谈类加载器-37.jpg]]
![[附件/image/中篇04_再谈类加载器-38.jpg]]

### 破坏双亲委派机制

#### 第一次破坏 (即双亲委派机制尚未存在)

![[附件/image/中篇04_再谈类加载器-39.jpg]]

#### 第二次破坏

![[附件/image/中篇04_再谈类加载器-40.jpg]]
![[附件/image/中篇04_再谈类加载器-41.jpg]]

#### 第三次破坏

![[附件/image/中篇04_再谈类加载器-42.jpg]]
![[附件/image/中篇04_再谈类加载器-43.jpg]]

### 热替换的实现

![[附件/image/中篇04_再谈类加载器-44.jpg]]
![[附件/image/中篇04_再谈类加载器-45.jpg]]

主要思路: 自定义类加载器 (重写 findClass 并调用) 主动完成类加载, 再用反射方法创建运行时类的实例, 则如果 class 文件发生改变, 那么实例发生实时改变, 完成热代码替换

## 6. 沙箱安全机制

![[附件/image/中篇04_再谈类加载器-46.jpg]]

### JDK1.0 时期

![[附件/image/中篇04_再谈类加载器-47.jpg]]

### JDK1.1 时期

![[附件/image/中篇04_再谈类加载器-48.jpg]]

### JDK1.2 时期

![[附件/image/中篇04_再谈类加载器-49.jpg]]

### JDK 1.6 时期

![[附件/image/中篇04_再谈类加载器-50.jpg]]

## 7. 自定义类加载器

![[附件/image/中篇04_再谈类加载器-51.jpg]]
![[附件/image/中篇04_再谈类加载器-52.jpg]]

- 实现方式
![[附件/image/中篇04_再谈类加载器-53.jpg]]

## 8. Java9 新特性

![[附件/image/中篇04_再谈类加载器-55.jpg]]
![[附件/image/中篇04_再谈类加载器-56.jpg]]
![[附件/image/中篇04_再谈类加载器-57.jpg]]
![[附件/image/中篇04_再谈类加载器-58.jpg]]
![[附件/image/中篇04_再谈类加载器-59.jpg]]
分工:
![[附件/image/中篇04_再谈类加载器-60.jpg]]
![[附件/image/中篇04_再谈类加载器-61.jpg]]
![[附件/image/中篇04_再谈类加载器-62.jpg]]

```java
public class ClassLoaderTest {
    public static void main(String[] args) {
        System.out.println(ClassLoaderTest.class.getClassLoader());
        System.out.println(ClassLoaderTest.class.getClassLoader().getParent());
        System.out.println(ClassLoaderTest.class.getClassLoader().getParent().getParent());
 
        //获取系统类加载器
        System.out.println(ClassLoader.getSystemClassLoader());
        //获取平台类加载器
        System.out.println(ClassLoader.getPlatformClassLoader());
        //获取类的加载器的名称
        System.out.println(ClassLoaderTest.class.getClassLoader().getName());
    }
}
```

————————————————
