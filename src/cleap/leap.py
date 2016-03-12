import os
import sys

import ctypes

LEAP_ON_INIT = 0x0001
LEAP_ON_CONNECT = 0x0002
LEAP_ON_DISCONNECT = 0x0003
LEAP_ON_EXIT = 0x0004
LEAP_ON_FRAME = 0x0005
LEAP_ON_FOCUS_GAINED = 0x0006
LEAP_ON_FOCUS_LOST = 0x0007


class LEAP_VECTOR(ctypes.Structure):
    _fields_ = [
        ('points', ctypes.c_float * 3),
    ]


class LEAP_FINGER(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_int),
        ('position', LEAP_VECTOR),
        ('velocity', LEAP_VECTOR),
        ('direction', LEAP_VECTOR),
    ]


class LEAP_HAND(ctypes.Structure):
    _fields_ = [
        ('finger_count', ctypes.c_int),
        ('fingers', LEAP_FINGER * 5),
        ('palm_position', LEAP_VECTOR),
        ('palm_normal', LEAP_VECTOR),
        ('direction', LEAP_VECTOR),
        ('sphere_radius', ctypes.c_float),
    ]


class LEAP_BOUNDS(ctypes.Structure):
    _fields_ = [
        ('center', LEAP_VECTOR),
        ('size', LEAP_VECTOR),
    ]


class LEAP_FRAME(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_long),
        ('timestamp', ctypes.c_long),
        ('hand_count', ctypes.c_int),
        ('hands', LEAP_HAND * 2),
        ('bounds', LEAP_BOUNDS),
    ]


class LEAP_EVENT(ctypes.Structure):
    _fields_ = [
        ('event_code', ctypes.c_int),
        ('frame', LEAP_FRAME)
    ]


class Vector(object):
    def __init__(self, vector):
        self.points = tuple(vector.points)

    def __repr__(self):
        return ('{0}({1:.2f}, {2:.2f}, {3:.2f})'
                ''.format(self.__class__.__name__, *self.points))


class Finger(object):

    def __init__(self, finger):
        self.id_ = finger.id
        self.position = Vector(finger.position)
        self.velocity = Vector(finger.velocity)
        self.direction = Vector(finger.direction)

    def __repr__(self):
        return ('{0}({1}, position={2}, velocity={3}, direction={4})'
                ''.format(self.__class__.__name__, self.id_, self.position,
                          self.velocity, self.direction)
                )


class Hand(object):
    def __init__(self, hand):
        self.sphere_radius = hand.sphere_radius
        self.palm_position = Vector(hand.palm_position)
        self.palm_normal = Vector(hand.palm_normal)
        self.direction = Vector(hand.direction)
        self.fingers = []
        for i in range(hand.finger_count):
            self.fingers.append(Finger(hand.fingers[i]))

    def __repr__(self):
        return ('{0}(sphere_radius={1}, palm_position={2}, '
                'palm_normal={3}, direction={4}, fingers={5})'
                ''.format(self.__class__.__name__, self.sphere_radius,
                          self.palm_position, self.palm_normal, self.direction,
                          self.fingers))


class Bounds(object):
    def __init__(self, bounds):
        self.center = Vector(bounds.center)
        self.size = Vector(bounds.size)

    def __repr__(self):
        return ('{0}(size={1}, center={2})'
                ''.format(self.__class__.__name__, self.size, self.center)
                )


class Frame(object):
    def __init__(self, frame):
        self.id_ = frame.id
        self.timestamp = frame.timestamp
        self.bounds = Bounds(frame.bounds)
        self.hands = [Hand(hand) for hand in frame.hands[:frame.hand_count]]

    def __repr__(self):
        return ('{0}(id_={1}, timestamp={2}, bounds={3}, hands={4})'
                ''.format(self.__class__.__name__, self.id_, self.timestamp,
                          self.bounds, self.hands))


class Event(object):
    def __init__(self, event):
        event = event.contents
        self.code = event.event_code
        self.frame = Frame(event.frame)

    def __repr__(self):
        return ('{0.__class__.__name__}(code={0.code}, '
                'frame={0.frame})'
                ''.format(self)
                )


def initialize_cleap(library_path=None, library_filename=None):
    if library_path is None:
        library_path = os.environ.get('LEAP_DLL_PATH', None)

    if not library_path:
        raise ImportError('Unable to locate leap DLLs')

    if library_filename is None:
        # Determine file based on system
        if sys.platform.startswith('win'):
            library_filename = 'libcleap.dll'
        elif sys.platform in ('darwin', ):
            library_filename = 'libcleap.dylib'
        else:
            library_filename = 'libcleap.so'

    # Load DLL
    LEAP = ctypes.CDLL(os.path.join(library_path, library_filename))
    if LEAP is None:
        raise ImportError('Unable to load leap DLLs')

    # Create a controller
    LEAP.leap_controller.restype = ctypes.c_void_p

    # Enable tracking when focus is lost on a controller
    LEAP.leap_enable_background.argtypes = [ctypes.c_void_p]

    # Dispose of a controller
    LEAP.leap_controller_dispose.argtypes = [ctypes.c_void_p]

    # Create a listener with a sized internal buffer.
    # At most the most recent size elements will be queued.
    LEAP.leap_listener.argtypes = [ctypes.c_int]
    LEAP.leap_listener.restype = ctypes.c_void_p

    # Dispose of a listener
    LEAP.leap_listener_dispose.argtypes = [ctypes.c_void_p]

    # Bind a listener to a controller
    LEAP.leap_add_listener.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    # Remove a listener from a controller
    LEAP.leap_remove_listener.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    # Fetch the next queued event
    LEAP.leap_poll_listener.argtypes = [ctypes.c_void_p]
    LEAP.leap_poll_listener.restype = ctypes.POINTER(LEAP_EVENT)
    return LEAP
