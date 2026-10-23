#include<iostream>

#include<iomanip>

#include<vector>

#include<string>

using namespace std;
struct Book {
    string id;
    string name;
    double price;
};

void select(vector < Book > & b) {
    for (size_t i = 0; i + 1 < b.size(); ++i) {
        size_t k = i;
        for (size_t j = i + 1; j < b.size(); ++j) {
            if (b[j].price >b[k].price) {
                k = j;
            }

        }
        if (k != i) {
            Book temp = b[k];
            for(size_t m=k;m>i;--m)
            {
              b[m]=b[m-1];
            }
            b[i] = temp;
        }
    }
}
int main() {
    vector < Book > book;
    string id, name;
    double price;
    while (cin >> id >> name >> price) {
        if (id == "0" && name == "0" &&
            price == 0) {
            break;
        }
        book.push_back({
            id,
            name,
            price
        });
    }
    select(book);
    
    cout << fixed << setprecision(2);
    for (size_t i = 0; i < book.size(); ++i) {
        cout << book[i].id << ' ' << book[i].name << ' ' << book[i].price << endl;
    }
    return 0;
}