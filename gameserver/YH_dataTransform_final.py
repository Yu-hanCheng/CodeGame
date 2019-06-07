# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:58:36 2019

@author: scream
"""
#%%
import numpy as np
import pickle
#%%
with open('log_4 (1).txt', 'r') as f:
    raw=f.readlines()
    
#%%
def raw2gameInfor(raw):
    def str2data_pos(stringdata, datatype_str):
        x=[]
        y=[]
        total_trials=stringdata.count("''")
        first_x_start=len(datatype_str)
        first_x_end=stringdata.find(',')
        first_y_start=first_x_end+1
        first_y_end=stringdata.find("''")
        x.append(stringdata[first_x_start: first_x_end])
        y.append(stringdata[first_y_start: first_y_end])
    
        new_string=stringdata[first_y_end+2:]
        # next_x_start = y_end+2
        for i in range(0, total_trials-1):
            x_end=new_string.find(",")
            x.append(new_string[0:x_end])
            y_start=x_end+1
            y_end=new_string.find("''")
            # new start = y_end+2
            y.append(new_string[y_start:y_end])
            new_string=new_string[y_end+2:]
        return x, y
    
    def str2int(matrix):
        x=[]
        for i in range(0, len(matrix)):
            x.append(int(matrix[i]))
        return np.array(x)[:, np.newaxis]
        
    def str2data_move(stringdata):
        m=[]
        total_trials=stringdata.count("''")-1
        new_string=stringdata
        for i in range(0, total_trials):
            first_m_start=new_string.find("''")+2
            first_m_end=new_string[first_m_start:].find("''")+first_m_start
            m.append(new_string[first_m_start:first_m_end])
#       next_m_start=first_m_end+2
            new_string=new_string[first_m_end:]
        return m
    
    BallPosition=raw[0]
    P1_Position=raw[2]
    P1_Move=raw[4]
    P2_Position=raw[6]
    P2_Move=raw[8]

    Ball_x, Ball_y= str2data_pos(BallPosition, "BALL: ")
    P1_x, P1_y= str2data_pos(P1_Position, "P1: ")
    P2_x, P2_y= str2data_pos(P2_Position, "P2: ")

    Ball_x, Ball_y= str2data_pos(BallPosition, "BALL: ")
    P1_x, P1_y= str2data_pos(P1_Position, "P1: ")
    P2_x, P2_y= str2data_pos(P2_Position, "P2: ")

    BallPosition_converted=np.hstack([str2int(Ball_x), str2int(Ball_y)])
    PlatformPosition_P1=np.hstack([str2int(P1_x), str2int(P1_y)])
    PlatformPosition_P2=np.hstack([str2int(P2_x), str2int(P2_y)])    

    m1=str2data_move(P1_Move)
    m2=str2data_move(P2_Move)

    Instruction_P1=str2int(m1)
    Instruction_P2=str2int(m2)

    GameInformation=[BallPosition_converted, PlatformPosition_P1, PlatformPosition_P2,Instruction_P1,Instruction_P2 ]
    return GameInformation

#%%
GameInformation=raw2gameInfor(raw)
filename="GameInfor_test.pickle"
pickle.dump(GameInformation, open(filename, 'wb'))

    