"""
Author: Stefan Palm
stefan.palm@hotmail.se

code is intended for learning
"""
import cv2 
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os.path
from pathlib import Path

#a little helperfunction i modified
def mouse_crop(event, x, y, flags, param):
    # grab references to the global variables
    global x_start, y_start, x_end, y_end, cropping
 
    # if the left mouse button was DOWN, start RECORDING
    # (x, y) coordinates and indicate that cropping is being
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start, x_end, y_end = x, y, x, y
        cropping = True
 
    # Mouse is Moving
    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping == True:
            x_end, y_end = x, y
 
    # if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates
        x_end, y_end = x, y
        cropping = False # cropping is finished
 
# Select the file to work on, need to use withdraw to get rid of dialouge window
root = tk.Tk()
root.withdraw()
#catching some info from root for later
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

videofile = filedialog.askopenfilename()

#Let us open the Video and start reading
cap = cv2.VideoCapture(videofile) 

# Check if video opened successfully - TBD: nice exit
if (cap.isOpened() == False): 
  print("Unable to read file!")
  exit()

while(cap.isOpened()):
    # Capture first frame and exit loop
    ret, frame = cap.read()
    break
# release the video capture object, make sure we start from frame 1 next time
cap.release()

#prep some stuff for cropping
cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
oriImage = frame.copy()

#prep a window, and place it at the center of the screen
cv2.namedWindow("select area, use q when happy")
cv2.setMouseCallback("select area, use q when happy", mouse_crop)
cv2.resizeWindow('select area, use q when happy', frame.shape[1], frame.shape[0]) 
x_pos = round(screen_width/2) - round(frame.shape[1]/2)
y_pos = round(screen_height/2) - round(frame.shape[0]/2)
cv2.moveWindow("select area, use q when happy", x_pos,y_pos)

#show image and let user crop, press q when happy
while True:
    i = frame.copy()
    if not cropping:
        cv2.imshow("select area, use q when happy", frame)
        if (x_start + y_start + x_end + y_end) > 0:
            cv2.rectangle(i, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)
            cv2.imshow("select area, use q when happy", i)

    elif cropping:
        cv2.rectangle(i, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)
        cv2.imshow("select area, use q when happy", i)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

#we now have the cropping parameters
#print(x_start, y_start, x_end, y_end)

#cropping by slicing original image[y:y+h, x:x+w]
cropped = oriImage[y_start:y_end, x_start:x_end]

#show the result - un-comment this out if you like
""" cv2.namedWindow('cropped area', cv2.WINDOW_NORMAL)
cv2.resizeWindow('cropped area', cropped.shape[1], cropped.shape[0]) 
x_pos = round(screen_width/2) - round(cropped.shape[1]/2)
y_pos = round(screen_height/2) - round(cropped.shape[0]/2)
cv2.moveWindow("cropped area", x_pos,y_pos)
cv2.imshow("cropped area", cropped)
cv2.waitKey(0)
cv2.destroyAllWindows() """

# Now let us crop the video with same cropping parameters
cap = cv2.VideoCapture(videofile)

#let's keep it simple...store the new file in same directory, same name, but add suffix
newFileName = os.path.join(str(Path(videofile).parents[0]), str(Path(videofile).stem) +'_cropped.avi')
frame_width = x_end - x_start
frame_height = y_end - y_start

#get fps info from file CV_CAP_PROP_FPS, if possible 
fps = int(round(cap.get(5)))
#check if we got a value, otherwise use any number - you might need to change this
if fps == 0:
    fps = 30 #so change this number if cropped video has stange steed, higher number gives slower speed
 
# create VideoWriter object and define the codec. This may be an area for warnings and errors - use google if so
out = cv2.VideoWriter(newFileName, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_height))
 
#read frame by frame
while(True):
  ret, frame = cap.read()
 
  if ret == True:
    #crop frame
    cropped = frame[y_start:y_end, x_start:x_end] 
    # Write the frame into the file 'output.avi'
    out.write(cropped)
 
    # Display the resulting frame - trying to move window, but does not always work
    cv2.namedWindow('producing video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('producing video', cropped.shape[1], cropped.shape[0]) 
    x_pos = round(screen_width/2) - round(cropped.shape[1]/2)
    y_pos = round(screen_height/2) - round(cropped.shape[0]/2)
    cv2.moveWindow("producing video", x_pos,y_pos)
    cv2.imshow('producing video',cropped)
 
    # Press Q on keyboard to stop recording early
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
 
  # Break the loop when done
  else:
    break 
 
# When everything done, release the video capture and video write objects
cap.release()
out.release()
 
# Make sure all windows are closed
cv2.destroyAllWindows()

# Leave a message
print("New cropped video created: ", newFileName)


