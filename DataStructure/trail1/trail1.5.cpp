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

int main()
{
  int n;
  cin>>n;
  vector<Book> book(n);
  for(int i=0;i<n;++i){
    cin>>book[i].id>>book[i].name>>book[i].price;
  }
  double mx=book[0].price;
  for(int i=1;i<n;++i){
    if(book[i].price>mx){
      mx=book[i].price;
    }
  }
  
  int cnt=0;
  for(int i=0;i<n;++i){
    if(book[i].price==mx){
      ++cnt;
    }
  }
  cout<<cnt<<endl;
  cout<<fixed<<setprecision(2);
  for(int i=0;i<n;++i)
  {
    if(book[i].price==mx){
      cout<<book[i].id<<' '<<book[i].name<<' '<<book[i].price<<endl;
    }
  }
  return 0;
}