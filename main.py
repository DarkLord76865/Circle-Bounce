import cv2
import numpy as np
import random
from math import pi, sqrt, sin, cos, atan


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
		#print(frame, (ball.x, ball.y), ball.r, ball.color, -1, cv2.LINE_AA, sep="\n")
		cv2.circle(frame, (int(round(ball.x, 0)), int(round(ball.y, 0))), ball.r, ball.color, -1, cv2.LINE_AA)
	#cv2.imshow("test", frame)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	return frame

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

	# simulation

	video = cv2.VideoWriter("test.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
	num_of_frames = video_length * fps
	for x in range(60):
		video.write(generate_frame(balls, width, height))

	for frame_num in range(num_of_frames):
		# print(f"{round((frame_num / num_of_frames) * 100, 2)} %")

		times = []
		for ball1 in range(len(balls)):
			times_ball1 = []
			for ball2 in range(ball1 + 1, len(balls)):
				min_dist_pow2 = (balls[ball1].r + balls[ball2].r) ** 2

				delta_x = balls[ball1].x - balls[ball2].x
				delta_y = balls[ball1].y - balls[ball2].y
				delta_vx = balls[ball1].v_x - balls[ball2].v_x
				delta_vy = balls[ball1].v_y - balls[ball2].v_y

				a = delta_vx + delta_vy
				if a != 0:
					b_divid_2 = delta_x * delta_vx + delta_y * delta_vy
					c = delta_x ** 2 + delta_y ** 2

					if (c - ((b_divid_2 ** 2) / a)) < min_dist_pow2:
						#print(b_divid_2, a, c, min_dist_pow2)
						discriminant_sqrt = sqrt((b_divid_2 ** 2) - (a * (c - min_dist_pow2)))
						sols = [(-b_divid_2 - discriminant_sqrt) / a, (-b_divid_2 + discriminant_sqrt) / a]
						sols = [x for x in sols if x >= 0]
						try:
							times_ball1.append(min(sols))
						except ValueError:
							times_ball1.append(None)
					else:
						times_ball1.append(None)
				else:
					times_ball1.append(None)
			times.append(times_ball1)
		# print(times)

		# za odbijene lopte provesti nove izracune vremena
		try:
			smallest_time = interval
			smallest_ind = (None, None)
			for x in range(len(times)):
				for y in range(len(times[x])):
					if times[x][y] is not None and times[x][y] < smallest_time:
						smallest_ind = (x, x + y + 1)
						smallest_time = times[x][y]
			if smallest_time <= interval and smallest_ind[0] is not None:
				print("prolaz")
				balls = move_balls(balls, smallest_time)
				for x in range(len(times)):
					for y in range(len(times[x])):
						if times[x][y] is not None:
							times[x][y] -= smallest_time

				# Handling collision

				print(f"Ball1:\nm: {balls[smallest_ind[0]].m}\nr: {balls[smallest_ind[0]].r}\nx: {balls[smallest_ind[0]].x}\ny: {balls[smallest_ind[0]].y}\nvx: {balls[smallest_ind[0]].v_x}\nvy: {balls[smallest_ind[0]].v_y}")
				print(f"Ball2:\nm: {balls[smallest_ind[1]].m}\nr: {balls[smallest_ind[1]].r}\nx: {balls[smallest_ind[1]].x}\ny: {balls[smallest_ind[1]].y}\nvx: {balls[smallest_ind[1]].v_x}\nvy: {balls[smallest_ind[1]].v_y}")

				# Ball_1: balls[smallest_ind[0]]
				# Ball_2: balls[smallest_ind[0] + smallest_ind[1] + 1]

				#m1_plus_m2 = balls[smallest_ind[0]].m + balls[smallest_ind[1]].m
				#m1_minus_m2 = balls[smallest_ind[0]].m - balls[smallest_ind[1]].m

				d = balls[smallest_ind[0]].r + balls[smallest_ind[1]].r
				nx = (balls[smallest_ind[1]].x - balls[smallest_ind[0]].x) / d
				ny = (balls[smallest_ind[1]].y - balls[smallest_ind[0]].y) / d
				p = (2 * (nx * (balls[smallest_ind[0]].v_x - balls[smallest_ind[1]].v_x) + ny * (balls[smallest_ind[0]].v_y - balls[smallest_ind[1]].v_y))) / (balls[smallest_ind[0]].m + balls[smallest_ind[1]].m)

				balls[smallest_ind[0]].v_x -= p * balls[smallest_ind[1]].m * nx
				balls[smallest_ind[0]].v_y -= p * balls[smallest_ind[1]].m * ny
				balls[smallest_ind[1]].v_x += p * balls[smallest_ind[0]].m * nx
				balls[smallest_ind[1]].v_y += p * balls[smallest_ind[0]].m * ny


				"""
				v1_xr = v1 * cos(angle1 - angle_phi)
				v1_yr = v1 * sin(angle1 - angle_phi)
				v2_xr = v2 * cos(angle2 - angle_phi)
				v2_yr = v2 * sin(angle2 - angle_phi)
				"""










				#delta_x = abs(balls[smallest_ind[0]].x - balls[smallest_ind[1]].x)
				#delta_y = abs(balls[smallest_ind[0]].y - balls[smallest_ind[1]].y)

				#cos_alpha = delta_y / d  # alpha -> angle near vertical axis
				#cos_beta = delta_x / d  # beta -> angle near horizontal axis

				#v_rel_1 = balls[smallest_ind[0]].v_x * cos_beta + balls[smallest_ind[0]].v_y * cos_alpha
				#v_rel_2 = balls[smallest_ind[1]].v_x * cos_beta + balls[smallest_ind[1]].v_y * cos_alpha

				#v_rel_1_new = ((m1_minus_m2 * v_rel_1) + (2 * balls[smallest_ind[1]].m * v_rel_2)) / m1_plus_m2
				#v_rel_2_new = (- (m1_minus_m2 * v_rel_2) + (2 * balls[smallest_ind[0]].m * v_rel_1)) / m1_plus_m2

				#balls[smallest_ind[0]].v_x += v_rel_1_new / cos_beta
				#balls[smallest_ind[0]].v_y += v_rel_1_new / cos_alpha

				#balls[smallest_ind[1]].v_x += v_rel_2_new / cos_beta
				#balls[smallest_ind[1]].v_y += v_rel_2_new / cos_alpha

				"""
				if delta_x == 0:
					v_rel_1 = r1_plus_r2 * (balls[smallest_ind[0]].v_y / delta_y)
					v_rel_2 = r1_plus_r2 * (balls[smallest_ind[1]].v_y / delta_y)
				elif delta_y == 0:
					v_rel_1 = r1_plus_r2 * (balls[smallest_ind[0]].v_x / delta_x)
					v_rel_2 = r1_plus_r2 * (balls[smallest_ind[1]].v_x / delta_x)
				else:
					v_rel_1 = r1_plus_r2 * ((balls[smallest_ind[0]].v_x / delta_x) + (balls[smallest_ind[0]].v_y / delta_y))
					v_rel_2 = r1_plus_r2 * ((balls[smallest_ind[1]].v_x / delta_x) + (balls[smallest_ind[1]].v_y / delta_y))
				"""

				# balls[smallest_ind[0]].v_x = ((m1_minus_m2 * balls[smallest_ind[0]].v_x) + (2 * balls[smallest_ind[1]].m * balls[smallest_ind[1]].v_x)) / m1_plus_m2
				# balls[smallest_ind[1]].v_x = (- (m1_minus_m2 * balls[smallest_ind[1]].v_x) + (2 * balls[smallest_ind[0]].m * balls[smallest_ind[0]].v_x)) / m1_plus_m2

				# balls[smallest_ind[0]].v_y = ((m1_minus_m2 * balls[smallest_ind[0]].v_y) + (2 * balls[smallest_ind[1]].m * balls[smallest_ind[1]].v_y)) / m1_plus_m2
				# balls[smallest_ind[1]].v_y = (- (m1_minus_m2 * balls[smallest_ind[1]].v_y) + (2 * balls[smallest_ind[0]].m * balls[smallest_ind[0]].v_y)) / m1_plus_m2

				print(f"Ball1:\nm: {balls[smallest_ind[0]].m}\nx: {balls[smallest_ind[0]].x}\ny: {balls[smallest_ind[0]].y}\nvx: {balls[smallest_ind[0]].v_x}\nvy: {balls[smallest_ind[0]].v_y}")
				print(f"Ball2:\nm: {balls[smallest_ind[1]].m}\nx: {balls[smallest_ind[1]].x}\ny: {balls[smallest_ind[1]].y}\nvx: {balls[smallest_ind[1]].v_x}\nvy: {balls[smallest_ind[1]].v_y}")

			else:
				raise IndexError
		except IndexError:
			balls = move_balls(balls, interval)

		# handle balls movement
		video.write(generate_frame(balls, width, height))
	video.release()
