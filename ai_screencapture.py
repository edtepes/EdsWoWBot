#! /usr/bin/python3
import mss, pyautogui, cv2 as cv, numpy as np, time, multiprocessing

import map_reader

class ScreenCaptureAgent:
    def __init__(self) -> None:
        self.img = None
        self.img_health = None
        self.img_health_HSV = None #HSV version of the image to help us differentiate the health colors
        self.capture_process = None
        self.fps = None
        self.enable_cv_preview = True #we can turn on and off our computer vision (might want to display this or not depending on PC resources)

        #HEALTH DETECTION
        self.health_top_left = (498, 799)
        self.health_bottom_right = (744, 830)
        
        #LOCATION DETECTION
        self.zone = None

        self.w, self.h = pyautogui.size()
        print("Screen Resolution: " + "w: " + str(self.w) + " h:" + str(self.h)) 
        self.monitor = {"top":0, "left": 0, "width": self.w, "height": self.h}

    def capture_screen(self):
        fps_report_time = time.time() #checks when was the last time we reported the fps
        fps_report_delay = 5          #lets us show an avg fps from the last 5 seconds 
        n_frames = 1
        with mss.mss() as sct:
            while True:
                self.img = sct.grab(self.monitor)
                self.img  = np.array(self.img) #takes that data and converts it to numpy array. Converting from rgb to bgr is not needed thanks to the grab function, since screenshot apps and opencv both work in bgr
                
                self.img_health = self.img[
                    self.health_top_left[1]:self.health_bottom_right[1],
                    self.health_top_left[0]:self.health_bottom_right[0]
                ]

                self.zone = map_reader.get_cur_zone(self.img)
                self.zone = self.zone.lower().strip()

                self.img_health_HSV = cv.cvtColor(self.img_health, cv.COLOR_BGR2HSV)

                if self.enable_cv_preview:
                    small = cv.resize(self.img, (0, 0), fx = 0.5, fy = 0.5) #small version of the screen image (a resize using scalars)

                    if self.fps is None:
                        fps_text = ""
                    else:
                        fps_text = f'FPS: {self.fps:.2f}'
                    
                    cv.putText(
                        small,
                        fps_text,
                        (25,40),
                        cv.FONT_HERSHEY_DUPLEX,
                        0.75,
                        (255,0,255),
                        1,
                        cv.LINE_AA
                    )
                    cv.putText(
                        small,
                        "Health: " + str(hue_match_pct(self.img_health_HSV, 238, 242)),
                        (25,80),
                        cv.FONT_HERSHEY_DUPLEX,
                        0.75,
                        (0,0,255),
                        1,
                        cv.LINE_AA
                    )
                    cv.putText(
                        small,
                        "Location: " + self.zone,
                        (25,120),
                        cv.FONT_HERSHEY_DUPLEX,
                        0.75,
                        (0,0,255),
                        1,
                        cv.LINE_AA
                    )
                    cv.imshow("Computer Vision", small) #displaying the image on the screen
                    cv.imshow("Health Bar",self.img_health) #displaying rectangle for health in seperate window
                    key = cv.waitKey(1) #introducing a 1ms delay so that we can see the screen or it will disapear to quickly
                
                elapsed_time = time.time() - fps_report_time #total time in seconds (since we started to run program)
                if elapsed_time >= fps_report_delay:
                    self.fps = (n_frames / elapsed_time) #frames per second
                    print("FPS: " + str(self.fps))
                    n_frames = 0
                    fps_report_time = time.time()
                n_frames += 1

class bcolors:
    PINK = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED   = '\033[91m'
    ENDC  = '\033[0m'

def convert_hue(hue):
    #gets the ratio of the HSV color to what OpenCV has for its color limits
    ratio = 361/180
    return np.round(hue / ratio, 2)

def hue_match_pct(img, hue_low, hue_high):
    match_pixels = 0
    no_match_pixels = 0
    for pixel in img:
        for h, s, v in pixel:
            if convert_hue(hue_low) <= h <= convert_hue(hue_high):
                match_pixels += 1
            else:
                no_match_pixels +=1
    total_pixels = match_pixels + no_match_pixels
    pct_health = np.round(match_pixels / total_pixels, 2) * 100
    return pct_health


def print_menu():
    print(f'{bcolors.CYAN}Command Menu{bcolors.ENDC}')
    print(f'\t{bcolors.GREEN}r - run{bcolors.ENDC}\t\t Start Screen Capture')
    print(f'\t{bcolors.RED}s - stop{bcolors.ENDC}\t Stop Screen Capture')
    print(f'\tq - quit\t Quit the program')

if __name__ == "__main__":
    screen_agent = ScreenCaptureAgent()
    
    while True:
    #Print Menu to User
        print_menu()
    #Get User Input
        user_input = input().strip().lower()
        if user_input == 'quit' or user_input == 'q':
            if screen_agent.capture_process is not None:  
                screen_agent.capture_process.terminate()
            break
        elif user_input == 'run' or user_input == "r":
            if screen_agent.capture_process is not None:
                print(f'{bcolors.YELLOW}WARNING:{bcolors.ENDC} Capture process is already running.')
                continue
            screen_agent.capture_process = multiprocessing.Process(
                target = screen_agent.capture_screen, #no () needed as we are passing the function, not the result of the function 
                args=(),
                name="screen capture process"
            )
            screen_agent.capture_process.start()
        elif user_input == 'stop' or user_input == "s":
            if screen_agent.capture_process is None:
                print(f'{bcolors.YELLOW}WARNING:{bcolors.ENDC} Capture process is not running.')
                continue
            screen_agent.capture_process.terminate()
            screen_agent.capture_process = None
        else:
            print(f'{bcolors.RED}ERROR:{bcolors.ENDC} Invalid selection.')
    #Start/Stop/Quit  

print("Done.")