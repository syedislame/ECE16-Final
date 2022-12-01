from ECE16Lib.Communication import Communication
from ECE16Lib.CircularList import CircularList
from matplotlib import pyplot as plt
from time import time
import numpy as np
import math

class IdleDetector():
    # set up timing variables
    __before_time = 0
    current_time = 0
    __idle_time = 0

    # set up state variables
    __detecting = False
    __idle = False
    __idle_long = False

    # set up plotting variables
    __num_samples = 250   # 10 seconds of data at 50 Hz
    __refresh_time = 1  # plot at 10 fps

    # raw data circular lists
    __times = CircularList([], __num_samples)
    __ax = CircularList([], __num_samples)
    __ay = CircularList([], __num_samples)
    __az = CircularList([], __num_samples)

    # additional circular lists
    __average_x = CircularList([], __num_samples)
    __delta_x = CircularList([], __num_samples)
    __L1 = CircularList([], __num_samples)
    __L2 = CircularList([], __num_samples)

    # set up communication
    __comms = Communication("COM6", 115200)

    def __init__(self):
        self.__before_time = 0
        self.current_time = time()
        self.__idle_time = time()

    # main method that runs the idle detector
    def run_detector(self):
        try:
            self.__before_time = 0
            while(True):
                message = self.__comms.receive_message()    # get the message from the serial buffer
                if (message != None):   # if the message is not an empty string
                    if ("toggled" in message):  # if the message contains the word "toggled"
                        self.__detecting = not self.__detecting # toggle detecting on or off
                        #print(message) # for testing
                    else:
                        try:
                            (m1, m2, m3, m4) = message.split(',')
                        except ValueError:
                            continue
                        self.append_values(m1, m2, m3, m4)
                        self.compute_transformations()
                        #print(self.current_time - self.__idle_time)
                        self.__detect_activity()
                        self.__plot_data()
                    self.determine_status()
                    self.__send_status()
        except(Exception, KeyboardInterrupt) as e:
            print(e)                     # Exiting the program due to exception
        finally:
            self.__comms.send_message("sleep")  # stop sending data
            self.__comms.close()        

    # add raw data to ends of circular lists
    def append_values(self, m1, m2, m3, m4):
        self.__times.add(int(m1))
        self.__ax.add(int(m2))
        self.__ay.add(int(m3))
        self.__az.add(int(m4))

    # compute and add processed data to circular lists
    def compute_transformations(self):
        # compute average of last N seconds of ax raw data and add to average_x
        average = np.mean(self.__ax)
        self.__average_x.add(average)
        # compute sample difference of x-axis
        difference = self.__ax[-1] - self.__ax[-2]
        self.__delta_x.add(difference)
        # compute L1-Norm
        l1_norm = abs(self.__ax[-1]) + abs(self.__ay[-1]) + abs(self.__az[-1])
        self.__L1.add(l1_norm)
        # compute L2-Norm
        l2_norm = math.sqrt(self.__ax[-1]**2 + self.__ay[-1]**2 + self.__az[-1]**2)
        self.__L2.add(l2_norm)

    # if the L2 norm exceeds 3700, update idle time
    def __detect_activity(self, steps, jumps):
        if (steps + jumps) > 0:
        #if self.__L2[-1] >= 3700:
          print("Activity Detected")
          self.__idle_time = time()

    # if enough time has elapsed, clear the axis, and plot L1 and L2
    def plot_data(self):
        self.current_time = time()
        if (self.current_time - self.__before_time > self.__refresh_time):
          self.__before_time = self.current_time
          # clear all subplots
          plt.subplot(211)
          plt.cla()
          plt.subplot(212)
          plt.cla()
          # plot L1 and L2
          plt.subplot(211)
          plt.ylabel("L1")
          plt.plot(self.__times, self.__L1)
          plt.subplot(212)
          plt.xlabel("time")
          plt.ylabel("L2")
          plt.plot(self.__times, self.__L2)
          plt.show(block=False)
          plt.pause(0.05)

    # resets the necessary bools to false
    def __reset_bools(self):
        self.__idle = False
        self.__idle_long = False

    # determines and sets the current status and resets as necessary
    def __determine_status(self):
        #print(str(self.current_time - self.__idle_time))
        if self.__detecting == False:
            self.__reset_bools()
            self.__idle_time = time()
        elif self.current_time - self.__idle_time < 5:
            self.__reset_bools()
        elif self.current_time - self.__idle_time <= 10:
            self.__idle = True
        else:
            self.__idle_long = True

    # sends the current status to the MCU
    def __send_status(self):
        self.__determine_status()
        if self.__detecting == False:
            self.__comms.send_message("Not Detecting")
        elif self.__idle == False:
            self.__comms.send_message("Nice Job")
        elif self.__idle_long == False:
            self.__comms.send_message("Time to Move")
        else:
            self.__comms.send_message("TIME TO MOVE")

    # returns the current status
    def get_status_message(self, steps, jumps):
        self.__detect_activity(steps, jumps)
        self.__determine_status()
        if self.__detecting == False:
            message = "Off"
        elif self.__idle == False:
            message = "Nice"
        elif self.__idle_long == False:
            message = "Move"
        else:
            message = "MOVE"
        return message

    # toggle detecting
    def set_detecting(self):
        self.__detecting = not self.__detecting