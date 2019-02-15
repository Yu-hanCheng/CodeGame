import socket, time, json, sys, base64
import subprocess
from subprocess import Popen, PIPE

address = (sys.argv[1], 5501)  # 127.0.0.1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s_sucess=""


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
        p = Popen(''+compiler + ' ' +"usercode" + fileEnd + ' 127.0.0.1 ' + str(user_id) + ' ',shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            print('stderr:', stderr)
        else:
            print('stdout:', stdout)
    except Exception as e:
        print('Popen error: ',e)

def save_code(code, fileEnd):
	# 傳新的程式碼會直接取代掉
    with open("usercode%s"%(fileEnd), "w") as f:
        f.write(code)
cnt=0
def recvall(sock):
    global cnt
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        cnt+=1
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data


while True:
    data = recvall(s)
    # data = s.recv(2048)
    print('cnt:',cnt)
    if data==b"":
        print("no msg")
        continue
    else:
        
        str_data = data.decode("utf-8")
        msg_recv = json.loads(str_data)
        code = base64.b64decode(msg_recv['code']).decode('utf-8')
        # 判斷 msg 類型, gameinfo or gameover
        if msg_recv['type']=='new_code': 
            binary =json.dumps({'type':'recved'}).encode()
            s.send(binary)
            on_gameinfo(msg_recv['log_id'],msg_recv['compiler'],msg_recv['user_id'],code,msg_recv['fileEnd'])
        elif msg_recv['type']=='kill_process':
            score(msg_recv['content'])
        else:
            pass


	