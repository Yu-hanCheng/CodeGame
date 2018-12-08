import socket , time, json
  
address = ('127.0.0.1', 8800)  # 127.0.0.1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
 
s_sucess=s.connect(address) 
connecttoserver = s.recv(2048)
print(connecttoserver)
msg={'type':'connect','who':'P2','content':'in'}	
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary) 


ball_pos=[[0,0],[0,0],[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=3
paddle_vel=0

def on_gameinfo(message):
	print(type(message))
	# tuple_msg=message['content']
	# # tuple([ball,paddle1[1],paddle2[1],cnt])
	# cnt = tuple_msg[-1]
	# if cnt>2:
	# 	del ball_pos[0]
	# ball_pos.append(tuple_msg[0])

	run()
	communicate(cnt)


def run():
	global paddle_vel,ball_pos,move_unit
	if (ball_pos[-1][0]-ball_pos[-2][0]) <0: 
		print("ball moves left")
		if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
			print("ball moves down")
			paddle_vel=move_unit
		elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
			print("ball moves up")
			paddle_vel=-move_unit
	else: 
		paddle_vel=0
		print("ball moves right, no need to move paddle1")

def communicate(cnt):
	global paddle_vel,s
	msg={'type':'info','who':'P2','content':paddle_vel, 'cnt':cnt}
	
	str_ = json.dumps(msg)
	binary =str_.encode()
	s.send(binary) 

def score():# CPU, MEM Utility
	pass
  
cnt =6000
while cnt>0:
	data = s.recv(2048)
	msg_recv = json.loads(data)
	on_gameinfo(msg_recv)
	
	cnt-=1
	time.sleep(0.001)

msg_leave={'type':'disconnect','who':'P2','content':'0'}	
str_leave = json.dumps(msg_leave)
binary_leave =str_leave.encode()
s.send(binary_leave) 
s.close()  
