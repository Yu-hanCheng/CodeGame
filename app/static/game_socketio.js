
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
    socket.emit('join_room',  {room: $('#join_room').val(),status: $('#room_status').val()});
    
    socket.on('arrived', function(data) {
        console.log("arrived:",data.msg)
        $('#game_playground').css("display","block");
        $('#page_title').html("Game Start");
    });
    socket.on('enter_room', function(data){
        $('#page_title').html("enter room");
        document.getElementById('section_code').style.display = "block";
        timeout_initial()
    }) 
    socket.on('wait_room', function(data){
        $('#page_title').html("wait for others");
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
        console.log("data:",data)
        // left_buff.push(data.msg[1][1]);
        // right_buff.push(data.msg[2][1]);
        // ball_buff.push(data.msg[0]);
        left_update(data.msg[1][1]);
        right_update(data.msg[2][1]);
        ball_update(data.msg[0]);
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

});
function select_code(){
    var code_selected = document.getElementById('mode').value;
    if(code_selected=="code_id"){
        code_selected=document.getElementById("mode").options[1].value;
    }
    document.getElementById('section_code').style.display = "none";
    document.getElementById('section_game').style.display = "block";
    socket.emit('select_code', {room: $('#join_room').val(),code_id:code_selected});
}
var countdownnumber=5;
var countdownid,x;
function timeout_initial(){
    x=document.getElementById("countdown");
    x.innerHTML=countdownnumber;
    countdownnumber--;
    countdownid=window.setInterval(countdownfunc,1000);
}
function countdownfunc(){ 
x.innerHTML=countdownnumber;
if (countdownnumber==0){
    alert("send code");
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
    
    mytable += "</tr><tr><td></td><td><button onclick=\"javascript:location.href='/games/rank_list/"+log_id+"'\" >rank</button></td></tr></tbody></table>";
    
    document.getElementById("myPopup_dom").innerHTML = mytable;

}

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

// setInterval(function(){
    
//     if (ball_buff.length>buff_normal){ 
//         start_flag=1;
//         // console.clear();   
//         speed=10;
//     }else if(ball_buff.length<buff_min){
//         speed=50;
//     }

//     if (start_flag==1){
//         left_update(left_buff.shift());
//         right_update(right_buff.shift());
//         ball_update(ball_buff.shift());
        
//     }
// },speed);

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