# Finding hsv range of target object SO
import cv2
import numpy as np
import time


# A required callback method that goes into the trackbar function.
def nothing(x):
    pass


# Initializing the webcam feed.
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Create a window named trackbars.
cv2.namedWindow("Trackbars")

# Now create 6 trackbars that will control the lower and upper range of
# H,S and V channels. The Arguments are like this: Name of trackbar,
# window name, range,callback function. For Hue the range is 0-179 and
# for S,V its 0-255.
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

while True:

    # Start reading the webcam feed frame by frame.
    ret, frame = cap.read()
    if not ret:
        break
    # Flip the frame horizontally (Not required)
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to HSV image.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # HSV Values
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    # Lower/Upper Range
    lower_range = np.array([l_h, l_s, l_v])
    upper_range = np.array([u_h, u_s, u_v])

    # Filter the image and get the binary mask, where white represents your target color
    mask = cv2.inRange(hsv, lower_range, upper_range)

    # Makes the mask image your target color
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # Mask with target color
    mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Stacking
    stacked = np.hstack((mask_3, frame, res))

    # Show this stacked frame at 40% of the size.
    cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=0.4, fy=0.4))

    # If the user presses ESC then exit the program
    key = cv2.waitKey(1)
    if key == 27:
        break


# Release the camera & destroy the windows.
cap.release()
cv2.destroyAllWindows()