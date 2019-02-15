import socket, time, json, sys


address = (sys.argv[1], 5501)  # 127.0.0.1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s_sucess=""
s_sucess=s.connect(address)
while True:
    data = s.recv(2048)
    if data==b"":
        print("no msg")
        continue
    else:
        print(data)
        msg_recv = json.loads(data.decode())
        # 判斷 msg 類型, gameinfo or gameover
        # msg={'type':'info','content':tuple([ball,paddle1[1],paddle2[1],cnt])}
        if msg_recv['type']=='new_code':
            on_gameinfo(msg_recv)
        elif msg_recv['type']=='kill_process':
            score(msg_recv['content'])
        else:
            pass
