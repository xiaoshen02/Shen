/*
（10）已知 f 为单链表的表头指针，链表中存储的都是整型数据，试写出实现下列运算的
递归算法：
① 求链表中的最大整数；
② 求链表的结点个数；
③ 求所有整数的平均值。
*/
#include <iostream>
using namespace std;

typedef struct LNode
{
    int data;           //数据域
    struct LNode *next; //指针域
} LNode, *LinkList;

//① 求链表中的最大整数（按不带头结点的单链表写，f 指向第一个数据结点）
int Max(LinkList f) {
    if (f == NULL)
        return 0; //空表没有最大值，返回 0
    if (f->next == NULL)
        return f->data; //只有一个结点，它就是最大
    int m = Max(f->next); //先求出后面所有结点的最大值
    return f->data > m ? f->data : m;
}

//② 求链表的结点个数
int Count(LinkList f) {
    if (f == NULL)
        return 0;
    return 1 + Count(f->next); //本结点 + 后面所有结点
}

//③ 求所有整数的平均值，n 为结点个数（用 Count(f) 得到）
//   递推式：前 n 个结点的平均值 = (后 n-1 个结点的平均值 × (n-1) + 第一个结点的值) / n
double Average(LinkList f, int n) {
    if (f == NULL || n <= 0)
        return 0;
    if (f->next == NULL)
        return (double)f->data / n; //尾结点，此时 n 为 1
    return (Average(f->next, n - 1) * (n - 1) + f->data) / n;
}
