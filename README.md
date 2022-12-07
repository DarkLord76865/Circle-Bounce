# Circle-Bounce
CLI app to generate a video of bouncing circles 
(with continuous collision detection)

![screenshot](https://user-images.githubusercontent.com/40371578/205990530-b4723a3e-3419-4fc6-b257-a8b336c3bd91.png)
Example: https://www.youtube.com/watch?v=ui5OTEb7xIs

## Usage
1. from command line run `*.exe` file with one argument (destination file)
2. add other optional arguments
3. for list of other arguments run `*.exe --help`
```
>circle-bounce-v1.0.0.exe --help

usage: circle-bounce-v1.0.0.exe [-h] [--video_length VIDEO_LENGTH] [--fps FPS] [--width WIDTH] [--height HEIGHT]
                                [--num_of_balls NUM_OF_BALLS] [--background_color BACKGROUND_COLOR]
                                [--ball_color BALL_COLOR] [--radius_min RADIUS_MIN] [--radius_max RADIUS_MAX]
                                [--ball_mass BALL_MASS] [--speed_min SPEED_MIN] [--speed_max SPEED_MAX]
                                destination_file

positional arguments:
  destination_file      File name and path where video will be saved

options:
  -h, --help            show this help message and exit
  --video_length VIDEO_LENGTH
                        Length of video (in seconds)
  --fps FPS             Frames per second (FPS) of video
  --width WIDTH         Width of video
  --height HEIGHT       Height of video
  --num_of_balls NUM_OF_BALLS
                        Number of balls
  --background_color BACKGROUND_COLOR
                        Background color (hex)
  --ball_color BALL_COLOR
                        Color of balls, random if empty
  --radius_min RADIUS_MIN
                        Minimal ball radius
  --radius_max RADIUS_MAX
                        Maximal ball radius
  --ball_mass BALL_MASS
                        Mass of all balls, or the way of calculating it (0.0 calculates as circles, -1.0 calculates as
                        spheres)
  --speed_min SPEED_MIN
                        Minimal ball speed
  --speed_max SPEED_MAX
                        Maximal ball speed
```

## Downloading
Prebuilt program is available under Releases

## Building
1. Clone repository
2. Run command: `pip install -r requirements.txt`
3. Run build.py
4. Built `*.exe` will be placed in the same folder