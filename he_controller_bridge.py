import math
import time

import vgamepad as vg

from shared.colors import bcolors
from shared.connect import read_device

from values import PATH, WAKE

WASD = False
DEADZONE = 0.01
CURVE_COEFFICIENT = 1.4
FPS_REPORTING = 240
FPS_SMOOTHING = 0.01
SHOW_PRINT = True

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


def main():
  gamepad = vg.VX360Gamepad()

  front = left = back = right = 0
  x_value = 0
  y_value = 0

  current_second = int(time.time()*FPS_REPORTING)
  frame_count = 0

  display_fps = None

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
    
    if SHOW_PRINT:
      
      now_second = int(time.time()*FPS_REPORTING)
      if now_second > current_second:
        fps = frame_count*FPS_REPORTING
        display_fps = math.floor(FPS_SMOOTHING * fps + (1.0 - FPS_SMOOTHING) * (display_fps if display_fps else fps))
        frame_count = 0
        current_second = now_second

      lines = [
        f'\r{bcolors.HEADER}{display_fps if display_fps else 0:16}Hz{bcolors.ENDC}',
        f'\r                  ',
        f'\r    {bcolors.OKCYAN}{front:3}{bcolors.ENDC}     {bcolors.FAIL}{y_value:6}{bcolors.ENDC}',
        f'\r{bcolors.OKCYAN}{left:3} {back:3} {right:3}{bcolors.ENDC} {bcolors.FAIL}{x_value:6}{bcolors.ENDC}'
      ]
      raw_count = 64//len(lines)
      if report:
        for i in range(len(lines)):
          lines[i] = f'{lines[i]}  {' '.join([f"{report[j]:3}" for j in range(raw_count*i, raw_count*(i+1))])}'
      print('\n'.join(lines), end=f'\x1B[{len(lines)-1}A')
      
      frame_count += 1


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print('')
