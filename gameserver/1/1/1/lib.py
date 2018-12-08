#!/usr/bin/python
import socket , time, json,sys

address = (sys.argv[1], 8802)  # 127.0.0.1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
  
s_sucess=""
s_sucess=s.connect(address)

	 
def gameover():
	# time.sleep(8)
	# pass
	sys.exit()

print(s_sucess)
connecttoserver = s.recv(2048)
msg={'type':'connect','who':who,'content':'in'}	
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary)


ball_pos=[[0,0],[0,0],[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=3
paddle_vel=0

def on_gameinfo(message):
	print(type(message))
	global paddle_vel
	# tuple_msg=message['content']
	# # tuple([ball,paddle1[1],paddle2[1],cnt])
	# cnt = tuple_msg[-1]
	# if cnt>2:
	# 	del ball_pos[0]
	# ball_pos.append(tuple_msg[0])

	run()
	communicate('info',paddle_vel)

def communicate(type_class,content):
	global paddle_vel,s,who
	msg={'type':type_class,'who':who,'content':content, 'cnt':cnt}
	
	str_ = json.dumps(msg)
	binary =str_.encode()
	s.send(binary)
	time.sleep(0.015) 

def score():# CPU, MEM Utility
	communicate('score',['cpu','mem'])
	gameover()
  


cnt =6000
while cnt>0:
	data = s.recv(2048)
	if data==b"":
		print("no")
		continue
	else:
		msg_recv = json.loads(data.decode())
		# 判斷 msg 類型, gameinfo or gameover
		# msg={'type':'info','content':tuple([ball,paddle1[1],paddle2[1],cnt])}
		# msg={'type':'over','content':"www"}
		if msg_recv['type']=='info':
			on_gameinfo(msg_recv)
		elif msg_recv['type']=='over':
			score()
		else:
			pass
	cnt-=1

msg_leave={'type':'disconnect','who':who,'content':'0'}	
str_leave = json.dumps(msg_leave)
binary_leave =str_leave.encode()
s.send(binary_leave) 
s.close()  
