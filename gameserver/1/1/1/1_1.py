def run():
    global paddle_vel,ball_pos,move_unit
    if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
        paddle_vel=move_unit
    elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
        paddle_vel=-move_unit
    else: 
        paddle_vel=0
    
