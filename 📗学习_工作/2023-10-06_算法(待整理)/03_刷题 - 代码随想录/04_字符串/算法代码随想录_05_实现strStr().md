---
date: 2024-09-07
mtime: 2024-09-25
---

# 28.实现 strStr()

```java
//手撕KMP
class Solution {
	public int strStr(String haystack, String needle) {
		if(needle == null || needle.length() == 0){
			return 0;
		}
		if(haystack == null || haystack.length() == 0 || haystack.length() < needle.length()){
			return -1;
		}
		int i1 = 0;
		int i2 = 0;
		char[] str1 = haystack.toCharArray();
		char[] str2 = needle.toCharArray();
		int[] next = getNextArray(str2);
		while(i1 < str1.length && i2 < str2.length){
			if(str1[i1] == str2[i2]){
				i1++;
				i2++;
			}else if(i2 == 0){
				i1++;
			}else{
				i2 = next[i2];
			}
		}
		return i2 == str2.length ? i1 - i2 : -1;
	}
	public int[] getNextArray(char[] arr){
		if(arr.length == 1){
			return new int[]{-1};
		}
		int[] next = new int[arr.length];
		next[0] = -1;
		next[1] = 0;
		int i = 2;
		int cn = 0;
		while(i < arr.length){
			if(arr[i - 1] == arr[cn]){
				next[i++] = ++cn;
			}else if(cn > 0){
				cn = next[cn];
			}else{
				next[i++] = 0;
			}
		}
		return next;
	}
}
```
