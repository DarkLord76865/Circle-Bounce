import cv2
import numpy as np
import random
import os


def generate_frame(ball_pos, ball_rad, ball_color, video, width, height):
	frame = np.zeros((height, width, 3), dtype="uint8")
	cv2.circle(frame, ball_pos, ball_rad, ball_color, -1, cv2.LINE_AA)
	video.write(frame)

def check_collision(ball_pos, ball_vel_vert, ball_vel_hor, ball_rad, time_left, width, height):
	sudari = []
	if ball_vel_vert > 0:
		tm = abs((height - ball_rad - ball_pos[1]) / ball_vel_vert)
		if tm <= time_left:
			sudari.append(("down", tm))
	else:
		tm = abs((ball_pos[1] - ball_rad) / ball_vel_vert)
		if tm <= time_left:
			sudari.append(("up", tm))
	if ball_vel_hor > 0:
		tm = abs((width - ball_rad - ball_pos[0]) / ball_vel_hor)
		if tm <= time_left:
			sudari.append(("right", tm))
	else:
		tm = abs((ball_pos[0] - ball_rad) / ball_vel_hor)
		if tm <= time_left:
			sudari.append(("left", tm))
	if len(sudari) == 2:
		if sudari[0][1] <= sudari[1][1]:
			return sudari[0]
		else:
			return sudari[1]
	elif len(sudari) == 1:
		return sudari[0]
	else:
		return sudari


width = 3840
height = 2160
fps = 60
video = cv2.VideoWriter("test.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
duljina_videa = 3600 * fps

ball_rad = 200
ball_pos = (random.randint(ball_rad, width - ball_rad), random.randint(ball_rad, height - ball_rad))
ball_vel_vert = random.randint(500, 600) * random.choice((1, -1))
ball_vel_hor = random.randint(500, 600) * random.choice((1, -1))
ball_color = [random.randint(0, 255) for i in range(3)]

time_between = 1 / fps


for x in range(duljina_videa):
	os.system("cls")
	print(f"{round(((x + 1) / duljina_videa) * 100, 2)} %")
	remain_tm = time_between

	while remain_tm != 0:
		bump = check_collision(ball_pos, ball_vel_vert, ball_vel_hor, ball_rad, remain_tm, width, height)
		if len(bump) != 0:
			match bump[0]:
				case "left":
					ball_vel_hor *= -1
					ball_pos = [ball_rad, ball_pos[1] + int(round(ball_vel_vert * bump[1], 0))]
				case "right":
					ball_vel_hor *= -1
					ball_pos = [width - ball_rad, ball_pos[1] + int(round(ball_vel_vert * bump[1], 0))]
				case "up":
					ball_vel_vert *= -1
					ball_pos = [ball_pos[0] + int(round(ball_vel_hor * bump[1], 0)), ball_rad]
				case "down":
					ball_vel_vert *= -1
					ball_pos = [ball_pos[0] + int(round(ball_vel_hor * bump[1], 0)), height - ball_rad]
			remain_tm -= bump[1]
			ball_color = [random.randint(0, 255) for i in range(3)]
		else:
			ball_pos = [ball_pos[0] + int(round(ball_vel_hor * remain_tm, 0)), ball_pos[1] + int(round(ball_vel_vert * remain_tm, 0))]
			remain_tm = 0

	generate_frame(ball_pos, ball_rad, ball_color, video, width, height)

video.release()
