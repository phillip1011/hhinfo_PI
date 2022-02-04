import sys
import datetime

time_tuple = ( 2012, # Year
                  9, # Month
                  6, # Day
                  0, # Hour
                 38, # Minute
                  0, # Second
                  0, # Millisecond
              )

def _win_set_time(time_tuple):
    import pywin32
    # http://timgolden.me.uk/pywin32-docs/win32api__SetSystemTime_meth.html
    # pywin32.SetSystemTime(year, month , dayOfWeek , day , hour , minute , second , millseconds )
    dayOfWeek = datetime.datetime(time_tuple).isocalendar()[2]
    pywin32.SetSystemTime( time_tuple[:2] + (dayOfWeek,) + time_tuple[2:])


def _linux_set_time(time_tuple):
    import ctypes
    import ctypes.util
    import time
    
    #print(time_tuple)
    # /usr/include/linux/time.h:
    #
    # define CLOCK_REALTIME                     0
    CLOCK_REALTIME = 0

    # /usr/include/time.h
    #
    # struct timespec
    #  {
    #    __time_t tv_sec;            /* Seconds.  */
    #    long int tv_nsec;           /* Nanoseconds.  */
    #  };
    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]

    librt = ctypes.CDLL(ctypes.util.find_library("rt"))
    print("OK-01")

    ts = timespec()
    ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
    ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond
    # http://linux.die.net/man/3/clock_settime
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))


def update():
    print(sys.platform)
    if sys.platform=='linux':
        _linux_set_time(time_tuple)

    elif  sys.platform=='win32':
        _win_set_time(time_tuple)


def update2(data):
    import os
    _date =  data["Year"] + "-" + data["Month"] +"-" + data["Day"]
    _time =  data["Hour"] + ":" + data["Minute"] + ":" + data["Second"] 
    
    os.system('sudo date -s "{} {}"'.format(_date,_time))
