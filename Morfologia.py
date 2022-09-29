import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(0)

cv2.namedWindow('trackbars')

cv2.createTrackbar('th','trackbars',230,255,nothing)
cv2.createTrackbar('opening','trackbars',1,10,nothing)

while(True):

    ret, frame = cap.read()
    frame = cv2.resize(frame, (334,180))

    th = cv2.getTrackbarPos('th','trackbars')
    ope = cv2.getTrackbarPos('opening','trackbars')

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    kernel = np.ones((5,5),np.uint8)
    
    ret, thresh = cv2.threshold(gray,th,255,cv2.THRESH_BINARY)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = ope)

    cv2.imshow('img',frame)
    cv2.imshow('thresh',thresh)
    cv2.imshow('opening',opening)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()