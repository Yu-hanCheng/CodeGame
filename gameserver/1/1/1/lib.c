// Write CPP code here 
#include <netdb.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <errno.h>   // for errno
#include <sys/socket.h> 
#include <json-c/json.h>
#define MAX 1024
#define SA struct sockaddr 
#define SIZE 2
#define MOVE_UNIT 3
#define WHO "P1" // game_exec

// A wrapper for array to make sure that array 
// is passed by value. 
struct ArrayWrapper 
{ 
    int arr[SIZE]; 
};
int paddle_vel;

// int cnt=0;
void send_togame(char* type_class, char* content, int sockfd){

	char str[64];	
	// if (strcmp(type_class,"info")==0){
	// 	cnt++;
	// }
	strcpy(str, "{'type':'");
	strcat(str, type_class);
	strcat(str, "','who':'");
	strcat(str, WHO);
	strcat(str, "','content':");
	strcat(str, content);
	// strcat(str, ",'cnt'");
	// strcat(str, cnt);
	strcat(str, "}");
	write(sockfd, str, sizeof(str));
}
int msg_address(char* msg_type_val, json_object* json_obj_pointer ){

	struct json_object *msg_content;
	struct json_object *msg_ball, *msg_paddle, *cnt;
	
	if (strcmp(msg_type_val,"conn")==0){
		send_togame("connect","user_id",user_id,sockfd );
	}else if (strcmp(msg_type_val,"info")==0){
		int content_paddle; 
		content_paddle=on_gameinfo(json_obj_pointer);
		printf("content_paddle:%d",content_paddle);
		char content_buffer[8];
		sprintf(content_buffer, "%d", content_paddle);
		send_togame("info","content",content_buffer,sockfd );
	}else if (strcmp(msg_type_val,"over")==0){
		struct Tuple_score t = score(json_obj_pointer);
		printf("recv gameover");
		char report[64];
		strcpy(report, "\"");
		strcpy(report, user_id);
		strcpy(report, ",");
		// strcpy(report, t.p_score);
		// strcpy(report, ",");
		// strcpy(report, t.cpu);
		// strcpy(report, ",");
		// strcpy(report, t.mem);
		// strcpy(report, ",");
		// strcpy(report, t.avg_time);
		strcpy(report,"\"");
		send_togame('score',"content",report,sockfd);
    
	}else if (strcmp(msg_type_val,"score_recved")==0){
	}
	return 0;
}
void func(int sockfd) 
{ 
	char buff[MAX]; 
	int n; 
	struct json_object *msg_type;
	struct json_object *parsed_json;
	
	bzero(buff, sizeof(buff)); 
	printf("in recv_fromgame:\n");
	read(sockfd, buff, sizeof(buff),0);
	printf("From Server : %s", buff);
	parsed_json = json_tokener_parse(buff);
	enum json_type type = json_object_get_type(parsed_json);
	if (type!=json_type_object){
		printf("not an object\n");
		return ;
	}
	json_object_object_get_ex(parsed_json, "type", &msg_type);
	int content_paddle;

	content_paddle=msg_address(json_object_get_string(msg_type),parsed_json,sockfd);
	
} 

int main(int argc, char *argv[]) { 
	int connfd,port_num; 
	struct sockaddr_in servaddr, cli; 
	char *port;
	char *addr_ip;
	errno=0;
	addr_ip=argv[1];
	long conv = strtol(argv[2], &port, 10);
	// socket create and varification 

	if (errno != 0 || *port != '\0') {
		printf("eerroor");
	} else { // No error
		port_num = conv;    
	}
	sockfd = socket(AF_INET, SOCK_STREAM, 0); 
	if (sockfd == -1) { 
		printf("socket creation failed...\n"); 
		exit(0); 
	} 
	else
		printf("Socket successfully created..\n"); 
	bzero(&servaddr, sizeof(servaddr)); 

	// assign IP, PORT 
	servaddr.sin_family = AF_INET; 
	servaddr.sin_addr.s_addr = inet_addr(addr_ip); 
	servaddr.sin_port = htons(port_num); 

	// connect the client socket to server socket 
	if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) { 
		printf("connection with the server failed...\n"); 
		exit(0); 
	} 
	else
		printf("connected to the server..\n"); 
	// function for chat 
	while(1){
		recv_fromgame(); 
	}
	// close the socket 
	close(sockfd); 
} 
int run(struct ArrayWrapper ball_array, int paddle){ //editor 上要隱藏
	int j;
	int *ball=ball_array.arr;
	int ball_last[2]={0,0};

	if((ball[1]-ball_last[1])>0){
		if((ball[1]-paddle)<8){
			paddle_vel=0;
		}
		else if((ball[1]-paddle)>8){
			paddle_vel=MOVE_UNIT*2;
		}
	}
	else if((ball[1]-ball_last[1])<0){
		if((ball[1]-paddle)<-8){
			paddle_vel=-MOVE_UNIT*2;
		}
		else if((ball[1]-paddle)>-8){
			paddle_vel=0;
		}
	}
	else{
		paddle_vel=0;
	}
	ball_last[0]=ball[0]; //editor 上要隱藏
	ball_last[1]=ball[1]; //editor 上要隱藏
	for (j=0; j < sizeof(ball_last) / sizeof(ball_last[0]); j++ ) {
		printf("ball_last[%d] = %d\n", j, ball_last[j] );
	}
	return paddle_vel;
}