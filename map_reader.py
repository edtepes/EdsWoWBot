import pytesseract, numpy, cv2 as cv
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def get_cur_zone(img):
    
    #img stored as numpy array
    top_left = (1724,5)
    bottom_right = (1914,22)

    zone_name_img = img[
        top_left[1]:bottom_right[1], 
        top_left[0]:bottom_right[0]
    ]

    #optional pre-processing steps for better accuracy
    zone_name_img = cv.cvtColor(zone_name_img, cv.COLOR_BGR2GRAY)
    zone_name_img = cv.threshold(zone_name_img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

    #create text
    zone = pytesseract.image_to_string(zone_name_img)
    
    return zone