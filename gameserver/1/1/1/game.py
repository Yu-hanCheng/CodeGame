#!/usr/bin/python
import socket,json,time,sys
import threading,math, random
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
from websocket import create_connection
socketIO=SocketIO('18.220.184.154', 5000, LoggingNamespace)
socketIO.emit('info',{'msg':'www','log_id':1})
log_id = sys.argv[1]
bind_ip = '0.0.0.0'
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
PAD_WIDTH = 8
PAD_HEIGHT = math.ceil(HEIGHT/3)
HALF_PAD_WIDTH = PAD_WIDTH // 3
HALF_PAD_HEIGHT = PAD_HEIGHT // 3
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
    horz = random.randrange(2, 4)
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


# def send_to_webserver(msg_type,msg_content,logId):
#     print("sendtoweb",msg_type,msg_content)
    # with SocketIO('18.220.184.154', 5000) as socketIO:
    #     Web_namespace = socketIO.define(WebNamespace)
    #     Web_namespace.emit(msg_type,{'msg':msg_content,'log_id':logId})#q1 log_id
def send_to_webserver(msg_type,msg_content,logId):
    print("web:",msg_content)
#     # #lock.acquire()
#     global ball,paddle1,paddle2,socketIO, score
    global socketIO
    try:
        socketIO.emit(msg_type,{'msg':msg_content,'log_id':logId})
    except (RuntimeError, TypeError, NameError) as e:
        print(' send_to_webserver error:',e)
#     #lock.release()
def send_to_gameserver(score_msg):
    global logId
    print('gameserver')
    ws = create_connection("ws://localhost:6005")
    ws.send(json.dumps({'from':"game",'logId':logId,'score_msg':score_msg}))
    ws.close()
    exit()
    quit()
    

def send_to_Players(instr):

    global cnt,barrier,ball,paddle1,paddle2
    

    if (instr == 'gameinfo') and barrier==[1,1]:
        cnt+=1
        msg={'type':'info','content':tuple([ball,paddle1[1],paddle2[1],[l_score,r_score],cnt])}
        
        for cli in range(0,len(playerlist)):
            playerlist[cli].send(json.dumps(msg).encode())
        barrier=[0,0]
        
    elif instr == 'endgame':
        msg={'type':'over','content':{'ball':ball,'score':[l_score,r_score]}}
        for cli in range(0,len(playerlist)):
            playerlist[cli].send(json.dumps(msg).encode())
        barrier=[0,0]
        print('endgame %f'%time.time())
        time.sleep(20)
    else:
        return
    barrier=[0,0]


def play():
    try:
        global paddle1, paddle2,paddle1_move,paddle2_move, ball, ball_vel, l_score, r_score, cnt
        global barrier,start
        # print('ball_play: ',ball)

        if paddle1[1] > HALF_PAD_HEIGHT and paddle1[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle1[1] += paddle1_move
            # print('p1 normal')
        elif paddle1[1] <= HALF_PAD_HEIGHT and paddle1_move > 0:
            paddle1[1] = HALF_PAD_HEIGHT
            paddle1[1] += paddle1_move
            # print('p1 top')
        elif paddle1[1] >= HEIGHT - HALF_PAD_HEIGHT and paddle1_move < 0:
            paddle1[1] = HEIGHT - HALF_PAD_HEIGHT
            paddle1[1] += paddle1_move
            # print('p1 bottom')
        else:
            print('p1 else')

        if paddle2[1] > HALF_PAD_HEIGHT and paddle2[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle2[1] += paddle2_move
            # print('p2 normal')
        elif paddle2[1] <= HALF_PAD_HEIGHT and paddle2_move > 0:
            paddle1[1] = HALF_PAD_HEIGHT
            paddle2[1] += paddle2_move
            # print('p2 top')
        elif paddle2[1] >= HEIGHT - HALF_PAD_HEIGHT and paddle2_move < 0:
            paddle1[1] =HEIGHT- HALF_PAD_HEIGHT
            paddle2[1] += paddle2_move
            # print('p2 bottom')
        else:
            print('p2 else')

        # print('paddle:(%d,%d,%d)'%(paddle1[1],paddle2[1],ball[0]))

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
            
            if r_score < 1:
                send_to_Players('get_score')
                ball_init(True)
            else:
                # barrier=1
                send_to_Players('endgame')
                ball_init(False)
                start=0

        if int(ball[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball[1]) in range(
                paddle2[1] - HALF_PAD_HEIGHT, paddle2[1] + HALF_PAD_HEIGHT, 1):
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
        elif int(ball[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
            l_score += 1
            print('l_score ',l_score)
            
            if l_score < 1:
                ball_init(False)
                
            else:
                # barrier=1
                send_to_Players('endgame')
                start=0
                print('ball ',ball)
                ball_init(True)
        else:
            print("else")
    except(RuntimeError, TypeError, NameError):
        # raise SystemExit
        print('play except')
        return
    
def game(where):
    try:
        print(where)
        play()
    except:
        return
    send_to_Players('gameinfo')

def handle_client_connection(client_socket):
    
    global paddle1_move,barrier,p1_rt,paddle2_move,p2_rt, playerlist, start,r_report,l_report
    
    client_socket.send(json.dumps({'type':"conn",'msg':"connected to server"}).encode())
    while True:
        print("first loop")
        request = client_socket.recv(1024)
        msg = json.loads(request.decode())
        if msg['type']=='connect':
            if msg['who']=='P1':
                print('P1 in',barrier)
                p1_rt=time.time()
                identify['P1']=msg['user_id']
                #lock.acquire()
                try:
                    barrier[0]=1
                    if barrier[1]==1:
                        print("p1_start")
                        start=1
                        send_to_webserver('gamemain_connect',identify,log_id)
                        send_to_Players("gameinfo")
                        break
                finally:
                    #lock.release()
                    pass

            elif msg['who']=='P2':
                print('P2 in',barrier)
                p2_rt=time.time()
                identify['P2']=msg['user_id']
                #lock.acquire()
                try:
                    barrier[1]=1
                    if barrier[0]==1:
                        print("p2_start")
                        start=1
                        send_to_webserver('gamemain_connect',identify,log_id)
                        send_to_Players("gameinfo")
                        break
                finally:
                    #lock.release()
                    pass
                    
    
    while True:
        print("second loop")
        if start == 1:
            try:
                print('current:',threading.current_thread())
                request = client_socket.recv(1024)
                msg = json.loads(request.decode())

                if msg['type']=='info':
                    print('info',msg['who'],msg['content'])#paddle_vel
                    if msg['who']=='P1':
                        paddle1_move=msg['content']
                        p1_rt=time.time()
                        #lock.acquire()
                        try:
                            barrier[0]=1
                            if barrier[1]==1:
                                send_to_webserver(msg['type'],tuple([ball,paddle1,paddle2]),log_id)
                                record_content.append([ball,paddle1,paddle2])
                                game('on_p1')
                        finally:
                            #lock.release()
                            pass

                    elif msg['who']=='P2':
                        # print('P2 content',msg['content'])
                        paddle2_move=msg['content']
                        p2_rt=time.time()
                        #lock.acquire()
                        try:
                            barrier[1]=1
                            if barrier[0]==1:
                                send_to_webserver(msg['type'],tuple([ball,paddle1,paddle2]),log_id)
                                record_content.append([ball,paddle1,paddle2])
                                game('on_p2')
                        finally:
                            #lock.release()
                            pass

                elif msg['type']=='score':
                    print("score")
                    if msg['who']=='P1':
                        l_report = msg['content']
                        print('l_report',l_report)
                        if r_report!="":
                            print("send report")
                            send_to_webserver('over',{'l_report':l_report,'r_report':r_report,'record_content':record_content},log_id)
                            send_to_gameserver(score)
                            start=0
                            break

                    elif msg['who']=='P2':
                        r_report = msg['content']
                        print('r_report',r_report)
                        if l_report!="":
                            print("ok send report")
                            send_to_webserver('over',{'l_report':l_report,'r_report':r_report,'record_content':record_content},log_id)
                            send_to_gameserver(score)
                            start=0
                            break

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
        else:
            print("game not start, or had over")
    

        
        # client_socket.close()

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

def timeout_check():
    global p1_rt, p2_rt,barrier, paddle1_move, paddle2_move, start,playerlist
    # print('active_count:',threading.active_count())
    timeout=0.5
    # while True:
        
        # time.sleep(0.3)   
    if start==1:
        # print("check")
        #lock.acquire()
        try:
            if barrier[0]==0:
                p1_rt_sub=time.time()-p1_rt
                # print('p1_rt_sub %f p2_rt_sub %f, barrier '%(p1_rt_sub,time.time()-p2_rt)+str(barrier))
                if p1_rt_sub>timeout:
                    if barrier[1]==0:
                        timeout+=0.005    
                        # print('p2 also no response, timeout increase: ',timeout)
                    paddle1_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    send_to_webserver('p1timeout',p1_rt_sub,log_id)
                    game('p1_timeout')
                    
    
            elif barrier[1]==0:
                p2_rt_sub = time.time()-p2_rt
                if (p2_rt_sub)>timeout:
                    # print('p2_rt',time.time()-p2_rt)
                    paddle2_move=0
                    barrier=[1,1]
                    p1_rt=time.time()
                    p2_rt=time.time()
                    send_to_webserver('p2timeout',p2_rt_sub,log_id)
                    game('p2_timeout')
                    
        finally:
            #lock.release()
            pass
            


if __name__ == '__main__':
    __init__()

    wst = threading.Thread(target=serve_app)
    wst.daemon = True
    wst.start()
    # wst.join()
    # timeout= threading.Thread(target=timeout_check)
    # timeout.start()
    StartTime=time.time()
    

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

# # start action every 0.6s
inter=setInterval(0.03,timeout_check)
print('just after setInterval -> time : {:.1f}s'.format(time.time()-StartTime))

# # will stop interval in 5s
t=threading.Timer(90,inter.cancel)
t.start()
