import time
import hid

def connect_device(path, wake):
  device = hid.device()
  device.open_path(path)
  device.set_nonblocking(1)
  device.send_feature_report(wake)

  return device

def read(device, freq):
  try:
    if freq == 0:
      while True:
        yield device.read(64)
    else:
      period = 1/freq
      while True:
        yield device.read(64)
        time.sleep(period)
  finally:
    device.close()

def read_device(path, wake, freq=1000):
  for report in read(connect_device(path, wake), freq):
    yield report
