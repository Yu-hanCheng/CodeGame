import socket, time, json, sys, base64
import subprocess
from subprocess import Popen, PIPE
# tcp://0.tcp.ngrok.io:16499
game_exec_ip=sys.argv[1]
game_exec_port=int(sys.argv[2])
game_port=game_exec_port+1
address = (game_exec_ip, game_exec_port) 
global s
s_sucess=""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_game():
    while True:
        try:
            s_sucess=s.connect(address)
            print("connected")
            break
        except:
            time.sleep(0.1)


def recvall(sock):
    
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        
        data += part
        print("part",len(part))
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data

connect_to_game()
while True:
    try:
        data = recvall(s)
        # data = s.recv(2048)
        print("data",len(data))
        if data==b"":
            print("no msg")
            time.sleep(2)
            continue
        else:
            s.send(json.dumps({'type':'over'}).encode())
            str_data = data.decode("utf-8")
            msg_recv = json.loads(str_data)
            # 判斷 msg 類型, gameinfo or gameover
            
    except Exception as e:
        print("e:",e)
        connect_to_game()
        


	