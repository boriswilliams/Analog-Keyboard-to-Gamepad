import vgamepad as vg
import time

from shared.connect import read_device

from values import PATH, WAKE

WASD = False
DEADZONE = 0.01
CURVE_COEFFICIENT = 1.5

MAX_IN = 339
MAX_JS = 32767

SCALE_FACTOR = MAX_JS / MAX_IN


def curve(value):
  return ((value/MAX_IN)**CURVE_COEFFICIENT)*MAX_IN


def remove_deadzone(value):
  sign = value/abs(value) if value > 0 else 0
  return value*(1-DEADZONE)+sign*MAX_IN*DEADZONE

def scale(value):
  return int(value * SCALE_FACTOR)

def clamp(value):
  return max(-MAX_JS-1, min(MAX_JS, value))

def process(value):
  mapped = remove_deadzone(value)
  scaled = scale(mapped)
  clamped = clamp(scaled)
  return clamped


def combine(neg, pos):
  neg_curve = curve(neg)
  pos_curve = curve(pos)
  curved = pos_curve - neg_curve
  return process(curved)


gamepad = vg.VX360Gamepad()

front = left = back = right = 0
x_value = 0
y_value = 0

current_second = int(time.time())
frame_count = 0

display_fps = 0

for report in read_device(PATH, WAKE, 0):
  
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

    x_value = combine(left, right)
    y_value = combine(back, front) if WASD else 0

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
