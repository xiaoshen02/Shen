#include<iostream>
using namespace std;

typedef char TElemType;

typedef struct BiTNode
{
    TElemType data;
    struct BiTNode *lchild, *rchild;
} BiTNode, *BiTree;

int IsEqual(BiTree T1, BiTree T2)
{
    if (T1 == NULL || T2 == NULL) return T1 == T2;   // 一个空一个不空 → 不相等；都空 → 相等
    if (T1->data != T2->data)     return 0;
    return IsEqual(T1->lchild, T2->lchild) && IsEqual(T1->rchild, T2->rchild);
}
