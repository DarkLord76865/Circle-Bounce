import cv2
import numpy as np
import random
from math import pi, sqrt


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
		cv2.circle(frame, (ball.x, ball.y), ball.r, ball.color, -1, cv2.LINE_AA)
	return frame

class Ball:
	def __init__(self, r, x, y, v_x, v_y, color):
		self.r = r
		self.m = (r ** 2) * pi
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
	video_length = 10

	interval = 1 / fps

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

	video = cv2.VideoWriter("test.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
	num_of_frames = video_length * fps
	for frame_num in range(num_of_frames):
		print(f"{round((frame_num / num_of_frames) * 100, 2)} %")

		times = []
		for ball1 in range(len(balls)):
			times_ball1 = []
			for ball2 in range(ball1 + 1, len(balls)):
				delta_x = balls[ball2].x - balls[ball1].x
				delta_y = balls[ball2].y - balls[ball1].y
				delta_vx = balls[ball2].v_x - balls[ball1].v_x
				delta_vy = balls[ball2].v_y - balls[ball1].v_y
				sum_r = balls[ball2].r + balls[ball1].r
				cross_xvy_sqr = (delta_x ** 2) * (delta_vy ** 2)
				cross_yvx_sqr = (delta_y ** 2) * (delta_vx ** 2)
				multiply_every_double = delta_x * delta_y * delta_vx * delta_y * 2
				print(cross_xvy_sqr + cross_yvx_sqr - multiply_every_double)
				if sqrt(cross_xvy_sqr + cross_yvx_sqr - multiply_every_double) < sum_r:
					sum_v_sqr = (delta_vx ** 2) + (delta_vy ** 2)
					under_root = sqrt(multiply_every_double - cross_xvy_sqr - cross_yvx_sqr + (sum_r ** 2) * sum_v_sqr)
					sols = [(- (delta_x * delta_vx + delta_y * delta_vy) - under_root) / sum_v_sqr, (- (delta_x * delta_vx + delta_y * delta_vy) + under_root) / sum_v_sqr]
					times_ball1.append(min(tuple(x for x in sols if x >= 0)))
				else:
					times_ball1.append(None)
			times.append(times_ball1)
		try:
			smallest_time = times[0][0]
			smallest_ind = (0, 0)
			for x in range(len(times)):
				for y in range(len(times[x])):
					if times[x][y] < smallest_time:
						smallest_ind = (x, y)
						smallest_time = times[x][y]
			if smallest_time <= interval:
				balls = move_balls(balls, smallest_time)
				for x in range(len(times)):
					for y in range(len(times)):
						times[x][y] -= smallest_time

				# Handling collision

				# Ball_1: balls[smallest_ind[0]]
				# Ball_2: balls[smallest_ind[0] + smallest_ind[1] + 1]
				m1_plus_m2 = balls[smallest_ind[0]].m + balls[smallest_ind[0] + smallest_ind[1] + 1].m
				m1_minus_m2 = balls[smallest_ind[0]].m - balls[smallest_ind[0] + smallest_ind[1] + 1].m

				balls[smallest_ind[0]].v_x = ((m1_minus_m2 * balls[smallest_ind[0]].v_x) + (2 * balls[smallest_ind[0] + smallest_ind[1] + 1].m * balls[smallest_ind[0] + smallest_ind[1] + 1].v_x)) / m1_plus_m2
				balls[smallest_ind[0] + smallest_ind[1] + 1].v_x = (- (m1_minus_m2 * balls[smallest_ind[0] + smallest_ind[1] + 1].v_x) + (2 * balls[smallest_ind[0]].m * balls[smallest_ind[0]].v_x)) / m1_plus_m2

				balls[smallest_ind[0]].v_y = ((m1_minus_m2 * balls[smallest_ind[0]].v_y) + (2 * balls[smallest_ind[0] + smallest_ind[1] + 1].m * balls[smallest_ind[0] + smallest_ind[1] + 1].v_y)) / m1_plus_m2
				balls[smallest_ind[0] + smallest_ind[1] + 1].v_y = (- (m1_minus_m2 * balls[smallest_ind[0] + smallest_ind[1] + 1].v_y) + (2 * balls[smallest_ind[0]].m * balls[smallest_ind[0]].v_y)) / m1_plus_m2

			else:
				raise IndexError
		except IndexError:
			balls = move_balls(balls, interval)

		# handle balls movement
		video.write(generate_frame(balls, width, height))
	video.release()
