# Linux 信号量实践

`linux man semop`

```cpp
NAME
       semop, semtimedop - System V semaphore operations

SYNOPSIS
       #include <sys/types.h>
       #include <sys/ipc.h>
       #include <sys/sem.h>

       int semop(int semid, struct sembuf *sops, size_t nsops);

       int semtimedop(int semid, struct sembuf *sops, size_t nsops,
                      const struct timespec *timeout);

   Feature Test Macro Requirements for glibc (see feature_test_macros(7)):

       semtimedop(): _GNU_SOURCE

DESCRIPTION
       Each semaphore in a System V semaphore set has the following associated values:

       unsigned short  semval;   /* semaphore value */
       unsigned short  semzcnt;  /* # waiting for zero */
       unsigned short  semncnt;  /* # waiting for increase */
       pid_t           sempid;   /* ID of process that did last op */


```

## 信号量实现生产者消费者

### 伪代码

```cpp
semaphore mutex=1; //临界区互斥信号量
semaphore empty=n;  //空闲缓冲区，初始值为buffer的大小
semaphore full=0;  //缓冲区初始化为空
producer () { //生产者进程
    while(1){
        produce an item in nextp;  //生产数据
        P(empty);  //获取空缓冲区单元
        P(mutex);  //进入临界区.
        add nextp to buffer;  //将数据放入缓冲区
        V(mutex);  //离开临界区,释放互斥信号量
        V(full);  //满缓冲区数加1
    }
}

consumer () {  //消费者进程
    while(1){
        P(full);  //获取满缓冲区单元
        P(mutex);  // 进入临界区
        remove an item from buffer;  //从缓冲区中取出数据
        V (mutex);  //离开临界区，释放互斥信号量
        V (empty) ;  //空缓冲区数加1
        consume the item;  //消费数据
    }
}
```

### linux c代码实现

信号量+互斥锁实现生产者，消费者问题

* test.cpp

```cpp
#include<iostream>
#include<unistd.h>  // sleep
#include<pthread.h>
#include"semaphore.h"

using namespace std;

#define N 5

semaphore mutex("/", 1);           // 临界区互斥信号量
semaphore empty("/home", N);       // 记录空缓冲区数，初值为N
semaphore full("/home/john",0); // 记录满缓冲区数，初值为0
int buffer[N];                     // 缓冲区，大小为N
int i=0;
int j=0;

void* producer(void* arg)
{
    empty.P();                 // empty减1
    mutex.P();

    buffer[i] = 10 + rand() % 90;
    printf("Producer %d write Buffer[%d]: %d\n",(int)arg,i+1,buffer[i]);
    i = (i+1) % N;

    mutex.V();
    full.V();                  // full加1 
    return arg;
}

void* consumer(void* arg)
{
    full.P();                  // full减1
    mutex.P();

    printf("                               \033[1;31m");
    printf("Consumer %d read Buffer[%d]: %d\n",(int)arg,j+1,buffer[j]);
    printf("\033[0m");
    j = (j+1) % N;

    mutex.V();
    empty.V();                 // empty加1
    return arg;
}

int main()
{
    pthread_t id[10];

    // 开10个生产者线程，10个消费者线程
    for(int k=0; k<10; ++k)
        pthread_create(&id[k], NULL, producer, (void*)(k+1));

    for(int k=0; k<10; ++k)
        pthread_create(&id[k], NULL, consumer, (void*)(k+1));

    sleep(1);
    return 0;
}
```

* semaphore.h

定义信号量类，以及P，V操作

```cpp
#include<iostream>
#include<cstdio>
#include<cstdlib>
#include<sys/sem.h>
using namespace std;

// 联合体，用于semctl初始化
union semun {
    int              val; /*for SETVAL*/
    struct semid_ds *buf;
    unsigned short  *array;
};


class semaphore {
private:
    int sem_id; //信号量ID，内核中创建
    int init_sem(int);
public:
    semaphore(const char*, int); /*构造函数*/
    ~semaphore();                /*析构函数*/
    void P();                    /*P操作*/
    void V();                    /*V操作*/
};
```

* semaphore.cpp

```cpp
#include"semaphore.h"

semaphore::semaphore(const char* path, int value)
{
    key_t key;
    /*获取key值*/
    if((key = ftok(path, 'z')) < 0) {
        perror("ftok error");
        exit(1);
    }

    /*创建信号量集，信号量的数量为1*/
    if((sem_id = semget(key, 1, IPC_CREAT|0666)) == -1) {
        perror("semget error");
        exit(1);
    }

    init_sem(value);
}


semaphore::~semaphore()
{
    union semun tmp;
    if(semctl(sem_id, 0, IPC_RMID, tmp) == -1) {
        perror("Delete Semaphore Error");
        exit(1);
    }
}

// 获得信号量 减去1
void semaphore::P()
{
    struct sembuf sbuf;
    sbuf.sem_num = 0; /*序号*/
    sbuf.sem_op = -1; /*P操作*/
    sbuf.sem_flg = SEM_UNDO;

    if(semop(sem_id, &sbuf, 1) == -1) {
        perror("P operation Error");
    }
}

//释放信号量 加上1
void semaphore::V()
{
    struct sembuf sbuf;
    sbuf.sem_num = 0; /*序号*/
    sbuf.sem_op = 1;  /*V操作*/
    sbuf.sem_flg = SEM_UNDO;

    if(semop(sem_id, &sbuf, 1) == -1) {
        perror("V operation Error");
    }
}


// 初始化信号量
int semaphore::init_sem(int value)
{
    union semun tmp;
    tmp.val = value;
    if(semctl(sem_id, 0, SETVAL, tmp) == -1) {
        perror("Init Semaphore Error");
        return -1;
    }
    return 0;
}
```

* 附：Makefile

```cpp
.PHONY: build clean

CC=g++
HEADERS=-I.
DEBUG=-g -ggdb  
WALL=-Wall -W  
CFLAGS=$(WALL) $(DEBUG)  
L_CC=$(CC) $(CFLAGS) $(HEADERS)


test:test.o semaphore.o
	$(L_CC) $^ -o $@ -lpthread

%.o:%.cpp
	$(L_CC) -c $<

clean:
	@-rm *.o
	@-rm test
```
