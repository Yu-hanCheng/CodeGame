import pickle, time
import numpy as np
ball_list=[]
p1_list=[]
p1_move_list=[]
p2_list=[]
p2_move_list=[]
with open('log_6 (2).txt', 'rb') as f:
	ball = f.readline()
	ball_info=ball.decode().split('\'\'')
	
	for e in ball_info[0:-1]:
		e_list=e.split(',')
		to_tuple=[]
		for ee in e_list:
			to_tuple.append(int(ee))
		ball_list.append(tuple(to_tuple))