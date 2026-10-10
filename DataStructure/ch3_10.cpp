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
    int data;
    struct LNode *next;
} LNode, *LinkList;

int Max(LinkList f) {
    if (f == NULL)
        return 0;
    int m = f->data;
    for (LinkList p = f->next; p != NULL; p = p->next) {
        if (p->data > m)
            m = p->data;
    }
    return m;
}

int Count(LinkList f) {
    if (f == NULL)
        return 0;
    return 1 + Count(f->next);
}

double Average(LinkList f, int n) {
    if (f == NULL || n <= 0)
        return 0;
    if (f->next == NULL)
        return (double)f->data / n;
    return (Average(f->next, n - 1) * (n - 1) + f->data) / n;
}
