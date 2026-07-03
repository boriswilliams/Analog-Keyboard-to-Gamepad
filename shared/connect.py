import time
import hid

from shared.colors import bcolors

def connect_device(path, wake):
  device = hid.device()
  device.open_path(path)
  device.set_nonblocking(1)
  device.send_feature_report(wake)

  print(f"{bcolors.OKCYAN}Wake-up packet transmitted to interface.{bcolors.ENDC}")

  return device

def read(device, freq):
  try:
    while True:
      yield device.read(64)
      time.sleep(1/freq)
  finally:
    device.close()

def read_device(path, wake, freq=1000):
  for report in read(connect_device(path, wake), freq):
    yield report
