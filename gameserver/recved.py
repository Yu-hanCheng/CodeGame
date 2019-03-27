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

def on_gameinfo(log_id,compiler,user_id,usercode,fileEnd):
    
    save_code(usercode,fileEnd)
    try:
        time.sleep(0.5)
        p = Popen(''+compiler + ' ' +"usercode" + fileEnd+ ' '  + str(game_exec_ip)+ ' '  + str(game_port)+ ' '  + str(user_id) + ' ',shell=True, stdout=PIPE, stderr=PIPE)
        # stdout, stderr = p.communicate()
        # if stderr:
        #     print('stderr:', stderr)
        #     p.kill()
        # else:
        #     print('stderr:',stdout)
        #     # p.kill()
        #     pass
    except Exception as e:
        print('Popen error: ',e)
    return

def save_code(code, fileEnd):
	# 傳新的程式碼會直接取代掉
    with open("usercode%s"%(fileEnd), "w") as f:
        f.write(code)
cnt=0
def recvall(sock):
    
    BUFF_SIZE = 4096 # 4 KiB
    data = ""
    data_len=0
    recv_cnt=0

    part = sock.recv(BUFF_SIZE)
    first_part_split=part.decode("utf-8").split("|")
    data_len= int(first_part_split[0])
    print('data_len',data_len)
    data += first_part_split[-1]

    while True:
        part = sock.recv(BUFF_SIZE)
        print('part',part)
        if part==b"":
            print("no msg")
            break 
        part_split=part.decode("utf-8").split("*")
        data += part_split[0]
        
        if len(part_split) > 1 : # There is a "*" in the part
            if len(part_split[1]) > 0:
                next_msg = part_split[1]
            break
    return data

connect_to_game()
while True:
    try:
        str_data = recvall(s)
        msg_recv = json.loads(str_data)
        # 判斷 msg 類型, gameinfo or gameover
        if msg_recv['type']=='new_code': 
            binary =json.dumps({'type':'recved'}).encode()
            s.send(binary)
            code = base64.b64decode(msg_recv['code']).decode('utf-8')
            on_gameinfo(msg_recv['log_id'],msg_recv['compiler'],msg_recv['user_id'],code,msg_recv['fileEnd'])
        else:
            pass
    except Exception as e:
        print("e:",e)
        connect_to_game()
        


	