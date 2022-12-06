import os
import random
from math import pi, sqrt

import cv2
import numpy as np


def rgb_bgr_convert(color):
	return color[::-1]

def move_balls(balls, interval):
	for ball in balls:
		ball.x += ball.v_x * interval
		ball.y += ball.v_y * interval
	return balls

def generate_frame(balls, width, height):
	frame = np.zeros((height, width, 3), dtype="uint8")
	for ball in balls:
		cv2.circle(frame, (int(round(ball.x, 0)), int(round(ball.y, 0))), ball.r, ball.color, -1, cv2.LINE_AA)
	return frame

def calculate_collision(balls, ball1, ball2):
	# write position of balls as functions of time (x + vx*t, y + vy*t)
	# write distance of 2 balls with those functions
	# square to get rid of square root
	# find minimum value of that distance^2 function, and if it is smaller than d^2, find solutions for that function, take the one that happens sooner

	d_pow2 = (balls[ball1].r + balls[ball2].r) ** 2  # distance between balls at collision squared (d^2)
	delta_x = balls[ball1].x - balls[ball2].x  # x1 - x2
	delta_y = balls[ball1].y - balls[ball2].y  # y1 - y2
	delta_vx = balls[ball1].v_x - balls[ball2].v_x  # vx1 - vx2
	delta_vy = balls[ball1].v_y - balls[ball2].v_y  # vy1 - vy2

	# calculate coefficients of distance^2 function
	a = (delta_vx ** 2) + (delta_vy ** 2)  # first coefficient
	if a != 0:  # if a is 0, then function is not quadratic, balls aren't moving, therefore, there is no collision
		b_divis_2 = (delta_x * delta_vx) + (delta_y * delta_vy)  # second coefficient divided by 2 (it simplifies function when in that form)
		c = (delta_x ** 2) + (delta_y ** 2)  # third coefficient

		if (c - ((b_divis_2 ** 2) / a)) < d_pow2:  # if minimum value of distance^2 function is smaller than d^2, then the balls would collide
			# find solutions for function, when it's value is d^2
			discriminant_sqrt = sqrt((b_divis_2 ** 2) - (a * (c - d_pow2)))  # calculate sqrt of discriminant
			sols = (
			(-b_divis_2 - discriminant_sqrt) / a, (-b_divis_2 + discriminant_sqrt) / a)  # calculate both solutions
			sols = [x for x in sols if x >= 0]  # take only solutions bigger than 0 (can't reverse time)
			if len(sols) != 0:
				return min(sols)
	return None

def calculate_wall_collision(balls, ball, wall):
	match wall:
		case 0:  # left
			result = (balls[ball].r - balls[ball].x) / balls[ball].v_x
		case 1:  # right
			result = (width - balls[ball].r - balls[ball].x) / balls[ball].v_x
		case 2:  # bottom
			result = (balls[ball].r - balls[ball].y) / balls[ball].v_y
		case 3:  # top
			result = (height - balls[ball].r - balls[ball].y) / balls[ball].v_y
	return result if result > 0 else None

class Ball:
	def __init__(self, r, x, y, v_x, v_y, color):
		self.r = r
		self.m = ((r ** 3) * pi * 4) / 3
		self.x = x
		self.y = y
		self.v_x = v_x
		self.v_y = v_y
		self.color = color


if __name__ == '__main__':
	fps = 60
	width = 1920
	height = 1080
	num_of_balls = 25
	video_length = 300

	interval = 1 / fps

	# generate balls
	balls = []
	for _ in range(num_of_balls):
		radius = random.randint(int(round(min(width, height) * 0.02, 0)), int(round(min(width, height) * 0.1, 0)))
		while True:
			x, y = random.randint(radius, width - radius - 1), random.randint(radius, height - radius - 1)
			valid = True
			for ball in balls:
				if abs(x - ball.x) <= (radius + ball.r) and abs(y - ball.y) <= (radius + ball.r):
					valid = False
					break
			if valid:
				break
		new_ball = Ball(radius,
		                x, y,
		                random.choice((- 1, 1)) * random.randint(int(round(min(width, height) * 0.05, 0)), int(round(min(width, height) * 0.15, 0))),
		                random.choice((- 1, 1)) * random.randint(int(round(min(width, height) * 0.05, 0)), int(round(min(width, height) * 0.15, 0))),
		                rgb_bgr_convert((random.randint(15, 255), random.randint(15, 255), random.randint(15, 255))))
		balls.append(new_ball)
	del new_ball, x, y, radius, valid

	# simulation
	video = cv2.VideoWriter("test.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
	num_of_frames = video_length * fps

	for frame_num in range(num_of_frames):
		os.system("cls")
		print(f"{round((frame_num / num_of_frames) * 100, 2)} %")

		times = []
		for ball1 in range(len(balls) - 1):
			times_ball1 = []
			for ball2 in range(ball1 + 1, len(balls)):
				times_ball1.append(calculate_collision(balls, ball1, ball2))
			times.append(times_ball1)
		wall_times = []
		for ball in range(len(balls)):
			ball_times = []
			for wall in range(4):  # 0 = left, 1 = right, 2 = bottom, 3 = top
				ball_times.append(calculate_wall_collision(balls, ball, wall))
			wall_times.append(ball_times)

		moved_time = 0
		while moved_time < interval:

			ball_2_ball_col = None  # None: no collision | True: ball 2 ball collision | False: ball 2 wall collision
			time_left = interval - moved_time
			smallest_time = time_left

			for x in range(len(times)):
				for y in range(len(times[x])):
					if times[x][y] is not None and times[x][y] <= smallest_time:
						smallest_ind = (x, x + y + 1)
						smallest_time = times[x][y]
						ball_2_ball_col = True
			for x in range(len(wall_times)):
				for y in range(len(wall_times[x])):
					if wall_times[x][y] is not None and wall_times[x][y] <= smallest_time:
						smallest_ind = (x, y)
						smallest_time = wall_times[x][y]
						ball_2_ball_col = False

			match ball_2_ball_col:
				case None:  # no collision
					balls = move_balls(balls, time_left)
					moved_time += time_left
				case True:  # ball 2 ball collision
					balls = move_balls(balls, smallest_time)

					# Handling collision
					d = balls[smallest_ind[0]].r + balls[smallest_ind[1]].r
					nx = (balls[smallest_ind[1]].x - balls[smallest_ind[0]].x) / d
					ny = (balls[smallest_ind[1]].y - balls[smallest_ind[0]].y) / d
					p = (2 * (nx * (balls[smallest_ind[0]].v_x - balls[smallest_ind[1]].v_x) + ny * (balls[smallest_ind[0]].v_y - balls[smallest_ind[1]].v_y))) / (balls[smallest_ind[0]].m + balls[smallest_ind[1]].m)
					balls[smallest_ind[0]].v_x -= p * balls[smallest_ind[1]].m * nx
					balls[smallest_ind[0]].v_y -= p * balls[smallest_ind[1]].m * ny
					balls[smallest_ind[1]].v_x += p * balls[smallest_ind[0]].m * nx
					balls[smallest_ind[1]].v_y += p * balls[smallest_ind[0]].m * ny

					# calculating new times for balls
					for x in range(len(times)):
						for y in range(len(times[x])):
							if x in smallest_ind or (x + y + 1) in smallest_ind:
								if x == smallest_ind[0] and (x + y + 1) == smallest_ind[1]:
									times[x][y] = None
								else:
									times[x][y] = calculate_collision(balls, x, x + y + 1)
							elif times[x][y] is not None:
								times[x][y] -= smallest_time

					for x in range(len(wall_times)):
						for y in range(4):
							if x in smallest_ind:
								wall_times[x][y] = calculate_wall_collision(balls, x, y)
							elif wall_times[x][y] is not None:
								wall_times[x][y] -= smallest_time

					moved_time += smallest_time
				case False:  # ball 2 wall collision
					balls = move_balls(balls, smallest_time)
					if smallest_ind[1] < 2:
						balls[smallest_ind[0]].v_x *= -1
					else:
						balls[smallest_ind[0]].v_y *= -1

					for x in range(len(times)):
						for y in range(len(times[x])):
							if x == smallest_ind[0] or (x + y + 1) == smallest_ind[0]:
								times[x][y] = calculate_collision(balls, x, x + y + 1)
							elif times[x][y] is not None:
								times[x][y] -= smallest_time

					for x in range(len(wall_times)):
						for y in range(4):
							if x == smallest_ind[0]:
								if y == smallest_ind[1]:
									wall_times[x][y] = None
								else:
									wall_times[x][y] = calculate_wall_collision(balls, x, y)
							elif wall_times[x][y] is not None:
								wall_times[x][y] -= smallest_time

					moved_time += smallest_time

		video.write(generate_frame(balls, width, height))
	video.release()
