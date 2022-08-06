import cv2
import numpy as np
import random
import time

video = cv2.VideoWriter("test.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 1, (1920, 1080))
for i in range(5):
	start = time.time()
	arr = np.zeros((1080, 1920, 3), dtype="uint8")
	print(time.time() - start)
	start2 = time.time()
	for x in range(1080):
		for y in range(1920):
			for z in range(3):
				arr[x][y][z] = random.randint(0, 255)
	print(start2 - time.time())
	start3 = time.time()
	video.write(arr)
	print(time.time() - start3)
video.release()
