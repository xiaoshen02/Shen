/*
有 n 个有糖果的孩子。给你一个数组 candies，其中 candies[i] 代表第 i 个孩子拥有的糖果数目，
和一个整数 extraCandies 表示你所有的额外糖果的数量。
返回一个长度为 n 的布尔数组 result，如果把所有的 extraCandies 给第 i 个孩子之后，
他会拥有所有孩子中 最多 的糖果，那么 result[i] 为 true，否则为 false。
注意，允许有多个孩子同时拥有 最多 的糖果数目。
*/
#include<iostream>
#include<vector>
using namespace std;
class Solution {
public:
    vector<bool> kidsWithCandies(vector<int>& candies, int extraCandies) {
        int n = candies.size();
        vector<bool> result;
        for(int j=0;j<n;++j){
            bool hasMostCandies = true;
            for(int k=0;k<n;++k){
                if(candies[j] + extraCandies < candies[k]){
                    hasMostCandies = false;
                    break;
                }
            }
            result.push_back(hasMostCandies);
        }
        return result;
    }
  
};

/* 正确写法（注释版，取消注释后使用）
#include <algorithm>

class Solution {
public:
    vector<bool> kidsWithCandies(vector<int>& candies, int extraCandies) {
        int maxCandies = *max_element(candies.begin(), candies.end());
        vector<bool> result;

        for (int candy : candies) {
            result.push_back(candy + extraCandies >= maxCandies);
        }

        return result;
    }
};
*/