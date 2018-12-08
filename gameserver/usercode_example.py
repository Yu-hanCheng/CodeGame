import random
import threading
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from flask_socketio import SocketIO, emit,disconnect
socketio = SocketIO(app, async_mode=async_mode)

class TaskThread(threading.Thread):
    """Thread that executes a task every N seconds"""
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = 1.0
        self.cnt = 30
    
    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval
    
    def shutdown(self):
        """Stop this thread"""
        self._finished.set()
    
    def run(self):
        while self.cnt > 1:
            if self._finished.isSet(): return
            self.task()
            
            # sleep for interval or until shutdown
            self._finished.wait(self._interval)
            self.cnt-=1
    
    def task(self):
        """The task done by this thread - override in subclasses"""
        print(self.cnt)#random.random()

t=TaskThread()
t.run()

# if __name__ == '__main__':
#     socketio.run(app, debug=True,port=5566)