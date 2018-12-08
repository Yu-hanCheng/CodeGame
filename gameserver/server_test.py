import logging
from websocket_server import WebsocketServer
import subprocess
import time
import json,sys
global path
path="games/easy/codes/"

def new_client(client, server):
    msg1="Hey all, a new client has joined us"
    server.send_message(client,msg1)

def message_received(client, server, message):
	#msg = {'code':editor_content,'room':room,'logId':name,'userId':current_user.id}
	print("Client(%d) said: %s" % (client['id'], message))
	data = json.loads(message)

	current_code = {'room':data['room'],'user':data['usrId']}
	log_info = Log.query.filter(id=logId).first()
	
	p_cnt=len(log_info.player_list)
	
	user_id_list=['P76051080','PpP']#left,right
	log=tuple([data['logId'],gameId,p_cnt,game_p_cnt,user_id_list])
	save_code(data['code'],json.dumps(log),data['room'],data['userId'])
	add=0
	for i in range(0,min(len(queuelist_2),10)):
		print(queuelist_2[i]['log'])
		if queuelist_2[i]['room']==current_code['room']:
        	queuelist_2.insert(i,current_code)
			add=1
       		break
	if not add:
		queuelist_2.append(current_code)
	
	#取出msg中的logId當作檔名存成.py檔, 放進queue
def save_code(code,room,user_id,logdata):
	f = open("%s%s_%s.py"%(path,room,user_id), "w") 
	f.write(code)#上傳新的程式碼會直接取代掉
	with open('%sgame_lib.py'%path) as fin:
		lines = fin.readlines() 
		print(lines)
		for i, line in enumerate(lines):
			if i >= 0 and i < 6800:
				f.write(line)
		f.close()
	
	logdata[2]+=1
	if logdata[2]==logdata[3]:
		execute_queue(logdata[0],room,logdata[4])
	
	


def execute_queue(logId,room,user_id_list):
	#在call subprocess 來執行 logId.py
	roomname=room.split()
	
	if logId :
		#left first # 1_<User P76051080>.py
		proc1 = subprocess.Popen(
			['python', '%s%d_%s.py'%(path,logId,user_id_list[0])],
			stdout=subprocess.PIPE)
		# proc2 = subprocess.Popen(
		# 	['python', '%s%d_%s.py'%(path,logId,user_id)],
		# 	stdout=subprocess.PIPE)	
		proc3 = subprocess.Popen(
			['python', '%spingpong.py'%path]+ roomname,
			stdout=subprocess.PIPE)
		out1, err1 = proc1.communicate()
		if(err1 is not None):
			print(err1.decode('utf-8'))
		# out2, err2 = proc2.communicate()
		# if(err2 is not None):
		# 	print(err2.decode('utf-8'))
		out3, err3 = proc3.communicate()
		if(err3 is not None):
			print(err3.decode('utf-8'))



server = WebsocketServer(6005, host='127.0.0.1', loglevel=logging.INFO)
server.set_fn_new_client(new_client)# set callback function
server.set_fn_message_received(message_received)
server.run_forever()