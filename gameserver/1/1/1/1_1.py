
def run():
    global paddle_vel,paddle_pos,ball_pos,move_unit
    paddle_vel=0
    ballarray=np.array(ball_pos[-1])[:, np.newaxis]
    padarray=np.array(paddle_pos)
    
    x_input=np.vstack([ballarray, padarray]).T
    paddle_vel=int(load_model.predict(x_input)[0])
    print("x_input,paddle_vel:",x_input,paddle_vel)
