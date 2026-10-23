/*
对于字符串 s 和 t，只有在 s = t + t + t + ... + t + t（t 自身连接 1 次或多次）时，我们才认定 “t 能除尽 s”。

给定两个字符串 str1 和 str2 。返回 最长字符串 x，要求满足 x 能除尽 str1 且 x 能除尽 str2 

*/
#include<iostream>
#include<numeric>//gcd()函数需要头文件<numeric>
#include<string>
using namespace std;

class Solution {
public:
    string gcdOfStrings(string str1, string str2) {
        int l1=str1.size();
        int l2=str2.size();
        int len=std::gcd(l1,l2);//计算两个数的最大公约数
        if (len == 0) {
            return "";
        }

        string str=str1.substr(0,len);
        for (int i=0; i<l1/len; i++) {
            if (str != str1.substr(i*len,len)) {
                return "";
            }
        }
        for (int i=0; i<l2/len; i++) {
            if (str != str2.substr(i*len,len)) {
                return "";
            }
        }
        return str;
    }
};
//不需要遍历，只要取最大公约数的字母就行了
//另一种方法
/*
string gcdOfStrings(string str1, string str2) {
    if (str1 + str2 != str2 + str1) {
        return "";
    }
    size_t len = std::gcd(str1.size(), str2.size());
    return str1.substr(0, len);
}
*/