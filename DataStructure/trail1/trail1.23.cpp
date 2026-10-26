#include<iostream>
using namespace std;

struct Node{
  int data;
  Node*next;
};

void print(Node*head){
  Node*p=head;
  while(p!=NULL){
    cout<<p->data;
    if(p->next!=NULL){
      cout<<' ';
    }
    p=p->next;
  }
  cout<<endl;
}

int main(){
  int m;
  cin>>m;
  Node*head=NULL,*tail=NULL;
  for(int i=0;i<m;++i){
    Node*no=new Node;
    cin>>no->data;
    no->next=NULL;
    if(head==NULL) head=tail=no;
    else{
      tail->next=no;
      tail=no;
    }
  }
  Node*cur=head;
  for(int i=0;i<m/2;++i){
    Node*pre=cur;
    while(pre->next->next!=NULL){
      pre=pre->next;
    }
    Node*last=pre->next;
    pre->next=NULL;
    last->next=cur->next;
    cur->next=last;
    cur=last->next;
    
  }
  print(head);
  return 0;
}