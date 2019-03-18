# WS get code from gameserver.py
# tcp send code to 2 subservers
# build subprocess to exec
# game send over to game_exec

from websocket import create_connection
import json, sys,os,time, socket, threading,copy
import subprocess,base64
from subprocess import PIPE,Popen
subserverlist=[]

bind_ip = '0.0.0.0'
bind_port = int(sys.argv[1])
subservers=2
identify={}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(subservers+1)  # max backlog of connections
global ws
p=""
Can_recving=False
Is_thread_created=False
def connectto_web(intervaltime):
    global ws
    while True:
        try:
            ws = create_connection("ws://127.0.0.1:6005")
            break
        except:
            print("cannot connect now")
            time.sleep(intervaltime)
    print("ws create_connection")
    
connectto_web(1)
def ws_recv_from_gameserv():
    # independent thread to run a loop for polling sebsocket of webserver(6005) to get exec codes
    global ws,Can_recving
    while True:
        if Can_recving:
            try:
                ws.send(json.dumps({'from':"game_exec",'msg':"get_codes"}))
            except:
                print("cannot connect now")
                connectto_web(0.3)
                ws.send(json.dumps({'from':"game_exec",'msg':"get_codes"}))
            try:
                recv_msg = ws.recv()
            except Exception as e:
                print("ws recv error:",e)
                connectto_web(0.3)
                recv_msg = ws.recv()

            if len(recv_msg) > 5:
                print("recved")
                Can_recving=False
                ws_msg_handler(recv_msg)
                
        time.sleep(1)

def ws_msg_handler(msg):
    # 每個 element的 內容：[0data['log_id'],1data['user_id'],\
    #    2)data['game_lib_id'],3)language_res[0],4)path,5)filename, 6)fileEnd, 7)data['player_list']]
    # [5, 1, 1, 'python', '1/1/python/', '5_1', '.py', 0]
    msg_converted = json.loads(msg) 
    log_id=0
    for i,element in enumerate(msg_converted): # msg is elephant
        with open(""+element[4]+element[5]+element[6],'a') as user_file:
            if element[3]=='c':
                user_file.write("\n#define WHO 'P"+str(i+1)+"'\n")
            elif element[3]=='python':
                user_file.write("\nwho='P"+str(i+1)+"'\n")
            with open(element[4]+'lib'+element[6]) as fin: 
                lines = fin.readlines() 
                for j, line in enumerate(lines):
                    if j >= 0 and j < 6800:
                        user_file.write(line)
        with open(""+element[4]+element[5]+element[6],'r') as user_file:
            the_code = user_file.read()
            tcp_send_to_subserver(i,element[0],element[1],element[3],element[6],the_code)
        log_id=element[0]
        time.sleep(0.1)
    start_game(log_id,element[4],element[3],element[6])
    

def start_game(log_id,path,compiler,fileEnd):
    global p
    try:
        p = Popen(''+compiler + ' ' + path+'game' + fileEnd + ' ' + bind_ip+' '+ str(bind_port)+' '+str(log_id) + ' ',shell=True)
    except Exception as e:
        print('Popen error: ',e)


def tcp_send_to_subserver(subserver_index,log_id,user_id,compiler, fileEnd, code):
    # subserverlist[subserver_cnt].send(json.dumps({'log_id':log_id,'user_id':user_id,'code':code}).encode())
    global subserverlist
    codeString = base64.b64encode(code.encode('utf-8')).decode('utf-8')
    jsonStr = json.dumps({'type':'new_code','compiler':compiler,'fileEnd':fileEnd,'log_id':log_id,'code':codeString,'user_id':user_id}).encode()
    print("len:",len(jsonStr).to_bytes(3,byteorder='big'))
    subserverlist[subserver_index].sendall( len(jsonStr).to_bytes(3,byteorder='big'))
    subserverlist[subserver_index].sendall(jsonStr)

def tcp_serve_for_sub():
    global subserver_cnt,subserverlist
    while True:
        client_sock, address = server.accept()
        # if address[0]!="127.0.0.1": # !=127.0.0.1 -> subserver, ==127.0.0.1 -> game
        if len(subserverlist)<2:
            subserverlist.append(client_sock)
            subserver_cnt+=1
        
        client_handler = threading.Thread(
            target=tcp_client_handle,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()
subserver_cnt=0
def recvall(sock):
    
    BUFF_SIZE = 1024 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data 
def tcp_client_handle(client_socket):
    global subserver_cnt,subservers,Is_thread_created,Can_recving
    copy_client_socket=copy.deepcopy(client_socket.getpeername())
    if subserver_cnt==subservers: # default setting: there are two subservers
        Can_recving=True
        if not Is_thread_created:
            Is_thread_created=True
            recv_from_gameserv_handler = threading.Thread(
                target=ws_recv_from_gameserv,
                # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
            )
            recv_from_gameserv_handler.start()
        
    while True:
        try:
            request = recvall(client_socket)
            msg = json.loads(request.decode())
            
            if msg['type']=='over': # from game
                print("over")
                global p
                p.kill()
                subserver_cnt-=1
                client_socket.close()
                Can_recving=True
            else:
                pass
        except Exception as e:
            subserver_cnt-=1
            Can_recving=False
            print("error:",e)           
            for i,e in enumerate(subserverlist):
                if e.getpeername() ==copy_client_socket:
                    subserverlist.remove(client_socket)
                    print("remove index",i)
            client_socket.close()
            return
            

if __name__ == '__main__':
    wst = threading.Thread(target=tcp_serve_for_sub)
    wst.start()
    wst.join()
    