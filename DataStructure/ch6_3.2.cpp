#include <iostream>
using namespace std;

/* ========================= 一、类型定义 ========================= */

const int MVNum = 100;
/* ↑ 数组【容量】上限。注意区分：
      MVNum  = 数组最多能装几个（常量，100）
      vexnum = 这张图实际有几个（变量，比如 6）
   声明数组用 MVNum，所有循环用 vexnum。 */

using VerTexType = char;
/* ↑ 顶点数据类型。想换成字符串/整数，只改这一行即可（C++11 起可用）。
   对应教材的 typedef char VerTexType; */

struct ArcNode {
    int adjvex;
    /* ↑ 邻接点在顶点表中的【下标】，是个 int，不是字符。
         读作"这条边通向第 adjvex 号顶点"。
         注意：它不表达方向——方向由"这个结点挂在谁的表里"决定。 */

    ArcNode *nextarc;
    /* ↑ 同源的下一条边。它只负责串起链表，【不代表图里的一条边】。
         C++ 里可以直接写 ArcNode*；C 语言必须写 struct ArcNode* */
};

struct VNode {
    VerTexType data;
    /* ↑ 顶点名，如 'A'。算法内部只用下标，名字只在输入输出时用。 */

    ArcNode *firstarc;
    /* ↑ 表头指针：指向这个顶点的【第一条边】。
         它是整条链表的唯一入口，一旦被覆盖，旧链就找不回来了。 */
};

struct ALGraph {
    VNode vertices[MVNum];
    /* ↑ 顶点表：本质是 VNode 数组，容量 MVNum。
         写法 B（教材）：AdjList vertices;  其中 AdjList = VNode[MVNum]
         两种完全等价，这里直接用数组，读起来更直白。 */

    int vexnum, arcnum;
    /* ↑ 实际顶点数、实际边数（无向图 arcnum 是【边数】，不是 2e） */
};

/* ========================= 二、辅助函数 ========================= */

int LocateVex(const ALGraph &G, VerTexType u)
/* 作用：输入顶点【名字】，返回它的【下标】；找不到返回 -1。
   算法内部一律用下标，因为数组只能按下标定位。
   const & 表示"只读引用"：不拷贝整张图，也不许修改它。 */
{
    for (int i = 0; i < G.vexnum; ++i)      /* 只查前 vexnum 个，不是 MVNum 个 */
        if (G.vertices[i].data == u) return i;
    return -1;                              /* ★ 调用方必须检查 -1，否则会越界访问 */
}

/* ========================= 三、建图 ========================= */

void CreateUDG(ALGraph &G)
/* 建无向图（邻接表，头插法）。
   输入格式：vexnum arcnum / 各顶点名 / 每条边的两个顶点名
   ★ 用 &G 是因为要修改 G，值传递改不到外面。 */
{
    cin >> G.vexnum >> G.arcnum;
    /* 先读规模，后面的循环全靠这两个数控制次数 */

    for (int i = 0; i < G.vexnum; ++i) {
        cin >> G.vertices[i].data;          /* 读顶点名 */
        G.vertices[i].firstarc = nullptr;   /* ★ 必须置空！
                                               局部变量的内存是随机残留值，
                                               不置空就是野指针，遍历时必崩 */
    }

    for (int k = 0; k < G.arcnum; ++k) {
        VerTexType v1, v2;
        cin >> v1 >> v2;                    /* 读一条边的两个【名字】 */

        int i = LocateVex(G, v1);           /* 名字 → 下标 */
        int j = LocateVex(G, v2);

        /* ---- 第一遍：把 j 挂到 i 的表里，表示"i 的邻居有 j" ---- */
        ArcNode *p1 = new ArcNode;
        p1->adjvex = j;                     /* ① 这条边通向 j */
        p1->nextarc = G.vertices[i].firstarc;  /* ② 新结点接住旧的链表 */
        G.vertices[i].firstarc = p1;        /* ③ 表头改指新结点 */
        /* ★ ②③ 顺序不能反：先改表头，旧链就丢了，内存泄漏 + 数据丢失。
              这就是"先接后断"。 */

        /* ---- 第二遍：把 i 挂到 j 的表里，表示"j 的邻居有 i" ---- */
        ArcNode *p2 = new ArcNode;
        p2->adjvex = i;                     /* 存的是 i（和第一遍相反） */
        p2->nextarc = G.vertices[j].firstarc;
        G.vertices[j].firstarc = p2;
        /* ★ 无向图必须建两个结点。只建一个 → 建出来的其实是有向图。 */
    }
}
void DFS_NonRecursive(const ALGraph &G, int v)
/* 思路：递归版 DFS 干的是"访问 u → 找第一个未访问的邻居 w → 递归 w"。
   用栈模拟时，核心是这一句：
   ★ 栈里存的是"正在处理、还没处理完"的顶点，栈顶【只读不弹】。
     它只是暂时卡在"等孩子回来"，等它的邻居全访问完才弹出。 */
{
    bool visited[MVNum] = {false};
    /* 访问标记。= {false} 能整数组清零（因为 false 就是 0，命中"其余补 0"的特例） */

    int stack[MVNum];                       /* 手工栈，顶多 n 个顶点同时在里面 */
    int top = -1;                           /* 空栈：top 是"栈顶元素的下标"，-1 表示没有 */

    /* ---- 起点：先输出 → 再标记 → 再入栈（三步顺序有讲究）---- */
    cout << G.vertices[v].data << " ";      /* ★ 先输出，漏了这行结果就少一个顶点 */
    visited[v] = true;                      /* ★ 必须在入栈前标记，否则会重复入栈 */
    stack[++top] = v;                       /* ++top 是"先加后取"：top 变 0，再写入 */

    while (top >= 0)                        /* 栈空（top == -1）就结束 */
    {
        int u = stack[top];
        /* ★ 只读，不弹出。写成 stack[top--] 就变成"用栈跑 BFS"，顺序全错 */

        ArcNode *p = G.vertices[u].firstarc;    /* 从 u 的边链表头开始找 */

        while (p != nullptr && visited[p->adjvex])
            p = p->nextarc;
        /* ★ 这行有两个要点：
           ① 条件顺序不能反：先判 nullptr，再取 p->adjvex，
              反了就是"解引用空指针"，程序直接崩溃
           ② 每次回溯后都从头扫，最坏 O(n·e)；要 O(n+e) 得在栈里
              同时存"扫到哪条边了" */

        if (p != nullptr)                   /* 找到了一个没访问过的邻居 */
        {
            int w = p->adjvex;              /* 邻居的下标 */
            cout << G.vertices[w].data << " ";  /* 先输出 */
            visited[w] = true;                  /* 再标记 */
            stack[++top] = w;                   /* 再入栈，继续往深处走 */
            /* ★ 此时 u 【还留在栈里】，等 w 那条支路走完再回来处理 u 的下一分支 */
        }
        else                                /* 一个没访问过的邻居都没有 */
        {
            --top;
            /* ★ 回溯：弹出栈顶，回到上一层。
               漏了这句 → 栈顶永远卡在同一个点 → 死循环 */
        }
    }
}