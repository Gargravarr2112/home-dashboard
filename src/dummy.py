"""
Fake classes to avoid RPi dependencies
"""
class Adafruit_DHT:
 DHT11 = 11
 def read_retry(sensor, pin):
   return(0, 0)

class Energenie:
  value = False
  def __init__(self, channel):
    pass
  def on(self):
    return True
  def off(self):
    return False
