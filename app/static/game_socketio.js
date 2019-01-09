
var script = document.createElement('script');
script.src = '../../static/jquery-3.3.1.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

var socket;
var left_buff=[],right_buff=[],ball_buff=[];
var buff_min=20,buff_normal=50;

namespace = '/test';
socket = io.connect('http://' + document.domain + ':' + location.port+namespace );

$(document).ready(function(){

    socket.on('arrived', function(data) {
        console.log("arrived:",data.msg)
        $('#game_playground').css("display","block");
        $('#page_title').html("Game Start");
    });
    socket.on('enter_room', function(data){
        console.log("enter rooom", data.msg)
        $('#page_title').html("enter room");
    }) 
    socket.on('connect_start', function(data){
        console.log("map Player:", data.msg)        
    })
    socket.on('status', function(data) {
        $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    socket.on('gameover', function(data){
        alert('l_report:'+ JSON.stringify(data.msg.l_report))
        myPopupjs(data.msg,data.log_id);
        // var popup = document.getElementById("myPopup");
        // popup.classList.toggle("show");
    });
    socket.on('gameobject', function(data) {
    // data=tuple([ball,paddle1[1],paddle2[1],[r_score,l_score]])
        left_buff.push(data.msg[1][1]);
        right_buff.push(data.msg[2][1]);
        ball_buff.push(data.msg[0]);
        score_update(data.msg[3]);

        $('#showgame').val($('#showgame').val() + data.msg[1][1]+ '\n');
        $('#showgame').scrollTop($('#showgame')[0].scrollHeight);
    });

    socket.on('message', function(data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    $('#text').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#text').val();
            $('#text').val('');
            socket.emit('text', {msg: text});
        }
    });
    $('select#mode').change(function(event) {
        socket.emit('check_code', {language: document.getElementById("mode").selectedIndex});
        console.log("check_code",document.getElementById("mode").selectedIndex)
    });
    $('form#join').submit(function(event) {
        socket.emit('join', {room: $('#join_room').val(),code: $('#join_code_id').val(), glanguage:document.getElementById("mode").selectedIndex});
        console.log("join_code:",$('#join_code_id').val());
        document.getElementById('join').style.display = "none";
        return false;
    });
    $('form#commit').submit(function(event) {
        var glanguage = document.getElementById("mode").selectedIndex;
        var editor_content=editor.getValue();
        var commit_msg = document.getElementById('commit_msg').value; 
        socket.emit('commit', {code: editor_content,commit_msg:commit_msg,glanguage:glanguage});
        return false;
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
function myPopupjs(data_msg,log_id){

    console.log('msg type parse:'+typeof(JSON.parse(data_msg.l_report)))
    var mytable = "<table class=\"popuptext\" ><tbody><tr>" ;
    var l_data = JSON.parse(data_msg.l_report)
    var r_data = JSON.parse(data_msg.r_report)
    
    mytable += "</tr><tr><td></td><td>SCORE</td></tr><tr>";
    mytable += "</tr><tr><td></td><td>P1</td><td>P2</td></tr><tr>";

    for(key in l_data){
        mytable += "</tr><tr><td>" +key+ "</td>"+ "<td>" + l_data[key]+ "</td>"+"<td>" + r_data[key]+ "</td>";
    }
    
    mytable += "</tr><tr><td></td><td><button onclick=\"javascript:location.href='/games/rank_list/"+log_id+"'\" >rank</button></td></tr></tbody></table>";
    
    document.getElementById("myPopup_dom").innerHTML = mytable;

}
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
editor.session.setMode("ace/mode/javascript");

// function changeMode(){
//     console.log("changeMode")
//     var mode = document.getElementById('mode').value;
//     editor.session.setMode("ace/mode/"+ mode);
//     var contents = {
//         c:'main(){}',
//         python: '\
// def run():\n\
//     global paddle_vel,ball_pos,move_unit\n\
//     if (ball_pos[-1][0]-ball_pos[-2][0]) <0: \n\
//         print("ball moves left")\n\
//         if (ball_pos[-1][1]-ball_pos[-2][1]) >0:\n\
//             print("ball moves down")\n\
//             paddle_vel=move_unit\n\
//         elif (ball_pos[-1][1]-ball_pos[-2][1])<0:\n\
//             print("ball moves up")\n\
//             paddle_vel=-move_unit\n\
//     else: \n\
//         paddle_vel=0\n\
//         print("ball moves right, no need to move paddle1")\n',
        
//         sh: '<value attr="something">Write something here...</value>'
//     };
//     editor.setValue(contents[mode]);
    
// }

function leave_room() {
    socket.emit('left', {}, function() {
        socket.disconnect();

        // go back to the login page
        window.location.href = "{{ url_for('games.index') }}";
    });
}


function ball_update(position){
    var width = $(".ball").outerWidth();
    var height = $(".ball").outerHeight();
    // console.log($(".ball").left())
    $(".ball").css({"left":position[0]-width/2,"top":position[1]-height/2});
}
function left_update(position){
    var windowHeight = $(window).height();
    var height = $(".left-goalkeeper").outerHeight();
    var p_top = position-height/2;
    var topMax = windowHeight - p_top - 5;
    if (p_top < 5) p_top = 5;
    if (p_top > topMax) p_top = topMax;
    $(".left-goalkeeper").css("top",p_top);	
}
function right_update(position){
    var windowHeight = $(window).height();
    var height = $(".right-goalkeeper").outerHeight();
    var p_top = position-height/2;
    var topMax = windowHeight - height - 5;
    if (p_top < 5) p_top = 5;
    if (p_top > topMax) p_top = topMax;
    $(".right-goalkeeper").css("top",p_top);	
}
function score_update(newscores){
    Scores.setLeft(newscores[0]);
    Scores.setRight(newscores[1]);
}
var startTime=new Date();
var speed=10;
var start_flag=0;

setInterval(function(){
    
    if (ball_buff.length>buff_normal){ 
        start_flag=1;
        // console.clear();   
        speed=10;
    }else if(ball_buff.length<buff_min){
        speed=50;
    }

    if (start_flag==1){
        left_update(left_buff.shift());
        right_update(right_buff.shift());
        ball_update(ball_buff.shift());
        
    }
},speed);

var Scores = {
	// set lsef tscore with animation
	setLeft: function(n) {
		n = n || 0;
        if ($(".left-score span").text() == n) {return;}
        else{
            $(".left-score span").text(n);
        }

	},
	// set right score with animation
	setRight: function(n) {
		n = n || 0;
		if ($(".right-score span").text() == n) {return;}
		else {
            $(".right-score span").text(n);
        }
	},
	// returns left score
	getLeft: function() {
		return parseInt($(".left-score span").text());
	},
	// returns right score
	getRight: function() {
		return parseInt($(".right-score span").text());
	},
	// resets the scores [ 0 - 0 ]
	reset: function() {
		$(".left-score span").text(0);
		$(".right-score span").text(0);
	},
	// plays the audio
	play: function() {
		$("#score")[0].play();
	}
}