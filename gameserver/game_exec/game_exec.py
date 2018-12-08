# game start and over msg both recv from gameserver.py 
# over: kill docker and send msg to notify gameserver 

from websocket import create_connection
import json, sys,os,time
import subprocess 

ws = create_connection("ws://localhost:6005")
serv_status=[0] * 5
recv_msg = ""

def aws_container(log_id, userId, compiler, path_, filename, link_dc):
	# 用 subprocess將欲執行的檔名當參數,執行 exec_script.sh, 使產生 docker container 來執行程式碼,指令如下 
	# sh test.sh cce238a618539(imageID) python3.7 output.py 
	# link= logid_gamemain
	from subprocess import Popen, PIPE
	image = "cce238a618539"
	
	try:
		p = Popen('sh game_exec/exec_script.sh ' + image + ' ' + compiler + ' ' + path_ + ' '+ filename + ' '+ link_dc + ' '+log_id+ ' ',shell=True)
		return 0
	except Exception as e:
		print('e: ',e)
		return 1

def msg_handler(msg):
	# 每個 element的 內容：[data['log_id'],data['user_id'],\
	#	data['game_lib_id'],language_res[0],path,filename,data['player_list']]
	# ['3', 2, 1, 'python3.7', '1/1/1/', '3_2.py', []]
	# 開 subprocess 
	
	msg_converted = json.loads(msg)
	
	for i,element in enumerate(msg_converted): # msg is elephant
		
		if i==0:
			
			aws_container(element[0],element[1],element[3],element[4],"gamemain.py","0")
			time.sleep(15)
		
		with open(""+element[4]+element[5],'r+') as user_file:
			code = user_file.read()
			user_file.write("\nwho='P"+str(i+1)+"'\n")
		# 執行package
		
		merge_com_lib(code,element[4],element[5],element[3])
		link_msg = element[0]+'gamemain.py'
		aws_container(element[0],element[1],element[3],element[4],element[5],link_msg)

def merge_com_lib(code,path,filename,compiler):
	# "w"上傳新的程式碼會直接取代掉
	# 加上不同語言與 webserver溝通的code
	# save code: 
	# path: category_id/game_id/language_id/
	# filename: log_id/user_id
	try:
		os.makedirs( path )
	except:
		pass
	with open(path+filename, 'a') as f:
		with open(path+'lib.py') as fin: 
			lines = fin.readlines() 
			for i, line in enumerate(lines):
				if i >= 0 and i < 6800:
					f.write(line)

import sched, time
s = sched.scheduler(time.time, time.sleep)
serv_status=[0] * 5
serv_status.append(1)
serv_status.insert(2,1)
serv_status.insert(5,1)
#[0, 0, 1, 0, 0, 1, 0, 1]
def game_over(index):
	serv_status[index]= 0

def send_serv_index(index):

	print('send serv_index to gameserver: ',serv_status)
	ws.send(json.dumps({'from':"game_exec",'serv_index':index}))
	recv_msg = ws.recv() # get elephant
	if len(recv_msg) > 5:
		serv_status[index]= 1#log_id, serve for which log
		msg_handler(recv_msg)

def check_serv_status():
	for i,x in enumerate(serv_status):
		if x==0:
			send_serv_index(i)
			break

	s.enter(1, 1, check_serv_status)

s.enter(1, 1, check_serv_status)
# scheduler.enter(delay, priority, action, argument=(), kwargs={})
s.run()