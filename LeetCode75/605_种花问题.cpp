/*
假设有一个很长的花坛，一部分地块种植了花，另一部分却没有。可是，花不能种植在相邻的地块上，它们会争夺水源，两者都会死去。
给你一个整数数组 flowerbed 表示花坛
由若干 0 和 1 组成，其中 0 表示没种植花，1 表示种植了花。
另有一个数 n ，能否在不打破种植规则的情况下种入 n 朵花？能则返回 true ，不能则返回 false 。
*/
#include<iostream>
#include<vector>
using namespace std;

class Solution {
public:
    bool canPlaceFlowers(vector<int>& flowerbed, int n) {
        int p = flowerbed.size();
        int cnt = 0;

        for (int i = 0; i < p; ++i) {
            if (flowerbed[i] == 0 && i == 0 && (p == 1 || flowerbed[i + 1] == 0)) {// 处理花坛只有一个地块的情况
                flowerbed[i] = 1;
                cnt++;
            }
            else if (flowerbed[i] == 0 && i == p - 1 && flowerbed[i - 1] == 0) {// 处理花坛最后一个地块的情况
                flowerbed[i] = 1;
                cnt++;
            }
            else if (flowerbed[i] == 0 && i > 0 && i < p - 1 &&
                     flowerbed[i - 1] == 0 && flowerbed[i + 1] == 0) {// 处理花坛中间的地块的情况
                flowerbed[i] = 1;
                cnt++;
            }
        }

        return cnt >= n;
    }
};


/*
class Solution {
public:
    bool canPlaceFlowers(vector<int>& flowerbed, int n) {
        int m = flowerbed.size();

        for (int i = 0; i < m; ++i) {
            if (flowerbed[i] == 0 &&
                (i == 0 || flowerbed[i - 1] == 0) &&
                (i == m - 1 || flowerbed[i + 1] == 0)) {
                flowerbed[i] = 1;
                n--;
            }
            if (n <= 0) return true;
        }
        return false;
    }
};
*/
