/*
（7）假设以数组 Q[m] 存放循环队列中的元素，同时设置一个标志 tag，以 tag == 0 和 tag == 1
来区别在队头指针（front）和队尾指针（rear）相等时，队列状态是“空”还是“满”。试编写与此
结构相应的插入（enqueue）和删除（dequeue）算法。
*/
#include <iostream>
using namespace std;

typedef struct
{
    int *Q;
    int front;
    int rear;
    int tag; //0 = 上次是出队（front == rear 时为空），1 = 上次是入队（front == rear 时为满）
    int m;
} CyQueue;

void Init(CyQueue &S, int m) {
    S.Q = new int[m];
    S.m = m;
    S.front = S.rear = 0;
    S.tag = 0;
}

bool isEmpty(CyQueue S) {
    return S.front == S.rear && S.tag == 0;
}

bool isFull(CyQueue S) {
    return S.front == S.rear && S.tag == 1;
}

bool EnQueue(CyQueue &S, int data) {
    if (isFull(S))
        return false;
    S.Q[S.rear] = data;
    S.rear = (S.rear + 1) % S.m;
    S.tag = 1;
    return true;
}

bool DeQueue(CyQueue &S, int &data) {
    if (isEmpty(S))
        return false;
    data = S.Q[S.front];
    S.front = (S.front + 1) % S.m;
    S.tag = 0;
    return true;
}
