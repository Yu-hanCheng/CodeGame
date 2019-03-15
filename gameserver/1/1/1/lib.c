// Write CPP code here 
#include <netdb.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <errno.h>   // for errno
#include <sys/socket.h> 
#include<json-c/json.h>
#define MAX 80 
// #define PORT 5502
#define SA struct sockaddr 
void func(int sockfd) 
{ 
	char buff[MAX]; 
	int n; 
	for (;;) { 
		bzero(buff, sizeof(buff)); 
		printf("Enter the string : "); 
		n = 0; 
		while ((buff[n++] = getchar()) != '\n') 
			; 
		write(sockfd, buff, sizeof(buff)); 
		bzero(buff, sizeof(buff)); 
		read(sockfd, buff, sizeof(buff)); 
		printf("From Server : %s", buff); 
		if ((strncmp(buff, "exit", 4)) == 0) { 
			printf("Client Exit...\n"); 
			break; 
		} 
	} 
} 

int main(int argc, char *argv[]) 
{ 
	int sockfd, connfd,port_num; 
	struct sockaddr_in servaddr, cli; 
	char *port;
	errno=0;
	long conv = strtol(argv[1], &port, 10);
	// socket create and varification 

	printf("argv[]=%d\n",conv);
	if (errno != 0 || *port != '\0') {
    // Put here the handling of the error, like exiting the program with
    // an error message
		printf("eeroor");
	} else {
		// No error
		port_num = conv;    
		printf("%d\n", port_num);
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
