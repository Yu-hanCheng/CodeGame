
// var script = document.createElement('script');
// script.src = '../../static/jquery-3.3.1.js';
// script.type = 'text/javascript';
// document.getElementsByTagName('head')[0].appendChild(script);

var socket;
var left_buff=[],right_buff=[],ball_buff=[];
var buff_min=20,buff_normal=50;
var scaling_ratio;
var editor = ace.edit("editor");    
editor.setTheme("ace/theme/twilight");

lan_mode = document.getElementById('mode');
countdown=document.getElementById("countdown");

namespace = '/test';
socket = io.connect('http://' + document.domain + ':' + location.port+namespace );

$(document).ready(function(){
    socket.emit('join_room',  {room: $('#join_room').val(),privacy: $('#room_privacy').val(),status: $('#room_status').val(),game_start:$('#game_start').val()});
    if($('#game_start').val()=="True"){
        socket.emit('get_players',{room:$('#join_room').val()});
    } 
    socket.on('get_players', function() {
        let left_player = $('#map_left_user').text();
        if(left_player!=" P1 username"){
            socket.emit('the_players',{room:$('#join_room').val(),left:$('#map_left_user').text(),right:$('#map_right_user').text()});  
        }
    });
    socket.on('the_players', function(data) {
        let players=[data.left,data.right];
        game_start(players);
    });
    
    socket.on('gamemain_connect', function(data) {
        game_start(data);
        socket.emit('game_start','');
    });
    socket.on('enter_room', function(data){
        $('#page_title').html("enter room");
        document.getElementById('btn_select_code').style.display = "block";
        document.getElementById('countdown').style.display = "block";
        
    }); 
    socket.on('wait_room', function(data){
        document.getElementById('btn_select_code').style.display = "none";
        $('#page_title').html("wait for others");
    }); 

    socket.on('gameover', function(data){ 
        // alert('l_report:'+ JSON.stringify(data.msg.l_report))
        myPopupjs(data.msg,data.log_id);
        // var popup = document.getElementById("myPopup");
        // popup.classList.toggle("show");
    });
    socket.on('gameobject', function(data) {
        let left = $('.left-goalkeeper')
        let right = $('.right-goalkeeper')
        paddle_update(data['msg'][1], left);
        paddle_update(data['msg'][2], right);
        ball_update(data.msg[0]);
        score_update(data.msg[3]);
    });

    socket.on('chat_message_broadcast', function(data) {
        $('#chat').val($('#chat').val() + '<' + data.user + '> '+ data.msg+'\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    socket.on('timeout', function(data) {
        alert("timeout:"+data)
    });
    socket.on('timeout_over', function(data) {
        alert("timeout_over:"+data)
        document.getElementById('countdown').style.display = "block";
        document.getElementById('btn_select_code').style.display = "block";
        $('#page_title').html("The code can't return paddle value in a second, please try another code");
        
    });
    socket.on('the_change_code', function(data) {
        if (data['code_id']==lan_mode.value){
            let code_decode = atob(data['code']);
            editor.setValue(code_decode);
            // $('#code_commit_msg').val(data['commit_msg'])
        }
    });
    socket.on('countdown', function(data) {
        countdown.innerHTML=data;
        if (data<1){
            $('#page_title').html("send code");
            select_code()
        }
    });
    $('#mode').on('change', function() {
        let lan_name = lan_mode.options[lan_mode.selectedIndex].text;
        
        editor.session.setMode("ace/mode/"+ lan_name.split("-")[0]);
        var code_selected = lan_mode.options[lan_mode.selectedIndex].value;
        if(code_selected=="code_id"){
            code_selected=lan_mode.options[1].value;
        }
        socket.emit('change_code', {room: $('#join_room').val(),code_id:code_selected});
      });
    $('#chattext').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#chattext').val();
            $('#chattext').val('');
            socket.emit('chat_message', text);
        }
    });
    window.addEventListener('resize', evt => {
        rwd_playground();
    });
});
function game_start(data){
    
    document.getElementById('countdown').style.display = "none";
    document.getElementById('btn_select_code').style.display = "none";
    document.getElementById('leave_btn').style.display = "none";
    $('#page_title').html("Game Start");
    $('#map_left_user').html(data[0]); 
    $('#map_right_user').html(data[1]);
    $('.play_space').css("display", "block");
    rwd_playground();
}
function rwd_playground() {
    scaling_ratio=$(".playground").width()/800;
        $(".playground").height(400 * scaling_ratio);
        // 球要在這邊設長寬
        let ball_r=40 * scaling_ratio;
        $(".ball").height(ball_r);
        $(".ball").width(ball_r);
}
function select_code(){
    
    $('#page_title').html("send code");
    var code_selected=lan_mode.value;
    if(lan_mode.value=="code_id"){
        code_selected=lan_mode.options[1].value;
    }
    // document.getElementById('section_code').style.display = "none";
    
    let opponent = document.getElementById('opponent_rank');
    let opponent_rank="";
    if (opponent){ 
        opponent_rank=opponent.value;
    }
    socket.emit('select_code', {room: $('#join_room').val(),code_id:code_selected,opponent:opponent_rank,status: $('#join_status').val()});
}
var countdownnumber=30;
var countdownid,x;
// function timeout_initial(){
    
    // x=document.getElementById("countdown");
    // x.style.display="block";
    // x.innerHTML=countdownnumber;
    // countdownnumber--;
    // countdownid=window.setInterval(countdownfunc,1000);
// }
function countdownfunc(){ 
x.innerHTML=countdownnumber;
if (countdownnumber<1){
    clearInterval(countdownid);
    select_code()
}
countdownnumber--;
}
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
    
    mytable += "</tr><tr><td></td><td><button class=\"button\" onclick=\"javascript:location.href='/games/rank_list/"+log_id+"'\" >rank</button></td></tr></tbody></table>";
    
    document.getElementById("myPopup_dom").innerHTML = mytable;

}
function left_room(){
    // socket.emit('left',{room: $('#join_room').val()});
    socket.disconnect();
    window.location.href = "../leftroom";
}
function ball_update(relative_pos){
    var width = $(".ball").outerWidth();
    var height = $(".ball").outerHeight();
    $(".ball").css({"left":relative_pos[0]+"%" ,"top":relative_pos[1]+"%"});
}
function paddle_update(relative_pos, direction){
    direction.css("top",relative_pos+"%");	
}
function score_update(newscores){

    Scores.setLeft(newscores[0]);
    Scores.setRight(newscores[1]);
}
var chatroom = document.getElementById("chatroom");


function addMsgToBox (data) {
    var msgBox = document.createElement("span")
        msgBox.className = "msg";
    var msg = document.createTextNode(data.msg);

    msgBox.appendChild(msg);
    chatroom.appendChild(msgBox);

    if (chatroom.children.length > max_record) {
        rmMsgFromBox();
    }
}

// 移除多餘的訊息
function rmMsgFromBox () {
    var childs = content.children;
    childs[0].remove();
}
var startTime=new Date();
var speed=10;
var start_flag=0;

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