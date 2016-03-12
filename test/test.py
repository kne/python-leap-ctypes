import os
import sys
import time
from os.path import dirname, join, abspath
sys.path.append(join(dirname(__file__), '..', 'src'))

# Set DLL path for leap libraries
os.environ['LEAP_DLL_PATH'] = abspath(join(dirname(__file__), '..', 'dll'))

# Import leap
from cleap import (leap, Event)

c = leap.leap_controller()
l = leap.leap_listener(500)
leap.leap_add_listener(c, l)
leap.leap_enable_background(c)

try:
    while True:
        waiting = False
        while not waiting:
            event = leap.leap_poll_listener(l)
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

    leap.leap_remove_listener(c, l)
    leap.leap_listener_dispose(l)
    leap.leap_controller_dispose(c)
