/*
  将编号为 0 和 1 的两个栈存放于一个数组空间 V[m] 中，栈底分别处于数组的两端。当
第 0 号栈的栈顶指针 top[0] 等于 −1 时该栈为空 ；当第 1 号栈的栈顶指针 top[1] 等于 m 时，该栈
为空。两个栈均从两端向中间填充（见图 3.23）。试编写双栈初始化，判断栈空、栈满、进栈和
出栈等算法的函数。双栈数据结构的定义如下 ：
typedef struct
{
 int top[2], bot[2]; //栈顶和栈底指针
 SElemType *V; //栈数组
 int m; //栈最大可容纳的元素个数
}DblStack;

*/
#include <iostream>
using namespace std;

typedef struct
{
    int top[2], bot[2]; //栈顶和栈底指针
    int *V; //栈数组
    int m; //栈最大可容纳的元素个数
}DblStack;
bool Init(DblStack &S,int m){
    S.V=new int[m];
    S.m=m;
    S.top[0]=S.bot[0]=-1;
    S.top[1]=S.bot[1]=m;
    return true;
}

bool isEmpty(DblStack S,int i){
    if(i==0){
        return S.top[0]==-1;
    }else{
        return S.top[1]==S.m;
    }
    return false;
}

bool isFull(DblStack S){
    return S.top[0]+1==S.top[1];
}

bool Push(DblStack &S,int i,int data){
    if(isFull(S))
        return false;
        if(i==0){
            S.V[++S.top[0]]=data;
        }
        else if(i==1){
            S.V[--S.top[1]]=data;
        }
        return true;
}

bool Pop(DblStack& S,int i){
    int data;
    if(isEmpty(S,i))
        return false;
    if(i==0){
        data=S.V[S.top[0]--];
    } 
    else if(i==1){
        data=S.V[S.top[1]++];
    }
    return true;
}