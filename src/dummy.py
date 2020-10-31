"""
Fake classes to avoid RPi dependencies
"""
class Adafruit_DHT:
 DHT11 = 11
 def read_retry(sensor, pin):
   return(50, 20)

class Energenie:
  value = False
  def __init__(self, channel):
    pass
  def on(self):
    self.value = True
    return True
  def off(self):
    self.value = False
    return False

class serial:
  class Serial:
    def __init__(self, port, timeout):
      pass
    def write(self, value):
      pass
    def read(self, length):
      return []