/*
（7）假设以数组 Q[m] 存放循环队列中的元素，同时设置一个标志 tag，以 tag == 0 和 tag == 1
来区别在队头指针（front）和队尾指针（rear）相等时，队列状态是“空”还是“满”。试编写与此
结构相应的插入（enqueue）和删除（dequeue）算法。
*/
#include <iostream>
using namespace std;

typedef struct
{
    int *Q;    //队列数组
    int front; //队头指针
    int rear;  //队尾指针
    int tag;   //标志：0 表示最近一次操作是出队，1 表示最近一次操作是入队
    int m;     //队列最大可容纳的元素个数
} CyQueue;

void Init(CyQueue &S, int m) {
    S.Q = new int[m];
    S.m = m;
    S.front = S.rear = 0;
    S.tag = 0; //初始时是空队列
}

//front == rear 且 tag == 0：上次是出队，说明队列空
bool isEmpty(CyQueue S) {
    return S.front == S.rear && S.tag == 0;
}

//front == rear 且 tag == 1：上次是入队，说明队列满
bool isFull(CyQueue S) {
    return S.front == S.rear && S.tag == 1;
}

bool EnQueue(CyQueue &S, int data) {
    if (isFull(S))
        return false;
    S.Q[S.rear] = data;          //先放元素
    S.rear = (S.rear + 1) % S.m; //队尾后移，到末尾就绕回 0
    S.tag = 1;                   //这次是入队
    return true;
}

bool DeQueue(CyQueue &S, int &data) {
    if (isEmpty(S))
        return false;
    data = S.Q[S.front];           //先取元素
    S.front = (S.front + 1) % S.m; //队头后移，到末尾就绕回 0
    S.tag = 0;                     //这次是出队
    return true;
}
