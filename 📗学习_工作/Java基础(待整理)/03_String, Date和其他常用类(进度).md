---
date: 2024-08-24
mtime: 2024-10-15
---

# String, Date 和其他常用类

**Java 高级**; **Java 常用类**

## 1. 字符串相关的类

- 复习 String 在内存中的存储方式 (JVM)
[JVM宋红康_上篇08_StringTable(字符串常量表)](JVM宋红康_上篇08_StringTable(字符串常量表).md)

### String 类及常用方法

- int length(): 返回字符串的长度：return value.length
- char charAt(int index): 返回某索引处的字符 return value[index]
- boolean isEmpty0: 判断是否是空字符串：return value..length == 0
- String toLowerCase0: 使用默认语言环境，将 String 中的所有字符转换为小写
- String toUpperCase(): 使用默认语言环境，将 String 中的所有字符转换为大写
- String trim0: 返回字符串的副本，忽略前导空白和尾部空白
- boolean equals(Object obj): 比较字符串的内容是否相同
- boolean equalslgnoreCase(String anotherString): 与 equals 方法类似，忽略大小写
- String concat(String str): 将指定字符串连接到此字符串的结尾。等价于用 "+"
- int compareTo(String anotherString): 比较两个字符串的大小
- String substring(int beginlndex): 返回一个新的字符串，它是此字符串的从 beginlndex 开始截取到最后的一个子字符串。
- String substring(int beginlndex,int endindex): 返回一个新字符串，它是此字符串从 beginlndex 开始截取到 endIndex((不包含) 的一个子字符串。
- boolean endsWith（String suffix）：测试此字符串是否以指定的后缀结束
- boolean startsWith（String prefix）：测试此字符串是否以指定的前缀开始
- boolean startsWith（String prefix， int toffset）：测试此字符串从指定索引开始的子字符串是否以指定前缀开始
- boolean contains（CharSequence s）：当且仅当此字符串包含指定的 char 值序列时，返回 true
- int indexOf（String str）：返回指定子字符串在此字符串中第一次出现处的索引
- int indexOf（String str， int fromlndex）：返回指定子字符串在此字符串中第一次出现处的索引，从指定的索引开始
- int lastindexOf（String str）：返回指定子字符串在此字符串中最右边出现处的索引
- int lastlndexOf（String str，int fromlndex）：返回指定子字符串在此字符串中最后一次出现处的索引，从指定的索引开始反向搜索注：indexOf 和 lastindexOf 方法如果未找到都是返回 -1
- String replace(char old Char， char new Char) ：返回一个新的字符串， 它是通过用 new Char 替换此字符串中出现的所有 old Char 得到的。
- String replace(Char Sequence target， Char Sequence replacement) ：使用指定的字面值替换序列替换此字符串所有匹配字面值目标序列的子字符串。
- String replace All(String regex， String replacement) ：使用给定的 replacement 替换此字符串所有匹配给定的正则表达式的子字符串。
- String replace First(String regex，String replacement) ：使用给定的 replacement 替换此字符串匹配给定的正则表达式的第一个子字符串。
- boolean matches(String regex) ：告知此字符串是否匹配给定的正则表达式
- String[] split(String regex) ：根据给定正则表达式的匹配拆分此字符串。
- String[] split(String regex， int limit) ：根据匹配给定的正则表达式来拆分此字符串， 最多不超过 limit 个， 如果超过了， 剩下的全部都放到最后一个元素中。

- matches
![[附件/image/03_String, Date和其他常用类(进度).jpg]]

- split
![[附件/image/03_String, Date和其他常用类(进度)-1.jpg]]


![[附件/image/03_String, Date和其他常用类(进度)-2.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-3.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-4.jpg]]

- 转码问题
![[附件/image/03_String, Date和其他常用类(进度)-5.jpg]]
- **面试题 Java 基础**;

![[附件/image/03_String, Date和其他常用类(进度)-6.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-7.jpg]]
- 算法题解答
	- 第一题

```java
/**
 * 自建trim
 * @author Item
 */
public class StringQ1 {
    @Test
    public void testMytrim() {
        String s = "  wer qw ";
        String s1 = myTrim(s);
        System.out.println(s1.length());
        System.out.println(s1);
    }

    public String myTrim(String s) {
        //判断数据正常
        if ((s != null) && (s.length() != 0)) {
            int start = 0;
            int end = s.length() - 1;

            //如果start<end并且存在空格, 则下标右移
            while ((start < end) && (s.charAt(start) == ' ')) {
                start++;
            }

            //如果end>start并且存在空格, 则下标左移
            while ((start < end) && (s.charAt(end) == ' ')) {
                end--;
            }

            //如果移完发现还是空格, 那么说明全部都是空格
            if (s.charAt(start) == ' ') {
                return "";
            }

            return s.substring(start, end + 1);
        }

        return null;
    }
}
```

- 第二题

```java
/**
 * 2.将字符串中指定部分进行反转。比如将“abcdefg”反转为”abfedcg”
 *
 * @author Item
 */
public class StringQ2 {
    /**
     * 字符串数组倒序
     * @param s     需要替换的字符串
     * @param start 需要替换部分的前下标
     * @param end   需要替换部分的后下标
     * @return java.lang.String
     **/
    public String reverse1(String s, int start, int end) {
        if ((s != null) && (s.length() != 0)) {
            char[] arr = s.toCharArray();

            for (; start < end; start++, end--) {
                char temp = arr[start];
                arr[start] = arr[end];
                arr[end] = temp;
            }

            return new String(arr);
        }

        return null;
    }

    /**
     * String字符串拼接
     * @param s     需要替换的字符串
     * @param start 需要替换部分的前下标
     * @param end   需要替换部分的后下标
     * @return java.lang.String
     **/
    public String reverse2(String s, int start, int end) {
        if ((s != null) && (s.length() != 0)) {
            String front = s.substring(0, start);
            String reverseStr = "";

            for (int i = end; i >= start; i--) {
                reverseStr += s.charAt(i);
            }

            return front + reverseStr + s.substring(end + 1, s.length());
        }

        return null;
    }

    /**
     * StringBuilder拼接字符串
     * @param s     需要替换的字符串
     * @param start 需要替换部分的前下标
     * @param end   需要替换部分的后下标
     * @return java.lang.String
     **/
    public String reverse3(String s, int start, int end) {
        if ((s != null) && (s.length() != 0)) {
            StringBuilder sb = new StringBuilder(s.length());
            sb.append(s.substring(0, start));

            for (int i = end; i >= start; i--) {
                sb.append(s.charAt(i));
            }

            return sb.append(s.substring(end + 1, s.length())).toString();
        }

        return null;
    }

    @Test
    public void testReverse() {
        String s = "abcdefgh";
        String s1 = reverse1(s, 2, 4);
        System.out.println("方法1结果:" + s1);

        String s2 = reverse2(s, 2, 4);
        System.out.println("方法2结果:" + s2);

        String s3 = reverse3(s, 2, 4);
        System.out.println("方法2结果:" + s3);
    }
}
```

- 第三题

```java
/**
 * 3.获取一个字符串在另一个字符串中出现的次数。
 * 比如：获取“ab”在 “cdabkkcadkabkebfkabkskab”
 * 中出现的次数
 * @author Item
 */
public class StringQ3 {
    public int find1(String mainStr, String subStr) {
        if (subStr.length() <= mainStr.length()) {
            int mainLength = mainStr.length();
            int subLength = subStr.length();
            int count = 0;
            int index = 0;

            while ((index = mainStr.indexOf(subStr)) != -1) {
                count++;
                mainStr = mainStr.substring(index + subLength);
            }

            return count;
        }

        return 0;
    }

    public int find2(String mainStr, String subStr) {
        if (subStr.length() <= mainStr.length()) {
            int mainLength = mainStr.length();
            int subLength = subStr.length();
            int count = 0;
            int index = 0;

            while ((index = mainStr.indexOf(subStr, index)) != -1) {
                count++;
                index += subLength;
            }

            return count;
        }

        return 0;
    }

    @Test
    public void testFind() {
        int count = find1("cdabkkcadkabkebfkabkskab", "cd");
        System.out.println("方法1:" + count);

        int count2 = find2("cdabkkcadkabkebfkabkskab", "cd");
        System.out.println("方法2:" + count2);
    }
}
```

- 第四题

```java
/**
 * 4.获取两个字符串中最大相同子串。比如：
 * str1 = "abcwerthelloyuiodef“;str2 = "cvhellobnm"//10
 * 提示：将短的那个串进行长度依次递减的子串与较长
 * 的串比较。
 *
 * @author Item
 */
public class StringQ4 {
    public ArrayList<String> findMaxString(String s1, String s2) {
        ArrayList<String> strings = new ArrayList<>();
        String maxStr = s1.length() > s2.length() ? s1 : s2;
        String minStr = s1.length() <= s2.length() ? s1 : s2;
        int length = minStr.length();
        //i为需要减少的字符数
        for (int i = 0; i < length; i++) {
            for (int x = 0, y = length - i; y <= length; x++, y++) {
                String str = minStr.substring(x, y);
                if (maxStr.contains(str)) {
                    strings.add(str);
                }
            }
            if (strings.size() > 0) {
                break;
            }
        }
        return strings;
    }

    @Test
    public void testFindMaxStrings() {
        ArrayList<String> maxStrings = findMaxString("abcwerthelloyuiodef", "cvhellobnmiodef");
        for (String str : maxStrings) {
            System.out.println(str);
        }
    }
}

```

- 第五题

```java
/**
 * 5.对字符串中字符进行自然顺序排序。"abcwerthelloyuiodef"
 * 提示：
 * 1）字符串变成字符数组。
 * 2）对数组排序，选择，冒泡，Arrays.sort(str.toCharArray());
 * 3）将排序后的数组变成字符串。
 *
 * @author Item
 */
public class StringQ5 {
    public String selectSort(String s) {
        int count = 0;
        char[] chars = s.toCharArray();

        for (int i = 0; i < (s.length() - 1); i++) {
            char min = chars[i];

            for (int j = i + 1; j < s.length(); j++) {
                if (chars[j] < min) {
                    min = chars[j];
                    chars[j] = chars[i];
                    chars[i] = min;
                    count++;
                }
            }
        }

        System.out.println("选择排序发生的次数" + count);

        return new String(chars);
    }

    public String bubbleSort(String s) {
        int count = 0;
        char[] chars = s.toCharArray();
        int length = s.length();
        int last = 0;
        char temp = 0;

        for (int i = 0; i < (length - 1); i++) {
            last = length - 1;

            for (int j = length - 1; j > i; j--) {
                if (chars[j] < chars[j - 1]) {
                    temp = chars[j - 1];
                    chars[j - 1] = chars[j];
                    chars[j] = temp;
                    //记录最后一次交换的位置; 如果未发生交换, 则i = length-1, 冒泡结束
                    last = j;
                    count++;
                }

                //此时最小的数字已经到了最左端
            }
			//制定下一次冒泡底
            i = last - 1;
        }

        System.out.println("冒泡次数" + count);

        return new String(chars);
    }

    @Test
    public void testSort() {
        String s = "qweoigvheiuobn";
        System.out.println("原数组长度为:" + s.length());

        String s1 = selectSort(s);
        System.out.println("选择排序结果:" + s1);
        System.out.println("选择排序后s1长度为:" + s1.length());

        String s2 = bubbleSort(s);
        System.out.println("冒泡排序结果:" + s2);
        System.out.println("冒泡排序后s2长度为:" + s2.length());
    }
}
```

### StringBuffer 与 StringBuider

重要方法:
- append
- delete(int start, int end)
- setCharAt(int n, char ch)/replace(int start , int end, String str)
- charAt(int n)
- insert(int offset ,xxx)
- length()
- 稍弱: 遍历: for() + charAt()/ toString()

#### StringBuffer 介绍

![[附件/image/03_String, Date和其他常用类(进度)-8.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-9.jpg]]

### StringBuffer 的常用方法

![[附件/image/03_String, Date和其他常用类(进度)-10.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-11.jpg]]

### StringBuider 类

![[附件/image/03_String, Date和其他常用类(进度)-12.jpg]]

- 效率对比
![[附件/image/03_String, Date和其他常用类(进度)-13.jpg]]
- **面试题 Java 基础**;

```java
面试1:
public class StringNullTest2 {  
 public static void main(String[] args) {  
	 String str = null;  
	 StringBuffer sb = new StringBuffer();  
	 sb.append(str);//调用的是appendNull方法
	 System.out.println(sb.length());  
	  
	 System.out.println(sb);  
	  
	 StringBuffer sb1 = new StringBuffer(str);//调用的是构造器方法  
	 System.out.println(sb1);  
 }  
}
结果:
4
null
Exception in thread "main" java.lang.NullPointerException
	at java.lang.StringBuffer.<init>(StringBuffer.java:139)
	at StringNullTest2.main(StringNullTest2.java:13)

```

- appendNull 方法

```java
appendNull方法
public AbstractStringBuilder append(String str) {  
	 if (str == null)  
	 return appendNull();  
	 int len = str.length();  
	 ensureCapacityInternal(count + len);  
	 str.getChars(0, len, value, count);  
	 count += len;  
	 return this;
 }
****************
private AbstractStringBuilder appendNull() {  
	 int c = count;  
	 ensureCapacityInternal(c + 4);  
	 final char[] value = this.value;  
	 value[c++] = 'n';  
	 value[c++] = 'u';  
	 value[c++] = 'l';  
	 value[c++] = 'l';  
	 count = c;  
	 return this;
 }
```

- 构造器方法

```java
构造器方法:
public StringBuffer(String str) {  
    super(str.length() + 16);  
 append(str);  
}
**************
String中的length()方法:
public int length() {  
    return value.length;  
}
**************
value属性:
private final char value[];

***********

理解: 此时value为空(null), 所以该length()方法报空指针异常
```

```java
package com;
 
public class StringTest2
{
    public static void main(String[] args)
    {
        StringBuffer sb = new StringBuffer();
        String s = null;
        sb.append(s);
        System.out.println(sb.length());
        StringBuilder sb2 = new StringBuilder();
        sb2.append(s);
        System.out.println(sb2.length());
    }
 
}
结果
4,4
```

源码:

```java
StringBuider
// Appends the specified string builder to this sequence.
    private StringBuilder append(StringBuilder sb) {
    if (sb == null)
            return append("null");
    int len = sb.length();
    int newcount = count + len;
    if (newcount > value.length)
        expandCapacity(newcount);
    sb.getChars(0, len, value, count);
    count = newcount;
        return this;
    }
StringBuffer
public AbstractStringBuilder append(String str) {
    if (str == null) str = "null";
        int len = str.length();
    if (len == 0) return this;
    int newCount = count + len;
    if (newCount > value.length)
        expandCapacity(newCount);
    str.getChars(0, len, value, count);
    count = newCount;
    return this;
}
```

**如果 str 是 null,就賦予 str = "null" 这个字符串,而不是 null 了.
而 "null" 这个字符串的长度自然是 4 了.**

```java
public class StringNullTest {
    public static void main(String[] args) {
        String s = null;
        System.out.println(s);
        System.out.println(s.length());
    }
}
结果:
null
Exception in thread "main" java.lang.NullPointerException
	at StringNullTest.main(StringNullTest.java:8)
```

## 2. 时间 API

![[附件/image/03_String, Date和其他常用类(进度)-14.jpg]]

### JDK8 之前

#### System 静态方法

![[附件/image/03_String, Date和其他常用类(进度)-15.jpg]]

#### Date 类

![[附件/image/03_String, Date和其他常用类(进度)-16.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-17.jpg]]
util.date -> sql.date

- 使用 getTime() 方法

```java
java.util.Date date1 = new java.util.Date();
java.sql.date date2 = new java.sql.Date(date1.getTime()); 
```

#### SimpleDateFormat 类

![[附件/image/03_String, Date和其他常用类(进度)-18.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-19.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-20.jpg]]
- 常用方式 和 转化 sql.date

```java
public class DateTest {  
 public static void main(String[] args) {  
	 Date date = new Date();  
	 SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");  
	 String s = sdf.format(date);  
	 System.out.println("原始date : " + date);  
	 System.out.println("date.getTime() : " + date.getTime());  
	 System.out.println("format过后的date:" + s);  
	  
	 java.sql.Date date2 = new java.sql.Date(date.getTime());  
	 SimpleDateFormat sdf2 = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");  
	 String s2 = sdf2.format(date2);  
	  
	 System.out.println("转为sql.Date之后的date2: " + date2);  
	 System.out.println("format之后的s2 : " + s2);  
 }  
}
```

#### Calendar 类

![[附件/image/03_String, Date和其他常用类(进度)-21.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-22.jpg]]

### JDK8 之后

![[附件/image/03_String, Date和其他常用类(进度)-23.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-24.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-25.jpg]]

#### LocalDate 类, LocalTime 类, LocalDateTime 类

![[附件/image/03_String, Date和其他常用类(进度)-26.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-27.jpg]]

#### Instant 类

![[附件/image/03_String, Date和其他常用类(进度)-28.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-29.jpg]]

#### DateTimeFormatter 类

![[附件/image/03_String, Date和其他常用类(进度)-30.jpg]]

#### 其他类

![[附件/image/03_String, Date和其他常用类(进度)-31.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-32.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-33.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-34.jpg]]
![[附件/image/03_String, Date和其他常用类(进度)-35.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-36.jpg]]

#### 参考

![[附件/image/03_String, Date和其他常用类(进度)-37.jpg]]

## 3. Java 比较器

![[附件/image/03_String, Date和其他常用类(进度)-38.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-39.jpg]]

### Comparable 接口

![[附件/image/03_String, Date和其他常用类(进度)-40.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-41.jpg]]
- 在对象中实现接口并使用
![[附件/image/03_String, Date和其他常用类(进度)-42.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-43.jpg]]

#### Comparator 接口

- 临时使用
![[附件/image/03_String, Date和其他常用类(进度)-44.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-45.jpg]]

## 4. System 类

![[附件/image/03_String, Date和其他常用类(进度)-46.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-47.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-48.jpg]]

## 5. Math 类

![[附件/image/03_String, Date和其他常用类(进度)-49.jpg]]

## 6. BigInteger 与 BigDecimal

![[附件/image/03_String, Date和其他常用类(进度)-50.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-51.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-52.jpg]]

![[附件/image/03_String, Date和其他常用类(进度)-53.jpg]]

————————————————
