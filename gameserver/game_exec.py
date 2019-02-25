# WS get code from gameserver.py
# tcp send code to 2 subservers
# build subprocess to exec
# game send over to game_exec

from websocket import create_connection
import json, sys,os,time, socket, threading
import subprocess,base64
from subprocess import PIPE,Popen
subserverlist=[]

bind_ip = '127.0.0.1'
bind_port = 5501
identify={}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(2)  # max backlog of connections
global ws
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
    global ws
    while True:
        try:
            ws.send(json.dumps({'from':"game_exec",'msg':"get_codes"}))
        except:
            print("cannot connect now")
            connectto_web(0.3)
            ws.send(json.dumps({'from':"game_exec",'msg':"get_codes"}))
        try:
            recv_msg = ws.recv()
        except:
            connectto_web(0.3)
            recv_msg = ws.recv()

        if len(recv_msg) > 5:
            ws_msg_handler(recv_msg)
            return 0
        time.sleep(1)

def ws_msg_handler(msg):
    # 每個 element的 內容：[0data['log_id'],1data['user_id'],\
    #    2)data['game_lib_id'],3)language_res[0],4)path,5)filename, 6)fileEnd, 7)data['player_list']]
    # [5, 1, 1, 'python', '1/1/python/', '5_1', '.py', 0]
    msg_converted = json.loads(msg) 
    log_id=0
    for i,element in enumerate(msg_converted): # msg is elephant
        with open(""+element[4]+element[5]+element[6],'a') as user_file:
            user_file.write("\nglobal paddle_vel,ball_pos,move_unit\npaddle_vel=0\nball_pos=[[0,0],[0,0],[0,0]]\nmove_unit=3\nrun()\n")#要給假值
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
    
    try:
        p = Popen(''+compiler + ' ' + path+'game' + fileEnd + ' ' + bind_ip+' '+ str(bind_port)+' '+str(log_id) + ' ',shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            print('stderr:', stderr)
        else:
            print('stdout:', stdout)
    except Exception as e:
        print('Popen error: ',e)


def tcp_send_to_subserver(subserver_cnt,log_id,user_id,compiler, fileEnd, code):
    # subserverlist[subserver_cnt].send(json.dumps({'log_id':log_id,'user_id':user_id,'code':code}).encode())
    codeString = base64.b64encode(code.encode('utf-8')).decode('utf-8')
    jsonStr = json.dumps({'type':'new_code','compiler':compiler,'fileEnd':fileEnd,'log_id':log_id,'code':codeString,'user_id':user_id}).encode()
    subserverlist[subserver_cnt].send(jsonStr)

def tcp_serve_for_sub():    
    while True:
        client_sock, address = server.accept()
        subserverlist.append(client_sock)
        client_handler = threading.Thread(
            target=tcp_client_handle,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()
subserver_cnt=0
def tcp_client_handle(client_socket):
    global subserver_cnt
    subserver_cnt+=1
    if subserver_cnt==2: # default setting: there are two subservers
        ws_recv_from_gameserv()
        while True:
            request = client_socket.recv(1024)
            msg = json.loads(request.decode())
            if msg['type']=='recved':
                pass
            elif msg['type']=='over':
                ws_recv_from_gameserv()
            else:
                pass

if __name__ == '__main__':
    wst = threading.Thread(target=tcp_serve_for_sub)
    wst.start()
    wst.join()
    