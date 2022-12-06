import argparse
import os
import random
from math import pi, sqrt

import cv2
import numpy as np


class Ball:
	def __init__(self, r, m, x, y, v_x, v_y, color):
		self.r = r
		self.m = m
		self.x = x
		self.y = y
		self.v_x = v_x
		self.v_y = v_y
		self.color = color

def rgb_2_bgr(color):
	return color[::-1]

def hex_2_rgb(hex_color):
	return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

def generate_frame(balls, width, height, background_color):
	frame = np.zeros((height, width, 3), dtype="uint8")
	frame[:, :] = background_color
	for ball in balls:
		cv2.circle(frame, (int(round(ball.x, 0)), int(round(ball.y, 0))), ball.r, ball.color, -1, cv2.LINE_AA)
	return frame

def move_balls(balls, interval):
	for ball in balls:
		ball.x += ball.v_x * interval
		ball.y += ball.v_y * interval
	return balls

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

def calculate_wall_collision(balls, ball, wall, width, height):
	# end position minus start position divided by speed
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

def simulation(file_destination, width, height, fps, video_length, balls, background_color):
	interval = 1 / fps

	video = cv2.VideoWriter(file_destination, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
	num_of_frames = video_length * fps

	progress = 0
	print(f"{progress} %")
	for frame_num in range(num_of_frames):
		temp_progress = int((frame_num / num_of_frames) * 100)
		if temp_progress > progress:
			progress = temp_progress
			print(f"{progress} %")

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
				ball_times.append(calculate_wall_collision(balls, ball, wall, width, height))
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
					p = (2 * (nx * (balls[smallest_ind[0]].v_x - balls[smallest_ind[1]].v_x) + ny * (
							balls[smallest_ind[0]].v_y - balls[smallest_ind[1]].v_y))) / (
							    balls[smallest_ind[0]].m + balls[smallest_ind[1]].m)
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
								wall_times[x][y] = calculate_wall_collision(balls, x, y, width, height)
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
									wall_times[x][y] = calculate_wall_collision(balls, x, y, width, height)
							elif wall_times[x][y] is not None:
								wall_times[x][y] -= smallest_time

					moved_time += smallest_time

		video.write(generate_frame(balls, width, height, background_color))
	video.release()
	print("100 %")

def start_sim(file_destination, video_length, fps, width, height, num_of_balls, background_color, ball_color, ball_radius_min, ball_radius_max, ball_mass, ball_speed_min, ball_speed_max):
	if not os.path.isdir(os.path.dirname(os.path.abspath(file_destination))):
		print("Invalid destination!")
		return
	elif os.path.splitext(file_destination)[-1] != ".mp4":
		print("Invalid extension! (should be *.mp4)")
		return
	elif os.path.isfile(file_destination):
		print("Destination file already exists!\nOverwrite? (Y/N)")
		if input() not in ("Y", "y"):
			return
	if not os.access(file_destination, os.W_OK):
		print("Can't write to target folder!")
		return

	if not type(video_length) == int or not video_length >= 1:
		print("Invalid video length! (should be integer greater than 0)")
		return

	if not type(fps) == int or not fps >= 1:
		print("Invalid FPS! (should be integer greater than 0)")
		return

	if not type(width) == int or not width >= 30:
		print("Invalid width! (should be integer equal to or greater than 30)")
		return

	if not type(height) == int or not width >= 30:
		print("Invalid height! (should be integer equal to or greater than 30)")
		return

	if not type(num_of_balls) == int or not num_of_balls >= 1:
		print("Invalid number of circles! (should be integer greater than 0)")
		return

	if not type(background_color) == str:
		print("Invalid background color! (should be hex value starting with #)")
		return
	try:
		hex_2_rgb(background_color)
	except ValueError:
		print("Invalid background color! (should be hex value starting with #)")
		return

	if ball_color != "":
		try:
			hex_2_rgb(ball_color)
		except ValueError:
			print("Invalid ball color! (should be hex value starting with # or empty string)")
			return

	if not type(ball_radius_min) == int or not type(ball_radius_max) == int or ball_radius_min < 5 or ball_radius_min > ball_radius_max:
		print("Invalid ball radius! (should be integer, minimal value 5)")
		return

	if not type(ball_mass) == float or not (ball_mass >= 0.0 or ball_mass == - 1.0):
		print("Invalid ball mass! (should be positive float, unless using 0.0 or -1.0)")
		return

	if not type(ball_speed_min) == int or not type(ball_speed_max) == int or ball_speed_min < 5 or ball_speed_min > ball_speed_max:
		print("Invalid ball speed! (should be integer, minimal value 5)")
		return

	# generate balls
	balls = []
	for _ in range(num_of_balls):
		# radius
		radius = random.randint(ball_radius_min, ball_radius_max)

		# x, y
		tries = 0
		while True:
			tries += 1
			if tries == 10_000:
				print("Can't fit all the balls in given area!")
				return
			x, y = random.randint(radius, width - radius - 1), random.randint(radius, height - radius - 1)
			valid = True
			for ball in balls:
				if abs(x - ball.x) <= (radius + ball.r) and abs(y - ball.y) <= (radius + ball.r):
					valid = False
					break
			if valid:
				break

		# mass
		if ball_mass == -1.0:
			mass = ((radius ** 3) * pi * 4) / 3
		elif ball_mass == 0.0:
			mass = (radius ** 2) * pi
		else:
			mass = ball_mass

		# vx, vy
		vx, vy = random.choice((-1, 1)) * random.randint(ball_speed_min, ball_speed_max), random.choice((-1, 1)) * random.randint(ball_speed_min, ball_speed_max)

		# color (bgr)
		if ball_color == "":
			color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
			while color == rgb_2_bgr(hex_2_rgb(background_color)):
				color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
		else:
			color = rgb_2_bgr(hex_2_rgb(ball_color))

		# add ball with selected properties
		balls.append(Ball(radius,
		                  mass,
		                  x, y,
		                  vx, vy,
		                  color))

	del x, y, radius, mass, vx, vy, color, valid

	# run_simulation
	simulation(file_destination, width, height, fps, video_length, balls, rgb_2_bgr(hex_2_rgb(background_color)))

def main():
	# file_destination: str = "video.mp4"   # Location of generated file (with .mp4 extension)
	# video_length: int = 60                # Length of video in seconds (integer)
	# fps: int = 60                         # Frames per second (FPS) of video (integer)
	# width: int = 1920                     # Width of video in pixels (integer)
	# height: int = 1080                    # Height of video in pixels (integer)
	# num_of_balls: int = 25                # Number of balls in video (integer)
	# background_color: str = "#000000"     # Color of background in video, hex value (str)
	# ball_color: str = ""                  # Color of balls, hex value (str) -> if empty color is random
	# ball_radius_min: int = 75             # Minimal size of balls, randomly chosen
	# ball_radius_max: int = 125            # Maximal size of balls, randomly chosen
	# ball_mass: float = 0.0                # Mass of balls, if set all balls have the same mass, otherwise each ball gets its own mass -> 0.0 means mass will be calculated from circles, -1.0 means mass will be calculated from spheres
	# ball_speed_min: int = 100             # Initial minimal speed of balls in x or y directions, randomly chosen
	# ball_speed_max: int = 150             # Initial maximal speed of balls in x or y directions, randomly chosen

	parser = argparse.ArgumentParser()
	parser.add_argument("destination_file", help="File name and path where video will be saved", type=str)
	parser.add_argument("--video_length", help="Length of video (in seconds)", type=int, default=60)
	parser.add_argument("--fps", help="Frames per second (FPS) of video", type=int, default=60)
	parser.add_argument("--width", help="Width of video", type=int, default=1920)
	parser.add_argument("--height", help="Height of video", type=int, default=1080)
	parser.add_argument("--num_of_balls", help="Number of balls", type=int, default=25)
	parser.add_argument("--background_color", help="Background color (hex)", type=str, default="#000000")
	parser.add_argument("--ball_color", help="Color of balls, random if empty", type=str, default="")
	parser.add_argument("--radius_min", help="Minimal ball radius", type=int, default=50)
	parser.add_argument("--radius_max", help="Maximal ball radius", type=int, default=100)
	parser.add_argument("--ball_mass", help="Mass of all balls, or the way of calculating it (0.0 calculates as circles, -1.0 calculates as spheres)", type=float, default=0.0)
	parser.add_argument("--speed_min", help="Minimal ball speed", type=int, default=80)
	parser.add_argument("--speed_max", help="Maximal ball speed", type=int, default=130)
	args = parser.parse_args()

	start_sim(args.destination_file,
	          args.video_length,
	          args.fps,
	          args.width,
	          args.height,
	          args.num_of_balls,
	          args.background_color,
	          args.ball_color,
	          args.radius_min,
	          args.radius_max,
	          args.ball_mass,
	          args.speed_min,
	          args.speed_max)


if __name__ == '__main__':
	main()
