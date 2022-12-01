from ECE16Lib.Communication import Communication
import face_recognition
import cv2
import os
import numpy as np
from time import time

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
syed_image = face_recognition.load_image_file("syed.jpg")
syed_face_encoding = face_recognition.face_encodings(syed_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file("biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    syed_face_encoding,
    biden_face_encoding
]
known_face_names = [
    "Syed Islam",
    "Joe Biden"
]

# Initialize some variables
face_locations = []
face_encodings = [biden_face_encoding]
face_names = []
process_this_frame = True

# Open serial communication and display start-up messages
comms = Communication("COM7", 115200)
print("Connected to COM7")
print("Security Door Activated")
# Remove extra junk and send "Activated" to remote
comms.clear()
comms.send_message("Activated")

# Initialize variable with the time that the program started
start_time = time()

# Function that sets the serial port to the port passed in the argument
def set_port(port):
    global comms
    if comms != None:
        # If the current port is COM7 and the user wants COM10
        if comms.ser.port == "COM7" and port == "COM10":
            print("Closing COM7...")
            comms.close()
            comms = Communication("COM10", 115200)
            print("Connected to COM10")
        # If the current port is COM10 and the user wants COM7
        elif comms.ser.port == "COM10" and port == "COM7":
            print("Closing COM10...")
            comms.close()
            comms = Communication("COM7", 115200)
            print("Connected to COM7")
try:
    # Initialize variables for conditionals
    door_opened = False
    system_enabled = True
    while(True):
        # Update time, message, and set name to "None detected"
        current_time = time()
        message = comms.receive_message()
        name = "None detected"
        
        ret, frame = video_capture.read() # Grab a single frame of video

        # Only process every other frame of video to save time
        if process_this_frame and system_enabled:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25) # Resize frame of video to 1/4 size for faster face recognition processing
            rgb_small_frame = small_frame[:, :, ::-1] # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                else:
                    name = "Unknown"

                    
                face_names.append(name)
                #print(name)

        process_this_frame = not process_this_frame # for capturing only every other frame

        if system_enabled:
            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        else:
            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 0
                right *= 0
                bottom *= 0
                left *= 0

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if system_enabled:
            # If the person is known by the system
            if name in known_face_names:
                print(name)
                set_port("COM10")
                comms.send_message("UNLOCK")
                set_port("COM7")
                comms.send_message(name)
            # Else if a person was detected but they are unknown by the system
            elif name == "Unknown":
                print(name)
                set_port("COM7")
                comms.send_message("UNKNOWN")
        else:
            name = "None detected"

        if message != None: # if the message is not empty
            # If receives "UNLOCK" from COM7, switch to COM10 and send "UNLOCK"
            if "UNLOCK" in message:
                print(message)
                set_port("COM10")
                comms.send_message("UNLOCK")

            # If receives "SAVE" from COM7
            if "SAVE" in message:
                # Save and process guest images
                img_num = 0
                img_path = "guest_"+str(img_num)+".jpg"
                while True:
                    if (not os.path.exists(img_path)):
                        cv2.imwrite(img_path, frame)
                        break
                    else:
                        img_num += 1
                        img_path = "guest_" + str(img_num) + ".jpg"

                # Send "UNLOCK" to COM10
                set_port("COM10")
                comms.send_message("UNLOCK")

                # Load the image that was just saved and create a face encoding with the image
                guest_image = face_recognition.load_image_file(img_path)
                guest_face_encoding = face_recognition.face_encodings(guest_image)[0]

                # Add the encoding to the list of known face encodings and "Guest #" to the list of face names
                known_face_encodings.append(guest_face_encoding)
                known_face_names.append("Guest " + str(img_num))

            # If receives "DISABLE" from COM7, toggle the system on or off
            if "DISABLE" in message:
                system_enabled = not system_enabled
                print("System enabled: " + str(system_enabled))

            # If receives "DOOR OPENED" from COM10, send "DOOR OPENED" to COM7 and set door_opened to True
            if "DOOR OPENED" in message:
                print(message)
                set_port("COM7")
                comms.send_message(message)
                set_port("COM10")
                door_opened = True

            # If receives "DOOR CLOSED" from COM10, send "DOOR CLOSED" to COM7 and set door_opened to False
            if "DOOR CLOSED" in message:
                print(message)
                door_opened = False
                set_port("COM7")
                comms.send_message(message)

except (KeyboardInterrupt or Exception) as e:
    print(e) # print exception or keyboard interrupt
finally:
    comms.close() # close serial communication
    video_capture.release() # release handle to the webcam
    cv2.destroyAllWindows() # destroy capture window
    print("Ending program")
