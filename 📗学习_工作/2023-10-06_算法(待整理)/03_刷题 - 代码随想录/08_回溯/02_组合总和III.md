---
date: 2024-09-07
mtime: 2024-09-25
---

# 216. 组合总和 III

```java
class Solution {
    List<Integer> path = new ArrayList<>();
    List<List<Integer>> res = new ArrayList<>();
    public List<List<Integer>> combinationSum3(int k, int n) {
        backTracing(n, k, 1, 0);
        return res;
    }

    public void backTracing(int target, int k, int startIndex, int sum){
        if(sum >target){
            return;
        }
        if(path.size() == k){
            if(sum == target){
                res.add(new ArrayList<>(path));
                return;
            }
        }
        //剩下的数字要够凑满k个, sum的条件已经在函数头进行判断过了.
        for(int i = startIndex; 9 - i + 1 >= k - path.size(); i++){
            path.add(i);
            sum += i;
            backTracing(target, k, i + 1, sum);
            sum -= i;
            path.remove(path.size() - 1);
        }
    }
}
```
