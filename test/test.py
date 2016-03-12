import os
import sys
import time
from os.path import dirname, join, abspath
sys.path.append(join(dirname(__file__), '..', 'src'))

# Set DLL path for leap libraries
os.environ['LEAP_DLL_PATH'] = abspath(join(dirname(__file__), '..', 'dll'))

# Import leap
from cleap.leap import *

c = leap_controller()
l = leap_listener(500)
leap_add_listener(c, l)
leap_enable_background(c)

try:
    while True:
      waiting = False
      while not waiting:
        event = leap_poll_listener(l)
        if event:
          e = Event(event)
          if not e.frame.hands:
              continue

          print('----')
          for hand in e.frame.hands:
              print(hand)
        else:
          waiting = True
      time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    print()
    print('Done')

    leap_remove_listener(c, l)
    leap_listener_dispose(l)
    leap_controller_dispose(c)
