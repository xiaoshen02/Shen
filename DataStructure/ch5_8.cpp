#include<iostream>
#include<cstdio>
using namespace std;

typedef char TElemType;

typedef struct BiTNode
{
    TElemType data;
    struct BiTNode *lchild, *rchild;
} BiTNode, *BiTree;

void Path(BiTree T, TElemType path[], int depth)
{
    if (T == NULL) return;

    path[depth] = T->data;

    if (T->lchild == NULL && T->rchild == NULL)
    {
        for (int i = depth; i >= 0; i--)
        {
            printf("%c", path[i]);
            if (i > 0) printf(" -> ");
        }
        printf("\n");
        return;
    }
    Path(T->lchild, path, depth + 1);
    Path(T->rchild, path, depth + 1);
}
