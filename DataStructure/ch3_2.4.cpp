/*
从键盘上输入一个后缀表达式，试设计算法计算表达式的值。规定 ：逆波兰表达
式的长度不超过一行，输入以“$”作为结束，操作数之间用空格分隔，操作符只可能有
“+”“−”“*”“/”4 种。例如 ：234 34 + 2*$。
*/

#include <iostream>
#include <string>
#include <sstream>
using namespace std;

#define MAXSIZE 100

struct Stack {
    int data[MAXSIZE];
    int top;                // 指向下一个空位
};

void InitStack(Stack& s) { s.top = 0; }

int Push(Stack& s, int x) {       
    if (s.top == MAXSIZE) return 0;
    s.data[s.top++] = x;
    return 1;
}

int Pop(Stack& s, int& x) {       
    if (s.top == 0) return 0;
    x = s.data[--s.top];
    return 1;
}

int main() {
    Stack s;
    InitStack(s);

    string line;
    getline(cin, line);

    /* 预处理：给运算符和 $ 前后补空格 */
    string fixed;
    for (size_t i = 0; i < line.size(); ++i) {
        char ch = line[i];
        if (ch == '+' || ch == '-' || ch == '*' || ch == '/' || ch == '$') {
            fixed += ' '; fixed += ch; fixed += ' ';
        } else {
            fixed += ch;
        }
    }

    istringstream iss(fixed);
    string token;

    while (iss >> token) {
        if (token == "$") break;

        if (token == "+" || token == "-" || token == "*" || token == "/") {
            int a, b, result;

            if (!Pop(s, b) || !Pop(s, a)) {      // 先弹 = 右操作数 b，后弹 = 左 a
                cout << "错误 "<< endl;
                return 1;
            }

            if      (token == "+") result = a + b;
            else if (token == "-") result = a - b;   
            else if (token == "*") result = a * b;
            else {
                if (b == 0) {
                    cout << "除数为 0" << endl;
                    return 1;
                }
                result = a / b;
            }
            Push(s, result);
        }
        else {
            Push(s, stoi(token));    //stoi把字符串类型的整数转化为int类型的整数          
        }
    }

    if (s.top != 1) {                           
        return 1;
    }

    cout << s.data[s.top - 1] << endl;
    return 0;
}