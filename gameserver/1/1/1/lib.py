#!/usr/bin/python
import socket , time, json,sys

<<<<<<< HEAD
address = (sys.argv[1], 8802)  # 127.0.0.1
=======
address = (sys.argv[1], 8800)  # 127.0.0.1
>>>>>>> af6fd4d... get report msg from gamemain
user_id = sys.argv[2]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

s_sucess=""
s_sucess=s.connect(address)

     
def gameover():
    # time.sleep(8)
    # pass
    # msg_leave={'type':'disconnect','who':who,'content':'0'} 
    # str_leave = json.dumps(msg_leave)
    # binary_leave =str_leave.encode()
    # s.send(binary_leave) 
    # s.close()  
    sys.exit()

print(s_sucess)
connecttoserver = s.recv(2048)
<<<<<<< HEAD
msg={'type':'connect','who':who,'user_id':user_id}	
=======
msg={'type':'connect','who':who,'user_id':user_id}  
>>>>>>> af6fd4d... get report msg from gamemain
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary)


ball_pos=[[0,0],[0,0],[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=3
paddle_vel=0

def on_gameinfo(message):
    print(type(message))
    global paddle_vel
    tuple_msg=message['content']
    print("tuple_msg[0]:",tuple_msg['0'])
    # # tuple([ball,paddle1[1],paddle2[1],cnt])
    # cnt = tuple_msg[-1]
    # if cnt>2:
    #   del ball_pos[0]
    # ball_pos.append(tuple_msg[0])

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
    print('l_score',msg_from_gamemain['score'])
	if who == 'P1':
		score = msg_from_gamemain['score'][0]
	elif who == 'P2':
		score = msg_from_gamemain['score'][1]
     
    communicate('score',json.dumps({'user_id':user_id,'score':score,'cpu':'50','mem':'30','time':'554400'}))#json.dumps({'cpu':'50','mem':'30','time':'554400'})
    gameover()
  


cnt =6000
while cnt>0:
    data = s.recv(2048)
    if data==b"":
        print("no")
        continue
    else:
        msg_recv = json.loads(data.decode())
        # 判斷 msg 類型, gameinfo or gameover
        # msg={'type':'info','content':tuple([ball,paddle1[1],paddle2[1],cnt])}
        # msg={'type':'over','content':"www"}
        if msg_recv['type']=='info':
            on_gameinfo(msg_recv)
        elif msg_recv['type']=='over':
            score(msg_recv['content'])
        else:
            pass
    cnt-=1

msg_leave={'type':'disconnect','who':who,'content':'0'} 
str_leave = json.dumps(msg_leave)
binary_leave =str_leave.encode()
s.send(binary_leave) 
s.close()  
