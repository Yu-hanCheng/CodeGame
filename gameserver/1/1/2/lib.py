global paddle_vel,ball_pos,move_unit
paddle_pos=0
paddle_vel=0
ball_pos=[[0,0],[0,0],[0,0]]
move_unit=3
run()

#!/usr/bin/python
import socket , time, json,sys,os,threading,psutil
from functools import reduce
address = (sys.argv[1], 8800)
user_id = sys.argv[2]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s_sucess=""
while True:
    try:
        s_sucess=s.connect(address)
        print("connected")
        break
    except:
        time.sleep(0.1)


cpu_list=[]
mem_list=[]
     
pid=os.getpid()
p = psutil.Process(pid)
def get_usage():
    global p,cpu_list, mem_list
    cpu_list.append(p.cpu_percent())
    mem_list.append(p.memory_percent())

class setInterval :
    def __init__(self,interval,func) :
        self.interval=interval
        self.func=func
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.func()

    def cancel(self) :
        self.stopEvent.set()

# start action every 0.6s
inter=setInterval(0.1,get_usage)


def gameover():
    sys.exit()

connecttoserver = s.recv(2048)
msg={'type':'connect','who':who,'user_id':user_id}
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary)


def on_gameinfo(message):
    global paddle_vel,paddle_pos
    tuple_msg=message['content']
    cnt = tuple_msg[-1]
    print("paddle_pos:",tuple_msg[1])
    if who=="P1":
        paddle_pos=tuple_msg[1]
    else:
        paddle_pos=tuple_msg[2]
    print("ball pos:",tuple_msg[0],cnt)
    if cnt>2:
        del ball_pos[0]
        ball_pos.append(tuple_msg[0])
    elif cnt == 1:
        ball_pos[0] = tuple_msg[0]
    elif cnt ==2:
        ball_pos[1] = tuple_msg[0]

    run()
    communicate('info',paddle_vel)

def communicate(type_class,content):
    global paddle_vel,s,who
    msg={'type':type_class,'who':who,'content':content, 'cnt':cnt}
    print('type_class:',type_class)
    str_ = json.dumps(msg)
    binary =str_.encode()
    s.send(binary)
    time.sleep(0.015) 

def score(msg_from_gamemain):# CPU, MEM Utility
    inter.cancel
    global p,cpu_list, mem_list
    print('l_score',msg_from_gamemain['score'])
    if who == 'P1':
        score = msg_from_gamemain['score'][0]

    elif who == 'P2':
        score = msg_from_gamemain['score'][1]

    cpu = round(reduce(lambda x, y: x + y, cpu_list) / len(cpu_list),3)
    mem = round(reduce(lambda x, y: x + y, mem_list) / len(mem_list),3)
    communicate('score',json.dumps({'user_id':user_id,'score':score,'cpu':cpu,'mem':mem,'time':'554400'}))
    
def recvall(sock):
    global cnt
    BUFF_SIZE = 2048 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        cnt+=1
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data  

cnt =6000
while cnt>0:
    data = recvall(s)
    if data==b"":
        print("no")
        gameover()
    else:
        try:
            msg_recv = json.loads(data.decode())
            if msg_recv['type']=='info':
                on_gameinfo(msg_recv)
            elif msg_recv['type']=='over':
                print("over")
                score(msg_recv['content'])
            elif msg_recv['type']=='score_recved':
                gameover()
            else:
                pass
        except(RuntimeError, TypeError, NameError) as e:
            print('e:',e)
            print("except data:",data)
    cnt-=1

msg_leave={'type':'disconnect','who':who,'content':'0'} 
str_leave = json.dumps(msg_leave)
binary_leave =str_leave.encode()
s.send(binary_leave) 
s.close()  
