import hid

from shared import bcolors
from connect import read_device

CYCLES = 1000

VENDOR_ID = 0x2E3C
PRODUCT_ID = 0xC365

WAKE = [0x1b, 0x00, 0xe0, 0x65, 0x80, 0x25, 0x8f, 0xa0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x01, 0x00, 0x10, 0x00, 0x04, 0x01, 0x00, 0x00, 0x00, 0x00]

print(f'Finding path for {hex(VENDOR_ID)} {hex(PRODUCT_ID)}')

for d in hid.enumerate():

  if d['vendor_id'] == VENDOR_ID and d['product_id'] == PRODUCT_ID:
    
    print(f"\n{bcolors.BOLD}Attempting to connect to {bcolors.ENDC}{bcolors.UNDERLINE}{d['path']}{bcolors.ENDC}")
    
    try:
      
      dead_reports = 0

      for report in read_device(d['path'], WAKE):
        
        if report:
          print(f"{bcolors.OKGREEN}Raw Data Recieved: {list(report)}{bcolors.ENDC}")
          exit(0)
            
        else:
          dead_reports += 1

        if dead_reports >= CYCLES:
          print(f"{bcolors.FAIL}No data recieved for {CYCLES} cycles, skipping{bcolors.ENDC}")
          break

    except Exception as e:
      print(f"{bcolors.FAIL}{e}{bcolors.ENDC}")
