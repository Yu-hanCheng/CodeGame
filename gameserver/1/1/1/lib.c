// Write CPP code here 
#include <netdb.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <errno.h>   // for errno
#include <sys/socket.h> 
#include <json-c/json.h>
#define MAX 100
#define WHO "P1"
#define SA struct sockaddr 


void msg_type(json_type msg_type_val ){
	switch(msg_type_val) {
        case json_type_null:
                printf("json_type_null\n");
                break;
        case json_type_boolean:
                printf("json_type_boolean\n");
                break;
        case json_type_double:
                printf("json_type_double\n");
                break;
        case json_type_int:
                printf("json_type_int\n");
                break;
        case json_type_object:
                printf("json_type_object\n");
                break;
        case json_type_array:
                printf("json_type_array\n");
                break;
        case json_type_string:
                printf("json_type_string\n");
                break;
        }
}
void msg_address(char* msg_type_val, json_object* json_obj_pointer ){

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

	}
	else if (strcmp(msg_type_val,"conn")==0){
		printf("okok");
	}

}
void func(int sockfd) 
{ 
	char buff[MAX]; 
	int n; 
	struct json_object *msg_type;
	struct json_object *parsed_json;
	
	bzero(buff, sizeof(buff)); 
	read(sockfd, buff, sizeof(buff));
	// printf("From Server : %s", buff);
	parsed_json = json_tokener_parse(buff);
	enum json_type type = json_object_get_type(parsed_json);
	if (type!=json_type_object){
		printf("not an object\n");
		return ;
	}
	json_object_object_get_ex(parsed_json, "type", &msg_type);
	printf("%s\n",json_object_get_string(msg_type));
	// printf("&&%s\n",&parsed_json);
	// printf("**%d\n",*parsed_json);
	// char* str=;
	msg_address(json_object_get_string(msg_type),parsed_json);
	// printf("type: %s\n", json_object_get_string(msg_type));


	// for (;;) { 
	// 	bzero(buff, sizeof(buff)); 
		
	// 	// n = 0; 
	// 	// while ((buff[n++] = getchar()) != '\n') 
	// 		// ; 
	// 	// char *buff = "{\"connect\": \"joys of programming\"}";
	// 	// char *buff = "connect";
	// 	write(sockfd, buff, sizeof(buff)); 
	// 	bzero(buff, sizeof(buff)); 
	// 	read(sockfd, buff, sizeof(buff)); 
	// 	printf("From Server : %s", buff); 

	// 	if ((strncmp(buff, "exit", 4)) == 0) { 
	// 		printf("Client Exit...\n"); 
	// 		break; 
	// 	} 
	// } 
} 

int main(int argc, char *argv[]) 
{ 
	int sockfd, connfd,port_num; 
	struct sockaddr_in servaddr, cli; 
	char *port;
	errno=0;
	long conv = strtol(argv[1], &port, 10);
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
	servaddr.sin_addr.s_addr = inet_addr("127.0.0.1"); 
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
