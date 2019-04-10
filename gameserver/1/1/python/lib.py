#!/usr/bin/python
global paddle_vel,ball_pos,move_unit
paddle_pos=0
paddle_vel=0
ball_pos=[[0,0],[0,0],[0,0]]
move_unit=3

import socket , time, json,sys,os,threading,psutil
from functools import reduce
game_ip = sys.argv[1]
game_port = int(sys.argv[2])
address = (game_ip, game_port)
user_id = sys.argv[3]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s_sucess=""
time.sleep(0.5)
while True:
    try:
        print("lib try conn")
        s_sucess=s.connect(address)
        print("lib connected")
        break
    except Exception as e :
        print("error:",e)
        time.sleep(0.1)



cpu_list=[0]
mem_list=[0]
     
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
    print("gameover")
    s.close()
    os._exit(0)

connecttoserver = s.recv(2048)
msg={'type':'connect','who':who,'user_id':user_id}
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary)


def on_gameinfo(message):
    global paddle_vel,paddle_pos
    tuple_msg=message['content']
    
    string = tuple_msg.replace("'", '"')
    json_loads_res = json.loads(string)
    cnt = json_loads_res['cnt']
    if who=="P1":
        paddle_pos=json_loads_res['paddle1']
    else:
        paddle_pos=json_loads_res['paddle2']
    if cnt>2:
        del ball_pos[0]
        ball_pos.append(json_loads_res['ball'])
    elif cnt == 1:
        ball_pos[0] = json_loads_res['ball']
    elif cnt ==2:
        ball_pos[1] = json_loads_res['ball']
    run()
    send_togame('info',paddle_vel)

def send_togame(type_class,content):
    global paddle_vel,s,who
    msg={'type':type_class,'who':who,'content':content, 'cnt':cnt}
    print('content:',content)
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
    avg_time=1
    # report="\""+str(user_id)+","+str(cpu)+","+str(mem)+","+str(avg_time)+"\""
    report= '{\'score\':'+str(score)+',\'user_id\':'+str(user_id)+',\'cpu\':'+str(cpu)+',\'mem\':'+str(mem)+',\'avg_time\':'+str(avg_time)+'}'
    # msg={'type':'info','content':'{\'ball\':'+str(ball)+',\'paddle1\':'+str(paddle1[1])+',\'paddle2\':'+str(paddle2[1])+',\'score\':'+str([l_score,r_score])+',\'cnt\':'+str(cnt)+'}'}
    send_togame('score',report)
def recvall(sock):
    
    BUFF_SIZE = 2048 # 4 KiB
    data = ""
    data_len=0
    recv_cnt=0

    part = sock.recv(BUFF_SIZE)
    first_part_split=part.decode("utf-8").split("|")
    if len(first_part_split)>7:
        print("two msg")
        for p in first_part_split:
            p_list = p.split("*")
            if len(p_list)>1:
                data_len=p_list[-1]
                break        
    else:
        print("one msg")
        data_len = first_part_split[0]
    data_tail = first_part_split[-1]
    print('len(data)',data_len,len(data_tail))
    if int(data_len)==len(data_tail)-1:
        print("==")
        part_split=data_tail.split("*")
        data += part_split[0]
    elif int(data_len)>len(data_tail):
        while True:
            part = sock.recv(BUFF_SIZE)
            print('part',part)
            if part==b"":
                print("no msg")
                data=""
                break
            part_split=part.decode("utf-8").split("*")
            data += part_split[0]
            
            if len(part_split) > 1 : # There is a "*" in the part
                if len(part_split[1]) > 0:
                    next_msg = part_split[1]
                break
    return data
cnt =6000
run()
while cnt>0:
    str_data = recvall(s)
    print("str_data",str_data)
    if str_data =="":
        print("none")
        gameover()
    else:
        try:
            msg_recv = json.loads(str_data)
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
            print("except data:",str_data)
    cnt-=1

msg_leave={'type':'disconnect','who':who,'content':'0'} 
str_leave = json.dumps(msg_leave)
binary_leave =str_leave.encode()
s.send(binary_leave) 
s.close()  
