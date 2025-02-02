#! /usr/bin/python3
import mss, pyautogui, cv2 as cv, numpy as np, time, multiprocessing

class ScreenCaptureAgent:
    def __init__(self) -> None:
        self.img = None
        self.capture_process = None
        self.fps = None
        self.enable_cv_preview = True #we can turn on and off our computer vision (might want to display this or not depending on PC resources)

        
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
                
                if self.enable_cv_preview:
                    small = cv.resize(self.img, (0, 0), fx = 0.5, fy = 0.5) #small version of the screen image (a resize using scalars)
                    cv.imshow("Computer Vision", small) #displaying the image on the screen
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