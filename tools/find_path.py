import hid

from shared.colors import bcolors
from shared.connect import read_device

from values import PRODUCT_ID, VENDOR_ID, WAKE

CYCLES = 1000

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
