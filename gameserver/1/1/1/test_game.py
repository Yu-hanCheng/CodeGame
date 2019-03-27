#!/usr/bin/python
import socket,json,time,sys,os
import threading,math, random,copy
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
from websocket import create_connection
import re
game_exec_ip = sys.argv[1]
game_exec_port = sys.argv[2]
log_id = sys.argv[3]

bind_ip = '0.0.0.0'
bind_port = int(game_exec_port)+1
identify={}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(3)  # max backlog of connections
print('Listening on {}:{}'.format(bind_ip, bind_port))

# send_to_Players: 1conn,3gameinfo,5over,7score_recved
# recv from Players: 2connect, 4info, 6score
playerlist = []
lock = threading.Lock()
libs=[0,0]
# 2 connect
identify={}
barrier=[0,1]
start=0

# 3 gameinfo
ball = [0, 0]
paddle1=400
paddle2=400
l_score = 0
r_score = 0
cnt=0

# 4 info
paddle1_move = 0
paddle2_move = 3

# 5 over
endgame=0

# 6score
l_report = ""
r_report = "okok"



def send_to_Players(instr):

    global cnt,barrier,ball,paddle1,paddle2,l_score,r_score
    

    if (instr == 'gameinfo') and barrier==[1,1]:
        cnt+=1
        msg={'type':'info','content':'{\'ball\':'+str(ball)+',\'paddle1\':'+str(paddle1[1])+',\'paddle2\':'+str(paddle2[1])+',\'score\':'+str([l_score,r_score])+',\'cnt\':'+str(cnt)+'}'}
        print("recv info")
    elif instr == 'over':
        msg={'type':'over','content':{'ball':ball,'score':[l_score,r_score]}}
        print('recv game over')

    elif instr =="score_recved":
        msg={'type':'score_recved','content':""}
        print("recv score_recved")
    else:
        return
    for cli in range(0,len(playerlist)):
        playerlist[cli].send(json.dumps(msg).encode())
    barrier=[0,1]

def handle_client_connection(client_socket):
    # connect就進入 socket就進入 handler了, 為什麼connect後還要recv？ 為了判斷是p1連進來 還是p2
    global ball,paddle1,paddle2
    global paddle1_move,barrier,paddle2_move, playerlist, start,endgame, l_score, r_score, r_report,l_report
    client_socket.sendall(json.dumps({'type':"conn",'msg':"connected to server"}).encode())
    if playerlist[0]==client_socket:
        print("==ok")
    recv_request = client_socket.recv(1024)
    print("which subserver:",client_socket.getpeername())
    # request=str(recv_request).split("\\x | \"")[1]
    request=re.split(r'(\"|\\x)\s*', str(recv_request))[2]
    if len(request)>5:
        print("this is c lib")
        for i,e in enumerate(playerlist):
            if client_socket==e:
                libs[i]=1
    print("libs:",libs)
    req =request.replace("\'","\"")
    req2=req.replace(" ","")
    print("request:",req2)
    
    if request!=b'':
        msg = json.loads(req2)
        if msg['type']=='connect':
            if msg['who']=='P1':
                identify['P1']=msg['user_id']
                print("p1 conn lock",lock.acquire())
                try:
                    barrier[0]=1
                    # print('P1 in',barrier)
                    if barrier[1]!=1:
                        pass
                    else:
                        print("recv connect p1_start")
                        start=1
                        send_to_Players("gameinfo")
                finally:
                    lock.release()
                    pass
                        
    while True:
        # print(client_socket.getpeername(),"communicate loop")
        try:
            request = client_socket.recv(1024)
            if request==b'':
                print("sys.exit()")
                os._exit(0)
                
            else:
                msg = json.loads(request.decode())
        except(RuntimeError, TypeError, NameError)as e: 
            print('error',e)
            os._exit(0)

        if start == 1:
            if msg['type']=='info':
                if msg['who']=='P1':
                    paddle1_move=msg['content']         
                    print("p1 info lock",lock.acquire())
                    try:
                        barrier[0]=1 ## return to 0 in send_to_player
                        if barrier[1]==1:
                            lock.release()
                            r_score += 1
                            send_to_Players('over')
                            start=0
                            endgame=1
                        else:
                            lock.release()
                    finally:
                        pass
                else:
                    pass
            else:
                pass
        elif endgame==1:
            
            if msg['type']=='score':
                
                if msg['who']=='P1':
                    print("p1 score lock",lock.acquire())
                    l_report = msg['content']                
                    if r_report!="":
                        lock.release()
                        send_to_Players('score_recved')
                        # sys.exit()
                        break
                    else:
                        lock.release()
                else:
                    print("can't recongnize msg who")
            else:
                print("the type is not score")

            
        else:
            time.sleep(0.5)
            # print("game not start, or had over")
            lock.release()

def serve_app():
    while True:
        client_sock, address = server.accept()
        playerlist.append(client_sock)
        # print ('[%i users online]\n' % len(playerlist))
        # print(playerlist)
        # print('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()


if __name__ == '__main__':

    wst = threading.Thread(target=serve_app)
    wst.daemon = False
    wst.start()
    wst.join()
    # timeout= threading.Thread(target=timeout_check)
    # timeout.start()
    StartTime=time.time()
