#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
};

void print(Node* head) {
    Node* p = head->next;
    while (p != NULL) {
        cout << p->data;
        if (p->next != NULL) cout << ' ';
        p = p->next;
    }
    cout << '\n';
}

void freelist(Node* head) {
    while (head != NULL) {
        Node* temp = head;
        head = head->next;
        delete temp;
    }
}

int main() {
    int n;
    while (cin >> n && n != 0) {
        Node* head1 = new Node{0, NULL};
        Node* tail1 = head1;
        Node* head2 = new Node{0, NULL};
        Node* tail2 = head2;

        for (int i = 0; i < n; ++i) {
            int x;
            cin >> x;

            if (x < 0) {
                tail1->next = new Node{x, NULL};
                tail1 = tail1->next;
            } else if (x > 0) {
                tail2->next = new Node{x, NULL};
                tail2 = tail2->next;
            }
        }

        print(head1);
        print(head2);

        freelist(head1);
        freelist(head2);
    }
    return 0;
}