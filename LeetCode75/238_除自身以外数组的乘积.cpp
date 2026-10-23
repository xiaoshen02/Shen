/*
给你一个整数数组 nums，返回 数组 answer ，其中 answer[i] 等于 nums 中除了 nums[i] 之外其余各元素的乘积 。
题目数据 保证 数组 nums之中任意元素的全部前缀元素和后缀的乘积都在  32 位 整数范围内。
请 不要使用除法，且在 O(n) 时间复杂度内完成此题
*/

#include <iostream>
#include <vector>
using namespace std;
class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums) {
        int n = nums.size();
        vector<int>left(n,1);
        for(int i=1;i<n;++i){
            left[i]=left[i-1]*nums[i-1];
        }
        vector<int>right(n,1);
        for(int i=n-2;i>=0;--i){
            right[i]=right[i+1]*nums[i+1];
        }
        vector<int>ans(n);
        for(int i=0;i<n;++i){
            ans[i]=left[i]*right[i];
        }
        return ans;
    }
};

//左侧乘积乘右侧乘积