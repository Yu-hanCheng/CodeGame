# WS get code from gameserver.py
# tcp send code to 2 subservers
# build subprocess to exec
# game send over to game_exec

from websocket import create_connection
import json, sys,os,time, socket, threading
import subprocess 
subserverlist=[]

def ws_recv_from_gameserv():
    while True:
        ws.send(json.dumps({'from':"game_exec",'msg':"get_codes"}))
        recv_msg = ws.recv()
        if len(recv_msg) > 5:
            ws_msg_handler(recv_msg)
            return 0
        time.sleep(1)

def ws_msg_handler(msg):
    # 每個 element的 內容：[0data['log_id'],1data['user_id'],\
    #    2)data['game_lib_id'],3)language_res[0],4)path,5)filename, 6)fileEnd, 7)data['player_list']]
    # [3, 2, 1, 'python3.7', '1/1/1/', '3_2.py', 2]
    
    msg_converted = json.loads(msg)
    log_id=0
    for i,element in enumerate(msg_converted): # msg is elephant

        with open(""+element[4]+element[5]+element[6],'r+') as user_file:
            user_file.write("\nwho='P"+str(i+1)+"'\n")
            with open(path+'lib'+element[6]) as fin: 
                lines = fin.readlines() 
                for i, line in enumerate(lines):
                    if i >= 0 and i < 6800:
                        user_file.write(line)
            encoded = base64.b64encode(user_file.readlines())
            tcp_send_to_subserver(i,element[0],element[1],encoded)
        log_id=element[0]
    start_game(log_id,element[3]],element[6])
    

def start_game(log_id,compiler,fileEnd):
    try:
		p = Popen(compiler + 'game' + fileEnd + str(log_id) + ' ',shell=True, stdout=PIPE, stderr=PIPE)
		 stdout, stderr = p.communicate()
        if stderr:
            print('stderr:', stderr)
        else:
            print('stdout:', stdout)
	except Exception as e:
		print('Popen error: ',e)


def tcp_send_to_subserver(i,log_id,user_id,code):
    subserverlist[i].send(json.dumps({'log_id':log_id,'user_id':user_id,'code':code}).encode())

def tcp_serve_for_sub():
    while True:
        client_sock, address = server.accept()
        subserverlist.append(client_sock)
        client_handler = threading.Thread(
            target=tcp_client_handle,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()

def tcp_client_handle(client_socket):
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
    wst.daemon = True
    wst.start()
    ws_recv_from_gameserv()