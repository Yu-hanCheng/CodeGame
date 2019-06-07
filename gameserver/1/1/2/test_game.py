#!/usr/bin/python
import socket,json,time,sys
import threading,math, random,copy
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
from websocket import create_connection
socketIO=SocketIO('127.0.0.1', 5500, LoggingNamespace)
socketIO.emit('game_connect',{'msg':'test game init'})
log_id =0
bind_ip = '127.0.0.1'
bind_port = 8800
identify={}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(3)  # max backlog of connections

print('Listening on {}:{}'.format(bind_ip, bind_port))

playerlist = []

WIDTH = 800
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 20
PAD_HEIGHT = math.floor(HEIGHT/3)
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = math.floor(PAD_HEIGHT // 2)
PAD_END = 346
PAD_CATCH = HALF_PAD_HEIGHT + BALL_RADIUS//2
paddle1 = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
paddle2 = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT //2]

ball = [0, 0]
ball_vel = [0, 0]
record_content=[]
paddle1_move = 0
paddle2_move = 0
l_score = 0
l_report = ""
r_score = 0
r_report = ""
identify={}
score={'type':'score','roomId':1,'l_score':0,'r_score':0}
barrier=[0,0] # ensure a round fair
cnt=0
p1_rt=0.0001
p2_rt=0.0001
start=0 # control timeout loop
lock = threading.Lock()
class WebNamespace(BaseNamespace):
    def on_connect(self):
        print('[Connected]')

def ball_init(right):
    global ball, ball_vel
    ball = [WIDTH // 2, HEIGHT // 2]
    horz = random.randrange(5,8)
    vert = random.randrange(1, 3)

    if right == False:
        print("init move left")
        horz = - horz
    ball_vel = [horz, -vert]

def __init__():
    global paddle1, paddle2, paddle1_move, paddle2_move, l_score, r_score  # these are floats
    global score1, score2  # these are ints
    paddle1 = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
    paddle2 = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT //2]
    l_score = 0
    r_score = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)


def send_to_webserver(msg_type,msg_content,logId):

    global socketIO
    try:
        socketIO.emit(msg_type,{'msg':msg_content,'log_id':logId})
    except (RuntimeError, TypeError, NameError) as e:
        print(' send_to_webserver error:',e)
    
def tcp_send_rule(str_tosend,startlen):
    msg_tosend=str(len(str_tosend))
    for i in range(startlen-len(msg_tosend)):
        msg_tosend+="|"
    return (msg_tosend+str_tosend+"*").encode()
 
def send_to_Players(instr):

    global cnt,barrier,ball,paddle1,paddle2
    

    if (instr == 'gameinfo'):
        cnt+=1
        json_str={'type':'info','content':'{\'ball\':'+str(ball)+',\'paddle1\':'+str(paddle1[1])+',\'paddle2\':'+str(paddle2[1])+',\'score\':'+str([l_score,r_score])+',\'cnt\':'+str(cnt)+'}'}
        msg=tcp_send_rule(json.dumps(json_str),8)
        playerlist[0].send(msg)
        
        
    elif instr == 'endgame':
        json_str={'type':'over','content':{'ball':ball,'score':[l_score,r_score]}}
        msg=tcp_send_rule(json.dumps(json_str),8)

        playerlist[0].send(msg)
        
        print('endgame %f'%time.time())
    else:
        return
    barrier=[0,0]


def play():
    try:
        global paddle1, paddle2,paddle1_move,paddle2_move, ball, ball_vel, l_score, r_score, cnt
        global barrier,start

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
            elif the_paddle >= PAD_END:
                the_paddle = PAD_END
                if the_move < 0:
                    the_paddle += the_move
            else:
                pass
            return the_paddle

        paddle1[1] = y_axis(copy.deepcopy(paddle1[1]),paddle1_move)
        ball[0] += int(ball_vel[0])
        ball[1] += int(ball_vel[1])


        if int(ball[1]) <= BALL_RADIUS:
            ball_vel[1] = - ball_vel[1]
        if int(ball[1]) >= HEIGHT + 1 - BALL_RADIUS:
            ball_vel[1] = - ball_vel[1]


        if int(ball[0]) <= BALL_RADIUS + PAD_WIDTH and int(ball[1]) in range(paddle1[1] - HALF_PAD_HEIGHT,
                                                                                     paddle1[1] + HALF_PAD_HEIGHT, 1):
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
        elif int(ball[0]) <= BALL_RADIUS + PAD_WIDTH:
            r_score += 1
            print('r_score ',r_score)
            send_to_Players('endgame')
            start=0
                
        if int(ball[0]) >= (WIDTH + 1 - BALL_RADIUS - PAD_WIDTH):
            if cnt>1000:
                l_score += 1
                send_to_Players('endgame')
                start=0
                
            else:
                ball_vel[0] = -ball_vel[0]
                ball_vel[0] *= 1.1
                ball_vel[1] *= 1.1
    except(RuntimeError, TypeError, NameError):
        # raise SystemExit
        print('play except')
        return
    
def game(where):
    global start
    try:
        play()
    except:
        return
    if start==1:
        send_to_Players('gameinfo')

def handle_client_connection(client_socket):
    
    global paddle1_move,barrier,p1_rt,paddle2_move,p2_rt, playerlist, start,r_report,l_report,cnt
    client_socket.send(json.dumps({'type':"conn",'msg':"connected to server"}).encode())

    request = client_socket.recv(1024)
    msg = json.loads(request.decode())
    if msg['type']=='connect':
        if msg['who']=='P1':
            p1_rt=time.time()
            identify['P1']=msg['user_id']
            #lock.acquire()
            try:
                start=1
                game('on_p1')
            except (RuntimeError, TypeError, NameError) as e:
                print("send_to_player error",e)
    while True:
        if start == 1:
            try:
                request = client_socket.recv(1024)
                if request==b'':
                    print("break")
                    break
                else:
                    msg = json.loads(request.decode())
                    
                    if msg['type']=='info':
                        print('info paddle_vel',msg['who'],msg['content'])#paddle_vel
                        if msg['who']=='P1':
                            paddle1_move=msg['content']
                            p1_rt=time.time()
                            #lock.acquire()
                            try:
                                after_play()
                            finally:
                                #lock.release()
                                pass

            except(RuntimeError, TypeError, NameError)as e: 
                print('error',e)
                sys.exit()
        else:
            try:
                request = client_socket.recv(1024)
                if request :
                    msg = json.loads(request.decode())            
                    if msg['type']=='score':                 
                        msg_tosend=tcp_send_rule(json.dumps({'type':"score_recved"}),8)
                        client_socket.send(msg_tosend)
                        if msg['who']=='P1':
                            l_report = msg['content']
                            r_report = {"user_id": "2", "score": 0, "cpu": 1.425, "mem": 0.054, "time": "554400"}
                            send_to_webserver('over',{'l_report':l_report,'r_report':r_report,'record_content':record_content},log_id)
                            time.sleep(1)
                            client_socket.close()
                            import os
                            os._exit(0)

                    elif msg['type']=='disconnect':
                        if msg['who']=='P1':
                            print('P1 leave',cnt)
                            # client_socket.close()
                        elif msg['who']=='P2':
                            print('P2 leave',cnt)
                            # client_socket.close()
            except(RuntimeError, TypeError, NameError)as e: 
                print('error',e)
                sys.exit()
            print("game not start, or had over")

def after_play():
    global ball, paddle1, paddle2
    ratio_ball=[round((ball[0]-BALL_RADIUS)/8,1),round((ball[1]-BALL_RADIUS)/4,1)]
    ratio_paddle1 = round((paddle1[1]-HALF_PAD_HEIGHT)/4,1)
    send_to_webserver('info',tuple([ratio_ball,ratio_paddle1,[l_score,r_score]]),log_id)
    record_content.append(copy.deepcopy([ball,paddle1,paddle2]))
    game('on_p1')

def serve_app():
    while True:
        client_sock, address = server.accept()
        playerlist.append(client_sock)
        inter=setInterval(0.1,timeout_check,client_sock)
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()

def timeout_check(client_socket):
    global p1_rt, p2_rt,barrier, paddle1_move, paddle2_move, start,playerlist
    timeout=0.5
    if start==1:
        try:
            barrier[1]=1
            if barrier[0]==0:
                p1_rt_sub=time.time()-p1_rt

                if p1_rt_sub>timeout:
                    if barrier[1]==0:
                        timeout+=0.005    
                    paddle1_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    send_to_webserver('timeout',p1_rt_sub,log_id)
                    client_socket.close()
        except Exception as e:
            print("timeout e:",e)
                    
        finally:
            #lock.release()
            pass
            

class setInterval :
    def __init__(self,interval,action,client) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval,args=(client,))
        thread.start()

    def __setInterval(self,client) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action(client)

    def cancel(self) :
        self.stopEvent.set()

if __name__ == '__main__':
    __init__()
    
    wst = threading.Thread(target=serve_app)
    wst.daemon = True
    wst.start()
    wst.join()
    StartTime=time.time()
print('just after setInterval -> time : {:.1f}s'.format(time.time()-StartTime))
# # will stop interval in 5s
t=threading.Timer(90,inter.cancel)
t.start()