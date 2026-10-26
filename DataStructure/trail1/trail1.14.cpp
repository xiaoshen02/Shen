#include<iostream>
#include<string>
#include<iomanip>
using namespace std;

struct Book{
  string id;
  string name;
  double price;
};
struct Node{
  Book data;
  Node* next;
};
int main()
{
  Node*head=NULL;
  Node*tail=NULL;
  Book book;
  double sum=0.0;
  int cnt=0;
  while(cin>>book.id>>book.name>>book.price){
    if(book.id=="0" && book.name=="0" && book.price==0) break;
    cnt++;
    sum+=book.price;
    Node*nb=new Node;
    nb->data=book;
    nb->next=NULL;
    if(head==NULL) head=tail=nb; 
    else{
      tail->next=nb;
      tail=nb;
    }
  }
  double avg=sum/cnt;
  Node*p=head;
  while(p!=NULL){
    if(p->data.price>=avg) p->data.price*=1.1;
    else{
      p->data.price*=1.2;
    }
    p=p->next;
  }
  cout<<fixed<<setprecision(2)<<endl;
  cout<<avg<<endl;
  Node*q=head;
  while(q!=nullptr){
    cout<<q->data.id<<' '<<q->data.name<<' '<<q->data.price<<endl;
    q=q->next;
  }
  return 0;
}