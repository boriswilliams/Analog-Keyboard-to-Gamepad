import vgamepad as vg
import time

from shared.connect import read_device

from values import PATH, WAKE

MAX_JS = 32767
MAX_IN = 339

WASD = False

SCALE_FACTOR = MAX_JS / MAX_IN

def scale(value):
  scaled = int(value * SCALE_FACTOR)
  clamped = max(-MAX_JS-1, min(MAX_JS, scaled))
  return clamped

gamepad = vg.VX360Gamepad()

front = left = back = right = 0
x_value = 0
y_value = 0

current_second = int(time.time())
frame_count = 0

display_fps = 0

for report in read_device(PATH, WAKE, 8000):
  
  if report:

    magnitude = report[10] * 255 + report[9]

    match tuple(report[7:9]):
      case (2, 2):
        front = magnitude
      case (3, 2):
        left = magnitude
      case (3, 3):
        back = magnitude
      case (3, 4):
        right = magnitude

    x_value = scale(right - left)
    y_value = scale(front - back) if WASD else 0

    gamepad.left_joystick(x_value=x_value, y_value=y_value)
    gamepad.update()
  
  # Display
  now_second = int(time.time())
  if now_second > current_second:
    display_fps = frame_count
    
    frame_count = 0
    current_second = now_second

  print(f'\rFPS: {display_fps}\n{' '.join([f"{x:3}" for x in report[5:15]])}\n    {front:3}      {y_value:6}\n{left:3} {back:3} {right:3}  {x_value:6}', end='\x1B[3A')
  
  frame_count += 1
