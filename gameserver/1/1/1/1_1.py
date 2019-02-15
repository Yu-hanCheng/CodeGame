# positove down 
def run():
    global paddle_vel,paddle_pos,ball_pos,move_unit
    paddle_vel=0
    if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
        if ball_pos[-2][1]>paddle_pos-5:
            paddle_vel=move_unit
    elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
        if ball_pos[-2][1]<paddle_pos+5:
            paddle_vel=-move_unit
    else: 
        paddle_vel=0
    
