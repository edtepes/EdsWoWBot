#! /usr/bin/python3
import mss, pyautogui, cv2 as cv, numpy as np, time, multiprocessing, threading, queue
import map_reader

def run_capture():
    agent = ScreenCaptureAgent()
    agent.capture_screen()

class ScreenCaptureAgent:
    def __init__(self) -> None:
        self.img = None
        self.img_health = None
        self.img_health_HSV = None  # HSV version for health colors
        self.img_mana = None
        self.img_mana_HSV = None    # HSV version for mana colors
        self.fps = None
        self.enable_cv_preview = True  # Toggle CV preview

        # HEALTH DETECTION
        self.health_top_left = (498, 799)
        self.health_bottom_right = (744, 830)

        # MANA DETECTION
        self.mana_top_left = (499, 834)
        self.mana_bottom_right = (744, 843)
        
        # LOCATION DETECTION (OCR result)
        self.zone = ""

        self.w, self.h = pyautogui.size()
        print("Screen Resolution: w:" + str(self.w) + " h:" + str(self.h)) 
        self.monitor = {"top": 0, "left": 0, "width": self.w, "height": self.h}

        # Set up OCR queue and thread
        self.ocr_queue = queue.Queue(maxsize=1)  # Only keep the most recent frame
        self.ocr_thread = threading.Thread(target=self.ocr_worker, daemon=True)
        self.ocr_thread.start()

    def capture_screen(self):
        fps_report_time = time.time()  # last FPS report time
        fps_report_delay = 5           # report every 5 seconds 
        n_frames = 1
        with mss.mss() as sct:
            while True:
                self.img = sct.grab(self.monitor)
                self.img = np.array(self.img)
                
                self.img_health = self.img[
                    self.health_top_left[1]:self.health_bottom_right[1],
                    self.health_top_left[0]:self.health_bottom_right[0]
                ]
                self.img_mana = self.img[
                    self.mana_top_left[1]:self.mana_bottom_right[1],
                    self.mana_top_left[0]:self.mana_bottom_right[0]
                ]
                
                self.img_health_HSV = cv.cvtColor(self.img_health, cv.COLOR_BGR2HSV)
                self.img_mana_HSV = cv.cvtColor(self.img_mana, cv.COLOR_BGR2HSV)

                # Enqueue image for OCR processing (asynchronously)
                try:
                    if self.ocr_queue.full():
                        self.ocr_queue.get_nowait()  # discard old frame
                    self.ocr_queue.put_nowait(self.img.copy())
                except queue.Full:
                    pass

                if self.enable_cv_preview:
                    small = cv.resize(self.img, (0, 0), fx=0.5, fy=0.5)  # Create a smaller preview version
                    fps_text = "" if self.fps is None else f'FPS: {self.fps:.2f}'
                    
                    cv.putText(small, fps_text, (25,20), cv.FONT_HERSHEY_DUPLEX, 0.75, (255,0,255), 1, cv.LINE_AA)
                    cv.putText(small, "Health: " + str(hue_match_pct(self.img_health_HSV, 238, 242)),
                               (25,40), cv.FONT_HERSHEY_DUPLEX, 0.75, (0,0,255), 1, cv.LINE_AA)
                    cv.putText(small, "Mana: " + str(hue_match_pct(self.img_mana_HSV, 212, 216)),
                               (25,60), cv.FONT_HERSHEY_DUPLEX, 0.75, (0,0,255), 1, cv.LINE_AA)
                    cv.putText(small, "Location: " + self.zone, (25,80),
                               cv.FONT_HERSHEY_DUPLEX, 0.75, (0,0,255), 1, cv.LINE_AA)
                    
                    cv.imshow("Computer Vision", small)
                    cv.imshow("Health Bar", self.img_health)
                    cv.imshow("Mana Bar", self.img_mana)
                    cv.waitKey(1)  # Short delay so the windows update

                elapsed_time = time.time() - fps_report_time
                if elapsed_time >= fps_report_delay:
                    self.fps = n_frames / elapsed_time
                    print("FPS: " + str(self.fps))
                    n_frames = 0
                    fps_report_time = time.time()
                n_frames += 1

    def ocr_worker(self):
        """Background thread to process OCR without blocking the capture loop."""
        while True:
            try:
                img = self.ocr_queue.get(timeout=1)
            except queue.Empty:
                continue
            # Use the map_reader OCR function on the image
            zone_text = map_reader.get_cur_zone(img)
            self.zone = zone_text.lower().strip()

class bcolors:
    PINK = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED   = '\033[91m'
    ENDC  = '\033[0m'

def convert_hue(hue):
    # Gets the ratio of the HSV color to what OpenCV uses
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
                no_match_pixels += 1
    total_pixels = match_pixels + no_match_pixels
    pct_health = np.round(match_pixels / total_pixels, 2) * 100
    return pct_health

def print_menu():
    print(f'{bcolors.CYAN}Command Menu{bcolors.ENDC}')
    print(f'\t{bcolors.GREEN}r - run{bcolors.ENDC}\t\t Start Screen Capture')
    print(f'\t{bcolors.RED}s - stop{bcolors.ENDC}\t Stop Screen Capture')
    print(f'\tq - quit\t Quit the program')

if __name__ == "__main__":
    capture_process = None
    while True:
        print_menu()
        user_input = input().strip().lower()
        if user_input in ['quit', 'q']:
            if capture_process is not None:
                capture_process.terminate()
            break
        elif user_input in ['run', 'r']:
            if capture_process is not None:
                print(f'{bcolors.YELLOW}WARNING:{bcolors.ENDC} Capture process is already running.')
                continue
            capture_process = multiprocessing.Process(
                target=run_capture,
                name="screen capture process"
            )
            capture_process.start()
        elif user_input in ['stop', 's']:
            if capture_process is None:
                print(f'{bcolors.YELLOW}WARNING:{bcolors.ENDC} Capture process is not running.')
                continue
            capture_process.terminate()
            capture_process = None
        else:
            print(f'{bcolors.RED}ERROR:{bcolors.ENDC} Invalid selection.')
    print("Done.")