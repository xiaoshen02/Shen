#include<iostream>
#include<iomanip>
#include<vector>
#include<string>
using namespace std;

struct Book{
  string id;
  string name;
  double price;
};

int main()
{
  int n;
  cin>>n;
vector<Book> book(n);
for(int i=0;i<n;++i){
  cin>>book[i].id>>book[i].name>>book[i].price;
}
for(int i=0;i<n/2;++i){
  swap(book[i],book[n-i-1]);
}
cout<<fixed<<setprecision(2);
for(int i=0;i<n;++i){
  cout<<book[i].id<<' '<<book[i].name<<' '<<book[i].price<<endl;
}
return 0;
}