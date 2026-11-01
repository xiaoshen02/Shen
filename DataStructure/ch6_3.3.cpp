#include<iostream>
using namespace std;

struct ArcNode{
    int adjvex;
    ArcNode*nextarc;
};

struct VNode{
    ArcNode*firstarc;
    int data;
};

struct ALGraph{
    VNode vertices[100];
    int vexnum,arcnum;
};
int FarthestVertex(const ALGraph &G, int v)
/* 思路：拆成两件事
     ① 求 v 到其余各点的最短距离 → BFS
     ② 在这些距离里挑最大的那个点 → 遍历一遍

   ★ 为什么用 BFS 不用 Dijkstra？
     题目说"图 G"，默认【无权图】，每条边代价都是 1。
     无权图的最短路径 = 最少经过几条边，而 BFS 按层展开，
     第 k 层正好就是距离为 k 的顶点 —— 天然有序。
     （若改成带权网，就换 Dijkstra，骨架不动，只改距离的计算方式）

   ★ 为什么不用 DFS？
     DFS 的"第一次到达"不保证最短，它只保证"走到了"。 */
{
    int dist[MVNum];
    for (int i = 0; i < MVNum; ++i) dist[i] = -1;
    /* ★ 用 -1 表示"还没到达"。
       不能用 0：0 会和"源点距离 0"冲突，导致源点被重复处理。
       ★ 也不能写 int dist[MVNum] = {-1}：那只会把第一个元素设成 -1，
         其余自动补 0（C/C++ 的"其余补 0"规则），必须用循环。 */

    int queue[MVNum];
    int front = 0, rear = 0;
    /* 手工队列：front 指向队头，rear 指向"下一个空位"。
       front == rear 表示队空（这里用数组不会真满，故不判满）。 */

    dist[v] = 0;                            /* 源点到自己的距离是 0 */
    queue[rear++] = v;                      /* 源点入队。rear++ 是"先用后加" */

    while (front < rear)                    /* 队不空 */
    {
        int u = queue[front++];             /* ★ 出队。这里是真弹出，和 DFS 的"只读"相反 */

        for (ArcNode *p = G.vertices[u].firstarc; p != nullptr; p = p->nextarc)
        {
            int w = p->adjvex;
            if (dist[w] == -1)              /* 第一次到达 → 这就是最短距离 */
            {
                dist[w] = dist[u] + 1;      /* ★ 一层加一，加的就是"边数" */
                queue[rear++] = w;
                /* ★ 入队的同时就标记（上一行已经写了 dist），
                   不要在"出队时"才标记，否则同一个点会被多个邻居重复入队 */
            }
        }
    }

    int best = v, maxd = 0;
    /* ★ maxd 从 0 起：如果图只有一个顶点，循环一次都不更新，
       返回它自己（距离 0）才是正确答案。 */

    cout << "从 " << G.vertices[v].data << " 出发各顶点距离：";
    for (int i = 0; i < G.vexnum; ++i)      /* 再扫一遍，取最大值 */
    {
        cout << G.vertices[i].data << "=" << dist[i] << "  ";   /* 把距离打出来，便于核对 */
        if (dist[i] > maxd)                 /* 严格大于才换，距离相同的保留先出现的 */
        {
            maxd = dist[i];
            best = i;
        }
    }
    cout << "\n最大距离 = " << maxd << endl;
    /* ★ 这个循环不能省，也不能用"最后一个出队的点"代替：
       ① 最远层可能有多个点，最后一个出队的只是其中一个
       ② 若图不连通（dist = -1 的点存在），情况更复杂 */

    return best;                            /* 返回下标，外面用 G.vertices[best].data 取名字 */
}
