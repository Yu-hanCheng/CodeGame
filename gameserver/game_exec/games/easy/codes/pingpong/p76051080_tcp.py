import socket , time, json

address = ('127.0.0.1', 8800)  # 127.0.0.1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s_sucess=s.connect(address)
connecttoserver = s.recv(2048)
print(connecttoserver)
msg={'type':'connect','who':'P1','content':'in'}
str_ = json.dumps(msg)
binary =str_.encode()
s.send(binary)


ball_pos=[[0,0],[0,0],[0,0]]
paddle1_pos=[0] # paddle only Y axis
move_unit=3
paddle_vel=0

def communicate(msg):
	global s
	binary =msg.encode()
	s.send(binary)

def run(msg_recv):
	global paddle_vel,ball_pos,move_unit
	print('in run:',msg_recv)
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

	msg={'type':'info','who':'P1','content':paddle_vel, 'cnt':cnt}
	str_ = json.dumps(msg)
	communicate(str_)


def score(msg):
	# CPU, MEM Utility
	msg={'type':'score','who':'P1','score':300, 'cnt':1}
	print("score ",msg)
	str_ = json.dumps(msg)
	communicate(str_)
	close_socket()

def close_socket():
	global s
	s.close()
	exit

cnt =6000
while cnt>0:
	print(cnt)
	data = s.recv(2048)
	msg_recv = json.loads(data)
	if msg_recv['type']=='info':
		run(msg_recv)
	elif msg_recv['type']=='gameover':
		score(msg_recv)
	else: lambda:print("Invalid msg")
	# switch = {
	# 		"gameinfo": run(msg_recv),
	# 		# "gameover": score(msg_recv)
	# 	}
	# func = switch.get(msg_recv['type'], lambda:"Invalid msg")
	cnt-=1
	time.sleep(0.001)

msg_leave={'type':'disconnect','who':'P1','content':'0'}
str_leave = json.dumps(msg_leave)
binary_leave =str_leave.encode()
s.send(binary_leave)
s.close()
