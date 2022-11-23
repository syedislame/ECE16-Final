"""
@author: Ramsin Khoshabeh
"""

from ECE16Lib.Communication import Communication
from time import sleep
from time import time
import socket, pygame

# Setup the Socket connection to the Space Invaders game
host = "127.0.0.1"
port = 65432
mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mySocket.connect((host, port))
mySocket.setblocking(False)

# Initialize accelerometer variables when stable
X_ZERO = 1987
Y_ZERO = 1977
Z_ZERO = 2360

class PygameController:
  comms = None

  def __init__(self, serial_name, baud_rate):
    self.comms = Communication(serial_name, baud_rate)

  def run(self):
    # 1. make sure data sending is stopped by ending streaming
    self.comms.send_message("stop")
    self.comms.clear()

    # 2. start streaming orientation data
    input("Ready to start? Hit enter to begin.\n")
    self.comms.send_message("start")

    # 3. Forever collect orientation and send to PyGame until user exits
    print("Use <CTRL+C> to exit the program.\n")
    previous_time = time()
    cooldown = 0.01 # determines how long between each send_message call; lower for higher controller sensitivity
    while True:
      message = self.comms.receive_message()  # receive first available message serial buffer
      command = None  # intialize empty variable to hold command
      if(message != None):  # if the message is not an empty string
        if ("FIRE" in message): # if the message contains "FIRE"
          command = "FIRE"  # set command to "FIRE"
          mySocket.send(command.encode("UTF-8"))  # send the command to the socket server
          print(command)  # for testing
        elif ("QUIT" in message): # else if the message contains "QUIT"
          raise KeyboardInterrupt # cause a KeyboardInterrupt, effectively quitting the game
        else: 
          try:
            m1, m2, m3, m4 = message.split(',') # split the message by comma into four strings
          except ValueError:  # skip if corrupted data
            continue
          
          # Convert strings with accelerometer data to ints
          ax = int(m2)
          ay = int(m3)
          az = int(m4)
          #print("%d, %d, %d" % (ax, ay, az)) # for testing

          # Calculate differences between live accelerometer values and stable values
          x = ax - X_ZERO
          y = ay - Y_ZERO
          z = az - Z_ZERO
          
          if (abs(x) >= abs(y) and abs(x) >= abs(z)): # if the board is tilted left or right
            if (x < -43): # if board is tilted left, move left
              command = "LEFT"
            elif (x > 23):  # if board it tilted right, move right
              command = "RIGHT"
          elif (abs(y) >= abs(x) and abs(y) >= abs(z)): # if the board is tilted up or down
            if (y < -200 and cooldown > 0.01):  # if front of board is tilted up, increase sensitivity
              command = "UP"
              cooldown -= 0.0005 # decrement cooldown to increase sensitivity linearly with time
            elif (y > 200 and cooldown < 0.05):  # if front of board is tilted down, decrease sensitivity
              command = "DOWN"
              cooldown += 0.001 # increment cooldown to decrease sensitivity linearly with time
          elif (abs(z) > abs(x) and abs(z) >= abs(y)):  # if flat, then do nothing
            command = "FLAT"

          # Send the command to the socket server if there is one and the cooldown has worn off
          current_time = time() # update current_time variable to current time
          if command is not None and (current_time - previous_time >= cooldown): 
            mySocket.send(command.encode("UTF-8"))  # send the command to the socket server
            print(command)  # for testing
            previous_time = current_time  # update previous_time to current time

      # Try to receive data from the socket server and send it if data is received
      try:
        data = mySocket.recv(1024)  # receive 1024 bytes of data
        data = data.decode("utf-8") # decode the data
        #print(data)
        self.comms.send_message(str(data))  # send the data to the serial buffer
      except BlockingIOError:
        pass # do nothing if there's no data


if __name__== "__main__":
  serial_name = "COM7"
  baud_rate = 115200
  controller = PygameController(serial_name, baud_rate)

  try:
    controller.run()
  except(Exception, KeyboardInterrupt) as e:
    print(e)
  finally:
    print("Exiting the program.")
    controller.comms.send_message("stop")
    controller.comms.close()
    mySocket.send("QUIT".encode("UTF-8"))
    mySocket.close()

  input("[Press ENTER to finish.]")
