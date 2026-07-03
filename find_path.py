import hid
import time
import vgamepad as vg

VENDOR_ID = 0x2E3C
PRODUCT_ID = 0xC365

CYCLES = 1000

for d in hid.enumerate():
    if d['vendor_id'] == VENDOR_ID and d['product_id'] == PRODUCT_ID:
        
        print(f"Attempting to connect to {d['path']}")
        
        try:
            device = hid.device()
            device.open_path(d['path'])
            device.set_nonblocking(1)
            wake_up_packet = [0x1b, 0x00, 0x10, 0x40, 0x2c, 0xec, 0x85, 0xc9, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x01, 0x00, 0x0c, 0x00, 0x04, 0x01, 0x40, 0x00, 0x00, 0x00, 0x01, 0x0d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
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
                    exit(0)
                    
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
