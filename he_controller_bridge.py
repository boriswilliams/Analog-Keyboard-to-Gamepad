import hid
import time
import vgamepad as vg

PATH = b'\\\\?\\HID#VID_2E3C&PID_C365&MI_02#a&778027b&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
WAKE = [0x1b, 0x00, 0x10, 0x40, 0x2c, 0xec, 0x85, 0xc9, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x01, 0x00, 0x0c, 0x00, 0x04, 0x01, 0x40, 0x00, 0x00, 0x00, 0x01, 0x0d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

previous = ()

try:
    device = hid.device()
    device.open_path(PATH)
    device.set_nonblocking(1)
    try:
        device.send_feature_report(WAKE)
        print("Wake-up packet transmitted to interface.")
    except Exception as e:
        print(f"Feature report notice: {e}. Trying standard write instead...")
        device.write([0x00, 0x01, 0x02] + [0x00]*61)

    gamepad = vg.VX360Gamepad()

    while True:
        report = device.read(64)
        
        if report:
            
            if tuple(report) != previous:
                for i in range(min(len(report), len(previous))):
                    print(f'{i:02}: ', end='')
                    if report[i] != previous[i]:
                        print(bcolors.WARNING, end='')
                        print(f'{previous[i]:03}', end='')
                        print(bcolors.OKGREEN, end='')
                    else:
                        print('   ', end='')
                    print(f'{report[i]:03}', end='')
                    if report[i] != previous[i]:
                        print(bcolors.ENDC, end='')
                    print(', ', end='')
                previous = tuple(report)
                print()

            raw_left = report[3]
            raw_right = report[4]
            
            left_joystick_x = 0
            if raw_left > 10: 
                left_joystick_x -= int((raw_left / 255.0) * 32767)
            if raw_right > 10:
                left_joystick_x += int((raw_right / 255.0) * 32767)
            
            gamepad.left_joystick(x_value=left_joystick_x, y_value=0)
            gamepad.update()
            
        time.sleep(0.001)

except Exception as e:
    print(e)
finally:
    device.close()
