from socketIO_client import SocketIO, LoggingNamespace
def send_to_webserver(msg_type,msg_content,log_id):
    global ball,paddle1,paddle2
    print("sendtoweb")
    with SocketIO('127.0.0.1', 5000, LoggingNamespace) as socketIO:
        socketIO.emit(msg_type,{'msg':msg_content,'log_id':log_id},)

identify={'P1':'001','P2':'002'}
send_to_webserver('gamemain_connect',identify,'1')
send_to_webserver('info',tuple([[30,30],[0,200],[200,0],2]),'1')