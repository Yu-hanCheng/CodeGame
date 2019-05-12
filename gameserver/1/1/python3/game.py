#!/usr/bin/python
import socket,json,time,sys,os
import threading,math, random,copy
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
from websocket import create_connection
import re
WIN_SCORE = 1
game_exec_ip = sys.argv[1]
game_exec_port = sys.argv[2]
log_id = sys.argv[3]

socketIO=SocketIO('http://192.168.0.54', 5000, LoggingNamespace)
socketIO.emit('info',{'msg':'gameconnected','log_id':log_id})
bind_ip = '0.0.0.0'
bind_port = int(game_exec_port)+1
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(3)  # max backlog of connections
print('Listening on {}:{}'.format(bind_ip, bind_port))

# send_to_Players: 1conn,3gameinfo,5over,7score_recved
# recv from Players: 2connect, 4info, 6score
playerlist = []
lock = threading.Lock()
# 2 connect
identify={}
barrier=[0,0]
start=0

# 3 gameinfo
WIDTH = 800
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 20
PAD_HEIGHT = math.ceil(HEIGHT/3)
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
PAD_END = HEIGHT - HALF_PAD_HEIGHT
PAD_CATCH = HALF_PAD_HEIGHT + BALL_RADIUS//2
paddle1 = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
paddle2 = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT //2]

ball = [0, 0]
ball_vel = [0, 0]
record_content=[]
l_score = 0
r_score = 0
cnt=0
p1_rt=0.0001
p2_rt=0.0001
p1_timeout=0
p2_timeout=0
# 4 info
paddle1_move = 0
paddle2_move = 3

# 5 over
endgame=0

# 6score
l_report = ""
r_report = ""




class WebNamespace(BaseNamespace):
    def on_connect(self):
        print('[Connected]')

def ball_init(right):
    global ball, ball_vel
    ball = [WIDTH // 2, HEIGHT // 2]
    horz = random.randrange(2, 4)
    vert = random.randrange(1, 3)

    if right == False:
        horz = - horz
    ball_vel = [horz, -vert]
    print("init move",horz,-vert)

def __init__():
    global paddle1, paddle2, paddle1_move, paddle2_move, l_score, r_score  # these are floats
    global score1, score2  # these are ints
    l_score = 0
    r_score = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)

def send_to_webserver(msg_type,msg_content,logId):
    if msg_type=="timeout_over":
        print("send timeout")
    global socketIO
    try:
        socketIO.emit(msg_type,{'msg':msg_content,'log_id':logId})
    except (RuntimeError, TypeError, NameError) as e:
        print(' send_to_webserver error:',e)
def send_to_gameserver(score_msg):
    global logId
    print('gameserver')
    ws = create_connection("ws://localhost:6005")
    ws.send(json.dumps({'from':"game",'logId':logId,'score_msg':score_msg}))
    ws.close()
    exit()
    quit()

def tcp_send_rule(str_tosend,startlen):
    msg_tosend=str(len(str_tosend))
    for i in range(startlen-len(msg_tosend)):
        msg_tosend+="|"
    return (msg_tosend+str_tosend+"*").encode()
    

def send_to_Players(instr):

    global cnt,barrier,ball,paddle1,paddle2,l_score,r_score

    if (instr == 'gameinfo') and barrier==[1,1]:
        cnt+=1
        json_str={'type':'info','content':'{\'ball\':'+str(ball)+',\'paddle1\':'+str(paddle1[1])+',\'paddle2\':'+str(paddle2[1])+',\'score\':'+str([l_score,r_score])+',\'cnt\':'+str(cnt)+'}'}
        print("send info")
    elif instr == 'over':
        json_str={'type':'over','content':{'ball':ball,'score':[l_score,r_score],'normal':[3,3]}} # '{\'ball\':'+str(ball)+'}' normal：[cpu,mem]
        print('send game over')

    elif instr =="score_recved":
        json_str={'type':'score_recved','content':""}
        print("send score_recved")
    else:
        return
    for cli in range(0,len(playerlist)):
        msg=tcp_send_rule(json.dumps(json_str),8)
        playerlist[cli].send(msg)
    barrier=[0,0]
    
def c_str_split(recv_msg):
    print("recv_msg:",recv_msg)
    request=re.split(r'(\"|\\x)\s*', str(recv_msg))[2]
    req =request.replace("\'","\"")
    req2=req.replace(" ","")
    return req2

def play():
    try:
        global paddle1, paddle2,paddle1_move,paddle2_move, ball, ball_vel, l_score, r_score, cnt
        global barrier,start,endgame
        
        def y_axis(the_paddle,the_move):
            if the_paddle > HALF_PAD_HEIGHT and the_paddle < PAD_END:
                
                if the_paddle + the_move > PAD_END:
                    the_paddle = PAD_END
                elif the_paddle + the_move < HALF_PAD_HEIGHT:
                    the_paddle = HALF_PAD_HEIGHT
                else:
                    the_paddle += the_move
            elif the_paddle <= HALF_PAD_HEIGHT and the_move > 0:
                the_paddle = HALF_PAD_HEIGHT
                the_paddle += the_move
            elif the_paddle >= PAD_END and the_move < 0:
                the_paddle = PAD_END
                the_paddle += the_move
            else:
                pass
            return the_paddle
        paddle2[1] = y_axis(copy.deepcopy(paddle2[1]),paddle2_move)    
        paddle1[1] = y_axis(copy.deepcopy(paddle1[1]),paddle1_move)
        print("paddle:",paddle1,paddle2)
        
        
        ball[0] += int(ball_vel[0])
        ball[1] += int(ball_vel[1])
        if int(ball[1]) <= BALL_RADIUS:
            ball[1] = BALL_RADIUS
        elif int(ball[1]) >= HEIGHT - BALL_RADIUS:
            ball[1] = HEIGHT - BALL_RADIUS

        # 上下邊界反彈
        if int(ball[1]) <= BALL_RADIUS:
            ball_vel[1] = - ball_vel[1]
        elif int(ball[1]) >= HEIGHT - BALL_RADIUS:
            ball_vel[1] = - ball_vel[1]

        # left normal catch
        if int(ball[0]) <= BALL_RADIUS + PAD_WIDTH and int(ball[1]) in range(paddle1[1] - PAD_CATCH,
                                                                                       paddle1[1] + PAD_CATCH, 1):
            if int(ball[0]) < PAD_WIDTH :
                ball[0] = BALL_RADIUS*2 + PAD_WIDTH
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1      
        # left no catch                                                             
        elif int(ball[0]) <= BALL_RADIUS:
            r_score += 1
            ball[0] = BALL_RADIUS
            print('r_score ',r_score)
            if r_score < WIN_SCORE:
                ball_init(True)
                after_play('onP1')
            else:
                # barrier=1
                send_to_Players('over')
                start=0
                endgame=1
                after_play('onP1')
        # right normal catch
        if int(ball[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball[1]) in range(
                paddle2[1] - PAD_CATCH, paddle2[1] + PAD_CATCH, 1):
            if int(ball[0]) > WIDTH - PAD_WIDTH :
                ball[0] = BALL_RADIUS*2 + PAD_WIDTH
            ball[0] = WIDTH - BALL_RADIUS*2 -1
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
        elif int(ball[0]) >= WIDTH + 1 - BALL_RADIUS:
            l_score += 1
            ball[0]=WIDTH + 1 - BALL_RADIUS
            print('l_score ',l_score)
            if l_score < WIN_SCORE:
                ball_init(False)
                after_play('onP2')
                
            else:
                # barrier=1
                send_to_Players('over')
                start=0
                endgame=1
                after_play('onP2')
        else:
            pass
    except(RuntimeError, TypeError, NameError) as e:
        # raise SystemExit
        print('play except',e)
        return
    
def game(where):
    global start
    if start==1:
        try:
            print(where)
            play()
            send_to_Players('gameinfo')
        except:
            return

def handle_client_connection(client_socket):
    # connect就進入 socket就進入 handler了, 為什麼connect後還要recv？ 為了判斷是p1連進來 還是p2
    global ball,paddle1,paddle2,record_content
    global paddle1_move,barrier,p1_rt,paddle2_move,p2_rt, playerlist, start,endgame, l_score, r_score, r_report,l_report
    client_socket.sendall(json.dumps({'type':"conn",'msg':"connected to server"}).encode())
    recv_request = client_socket.recv(1024)
    request=re.split(r'(\"|\\x)\s*', str(recv_request))[2]
    lib_lan=0
    if len(request)>15:
        print("this is c lib")
        lib_lan=1
        req =request.replace("\'","\"")
        req_split=req.replace(" ","")      
    else:
        req_split=recv_request.decode()

    if req_split!=b'':
        msg = json.loads(req_split)
        if msg['type']=='connect':
            if msg['who']=='P1':
                
                identify['P1']=msg['user_id']
                print("p1 conn lock",lock.acquire())
                try:
                    barrier[0]=1
                    if barrier[1]!=1:
                        pass
                    else:
                        print("recv connect p1_start")
                        start=1
                        send_to_webserver('gamemain_connect',identify,log_id)
                        p1_rt=time.time()
                        p2_rt=time.time()
                        game('on_p1')
                finally:
                    lock.release()
                    pass
            elif msg['who']=='P2':
                identify['P2']=msg['user_id']
                print("p2 conn lock",lock.acquire())
                try:
                    barrier[1]=1
                    if barrier[0]!=1:
                        pass
                    else:
                        print("p2_start")
                        start=1
                        send_to_webserver('gamemain_connect',identify,log_id)
                        p1_rt=time.time()
                        p2_rt=time.time()
                        game('on_p2')
                        # break
                finally:
                    lock.release()
                    pass
    if lib_lan==1: # c
        while True:
            
            try:
                request = client_socket.recv(1024)
                req_split=c_str_split(request)
                if req_split==b'':
                    print("sys.exit()")
                    os._exit(0)
                    
                else:
                    msg = json.loads(req_split)
            except(RuntimeError, TypeError, NameError)as e: 
                print('error',e)
                os._exit(0)

            if start == 1:
                if msg['type']=='info':
                    if msg['who']=='P1':
                        paddle1_move=msg['content']         
                        print("p1 info lock",lock.acquire())
                        p1_rt=time.time()
                        try:
                            barrier[0]=1 ## return to 0 in send_to_player
                            if barrier[1]==1:
                                after_play('on_p1')
                                lock.release()
                            else:
                                lock.release()
                        finally:
                            pass
                    elif msg['who']=='P2':
                        paddle2_move=msg['content'] 
                        print("p2 info lock",lock.acquire())
                        p2_rt=time.time()
                        try:
                            barrier[1]=1
                            if barrier[0]==1:
                                after_play('on_p2')
                                lock.release()
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
                            send_to_webserver('over',{'l_report':l_report,'r_report':r_report,'record_content':record_content},log_id)

                            game_exec_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                            game_exec_address = (game_exec_ip, int(game_exec_port))
                            print("game_exec_address:",game_exec_address)
                            while True:
                                try:
                                    game_exec=game_exec_client.connect(game_exec_address)
                                    print("connected")
                                    break
                                except:
                                    time.sleep(0.1)
                            binary =json.dumps({'type':'over'}).encode()
                            print("binary:",binary)
                            game_exec_client.send(binary)
                            print("send game_exec:",game_exec_client)
                            send_to_Players('score_recved')
                            # sys.exit()
                            break
                        else:
                            lock.release()
                    elif msg['who']=='P2':
                        print("p2 score lock",lock.acquire())
                        r_report = msg['content']
                        if l_report!="":
                            lock.release()
                            send_to_webserver('over',{'l_report':l_report,'r_report':r_report,'record_content':record_content},log_id)                       
                            game_exec_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                            game_exec_address = (game_exec_ip, int(game_exec_port))
                            print("game_exec_address:",game_exec_address)
                            while True:
                                try:
                                    game_exec=game_exec_client.connect(game_exec_address)
                                    print("connected")
                                    break
                                except:
                                    time.sleep(0.1)
                            binary =json.dumps({'type':'over'}).encode()
                            print("binary:",binary)
                            game_exec_client.send(binary)
                            send_to_Players('score_recved')
                            break
                else:
                    print("the type is not score")

                
            else:
                time.sleep(0.2)
                lock.release()
    elif lib_lan==0:#python
        while True:
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
                        p1_rt=time.time()
                        try:
                            barrier[0]=1 ## return to 0 in send_to_player
                            if barrier[1]==1:
                                after_play('python on_p1')
                                lock.release()
                            else:
                                lock.release()
                        finally:
                            pass

                    elif msg['who']=='P2':
                        paddle2_move=msg['content'] 
                        print("p2 info lock",lock.acquire())
                        p2_rt=time.time()
                        try:
                            barrier[1]=1
                            if barrier[0]==1:
                                after_play('python on_p2')
                                lock.release()
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
                            gameover("over",l_report,r_report,record_content,log_id)
                            break
                        else:
                            lock.release()

                    elif msg['who']=='P2':
                        print("p2 score lock",lock.acquire())
                        r_report = msg['content']
                        if l_report!="":
                            lock.release()
                            gameover("over",l_report,r_report,record_content,log_id)
                            break
                        else:
                            lock.release()
                    else:
                        print("can't recongnize msg who")
                else:
                    print("the type is not score")

                
            else:
                time.sleep(0.2)
                lock.release()
                
def gameover(msg_type,l_report,r_report,record_content,log_id):
    global game_exec_ip,game_exec_port
    print("gameover",msg_type)
    if msg_type=="timeout_over":
        send_to_webserver(msg_type,record_content,log_id)                       
    else:
        send_to_webserver(msg_type,{'l_report':l_report,'r_report':r_report,'record_content':record_content},log_id)                       
    game_exec_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    game_exec_address = (game_exec_ip, int(game_exec_port))
    print("game_exec_address:",game_exec_address)
    
    while True:
        try:
            game_exec=game_exec_client.connect(game_exec_address)
            print("connected")
            break
        except:
            time.sleep(0.1)
    binary =json.dumps({'type':'over'}).encode()
    game_exec_client.send(binary)
    send_to_Players('score_recved')
def timeout_check():
    global p1_rt, p2_rt,barrier, paddle1_move, paddle2_move, start,playerlist,p1_timeout,p2_timeout
    
    timeout=0.7
    if start==1:
        try:
            if barrier[0]==0:
                p1_rt_sub=time.time()-p1_rt        
                if p1_rt_sub>timeout:
                    if barrier[1]==0:
                        timeout+=0.05    
                    paddle1_move=0
                    barrier=[1,1]
                    print("p1timeout:",p1_timeout,p1_rt_sub)
                    p1_timeout+=1
                    send_to_webserver('timeout',{'user':"P1","sub":p1_rt_sub},log_id)
                    if p1_timeout==3:
                        gameover("timeout_over","","",{'user':"P1","sub":p1_rt_sub},log_id)                
                    after_play('p1_timeout')
                    p1_rt=time.time()
                    p2_rt=time.time()
    
            elif barrier[1]==0:
                p2_rt_sub = time.time()-p2_rt
                if (p2_rt_sub)>timeout:
                    paddle2_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    print("p2timeout:",p2_timeout)
                    p2_timeout+=1
                    if p2_timeout==3:
                        gameover("timeout_over","","",{'user':"P2","sub":p2_rt_sub},log_id)
                    after_play('p2_timeout')
        except Exception as e:
            print("timeout e:",e)
                    
        finally:
            #lock.release()
            pass
            
def after_play(game_whom):
    global ball, paddle1, paddle2,paddle1_movel,paddle2_move
    send_to_webserver('info',tuple([ball,paddle1,paddle2,[l_score,r_score]]),log_id)
    record_content.append(copy.deepcopy([ball,paddle1,paddle1_move,paddle2,paddle2_move]))
    game(game_whom)


class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()

if __name__ == '__main__':
    __init__()
    game_exec_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    game_exec_address = (game_exec_ip, int(game_exec_port))
    game_exec=game_exec_client.connect(game_exec_address)
    binary =json.dumps({'type':'game_setted'}).encode()
    game_exec_client.send(binary)
    game_exec_client.close()
    inter=setInterval(0.03,timeout_check)
    while True:
        client_sock, address = server.accept()
        playerlist.append(client_sock)
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()


print('just after setInterval -> time : {:.1f}s'.format(time.time()-StartTime))

# # will stop interval in 5s
t=threading.Timer(90,inter.cancel)
t.start()
