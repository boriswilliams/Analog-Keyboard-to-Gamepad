import hid
import vgamepad

from values import PATH

DEADZONE = 0.01
CURVE_COEFFICIENT = 1.4

MAX_IN = 339
MAX_JS = 32767
SIZE = 64

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
  
  device = hid.device()
  device.open_path(PATH)
  device.set_nonblocking(1)

  gamepad = vgamepad.VX360Gamepad()

  left = right = 0
  x_value = 0

  try:

    while True:
      
      if (report := device.read(SIZE)):

        magnitude = report[10] * 255 + report[9]

        match (report[7], report[8]):
          case (3, 2):
            left = magnitude
          case (3, 4):
            right = magnitude

        x_value = combine(left, right)

        gamepad.left_joystick(x_value=x_value, y_value=0)
        gamepad.update()

  finally:

    device.close()


if __name__ == '__main__':
  main()
