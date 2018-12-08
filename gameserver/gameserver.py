import logging
from websocket_server import WebsocketServer

import time
import json,sys,os
game_exec_id=0
servs_full=0
servs_full_right=1

server = WebsocketServer(6005, host='127.0.0.1')

class MaxSizeList(object):

	def __init__(self, max_length):
		self.max_length = max_length
		self.ls = []

	def insert(self, i, user_element):
		try:
			if len(self.ls) == self.max_length:
				raise EOFError("fulled")
			else:
				self.ls.insert(i,user_element)
				return 0
		except Exception as e:
			print("push error: ",e)
			return 1

	def push(self, st):
		try:
			if len(self.ls) == self.max_length:
				raise EOFError("fulled")
			else:
				self.ls.append(st)
				return 0
		except Exception as e:
			print("push error: ",e)
			return 1

	def pop_index(self,i):
		try:
			if i > len(self.ls):
				raise EOFError("empty")
			else:
				return [0,self.ls.pop(i)]
		except Exception as e:
			print("push error: ",e)
			return [1,e]
	
	def get_list(self):
		return self.ls

	def get_len(self):
		return len(self.ls)


room_list=MaxSizeList(100)
serv_list=MaxSizeList(50)

def new_client(client, server):
	msg1="Hey all, a new client has joined us"
	# server.send_message(client,msg1)

def push_to_room_list(user_code_str):
	# 將經過 sandbox的 code 放進 room_list, check是否到齊 若有到齊, return logid, 否則 return 0
	if len(room_list.get_list()) == 0:
		room_list.push(user_code_str)
	else:
		# lock
		rooms = room_list.get_list()
		print(len(rooms))
		for i in range(0,len(rooms)):
			if user_code_str[0]==rooms[i][0]: #find same room
				(rooms[i][-1]).remove(user_code_str[1]) # rooms[i][-1]== player_list
				user_code_str[-1]=rooms[i][-1] # update player_list
				if len(user_code_str[-1])==0: # if all arrived
					room_list.insert(i,user_code_str)
					return i # arrived_index
			else:
				pass
		room_list.push(user_code_str) # no same room, then append to the last
		
	return -1
	
	
def pop_code_in_room(i,the_log_id):
	popped =[]
	# _rooms = copy.copy(room_list.get_list())
	_rooms = room_list.get_list()
	while _rooms[i][0]== the_log_id:
		pop = room_list.pop_index(i)
		if pop[0]:
			print("error: ",pop[1])
		else:
			popped.append(pop[1])
			if len(_rooms) == 0:
				break



	return popped#[len(popped),popped]

def push_to_serv_list(elephant):
	# 將 players_list push to server, update server_list_full 
	if 	serv_list.push(elephant)< 1:
		return 0
	else:
		return 1


def sandbox(compiler,path_, filename):
	# 用 subprocess將預測試的檔名當參數執行 script.sh, 使產生 docker container 來驗證程式碼,指令如下 
	# sh test.sh cce238a618539(imageID) python3.7 output.py 
	
	from subprocess import Popen, PIPE
	image='cce238a618539'
	try:
		p = Popen('sh sandbox/script.sh ' + image + ' ' + compiler + ' ' + path_ + ' '+ filename + '',shell=True, stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate()
		if stderr:
			print('stderr:', stderr)
			return [0,stderr]
		else:
			print('stdout:', stdout)
			return [1,stdout]
	except Exception as e:
		print('e: ',e)
		return e
def set_language(language):
	compiler = {
		"0": ["gcc",".c"],
		"1": ["python3",".py"],
		"2": ["sh",".sh"]
	}
	language_obj = compiler.get(language, "Invalid language ID")
	
	return language_obj 

def save_code(code,log_id,user_id,category_id,game_id,language):
	# data['code'],data['log_id'],data['user_id'],data['category_id'],data['game_id'],data['language']
	# 在呼叫 sandbox前 將程式碼依遊戲人數？分類？為路徑 加上 lib後 存於 gameserver並回傳檔名
	# "w"上傳新的程式碼會直接取代掉
	language_res = set_language(str(language))
	print('language_res',language_res)
	path = "%s/%s/%s/"%(category_id,game_id,language)
	filename = "%s_%s%s"%(log_id,user_id,language_res[1])
	try:
		os.makedirs( path )
	except:
		pass
	with open("%s%s"%(path,filename), "w") as f:
		f.write(code+'\n')
		f.write("global paddle_vel,ball_pos,move_unit\npaddle_vel=0\nball_pos=[[0,0],[0,0],[0,0]]\nmove_unit=3\nrun()\n")#要給假值
		# with open('%s%s%s'%(path,game_lib_id,language)) as fin: # lib應該是改取資料庫, 而非開文件
		# 	lines = fin.readlines() 
		# 	for i, line in enumerate(lines):
		# 		if i >= 0 and i < 6800:
		# 			f.write(line)
	return path,filename,language_res[0]



def code_address(server,data):
	# 先經過 sandbox, 將結果回傳給user, (確定要使用)再排進 room_list
	global webserver_id,room_list
	
	path, filename, compiler = save_code(data['code'],data['log_id'],data['user_id'],data['category_id'],data['game_id'],data['language'])
	# filename include .xxx
	test_result = sandbox(compiler,path,filename)
	if test_result[0]: # 1: ok / 0: error 
		msg=test_result[1].decode('utf-8')
		
		log_id_index = push_to_room_list([data['log_id'],data['user_id'],\
		data['category_id'],compiler,path,filename,data['player_list']]) # player_list must put on last
		if log_id_index >= 0: # arrived 

			popped_codes_list = pop_code_in_room(log_id_index, data['log_id'])
			print("popped_codes_list:",popped_codes_list)
			push_to_serv_list(popped_codes_list)
		else:
			msg +="wait for other players..." 
			
	else:
		msg ="sandbox error output: "+ test_result[1].decode("utf-8")
		
	server.send_message(webserver_id,msg) # 回傳程式碼處理結果給user

def message_received(client, server, message):
	# ws server的client 來源有2: 1. webserver 2. gamemain
	# 1. webserver: call code_adddress
	# 2. gamemain: 某 room遊戲結束, 通知 game_exec kill 該 room的 dc container, 並執行< movetoserv_q >;
	# 續上：同時傳遞遊戲結果的訊息給 webserver (games/event.py 接收)

	#msg include code room logId language(compiler, Filename Extension)
	print("Client(%d) said: %s" % (client['id'], message))
	global game_exec_id
	data = json.loads(message)
	
	if data['from']=='webserver':
		global webserver_id
		webserver_id = client
		code_address(server,data)

	elif data['from']=='game_exec':
		game_exec_id = client
		go_exec_item = serv_list.pop_index(0)
		if go_exec_item[0]:
			server.send_message(game_exec_id, 'empty')
		else:
			server.send_message(game_exec_id, json.dumps(go_exec_item[1]))

	elif data['from']=='game':
		print("gameover")
					
	
server.set_fn_new_client(new_client)# set callback function
server.set_fn_message_received(message_received)
server.run_forever()





