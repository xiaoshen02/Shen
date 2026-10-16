/*
给定一个数组 nums，编写一个函数将所有 0 移动到数组的末尾，同时保持非零元素的相对顺序。
请注意 ，必须在不复制数组的情况下原地对数组进行操作。
*/
#include <iostream>
#include <vector>
using namespace std;
class Solution {
public:
    void moveZeroes(vector<int>& nums) {
        int len = nums.size();
        int i = 0, j = 0;     
        for (i = 0; i < len; ++i) {
            if (nums[i] != 0) {
                nums[j] = nums[i]; 
                ++j;
            }
        }
        while (j < len) {        
            nums[j] = 0;
            ++j;
        }
    }
};