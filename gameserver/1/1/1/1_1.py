def run():
    global paddle_vel,paddle_pos,ball_pos,move_unit
    paddle_vel=0
    if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
        if ball_pos[-1][1]-paddle_pos<8:
            paddle_vel=0
        elif ball_pos[-1][1]-paddle_pos>8:
            paddle_vel=move_unit*2
    elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
        if ball_pos[-1][1]-paddle_pos>-8:
            paddle_vel=0
        elif ball_pos[-1][1]-paddle_pos<-8:
            paddle_vel=-move_unit*2
    else:
        paddle_vel=0