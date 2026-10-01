/*
给你两个字符串 word1 和 word2 。请你从 word1 开始，通过交替添加字母来合并字符串。如果一个字符串比另一个字符串长，就将多出来的字母追加到合并后字符串的末尾。
返回 合并后的字符串 。
*/
#include<iostream>
#include<string>
using namespace std;
class Solution {
public:
    string mergeAlternately(string word1, string word2) {
        int l1=word1.length();
        int l2=word2.length();
        string word;
        int i=0;
        while(i<l1 && i<l2){
            word+=word1[i];
            word+=word2[i];
            i++;
        }
        if(l1>l2){
            for(int j=i;j<l1;++j){
                word+=word1[j];
            }
        }
        else{
            for(int j=i;j<l2;++j){
                word+=word2[j];
            }
        }



        return word;
    }
};