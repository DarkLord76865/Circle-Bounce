def check_collision(ball_pos, ball_vel_vert, ball_vel_hor, ball_rad, time_left, width, height):
	sudari = []
	if ball_vel_vert > 0:
		print("down")
		tm = abs((height - ball_rad - ball_pos[1]) / ball_vel_vert)
		if tm <= time_left:
			sudari.append(("down", tm))
	else:
		print("up")
		tm = (ball_pos[1] - ball_rad) / ball_vel_vert
		print(tm)
		if tm <= time_left:
			sudari.append(("up", tm))
	if ball_vel_hor > 0:
		print("right")
		tm = (width - ball_rad - ball_pos[0]) / ball_vel_hor
		print(tm)
		if tm <= time_left:
			sudari.append(("right", tm))
	else:
		print("left")
		tm = (ball_pos[0] - ball_rad) / ball_vel_hor
		if tm <= time_left:
			sudari.append(("left", tm))

	print(sudari)
	if len(sudari) == 2:
		if sudari[0][1] <= sudari[1][1]:
			return sudari[0]
		else:
			return sudari[1]
	elif len(sudari) == 1:
		return sudari[0]
	else:
		return sudari


print(check_collision((1637, 1055), -113, 142, 25, 0.016666666666667496, 1920, 1080))
