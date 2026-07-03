import sys
import vgamepad as vg
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from shared.connect import read_device

NUMBER_OF_BARS = 64

PATH = b'\\\\?\\HID#VID_2E3C&PID_C365&MI_02#a&778027b&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'
WAKE = [0x1b, 0x00, 0x60, 0x56, 0x17, 0x0b, 0x8f, 0xa0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x01, 0x00, 0x10, 0x00, 0x04, 0x01, 0x40, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

class LiveGraphWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Live Keyboard Output (PyQtGraph)")
    self.resize(1000, 500)
    
    # Setup Layout
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Setup Plot Window
    self.plot_widget = pg.PlotWidget()
    layout.addWidget(self.plot_widget)
    self.plot_widget.setYRange(0, 260, padding=0)
    self.plot_widget.setXRange(-1, NUMBER_OF_BARS, padding=0)
    
    # Create Bar Items
    self.x_indices = list(range(NUMBER_OF_BARS))
    self.heights = [0] * NUMBER_OF_BARS
    self.bar_chart = pg.BarGraphItem(x=self.x_indices, height=self.heights, width=0.8, brush='c')
    self.plot_widget.addItem(self.bar_chart)
    
    # Initialize Gamepad and Device
    self.gamepad = vg.VX360Gamepad()
    self.device_stream = read_device(PATH, WAKE, 0)
    
    # Set up a high-speed background loop via Qt Timer (runs at 0ms delay)
    self.timer = QtCore.QTimer()
    self.timer.timeout.connect(self.update_data)
    self.timer.start(0) 

  def update_data(self):
    try:
      # Grab the next available device packet
      report = next(self.device_stream)
      if report:
        # Update visual bar heights instantly
        # Using a subset slice ensures it safely stays within 64 bars
        self.heights = list(report[:NUMBER_OF_BARS])
        self.bar_chart.setOpts(height=self.heights)
        
        # TODO: Add your live gamepad updates here
        # self.gamepad.update()
          
    except StopIteration:
      self.timer.stop()
    except Exception as e:
      print(f"Error: {e}")

if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = LiveGraphWindow()
  window.show()
  sys.exit(app.exec())
