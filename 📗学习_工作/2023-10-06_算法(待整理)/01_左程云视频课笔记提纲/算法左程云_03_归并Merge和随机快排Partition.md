---
date: 2024-09-07
mtime: 2024-09-25
---

# 归并排序 Merge

## 递归版本

```java
public void mergeSort1(int[] nums){
	if(nums == null || nums.length == 0){
		return;
	}
	process(nums, 0, nums.length - 1);
}

public void process(int [] nums, int L, int R){
	if(L == R){
		return;
	}
	int mid = L + ((R - L) );
	process(nums, L, mid);
	process(nums, mid + 1, R);
	merge(nums, L, mid, R);
}

public void merge(int[] nums, int L, int mid, int R){
	int[] help = new int[R - L + 1];
	int i = 0;
	int p1 = L;
	int p2 = mid + 1;
	while(p1 <= mid && p2 <= R){
		if(nums[p1] <= nums[p2]){
			help[i++] = nums[p1++];
		}else{
			help[i++] = nums[p2++];
		}
	}
	while(p1 <= mid){
		help[i++] = nums[p1++];
	}
	while(p2 <= R){
		help[i++] = nums[p2++];
	}
	for(int i = 0; i < help.length; i++){
		arr[L + i] = help[i];
	}
}
```

## 非递归的归并排序

```java
public void mergeSort2(int[] nums){
	判空省略
	int N = nums.length;
	
	int mergeSize = 1;
	while(mergeSize < N){
		int L = 0;
		while(L < N){
			int mid = L + mergeSize - 1;
			if(mid >= N){
				break;
			}
			int R = Math.min(mid + mergeSize, N - 1);
			merge(nums, L, mid, R);
			L = R + 1;
		}
		if(mergeSize > N / 2){
			break;
		}else{
			mergeSize <<= 1;
		}
	}
}
```

## 归并排序的复杂度分析

- 时间:O(nlogn)
- 空间:O(N)

## 小和问题

- 问题描述: 在一不数组中, 一个数左边比它小的数的总和, 叫数的小和, 所有数的小和累加起来, 叫数组小和。求数组小和。
- merge 时, 左组比有组小的地方, 计算小和;

```java
	public static int littleSum(int[] arr){
		if(arr == null || arr.length < 2){
			return 0;
		}
		
		return process(arr, 0, arr.length - 1 );
	}
	
	public static int process(int[] arr, int L, int R){
		if(L == R){
			return 0;
		}
		
		int mid = L + ((R - L) >> 1);
		//
		return process(arr, L, mid) + process(arr, mid + 1, R) + merge(arr, L, mid, R);
	}
	
	public static int merge(int[] arr, int L, int M , int R){
		int sum = 0;
		int[] help = new int[R - L + 1];
		int i = 0;
		int p1 = L;
		int p2 = M+1;
		while(p1 <= M && p2 <= R){
			if(arr[p1] < arr[p2]){
				//多了这一步
				sum = sum + arr[p1] * (R - p2 + 1);
			}
			help[i++] = arr[p1] < arr[p2] ? arr[p1++] : arr[p2++];
			
		}
		while(p1 <= M){
			help[i++] = arr[p1++];
		}
		while(p2 <= R){
			help[i++] = arr[p2++];
		}
		for (i = 0; i < help.length; i++) {
			arr[L + i] = help[i];
		}
		return sum;
	}
```

## 降序对问题

- 问题描述: 再数组中任意两数前数比后数大, 称为降序对.求降序对数量
-

```java
	public static int reversePair(int[] arr){
		if(arr == null || arr.length < 2){
			return 0;
		}
		
		return process(arr, 0, arr.length - 1);
	}
	
	public static int process(int[] arr, int L, int R){
		if(L == R){
			return 0;
		}
		int mid = L + ((R - L) >> 1);
		return process(arr, L, mid) 
				+ process(arr, mid + 1, R)
				+ merge(arr, L, mid, R);
	}
	
	public static int merge(int[] arr, int L, int M, int R){
		int result = 0;
		int i= 0;
		int[] help = new int[R - L + 1];
		int p1 = L;
		int p2 = M+1;
		while(p1 <= M && p2 <= R){
			if(arr[p1] > arr[p2]){
				result += M - p1 + 1;
			}
			help[i++] = arr[p1] > arr[p2] ? arr[p1++] : arr[p2++];
		}
		while(p1 <= M){
			help[i++] = arr[p1++];
		}
		while(p2 <= R){
			help[i++] = arr[p2++];
		}
		for(int j = 0; j < help.length; j++){
			arr[L+j] = help[j];
		}
		
		return result;
	}
```

# 随机快排 Partition

## Partition 过程 1

- 问题: 建立一个以 arr[R] 为标准的小于等于区
- 思路: 一开始将边界设在 L - 1, 如果满足条件, 则将 index 与 ++lessEqual 交换. 结果返回 lessEqual
- 代码:

```java
public int partition (int[] nums, int L, int R){
	if(L > R){
		return -1;
	}
	if(L == R){
		return L;
	}
	int lessEqual = L - 1;
	int index = L;
	while(index < R){
		if(nums[index] <= nums[R]){
			swap(nums, index, ++lessEqual);
		}
		index++;
	}
	return lessEqual;	
}
```

## Partition 过程 2(荷兰国旗问题)

- 问题: 三个区
- 思路:
	1. 初始: `lessEqual = L - 1; moreThan = R`, num 设置为 arr[R]
	2. index 从左边出发, 如果 arr[index] < num, 那么 swap(index, ++lessEqual), index++; 如果 arr[index] > num, 那么 swap(index, --moreThan), index 不变; 如果 arr[index] == num, 那么 index++;
	3. 最后 swap(moreThan, R)

```java
public int[] partition2(int[] arr, int L, int R){
	if(L > R){
		return new int[]{-1, -1};
	}
	if(L == R){
		return new int[]{L, L};
	}
	int lessIndex = L - 1;
	int moreIndex = R;
	int index = L;
	while(index < R){
		if(arr[index] < arr[R]){
			swap(arr, index, --moreIndex);
		}else if(arr[index] == arr[R]){
			index++;
		}else{
			swap(arr, index, lessIndex++);
		}
	}
	//最后处理一下边界
	swap(arr, moreIndex, R);
	return new int[]{lessIndex + 1, moreIndex}
}
```

## 快排的版本

## 快排 1.0 搞定一个数

```java
	public static void partitionSort1(int[] arr){
		if (arr == null || arr.length < 2){
			return;
		}
		
		process1(arr, 0, arr.length - 1);
	}
	
	public static void process1(int[] arr, int L, int R){
		if(L >= R){
			return;
		}
		//返回小于等于区的最大值, 就是已经安排好的那个数
		int M = partition(arr, L, R);
		process1(arr, L, M - 1);
		process1(arr, M + 1, R);
	}
```

## 快排 2.0 搞定一批数

```java
	public static void partitionSort2(int[] arr){
		if (arr == null || arr.length < 2){
			return;
		}
		process2(arr,0,arr.length -1);
	}
	
	public static void process2(int[] arr, int L, int R){
		if(L >= R){
			return ;
		}
		int[] equalArea = netherlandsFlag(arr, L, R);
		process2(arr, L, equalArea[0] - 1);
		process2(arr, equalArea[1] + 1, R);
	}
```

## 快排 3.0 随机选一个数搞定一批数 (随机快排)

找到数组的随机下标 (int)Math.random() * (R - L + 1), 并交换; 然后再进行荷兰过程的排序;

```java
	public static void partitionSort3(int[] arr) {
		if (arr == null || arr.length < 2) {
			return;
		}
		process3(arr, 0, arr.length - 1);
	}
	
	public static void process3(int[] arr, int L, int R) {
		if (L >= R) {
			return;
		}
		//先交换, 再做这个动作
		swap(arr, L + (int) (Math.random() * (R - L + 1)), R);
		int[] equalArea = netherlandsFlag(arr, L, R);
		process3(arr, L, equalArea[0] - 1);
		process3(arr, equalArea[1] + 1, R);
	}
```

### 随机快排的复杂度推算

### 复杂度结论

- 时间: O(N * logN)
- 空间: O(N)
