/*
给你一个字符串 s ，仅反转字符串中的所有元音字母，并返回结果字符串。
元音字母包括 'a'、'e'、'i'、'o'、'u'，且可能以大小写两种形式出现不止一次。
*/

#include<iostream>
#include<string>
#include<vector>
using namespace std;
class Solution {
public:
    string reverseVowels(string s) {
        vector<char>ss;
        for(int i=0;i<s.size();i++){
            if(s[i]=='a'||s[i]=='e'||s[i]=='i'||s[i]=='o'||s[i]=='u'||s[i]=='A'||s[i]=='E'||s[i]=='I'||s[i]=='O'||s[i]=='U'){
                ss.push_back(s[i]);
            }
        }
        int len=ss.size();
        for(int i=0;i<len/2;i++){
            swap(ss[i],ss[len-1-i]);
        }
        for(int i=0,j=0;i<s.size();i++){
            if(s[i]=='a'||s[i]=='e'||s[i]=='i'||s[i]=='o'||s[i]=='u'||s[i]=='A'||s[i]=='E'||s[i]=='I'||s[i]=='O'||s[i]=='U'){
                s[i]=ss[j++];
            }
        }
        return s;
    }
};

/*
优化思路：双指针直接交换元音字母，不需要额外存储所有元音数组。
思路如下：
1. left 指向字符串左边，right 指向字符串右边；
2. 从左往右找到第一个元音，从右往左找到最后一个元音；
3. 如果两者都存在，则交换它们；
4. 继续向中间靠拢，直到 left >= right。

时间复杂度：O(n)
空间复杂度：O(1)

class Solution {
public:
    bool isVowel(char c) {
        c = tolower(c);
        return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
    }

    string reverseVowels(string s) {
        int left = 0, right = s.size() - 1;

        while (left < right) {
            while (left < right && !isVowel(s[left])) {
                left++;
            }
            while (left < right && !isVowel(s[right])) {
                right--;
            }

            if (left < right) {
                swap(s[left], s[right]);
                left++;
                right--;
            }
        }

        return s;
    }
};
*/
//优化版
