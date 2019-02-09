var script = document.createElement('script');
script.src = '../../static/jquery-3.3.1.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

var socket;
var left_buff=[],right_buff=[],ball_buff=[];
var buff_min=20,buff_normal=50;
web_port=5000

namespace = '/local';
socket = io.connect('http://' + document.domain + ':' + web_port );

$(document).ready(function(){
    
    socket.on('lan_list', function(data) {
//Game_lib.id,Category.id,Category.name,Game.id,Game.gamename,Language.id, Language.language_name, Language.filename_extension)
        console.log("lan_list:",data)
        set_lan_list(data)
    });
    socket.on('library', function(data) {
        //Game_lib.id,Category.id,Category.name,Game.id,Game.gamename,Language.id, Language.language_name, Language.filename_extension)
                var FD  = new FormData();

                FD.append("path", data[0]);
                FD.append("end", data[1]);
                FD.append("lib", String.fromCharCode.apply(null,  new Uint8Array(data[2])));
                FD.append("test_game", String.fromCharCode.apply(null,  new Uint8Array(data[3])));

                document.getElementById('commit').style.display="block";
                
                send_to_back(FD,"multipart/form-data","library")
            });
    $('form#commit').submit(function(event) {
        const editor_content=editor.getValue();
        var encodedData = window.btoa(editor_content);

        before_sendback(encodedData,"application/json","commit")
        // need to send back to localapp to sandbox
    });

    $('form#upload_to_server').submit(function(event) {
        
        let choosed= $("#chooseFile")[0].files;
        convertFile(choosed[0]).then(data => {
            // 把編碼後的字串 send to webserver
            before_sendback(data,"application/json","commit")
            return false;//return回哪裡QAQ
          })
          .catch(err => console.log(err))
        
    });

});

function previewFiles(files) {
    if (files && files.length >= 1) {
        $.map(files, file => {
            convertFile(file)
                .then(data => {
                  // 把編碼後的字串輸出到console
                //   const upload_file = data
                  console.log('preview: ',data)
                //   showPreviewImage(data, file.name)
                })
                .catch(err => console.log(err))
        })
    }

}

// 使用FileReader讀取檔案，並且回傳Base64編碼後的source
function convertFile(file) {
    return new Promise((resolve,reject)=>{
        // 建立FileReader物件
        let reader = new FileReader()
        // 註冊onload事件，取得result則resolve (會是一個Base64字串)
        reader.onload = () => { resolve(reader.result) }
        // 註冊onerror事件，若發生error則reject
        reader.onerror = () => { reject(reader.error) }
        // 讀取檔案
        reader.readAsDataURL(file)
    })
}

// 當上傳檔案改變時清除目前預覽圖，並且呼叫previewFiles()
$("#chooseFile").change(function(){
    console.log(this)
    $("#previewDiv").empty() // 清空當下預覽
    previewFiles(this.files) // this即為<input>元素
    console.log('this.files',this.files);
})

var editor = ace.edit("editor");    
editor.setTheme("ace/theme/twilight");
editor.session.setMode("ace/mode/python");

function changeMode(){
    // Game_lib.id,Category.id,Category.name,Game.id,Game.gamename,Language.id, Language.language_name, Language.filename_extension
    // filename = "%s_%s%s"%(log_id,user_id,language_res[1]) 
    
    var mode = document.getElementById('mode').value.split(",");
    socket.emit('get_lib', {category_id: mode[1],game_id: mode[3],language_id:mode[5], filename_extension:mode[7]});
    editor.session.setMode("ace/mode/"+ mode[6]);
    var contents = {
        c:'main(){}',
        python: '\
def run():\n\
    global paddle_vel,ball_pos,move_unit\n\
    if (ball_pos[-1][0]-ball_pos[-2][0]) <0: \n\
        if (ball_pos[-1][1]-ball_pos[-2][1]) >0:\n\
            paddle_vel=move_unit\n\
        elif (ball_pos[-1][1]-ball_pos[-2][1])<0:\n\
            paddle_vel=-move_unit\n\
    else: \n\
        paddle_vel=0\n',
        sh: '<value attr="something">Write something here...</value>'
    };
    editor.setValue(contents[mode[6]]);
    
}

function leave_room() {
    socket.emit('left', {}, function() {
        socket.disconnect();
        // go back to the login page
        window.location.href = "{{ url_for('games.index') }}";
    });
}
function changeGame(){
    var game_selected = document.getElementById('Game')
    socket.emit('get_lanlist', {game_id: game_selected.value});
}
function send_to_back(content,Content_type,dest){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        document.getElementById("sandbox_res").innerHTML = this.responseText;
        // check code in Docker container first
        // socket.emit('commit', {code: editor_content, commit_msg:commit_msg, game_id:game_id, glanguage:glanguage, user_id:1});
    }
    };
    
    xhttp.open("POST", dest, true);
    xhttp.send(content);
}
function set_lan_list(language_list) {
    //先清空舊的語言選項,在新增新的語言選項,保留第一個option為 default
    // Game_lib.id,Category.id,Category.name,Game.id,Game.gamename,Language.id, Language.language_name, Language.filename_extension)
    var mode_select = document.getElementById('mode')
    while (mode_select.length > 1) {
        mode_select.remove(mode_select.length-1);
      }
    for (let index = 1; index < language_list.length+1; index++) {
        const lan_obj = language_list[index-1];
        console.log('lan_ob:',lan_obj)
        mode_select.options[index] = new Option(lan_obj[6], lan_obj);//(text,value(str))
    }
}
function before_sendback(Data,content_type,post_dest){
    const obj = document.getElementById("mode").value;
        // 0Game_lib.id,1Category.id,2Category.name,3Game.id,4Game.gamename,5Language.id, 6Language.language_name, 7Language.filename_extension
    var commit_msg = document.getElementById('commit_msg').value; 
    var lan_compiler
        switch(obj[-1]) {
            case ".py":
            lan_compiler = "python3"
              break;
            case ".c":
            lan_compiler = "gcc"
              break;
            default:
            lan_compiler = "python"
        }
    var user_id = document.getElementById('user_id').value;
    content_to_send=JSON.stringify({"encodedData":Data,"commit_msg":commit_msg,"lan_compiler":lan_compiler,'obj':obj,'user_id':user_id})
    send_to_back(content_to_send,content_type,post_dest)
}
