/*
给你一个字符串s,请你反转字符串中 单词 的顺序。
单词 是由非空格字符组成的字符串。
返回 单词 顺序颠倒且 单词 之间用单个空格连接的结果字符串。
注意:输入字符串 s中可能会存在前导空格、尾随空格或者单词间的多个空格。返回的结果字符串中,单词间应当仅用单个空
格分隔,且不包含任何额外的空格。
s 中使用至少一个空格将字符串中的单词 分隔开。
*/

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;


class Solution {
public:
    string reverseWords(string s) {
        vector<string> words;
        int len = s.size();
        int i = 0;

        // 这种写法是修正后的思路：先跳过前导空格和连续空格，再提取单词
        while (i < len) {
            while (i < len && s[i] == ' ') {
                i++;  // 跳过空格：忽略前导空格、尾随空格和多个空格
            }
            if (i >= len) {
                break;
            }

            int j = i;
            while (j < len && s[j] != ' ') {
                j++;
            }
            words.push_back(s.substr(i, j - i));
            i = j;
        }

        reverse(words.begin(), words.end());//把一个区间里的元素反过来

        string ans;
        for (int k = 0; k < words.size(); k++) {
            if (k > 0) {
                ans += ' ';
            }
            ans += words[k];
        }

        return ans;
    }
};
