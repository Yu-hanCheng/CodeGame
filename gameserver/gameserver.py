import logging
from websocket_server import WebsocketServer

import time
import json,sys,os,base64
game_exec_id=0
servs_full=0
servs_full_right=1

server = WebsocketServer(6005, host='0.0.0.0')

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
	#[data['log_id'],data['user_id'],data['category_id'],compiler,path,filename,player_num]
	r_list = room_list.get_list()
	if len(r_list) == 0:
		room_list.push(user_code_str)
		r_list[0][-1] -=1 #player_num 應到人數
	else:
		# lock
		rooms = room_list.get_list()
		for i in range(0,len(rooms)):
			if user_code_str[0]==rooms[i][0]: #find same room
				# 應該不會發生同一位玩家重複傳訊息來,所以直接-1不用check(前端的join btn按完就會鎖)
				if user_code_str[1]==rooms[i][1]: #怕怕的,還是check一下,如果已經有 userId就直接 return -1(不用update因為是一樣的東西)
					return -1

				rooms[i][-1] -=1 #應到人數-1，結果代表還剩幾位玩家可以加入
				user_code_str[-1]=rooms[i][-1]
				if user_code_str[-1]==0: # if all arrived
					room_list.insert(i,user_code_str)
					return i #arrived_index
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

def set_language(language):
	compiler = {
		"gcc": [1,".c"],
		"python": [2,".py"],
		"sh": [3,".sh"]
	}
	language_obj = compiler.get(language, "Invalid language ID")
	
	return language_obj 

def save_code(code,log_id,user_id,category_id,game_id,language):
	# data['code'],data['log_id'],data['user_id'],data['category_id'],data['game_id'],data['language']
	# 在呼叫 sandbox前 將程式碼依遊戲人數？分類？為路徑 加上 lib後 存於 gameserver並回傳檔名
	# "w"上傳新的程式碼會直接取代掉

	language_res = set_language(str(language))
	path = "%s/%s/%s/"%(category_id,game_id,language)
	filename = "%s_%s"%(log_id,user_id)
	try:
		os.makedirs( path )
	except:
		pass
	decoded = base64.b64decode(code)
		
	with open("%s%s%s"%(path,filename,language_res[1]), "wb") as f:
		f.write(decoded)
	return path,filename,language_res[1],language



def code_address(server,data):
	# 先經過 sandbox, 將結果回傳給user, (確定要使用)再排進 room_list
	global webserver_id,room_list

	path, filename, fileEnd, compiler = save_code(data['code'],data['log_id'],data['user_id'],data['category_id'],data['game_id'],data['language'])

	msg=""	
	log_id_index = push_to_room_list([data['log_id'],data['user_id'],\
	data['category_id'],compiler,path,filename,fileEnd,data['player_num']]) # player_list must put on last
	if log_id_index >= 0: # arrived 
		popped_codes_list = pop_code_in_room(log_id_index, data['log_id'])
		print("popped_codes_list:",popped_codes_list)
		push_to_serv_list(popped_codes_list) 
	else:
		msg +="wait for other players..." 

	server.send_message(webserver_id,msg) # 回傳程式碼處理結果給user

def message_received(client, server, message):
	# ws server的client 來源有2: 1. webserver 2. gamemain
	# 1. webserver: call code_adddress
	# 2. gamemain: 某 room遊戲結束, 通知 game_exec kill 該 room的 dc container, 並執行< movetoserv_q >;
	# 續上：同時傳遞遊戲結果的訊息給 webserver (games/event.py 接收)

	global game_exec_id,serv_list
	try:
		data = json.loads(message)
	except Exception as e:
		print("data json loads failed:",e)
		return
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
			print("send code")
			try:
				server.send_message(game_exec_id, json.dumps(go_exec_item[1]))
			except Exception as e:
				print("send_message:",e)

	elif data['from']=='game':
		print("gameover")
					
while True:
	try:
		server.set_fn_new_client(new_client)# set callback function
		server.set_fn_message_received(message_received)
		server.run_forever()
	except Exception as e:
		print("server exception:",e)





