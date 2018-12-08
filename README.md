# Usage
### web server
1. `virtualenv venv`
2. `source ./venv/bin/activate`
3. `pip install -r requirements.txt`
4. `export FLASK_APP=codegame.py`
5. `flask db init`
6. `flask db migrate`
7. `flask db upgrade`
8. `flask run` and Running on http://127.0.0.1:5000/


### game server
1. `cd gameserver`
2. `virtualenv venv`
3. `source ./venv/bin/activate`
4. `pip install -r requirements.txt`
5. delete server_test.py line66 `, loglevel=logging.INFO` 
6. `python server_test.py`and Running on http://127.0.0.1:6005/



# Descript 
## Data flow
### 玩家上傳程式碼到 gameserver執行

1. 程式碼由 app/games/routes.py 的 game_view function中上傳，就build a websocket client: ws = create_connection("ws://localhost:6005")
2. gameserver這邊由 server_test.py build websocket server接收 玩家程式碼
~~3. server_test.py 等待兩位玩家都上傳程式碼~~
~~4. fork 3 processes to execute 玩家程式碼 和 遊戲程式~~

### 玩家進入遊戲畫面、聊天室、~~遊戲訊息溝通~~
1. 由 url: `http://localhost:5000/games` 輸入要進入的聊天室
2. Webserver 透過 app/main/events.py 來接收 socket 訊息(聊天室和~~遊戲物件位置~~)
