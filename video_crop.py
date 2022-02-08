"""
Author: Stefan Palm
stefan.palm@hotmail.se

code is intended for learning
"""

import cv2
import tkinter as tk
from tkinter import filedialog
import os.path
from pathlib import Path


class Cropper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        #catching some info from root for later
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Select the file to work on, need to use withdraw to get rid of dialogue window
        self.videofile = filedialog.askopenfilename()

        #Let us open the Video and start reading
        self.cap = cv2.VideoCapture(self.videofile)

        # Check if video opened successfully - TBD: nice exit
        if (self.cap.isOpened() == False):
          print("Unable to read file!")
          exit()

        while(self.cap.isOpened()):
            # Capture first frame and exit loop
            self.ret, self.frame = self.cap.read()
            break
        # release the video capture object, make sure we start from frame 1 next time
        self.cap.release()

        #prep some stuff for cropping
        self.cropping = False
        self.x_start, self.y_start, self.x_end, self.y_end = 0, 0, 0, 0
        self.oriImage = self.frame.copy()

        #prep a window, and place it at the center of the screen
        cv2.namedWindow("select area, use q when happy")
        cv2.setMouseCallback("select area, use q when happy", self.mouse_crop)
        cv2.resizeWindow('select area, use q when happy', self.frame.shape[1], self.frame.shape[0])
        self.x_pos = round(self.screen_width/2) - round(self.frame.shape[1]/2)
        self.y_pos = round(self.screen_height/2) - round(self.frame.shape[0]/2)
        cv2.moveWindow("select area, use q when happy", self.x_pos, self.y_pos)

        #show image and let user crop, press q when happy
        while True:
            i = self.frame.copy()
            if not self.cropping:
                cv2.imshow("select area, use q when happy", self.frame)
                if (self.x_start + self.y_start + self.x_end + self.y_end) > 0:
                    cv2.rectangle(i, (self.x_start, self.y_start), (self.x_end, self.y_end), (255, 0, 0), 2)
                    cv2.imshow("select area, use q when happy", i)

            elif self.cropping:
                cv2.rectangle(i, (self.x_start, self.y_start), (self.x_end, self.y_end), (255, 0, 0), 2)
                cv2.imshow("select area, use q when happy", i)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

        #we now have the cropping parameters
        #print(x_start, y_start, x_end, y_end)

        #cropping by slicing original image[y:y+h, x:x+w]
        self.cropped = self.oriImage[self.y_start:self.y_end, self.x_start:self.x_end]

        # #show the result - un-comment this out if you like
        # cv2.namedWindow('cropped area', cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('cropped area', self.cropped.shape[1], self.cropped.shape[0])
        # self.x_pos = round(self.screen_width/2) - round(self.cropped.shape[1]/2)
        # self.y_pos = round(self.screen_height/2) - round(self.cropped.shape[0]/2)
        # cv2.moveWindow("cropped area", self.x_pos, self.y_pos)
        # cv2.imshow("cropped area", self.cropped)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Now let us crop the video with same cropping parameters
        self.cap = cv2.VideoCapture(self.videofile)

        #let's keep it simple...store the new file in same directory, same name, but add suffix
        self.newFileName = os.path.join(str(Path(self.videofile).parents[0]), str(Path(self.videofile).stem) +'_cropped.avi')
        self.frame_width = self.x_end - self.x_start
        self.frame_height = self.y_end - self.y_start

        #get fps info from file CV_CAP_PROP_FPS, if possible
        self.fps = int(round(self.cap.get(5)))
        #check if we got a value, otherwise use any number - you might need to change this
        if self.fps == 0:
            self.fps = 30 #so change this number if cropped video has stange steed, higher number gives slower speed

        # create VideoWriter object and define the codec. This may be an area for warnings and errors - use google if so
        self.out = cv2.VideoWriter(self.newFileName, cv2.VideoWriter_fourcc('M','J','P','G'), self.fps, (self.frame_width,self.frame_height))

        #read frame by frame
        while(True):
            self.ret, self.frame = self.cap.read()
            if self.ret:
                #crop frame
                self.cropped = self.frame[self.y_start:self.y_end, self.x_start:self.x_end]
                # Write the frame into the file 'output.avi'
                self.out.write(self.cropped)

                # Display the resulting frame - trying to move window, but does not always work
                cv2.namedWindow('producing video', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('producing video', self.cropped.shape[1], self.cropped.shape[0])
                x_pos = round(self.screen_width/2) - round(self.cropped.shape[1]/2)
                y_pos = round(self.screen_height/2) - round(self.cropped.shape[0]/2)
                cv2.moveWindow("producing video", self.x_pos,self.y_pos)
                cv2.imshow('producing video',self.cropped)

                # Press Q on keyboard to stop recording early
                if cv2.waitKey(1) & 0xFF == ord('q'):
                  break

        # Break the loop when done
            else:
                break

        # When everything done, release the video capture and video write objects
        self.cap.release()
        self.out.release()

        # Make sure all windows are closed
        cv2.destroyAllWindows()

        # Leave a message
        print("New cropped video created: ", self.newFileName)

    def mouse_crop(self, event, x, y, flags, param):
        # if the left mouse button was DOWN, start RECORDING
        # (x, y) coordinates and indicate that cropping is being
        if event == cv2.EVENT_LBUTTONDOWN:
            self.x_start, self.y_start, self.x_end, self.y_end = x, y, x, y
            self.cropping = True

        # Mouse is Moving
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.cropping:
                self.x_end, self.y_end = x, y

        # if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates
            self.x_end, self.y_end = x, y
            self.cropping = False # cropping is finished

if __name__ == "__main__":
    app = Cropper()
