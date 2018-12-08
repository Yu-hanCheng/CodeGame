# game start and over msg both recv from gameserver.py 
# over: kill docker and send msg to notify gameserver

from websocket import create_connection
import json, sys
import subprocess

ws = create_connection("ws://localhost:6005")
recv_msg=[]
def aws_container(room,userId,compiler,path_, filename):
	# 用 subprocess將欲執行的檔名當參數執行 exec_script.sh, 使產生 docker container 來執行程式碼,指令如下 
	# sh test.sh cce238a618539(imageID) python3.7 output.py 
	from subprocess import Popen, PIPE
	image='cce238a618539'
	try:
		# room,userId,path,filename,'player_list'
		p = Popen('sh exec_script.sh '+image+' '+compiler+' '+path_+' '+filename+'',shell=True, stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate()
		print('stdout: ',stdout)
		return 0
	except Exception as e:
		print('e: ',e)
		return 1


recv_msg = ws.recv() # [room,userId,path,filename,'player_list']
# execute_queue(recv_msg[],recv_msg[],recv_msg[])
aws_container(recv_msg['room'],recv_msg['userId'],recv_msg['compiler'],recv_msg['path'],recv_msg['filename'])



print("Sending 'Hello, World'...")
ws.send(json.dumps({'from':"servers"}))
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)

