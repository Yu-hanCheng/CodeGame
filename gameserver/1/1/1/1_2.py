def run():
    global paddle_vel,ball_pos,move_unit
    if (ball_pos[-1][0]-ball_pos[-2][0]) <0: 
        print("ball moves left")
        if (ball_pos[-1][1]-ball_pos[-2][1]) >0:
            print("ball moves down")
            paddle_vel=move_unit
        elif (ball_pos[-1][1]-ball_pos[-2][1])<0:
            print("ball moves up")
            paddle_vel=-move_unit
    else: 
        paddle_vel=0
        print("ball moves right, no need to move paddle1")

global paddle_vel,ball_pos,move_unit
paddle_vel=0
ball_pos=[[0,0],[0,0],[0,0]]
move_unit=3
run()
