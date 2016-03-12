import os
import time

import cleap

script_path = os.path.dirname(__file__)
# by default, this is looking for the leap library in ../dll
library_path = os.path.abspath(os.path.join(script_path, '..', 'dll'))

leap = cleap.initialize_cleap(library_path=library_path)
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
                e = cleap.Event(event)
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
