---
date: 2024-09-07
mtime: 2024-09-25
---

# Java8 新特性

**Java 高级**; **Java 新特性**

## Java8 新特性简介

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-45.jpg]]
![[附件/image/11_Lambda方法引用 Stream类(Java8新特性).jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-46.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-47.jpg]]

## 1. Lambda 表达式

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-48.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-49.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-50.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-51.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-52.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-53.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-54.jpg]]

```java
/**
 * Lambda表达式的使用
 *
 * 1.举例： (o1,o2) -> Integer.compare(o1,o2);
 * 2.格式：
 *      -> :lambda操作符 或 箭头操作符
 *      ->左边：lambda形参列表 （其实就是接口中的抽象方法的形参列表）
 *      ->右边：lambda体 （其实就是重写的抽象方法的方法体）
 *
 * 3. Lambda表达式的使用：（分为6种情况介绍）
 *
 *    总结：
 *    ->左边：lambda形参列表的参数类型可以省略(类型推断)；如果lambda形参列表只有一个参数，其一对()也可以省略
 *    ->右边：lambda体应该使用一对{}包裹；如果lambda体只有一条执行语句（可能是return语句），省略这一对{}和return关键字
 *
 * 4.Lambda表达式的本质：作为函数式接口的实例
 *
 * 5. 如果一个接口中，只声明了一个抽象方法，则此接口就称为函数式接口。我们可以在一个接口上使用 @FunctionalInterface 注解，
 *   这样做可以检查它是否是一个函数式接口。
 *
 * 6. 所以以前用匿名实现类表示的现在都可以用Lambda表达式来写。
 *
 * @author shkstart
 * @create 2019 上午 11:40
 */
public class LambdaTest1 {
    //语法格式一：无参，无返回值
    @Test
    public void test1(){
        Runnable r1 = new Runnable() {
            @Override
            public void run() {
                System.out.println("我爱北京天安门");
            }
        };

        r1.run();

        System.out.println("***********************");

        Runnable r2 = () -> {
            System.out.println("我爱北京故宫");
        };

        r2.run();
    }
    //语法格式二：Lambda 需要一个参数，但是没有返回值。
    @Test
    public void test2(){

        Consumer<String> con = new Consumer<String>() {
            @Override
            public void accept(String s) {
                System.out.println(s);
            }
        };
        con.accept("谎言和誓言的区别是什么？");

        System.out.println("*******************");

        Consumer<String> con1 = (String s) -> {
            System.out.println(s);
        };
        con1.accept("一个是听得人当真了，一个是说的人当真了");

    }

    //语法格式三：数据类型可以省略，因为可由编译器推断得出，称为“类型推断”
    @Test
    public void test3(){

        Consumer<String> con1 = (String s) -> {
            System.out.println(s);
        };
        con1.accept("一个是听得人当真了，一个是说的人当真了");

        System.out.println("*******************");

        Consumer<String> con2 = (s) -> {
            System.out.println(s);
        };
        con2.accept("一个是听得人当真了，一个是说的人当真了");

    }

    @Test
    public void test4(){

        ArrayList<String> list = new ArrayList<>();//类型推断

        int[] arr = {1,2,3};//类型推断

    }

    //语法格式四：Lambda 若只需要一个参数时，参数的小括号可以省略
    @Test
    public void test5(){
        Consumer<String> con1 = (s) -> {
            System.out.println(s);
        };
        con1.accept("一个是听得人当真了，一个是说的人当真了");

        System.out.println("*******************");

        Consumer<String> con2 = s -> {
            System.out.println(s);
        };
        con2.accept("一个是听得人当真了，一个是说的人当真了");


    }

    //语法格式五：Lambda 需要两个或以上的参数，多条执行语句，并且可以有返回值
    @Test
    public void test6(){

        Comparator<Integer> com1 = new Comparator<Integer>() {
            @Override
            public int compare(Integer o1, Integer o2) {
                System.out.println(o1);
                System.out.println(o2);
                return o1.compareTo(o2);
            }
        };

        System.out.println(com1.compare(12,21));

        System.out.println("*****************************");
        Comparator<Integer> com2 = (o1,o2) -> {
            System.out.println(o1);
            System.out.println(o2);
            return o1.compareTo(o2);
        };

        System.out.println(com2.compare(12,6));


    }

    //语法格式六：当 Lambda 体只有一条语句时，return 与大括号若有，都可以省略
    @Test
    public void test7(){

        Comparator<Integer> com1 = (o1,o2) -> {
            return o1.compareTo(o2);
        };

        System.out.println(com1.compare(12,6));

        System.out.println("*****************************");

        Comparator<Integer> com2 = (o1,o2) -> o1.compareTo(o2);

        System.out.println(com2.compare(12,21));

    }

    @Test
    public void test8(){
        Consumer<String> con1 = s -> {
            System.out.println(s);
        };
        con1.accept("一个是听得人当真了，一个是说的人当真了");

        System.out.println("*****************************");

        Consumer<String> con2 = s -> System.out.println(s);

        con2.accept("一个是听得人当真了，一个是说的人当真了");
    }
}

```

## 2. 函数式 (Functional) 接口

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-55.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-56.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-57.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-58.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-59.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-60.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-61.jpg]]

```java
/**
 * java内置的4大核心函数式接口
 * <p>
 * 消费型接口 Consumer<T>     void accept(T t)
 * 供给型接口 Supplier<T>     T get()
 * 函数型接口 Function<T,R>   R apply(T t)
 * 断定型接口 Predicate<T>    boolean test(T t)
 *
 * @author shkstart
 * @create 2019 下午 2:29
 */
public class LambdaTest2 {

    @Test
    public void test1() {

        happyTime(500, new Consumer<Double>() {
            @Override
            public void accept(Double aDouble) {
                System.out.println("学习太累了，去天上人间买了瓶矿泉水，价格为：" + aDouble);
            }
        });

        System.out.println("********************");

        happyTime(400, spent -> System.out.println("学习太累了，去天上人间喝了口水，价格为：" + spent));
    }

    public void happyTime(double money, Consumer<Double> con) {
        con.accept(money);
    }


    @Test
    public void test2() {
        List<String> list = Arrays.asList("北京", "南京", "天津", "东京", "西京", "普京");

        List<String> filterStrs = filterString(list, new Predicate<String>() {
            @Override
            public boolean test(String s) {
                return s.contains("京");
            }
        });

        System.out.println(filterStrs);

        List<String> filterStrs1 = filterString(list, s -> s.contains("京"));
        System.out.println(filterStrs1);
    }

    //根据给定的规则，过滤集合中的字符串。此规则由Predicate的方法决定
    public List<String> filterString(List<String> list, Predicate<String> pre) {

        ArrayList<String> filterList = new ArrayList<>();

        for (String s : list) {
            if (pre.test(s)) {
                filterList.add(s);
            }
        }
        return filterList;
    }

}

```

## 3. 方法引用与构造器引用

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-62.jpg]]

```java
/**
 * 方法引用的使用
 *
 * 1.使用情境：当要传递给Lambda体的操作，已经有实现的方法了，可以使用方法引用！
 *
 * 2.方法引用，本质上就是Lambda表达式，而Lambda表达式作为函数式接口的实例。所以
 *   方法引用，也是函数式接口的实例。
 *
 * 3. 使用格式：  类(或对象) :: 方法名
 *
 * 4. 具体分为如下的三种情况：
 *    情况1     对象 :: 非静态方法
 *    情况2     类 :: 静态方法
 *
 *    情况3     类 :: 非静态方法
 *
 * 5. 方法引用使用的要求：要求接口中的抽象方法的形参列表和返回值类型与方法引用的方法的
 *    形参列表和返回值类型相同！（针对于情况1和情况2）
 *
 * Created by shkstart.
 */
public class MethodRefTest {

	// 情况一：对象 :: 实例方法
	//Consumer中的void accept(T t)
	//PrintStream中的void println(T t)
	@Test
	public void test1() {
		Consumer<String> con1 = str -> System.out.println(str);
		con1.accept("北京");

		System.out.println("*******************");
		PrintStream ps = System.out;
		Consumer<String> con2 = ps::println;
		con2.accept("beijing");
	}
	
	//Supplier中的T get()
	//Employee中的String getName()
	@Test
	public void test2() {
		Employee emp = new Employee(1001,"Tom",23,5600);

		Supplier<String> sup1 = () -> emp.getName();
		System.out.println(sup1.get());

		System.out.println("*******************");
		Supplier<String> sup2 = emp::getName;
		System.out.println(sup2.get());
	}

	// 情况二：类 :: 静态方法
	//Comparator中的int compare(T t1,T t2)
	//Integer中的int compare(T t1,T t2)
	@Test
	public void test3() {
		Comparator<Integer> com1 = (t1,t2) -> Integer.compare(t1,t2);
		System.out.println(com1.compare(12,21));

		System.out.println("*******************");

		Comparator<Integer> com2 = Integer::compare;
		System.out.println(com2.compare(12,3));

	}
	
	//Function中的R apply(T t)
	//Math中的Long round(Double d)
	@Test
	public void test4() {
		Function<Double,Long> func = new Function<Double, Long>() {
			@Override
			public Long apply(Double d) {
				return Math.round(d);
			}
		};

		System.out.println("*******************");

		Function<Double,Long> func1 = d -> Math.round(d);
		System.out.println(func1.apply(12.3));

		System.out.println("*******************");

		Function<Double,Long> func2 = Math::round;
		System.out.println(func2.apply(12.6));
	}

	// 情况三：类 :: 实例方法  (有难度)
	// Comparator中的int comapre(T t1,T t2)
	// String中的int t1.compareTo(t2)
	@Test
	public void test5() {
		Comparator<String> com1 = (s1,s2) -> s1.compareTo(s2);
		System.out.println(com1.compare("abc","abd"));

		System.out.println("*******************");

		Comparator<String> com2 = String :: compareTo;
		System.out.println(com2.compare("abd","abm"));
	}

	//BiPredicate中的boolean test(T t1, T t2);
	//String中的boolean t1.equals(t2)
	@Test
	public void test6() {
		BiPredicate<String,String> pre1 = (s1,s2) -> s1.equals(s2);
		System.out.println(pre1.test("abc","abc"));

		System.out.println("*******************");
		BiPredicate<String,String> pre2 = String :: equals;
		System.out.println(pre2.test("abc","abd"));
	}
	
	// Function中的R apply(T t)
	// Employee中的String getName();
	@Test
	public void test7() {
		Employee employee = new Employee(1001, "Jerry", 23, 6000);


		Function<Employee,String> func1 = e -> e.getName();
		System.out.println(func1.apply(employee));

		System.out.println("*******************");


		Function<Employee,String> func2 = Employee::getName;
		System.out.println(func2.apply(employee));
	}

}

```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-63.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-64.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-65.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-66.jpg]]

```java
/**
 * 一、构造器引用
 *      和方法引用类似，函数式接口的抽象方法的形参列表和构造器的形参列表一致。
 *      抽象方法的返回值类型即为构造器所属的类的类型
 *
 * 二、数组引用
 *     大家可以把数组看做是一个特殊的类，则写法与构造器引用一致。
 *
 * Created by shkstart
 */
public class ConstructorRefTest {
	//构造器引用
    //Supplier中的T get()
    //Employee的空参构造器：Employee()
    @Test
    public void test1(){

        Supplier<Employee> sup = new Supplier<Employee>() {
            @Override
            public Employee get() {
                return new Employee();
            }
        };
        System.out.println("*******************");

        Supplier<Employee>  sup1 = () -> new Employee();
        System.out.println(sup1.get());

        System.out.println("*******************");

        Supplier<Employee>  sup2 = Employee :: new;
        System.out.println(sup2.get());
    }

	//Function中的R apply(T t)
    @Test
    public void test2(){
        Function<Integer,Employee> func1 = id -> new Employee(id);
        Employee employee = func1.apply(1001);
        System.out.println(employee);

        System.out.println("*******************");

        Function<Integer,Employee> func2 = Employee :: new;
        Employee employee1 = func2.apply(1002);
        System.out.println(employee1);

    }

	//BiFunction中的R apply(T t,U u)
    @Test
    public void test3(){
        BiFunction<Integer,String,Employee> func1 = (id,name) -> new Employee(id,name);
        System.out.println(func1.apply(1001,"Tom"));

        System.out.println("*******************");

        BiFunction<Integer,String,Employee> func2 = Employee :: new;
        System.out.println(func2.apply(1002,"Tom"));

    }

	//数组引用
    //Function中的R apply(T t)
    @Test
    public void test4(){
        Function<Integer,String[]> func1 = length -> new String[length];
        String[] arr1 = func1.apply(5);
        System.out.println(Arrays.toString(arr1));

        System.out.println("*******************");

        Function<Integer,String[]> func2 = String[] :: new;
        String[] arr2 = func2.apply(10);
        System.out.println(Arrays.toString(arr2));
    }
}

```

## 4. 强大的 Stream API

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-67.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-68.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-69.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-70.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-71.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-72.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-73.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-74.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-75.jpg]]

```java
/**
 * 1. Stream关注的是对数据的运算，与CPU打交道
 * 集合关注的是数据的存储，与内存打交道
 * <p>
 * 2.
 * ①Stream 自己不会存储元素。
 * ②Stream 不会改变源对象。相反，他们会返回一个持有结果的新Stream。
 * ③Stream 操作是延迟执行的。这意味着他们会等到需要结果的时候才执行
 * <p>
 * 3.Stream 执行流程
 * ① Stream的实例化
 * ② 一系列的中间操作（过滤、映射、...)
 * ③ 终止操作
 * <p>
 * 4.说明：
 * 4.1 一个中间操作链，对数据源的数据进行处理
 * 4.2 一旦执行终止操作，就执行中间操作链，并产生结果。之后，不会再被使用
 * <p>
 * <p>
 * 测试Stream的实例化
 *
 * @author shkstart
 * @create 2019 下午 4:25
 */
public class StreamAPITest {

    //创建 Stream方式一：通过集合
    @Test
    public void test1() {
        List<Employee> employees = EmployeeData.getEmployees();

        //default Stream<E> stream() : 返回一个顺序流
        Stream<Employee> stream = employees.stream();

        //default Stream<E> parallelStream() : 返回一个并行流
        Stream<Employee> parallelStream = employees.parallelStream();

    }

    //创建 Stream方式二：通过数组
    @Test
    public void test2() {
        int[] arr = new int[]{1, 2, 3, 4, 5, 6};
        //调用Arrays类的static <T> Stream<T> stream(T[] array): 返回一个流
        IntStream stream = Arrays.stream(arr);

        Employee e1 = new Employee(1001, "Tom");
        Employee e2 = new Employee(1002, "Jerry");
        Employee[] arr1 = new Employee[]{e1, e2};
        Stream<Employee> stream1 = Arrays.stream(arr1);

    }

    //创建 Stream方式三：通过Stream的of()
    @Test
    public void test3() {

        Stream<Integer> stream = Stream.of(1, 2, 3, 4, 5, 6);

    }

    //创建 Stream方式四：创建无限流
    @Test
    public void test4() {

        //迭代
        //public static<T> Stream<T> iterate(final T seed, final UnaryOperator<T> f)
        //遍历前10个偶数
        Stream.iterate(0, t -> t + 2).limit(10).forEach(System.out::println);


        //生成
        //public static<T> Stream<T> generate(Supplier<T> s)
        Stream.generate(Math::random).limit(10).forEach(System.out::println);

    }

}

```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-76.jpg]]

```java
//1-筛选与切片
@Test
public void test1() {
	List<Employee> list = EmployeeData.getEmployees();
	//filter(Predicate p)——接收 Lambda ， 从流中排除某些元素。
	Stream<Employee> stream = list.stream();
	//练习：查询员工表中薪资大于7000的员工信息
	stream.filter(e -> e.getSalary() > 7000).forEach(System.out::println);

	System.out.println();
	//limit(n)——截断流，使其元素不超过给定数量。
	list.stream().limit(3).forEach(System.out::println);
	System.out.println();

	//skip(n) —— 跳过元素，返回一个扔掉了前 n 个元素的流。若流中元素不足 n 个，则返回一个空流。与 limit(n) 互补
	list.stream().skip(3).forEach(System.out::println);

	System.out.println();
	//distinct()——筛选，通过流所生成元素的 hashCode() 和 equals() 去除重复元素

	list.add(new Employee(1010, "刘强东", 40, 8000));
	list.add(new Employee(1010, "刘强东", 41, 8000));
	list.add(new Employee(1010, "刘强东", 40, 8000));
	list.add(new Employee(1010, "刘强东", 40, 8000));
	list.add(new Employee(1010, "刘强东", 40, 8000));

	//System.out.println(list);

	list.stream().distinct().forEach(System.out::println);
}
```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-77.jpg]]

```java
//映射
public StreamAPITest1{
	@Test
	public void test2() {
		//map(Function f)——接收一个函数作为参数，将元素转换成其他形式或提取信息，该函数会被应用到每个元素上，并将其映射成一个新的元素。
		List<String> list = Arrays.asList("aa", "bb", "cc", "dd");
		list.stream().map(str -> str.toUpperCase()).forEach(System.out::println);
	
		//练习1：获取员工姓名长度大于3的员工的姓名。
		List<Employee> employees = EmployeeData.getEmployees();
		Stream<String> namesStream = employees.stream().map(Employee::getName);
		namesStream.filter(name -> name.length() > 3).forEach(System.out::println);
		System.out.println();
		//练习2：
		Stream<Stream<Character>> streamStream = list.stream().map(StreamAPITest1::fromStringToStream);
		streamStream.forEach(s -> {
			s.forEach(System.out::println);
		});
		System.out.println();
		//flatMap(Function f)——接收一个函数作为参数，将流中的每个值都换成另一个流，然后把所有流连接成一个流。
		Stream<Character> characterStream = list.stream().flatMap(StreamAPITest1::fromStringToStream);
		characterStream.forEach(System.out::println);
	
	}
	
	//将字符串中的多个字符构成的集合转换为对应的Stream的实例
	public static Stream<Character> fromStringToStream(String str) {//aa
		ArrayList<Character> list = new ArrayList<>();
		for (Character c : str.toCharArray()) {
			list.add(c);
		}
		return list.stream();
	}
	
	//flatMap
	@Test
	public void test3() {
		ArrayList list1 = new ArrayList();
		list1.add(1);
		list1.add(2);
		list1.add(3);
	
		ArrayList list2 = new ArrayList();
		list2.add(4);
		list2.add(5);
		list2.add(6);
	
		//        list1.add(list2);
		list1.addAll(list2);
		System.out.println(list1);
	}
}
```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-78.jpg]]

```java
//3-排序  
@Test  
public void test4() {  
 //sorted()——自然排序  
 List<Integer> list = Arrays.asList(12, 43, 65, 34, 87, 0, -98, 7);  
 list.stream().sorted().forEach(System.out::println);  
 //抛异常，原因:Employee没有实现Comparable接口  
 //List<Employee> employees = EmployeeData.getEmployees();  
 //employees.stream().sorted().forEach(System.out::println);  
  
 //sorted(Comparator com)——定制排序  
  
 List<Employee> employees = EmployeeData.getEmployees();  
 employees.stream().sorted((e1, e2) -> {  

 int ageValue = Integer.compare(e1.getAge(), e2.getAge());  
	 if (ageValue != 0) {
	            return ageValue;  
	 } else {  
	            return -Double.compare(e1.getSalary(), e2.getSalary());
	 }
    }).forEach(System.out::println);  
}
```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-79.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-80.jpg]]

```java
//1-匹配与查找
@Test
public void test1() {
	List<Employee> employees = EmployeeData.getEmployees();

	//allMatch(Predicate p)——检查是否匹配所有元素。
	//练习：是否所有的员工的年龄都大于18
	boolean allMatch = employees.stream().allMatch(e -> e.getAge() > 18);
	System.out.println(allMatch);

	//anyMatch(Predicate p)——检查是否至少匹配一个元素。
	//练习：是否存在员工的工资大于 10000
	boolean anyMatch = employees.stream().anyMatch(e -> e.getSalary() > 10000);
	System.out.println(anyMatch);

	//noneMatch(Predicate p)——检查是否没有匹配的元素。
	//练习：是否存在员工姓“雷”
	boolean noneMatch = employees.stream().noneMatch(e -> e.getName().startsWith("雷"));
	System.out.println(noneMatch);
	//findFirst——返回第一个元素
	Optional<Employee> employee = employees.stream().findFirst();
	System.out.println(employee);
	//findAny——返回当前流中的任意元素
	Optional<Employee> employee1 = employees.parallelStream().findAny();
	System.out.println(employee1);
}

@Test
public void test2() {
	List<Employee> employees = EmployeeData.getEmployees();
	// count——返回流中元素的总个数
	long count = employees.stream().filter(e -> e.getSalary() > 5000).count();
	System.out.println(count);
	//max(Comparator c)——返回流中最大值
	//练习：返回最高的工资：
	Stream<Double> salaryStream = employees.stream().map(e -> e.getSalary());
	Optional<Double> maxSalary = salaryStream.max(Double::compare);
	System.out.println(maxSalary);
	//min(Comparator c)——返回流中最小值
	//练习：返回最低工资的员工
	Optional<Employee> employee = employees.stream().min((e1, e2) -> Double.compare(e1.getSalary(), e2.getSalary()));
	System.out.println(employee);
	System.out.println();
	//forEach(Consumer c)——内部迭代
	employees.stream().forEach(System.out::println);
	//使用集合的遍历操作
	employees.forEach(System.out::println);
}
```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-81.jpg]]

```java
//2-归约
@Test
public void test3() {
	//reduce(T identity, BinaryOperator)——可以将流中元素反复结合起来，得到一个值。返回 T
	//练习1：计算1-10的自然数的和
	List<Integer> list = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
	Integer sum = list.stream().reduce(0, Integer::sum);
	System.out.println(sum);

	//reduce(BinaryOperator) ——可以将流中元素反复结合起来，得到一个值。返回 Optional<T>
	//练习2：计算公司所有员工工资的总和
	List<Employee> employees = EmployeeData.getEmployees();
	Stream<Double> salaryStream = employees.stream().map(Employee::getSalary);
	//Optional<Double> sumMoney = salaryStream.reduce(Double::sum);
	Optional<Double> sumMoney = salaryStream.reduce((d1, d2) -> d1 + d2);
	System.out.println(sumMoney.get());

}
```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-82.jpg]]

```java
//3-收集
@Test
public void test4() {
	//collect(Collector c)——将流转换为其他形式。接收一个 Collector接口的实现，用于给Stream中元素做汇总的方法
	//练习1：查找工资大于6000的员工，结果返回为一个List或Set

	List<Employee> employees = EmployeeData.getEmployees();
	List<Employee> employeeList = employees.stream().filter(e -> e.getSalary() > 6000).collect(Collectors.toList());

	employeeList.forEach(System.out::println);
	System.out.println();
	Set<Employee> employeeSet = employees.stream().filter(e -> e.getSalary() > 6000).collect(Collectors.toSet());

	employeeSet.forEach(System.out::println);
}
```

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-83.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-84.jpg]]

## 5. Optional 类

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-85.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-86.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-87.jpg]]

![[附件/image/11_Lambda方法引用 Stream类(Java8新特性)-88.jpg]]

```java
/**
 * Optional类：为了在程序中避免出现空指针异常而创建的。
 *
 * 常用的方法：ofNullable(T t)
 *            orElse(T t)
 *
 * @author shkstart
 * @create 2019 下午 7:24
 */
public class OptionalTest {
    /*
    Optional.of(T t) : 创建一个 Optional 实例，t必须非空；
    Optional.empty() : 创建一个空的 Optional 实例
    Optional.ofNullable(T t)：t可以为null

     */
    @Test
    public void test1() {
        Girl girl = new Girl();

        //girl = null;
        //of(T t):保证t是非空的
        Optional<Girl> optionalGirl = Optional.of(girl);
    }

    @Test
    public void test2() {
        Girl girl = new Girl();

        //girl = null;
        //ofNullable(T t)：t可以为null
        Optional<Girl> optionalGirl = Optional.ofNullable(girl);
        System.out.println(optionalGirl);

        //orElse(T t1):如果单前的Optional内部封装的t是非空的，则返回内部的t.
        //如果内部的t是空的，则返回orElse()方法中的参数t1.
        Girl girl1 = optionalGirl.orElse(new Girl("赵丽颖"));
        System.out.println(girl1);
    }

    public String getGirlName(Boy boy) {
        return boy.getGirl().getName();
    }

	
    @Test
    public void test3() {
        //有可能出现空指针异常
		Boy boy = new Boy();
        boy = null;

        String girlName = getGirlName(boy);
        System.out.println(girlName);
    }

    //优化以后的getGirlName():
    public String getGirlName1(Boy boy) {
        if (boy != null) {
            Girl girl = boy.getGirl();

            if (girl != null) {
                return girl.getName();
            }
        }
        return null;
    }

    @Test
    public void test4() {
        Boy boy = new Boy();
        boy = null;

        String girlName = getGirlName1(boy);
        System.out.println(girlName);
    }

    //使用Optional类的getGirlName():
    public String getGirlName2(Boy boy) {
        Optional<Boy> boyOptional = Optional.ofNullable(boy);

        //此时的boy1一定非空
        Boy boy1 = boyOptional.orElse(new Boy(new Girl("迪丽热巴")));

        Girl girl = boy1.getGirl();

        Optional<Girl> girlOptional = Optional.ofNullable(girl);

        //girl1一定非空
        Girl girl1 = girlOptional.orElse(new Girl("古力娜扎"));

        return girl1.getName();
    }

    @Test
    public void test5() {
        Boy boy = null;
        boy = new Boy();
        boy = new Boy(new Girl("苍老师"));

        String girlName = getGirlName2(boy);
        System.out.println(girlName);
    }
}

```

————————————————
