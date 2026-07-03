import hid
import time
import vgamepad as vg

VENDOR_ID = 0x2E3C
PRODUCT_ID = 0xC365

CYCLES = 10000

for d in hid.enumerate():
    if d['vendor_id'] == VENDOR_ID and d['product_id'] == PRODUCT_ID:
        
        print(f"Attempting to connect to {d['path']}")
        
        try:
            device = hid.device()
            device.open_path(d['path'])
            device.set_nonblocking(1)
            wake_up_packet = [0x00] + [0x01, 0x02, 0x00, 0x00] + [0x00]*60 
            try:
                device.send_feature_report(wake_up_packet)
                print("Wake-up packet transmitted to interface.")
            except Exception as e:
                print(f"Feature report notice: {e}. Trying standard write instead...")
                device.write([0x00, 0x01, 0x02] + [0x00]*61)

            gamepad = vg.VX360Gamepad()
            
            dead_reports = 0

            while True:
                report = device.read(64)
                
                if report and len(report) > 0:
                    print(f"Raw Data Recieved: {list(report)}")
                    
                    if len(report) >= 5:
                        raw_left = report[3]  
                        raw_right = report[4] 
                        
                        left_joystick_x = 0
                        if raw_left > 10: 
                            left_joystick_x -= int((raw_left / 255.0) * 32767)
                        if raw_right > 10:
                            left_joystick_x += int((raw_right / 255.0) * 32767)
                        
                        gamepad.left_joystick(x_value=left_joystick_x, y_value=0)
                        gamepad.update()
                
                else:
                    dead_reports += 1
                    
                time.sleep(0.001)

                if dead_reports >= CYCLES:
                    print(f"No data recieved for {CYCLES} cycles, skipping")
                    break
        except Exception as e:
            print(e)
        finally:
            device.close()
