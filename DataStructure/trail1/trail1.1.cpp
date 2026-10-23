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

int main() {
    vector < Book > book;
    string id, name;
    double price;
    while (cin >> id >> name >> price) {
        if (id == "0" && name == "0" && price == 0) break;
        book.push_back({
            id,
            name,
            price
        });

    }

    cout << book.size() << endl;
    cout << fixed << setprecision(2);
    for (size_t i = 0; i < book.size(); ++i) {
        cout << book[i].id << ' ' << book[i].name << ' ' << book[i].price << endl;
    }
    return 0;
}