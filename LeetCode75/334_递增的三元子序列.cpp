/*
给你一个整数数组 nums ，判断这个数组中是否存在长度为 3 的递增子序列。
如果存在这样的三元组下标 (i, j, k) 且满足 i < j < k ，使得 nums[i] < nums[j] < nums[k] ，返回 true ；否则，返回 false 
*/
#include <iostream>
#include <vector>
#include <climits>
using namespace std;
class Solution {
public:
    bool increasingTriplet(vector<int>& nums) {
        int len= nums.size();
        int first=INT_MAX,second=INT_MAX;
        for(int i=0;i<len;++i){
            if(nums[i]<=first){
                first=nums[i];
            }else if(nums[i]<=second){
                second=nums[i];
            }else{
                return true;
            }
        }
        return false;
    }
};