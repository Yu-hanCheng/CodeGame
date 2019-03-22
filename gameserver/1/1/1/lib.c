// Write CPP code here 
#include <netdb.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <errno.h>   // for errno
#include <sys/socket.h> 
#include <json-c/json.h>
#define MAX 256
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

	char str[128];	
	// if (strcmp(type_class,"info")==0){
	// 	cnt++;
	// }
	strcpy(str, "{'type':");
	strcat(str, type_class);
	strcat(str, ",'who'");
	strcat(str, WHO);
	strcat(str, ",'content'");
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
		printf("okok");
	}
	else if (strcmp(msg_type_val,"info")==0){
		
		json_object_object_get_ex(json_obj_pointer, "content", &msg_content);
		
		json_object *jobj = json_tokener_parse(json_object_get_string(msg_content));
		
		json_object_object_get_ex(jobj, "ball", &msg_ball);
		if (strcmp(WHO,"P1")==0){
			json_object_object_get_ex(jobj, "paddle1", &msg_paddle);
		}
		else{
			json_object_object_get_ex(jobj, "paddle2", &msg_paddle);
		}
		
		json_object_object_get_ex(jobj, "cnt", &cnt);
		printf("%s %s %s\n",json_object_get_string(msg_ball),json_object_get_string(msg_paddle),json_object_get_string(cnt));
		char *str= json_object_get_string(msg_ball);
		char delim[] = {","};
		char *ptr = strtok(str, delim);
		struct ArrayWrapper ball_int;
		int i=0,j=0;
		while(ptr != NULL)
		{	
			printf("'%s'\n", ptr);
			ball_int.arr[i]=strtol(ptr+1,NULL,10);
			i++;
			ptr = strtok(NULL, delim);
		}
		// for (j=0; j < sizeof(ball_int.arr) / sizeof(ball_int.arr[0]); j++ ) {
		// 	printf("Element[%d] = %d\n", j, ball_int.arr[j] );
		// }
		char * cnt="3";
		int return_paddle;
		return_paddle = run(ball_int,strtol(json_object_get_string(msg_paddle),NULL,10));
		return return_paddle;
		
	}
	else if (strcmp(msg_type_val,"conn")==0){
		printf("okok");
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
	printf("in func sockfd:%d\n",sockfd);
	read(sockfd, buff, sizeof(buff));
	printf("From Server : %s", buff);
	parsed_json = json_tokener_parse(buff);
	enum json_type type = json_object_get_type(parsed_json);
	if (type!=json_type_object){
		printf("not an object\n");
		return ;
	}
	json_object_object_get_ex(parsed_json, "type", &msg_type);
	int content_paddle;
	content_paddle=msg_address(json_object_get_string(msg_type),parsed_json);
	printf("paddle:%d",content_paddle)
	char content_buffer[8],sockfd_buffer[8];
	sprintf(content_buffer, "%d", content_paddle);
	sprintf(sockfd_buffer, "%d", sockfd);
	send_togame("info",content_buffer,sockfd );
	// for (;;) { 
	// 	bzero(buff, sizeof(buff)); 
		
	// 	// n = 0; 
	// 	// while ((buff[n++] = getchar()) != '\n') 
	// 		// ; 
	// 	// char *buff = "{\"connect\": \"joys of programming\"}";
	// 	// char *buff = "connect";
	// write(sockfd, buff, sizeof(buff)); 
	// 	bzero(buff, sizeof(buff)); 
	// 	read(sockfd, buff, sizeof(buff)); 
	// 	printf("From Server : %s", buff); 

	// 	if ((strncmp(buff, "exit", 4)) == 0) { 
	// 		printf("Client Exit...\n"); 
	// 		break; 
	// 	} 
	// } 
} 

int main(int argc, char *argv[]) { 
	int sockfd, connfd,port_num; 
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
	func(sockfd); 

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