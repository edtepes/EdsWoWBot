#! /usr/bin/python3
import mss, pyautogui, cv2 as cv, numpy as np, time

w, h = pyautogui.size()
print("Screen Resolution: " + "w: " + str(w) + " h:" + str(h)) 

img = None
monitor = {"top":0, "left": 0, "width": w, "height": h}
with mss.mss() as sct:
    while True:
        img = sct.grab(monitor)
        img  = np.array(img) #takes that data and converts it to numpy array. Converting from rgb to bgr is not needed thanks to the grab function, since screenshot apps and opencv both work in bgr

        small = cv.resize(img, (0, 0), fx = 0.5, fy = 0.5) #small version of the screen image (a resize using scalars)

        cv.imshow("Computer Vision", small) #displaying the image on the screen

        key = cv.waitKey(1) #introducing a 1ms delay so that we can see the screen or it will disapear to quickly
        if key == ord('q'):
            break

cv.destroyAllWindows()
