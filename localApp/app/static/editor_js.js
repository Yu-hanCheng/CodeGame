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
        console.log("lan_list:",data)
        set_lan_list(data)
    });
    $('form#commit').submit(function(event) {
        console.log("commit")
        const game_id = document.getElementById("Game").value;
        const glanguage = document.getElementById("mode").value;
        const editor_content=editor.getValue();
        const commit_msg = document.getElementById('commit_msg').value; 
        socket.emit('commit', {code: editor_content, commit_msg:commit_msg, game_id:game_id, glanguage:glanguage, user_id:1});
        
    });

    $('form#upload_to_server').submit(function(event) {
        
        var glanguage = document.getElementById("mode").selectedIndex;
        var commit_msg = document.getElementById('commit_msg').value; 

        let choosed= $("#chooseFile")[0].files;
        convertFile(choosed[0]).then(data => {
            // 把編碼後的字串 send to webserver
            socket.emit('commit', {code: data,commit_msg:commit_msg,glanguage:glanguage});
        return false;
            
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
console.log("editor",editor)
editor.setTheme("ace/theme/twilight");
editor.session.setMode("ace/mode/python");

function changeMode(){
    
    document.getElementById('commit').style.display="block";
    var mode_selected = document.getElementById('mode');
    mode = mode_selected.options[mode_selected.selectedIndex].text;
    console.log("changeMode:",mode);
    editor.session.setMode("ace/mode/"+ mode);
    var contents = {
        c:'main(){}',
        python: '\
def run():\n\
    global paddle_vel,ball_pos,move_unit\n\
    if (ball_pos[-1][0]-ball_pos[-2][0]) <0: \n\
        print("ball moves left")\n\
        if (ball_pos[-1][1]-ball_pos[-2][1]) >0:\n\
            print("ball moves down")\n\
            paddle_vel=move_unit\n\
        elif (ball_pos[-1][1]-ball_pos[-2][1])<0:\n\
            print("ball moves up")\n\
            paddle_vel=-move_unit\n\
    else: \n\
        paddle_vel=0\n\
        print("ball moves right, no need to move paddle1")\n',
        
        sh: '<value attr="something">Write something here...</value>'
    };
    editor.setValue(contents[mode]);
    
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
function set_lan_list(language_list) {
    //先清空舊的語言選項,在新增新的語言選項,保留第一個option為 default
    //[Game_lib.id, Language.id, Language.language_name, Language.language_compiler]
    var mode_select = document.getElementById('mode')
    while (mode_select.length > 1) {
        mode_select.remove(mode_select.length-1);
      }
    for (let index = 1; index < language_list.length+1; index++) {
        const lan_obj = language_list[index-1];
        console.log('lan_obj[1]:',lan_obj[1])
        mode_select.options[index] = new Option(lan_obj[2], lan_obj[3]);//(text,value)
    }
}

