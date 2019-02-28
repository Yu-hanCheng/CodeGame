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
subprocess_str=""
def connect_to_game():
    while True:
        try:
            s_sucess=s.connect(address)
            print("connected")
            break
        except:
            time.sleep(0.1)

def on_gameinfo(log_id,compiler,user_id,usercode,fileEnd):
    global subprocess_str
    save_code("usercode", usercode,fileEnd,"w")
    subprocess_str=''+compiler + ' ' +"usercode" + fileEnd+ ' '  + str(game_exec_ip)+ ' '  + str(game_port)+ ' '  + str(user_id) + ' '
    return

def save_code(filename, file, fileEnd,w_mode):
	# 傳新的程式碼會直接取代掉
    with open("%s%s"%(filename,fileEnd), w_mode) as f:
        f.write(file)
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
    if data_len < BUFF_SIZE:
        
        part_split=data.split("*")
        data = part_split[0]
        print("instruction data:",data)
        return data

    while True:
        part = sock.recv(BUFF_SIZE)
        # print('part',part)
        if part==b"":
            print("no msg")
            break 
        part_split=part.decode("utf-8").split("*")
        data += part_split[0]
        print('data_len',len(data))
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
            model=""
            if msg_recv['ml_file']!="":
                print(msg_recv['ml_file'])
                model = base64.b64decode(msg_recv['ml_file'])
                save_code('model',model,".sav","wb")
            code = base64.b64decode(msg_recv['code']).decode('utf-8')
            on_gameinfo(msg_recv['log_id'],msg_recv['compiler'],msg_recv['user_id'],code,msg_recv['fileEnd'])
        elif msg_recv['type']=='fork_subprocess':
            print("recv fork_subprocess")
            try:
                p = Popen(subprocess_str,shell=True)
            except Exception as e:
                print("Popen error:",e)


        else:
            print('type',msg_recv['type'])
            
    except Exception as e:
        print("e:",e)
        connect_to_game()
        


	