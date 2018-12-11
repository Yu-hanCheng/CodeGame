# # gamemain send over report to event.py
# # event.py(webserver) send gameover to game_socketio.js
# # {l_score, r_score, gametime}
# from socketIO_client import SocketIO, BaseNamespace
# import json
# log_id='1'
# msg=[json.dumps({'l_score':{'cpu':'50','mem':'30','time':'554400'},'r_score':{'cpu':'52','mem':'32','time':'556600'},'gametime':'554400'}),'ooo',log_id]
# class WebNamespace(BaseNamespace):
#     def on_aaa_response(self, *args):
#         print('on_aaa_response', args)

# def init():
#     with SocketIO('127.0.0.1', 5000) as socketIO:
#         print("init")
#         Web_namespace = socketIO.define(WebNamespace, '/test')
#         print("init")
#         stat=Web_namespace.emit('over',{'msg':[msg]})#q1 log_id
#         print("stat: ",stat)
# init()

# room = message['msg'][2]
from socketIO_client import SocketIO, LoggingNamespace
import json
# def on_bbb_response(*args):
#     print('on_bbb_response', args)

# with SocketIO('localhost', 5000, LoggingNamespace) as socketIO:
#     msg={'msg':{'l_score':{'cpu':'50','mem':'30','time':'554400'},'r_score':{'cpu':'52','mem':'32','time':'556600'},'gametime':'554400'},'log_id':'1'}
#     # {'msg':tuple([ball,paddle1,paddle2,log_id])}
#     socketIO.emit('over', msg, on_bbb_response)
#     socketIO.wait_for_callbacks(seconds=1)

socketIO=SocketIO('127.0.0.1', 5000, LoggingNamespace)

l_report=json.dumps({'user_id':'1','score':'0','cpu':'50','mem':'30','time':'554400'})
r_report=json.dumps({'user_id':'2','score':'1','cpu':'66','mem':'33','time':'333333'})
log_id='1'

def send_to_webserver(msg_type,msg_content,logId):
    print("web:",msg_content)
    # #lock.acquire()
    global ball,paddle1,paddle2,socketIO, score
    socketIO.emit(msg_type,{'msg':msg_content,'log_id':logId})


import sys
filepath = 'display_data.txt'  
with open(filepath) as fp:  
    
    record_content=[]
    content=fp.read().splitlines()
    for e in content:
    	record_content.append(e)

record_content_str=''.join(record_content)
    
print(sys.getsizeof(record_content))
print(record_content)

send_to_webserver('over',{'l_report':l_report,'r_report':r_report,'record_content':record_content_str},log_id)



