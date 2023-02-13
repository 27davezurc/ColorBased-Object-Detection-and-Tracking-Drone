import time
import cv2
import numpy as np
from djitellopy import Tello

# DRONE CONTOURS FILE

# Used for setting the dimensions of the frame
WIDTH = 1440
HEIGHT = 780

# Coordinates for the center of the frame
# centerX = int(WIDTH / 2)
# centerY = int(HEIGHT / 2)

isFlying = True    # False for testing, True for flying
# isFlying = False

# Connect to Tello
tello = Tello()
tello.connect()
tello.forwardBackward_velocity = 0
tello.upDown_velocity = 0
tello.yaw_velocity = 0
tello.speed = 0

tello.streamoff()
tello.streamon()

print(tello.get_battery())

if isFlying:
    tello.takeoff()

while True:

    frameRead = tello.get_frame_read()
    myFrame = frameRead.frame

    # Resizing window
    myFrame = cv2.resize(myFrame, (WIDTH, HEIGHT))

    # Flip the myFrame horizontally
    # myFrame = cv2.flip(myFrame, 1)

    # Improvement to reduce noise:
    blurred_frame = cv2.GaussianBlur(myFrame, (5, 5), 0)
    hsv = cv2.cvtColor(myFrame, cv2.COLOR_BGR2HSV)

    # Change values as necessary
    lowColor = np.array([6, 115, 156])
    highColor = np.array([179, 255, 255])


    mask = cv2.inRange(hsv, lowColor, highColor)

    # Function findContours returns 2 values: NOTE ONLY 2 VALUES
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Another improvement: only draw contours around largest object
    maxArea = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > maxArea:
            maxArea = area
        # Prints area. This is used to only draw contours larger than a specified area
        # print(area)
        # print(maxArea)

        # if maxArea > 40000:
        if maxArea > 10000:
            cv2.drawContours(myFrame, contour, -1, (0, 255, 0), 3)

            # Moved inside if statement
            # Bounding rectangle around contoured object
            if area > 10000:
                approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
                x, y, w, h = cv2.boundingRect(approx)
                cv2.rectangle(myFrame, (x, y), (x + w, y + h), (255, 0, 0), 4)

                # Centroid of rectangle
                M = cv2.moments(contour)
                if M['m00'] != 0:
                    cX = int(M['m10'] / M['m00'])
                    cY = int(M['m01'] / M['m00'])

            # Draw centroid of rectangle
            cv2.circle(myFrame, (int(cX), int(cY)), 7, (255, 255, 255), -1)

            # Print coordinates of centroid (the white circle)
            # print("cX: " + str(cX) + " cY: " + str(cY))

            # Then, drone moves left or right based on where it is
            if WIDTH / 3 <= cX <= 2 * (WIDTH / 3) and HEIGHT / 3 <= cY <= 2 * (HEIGHT / 3):
                tello.send_rc_control(0, 0, 0, 0)                                                       # STAY IN CENTER
                print("STAY CENTERED")
                continue
            elif WIDTH / 3 <= cX <= 2 * (WIDTH / 3) and cY <= HEIGHT / 3:
                tello.send_rc_control(0, 0, 20, 0)                                                      # GO DOWN
                print("GO UP")
            elif WIDTH / 3 <= cX <= 2 * (WIDTH / 3) and cY >= 2 * (HEIGHT / 3):
                tello.send_rc_control(0, 0, -20, 0)                                                     # GO UP
                print("GO DOWN")
            elif cX <= WIDTH / 3 and HEIGHT / 3 <= cY <= 2 * (HEIGHT / 3):
                tello.send_rc_control(-20, 0, 0, 0)                                                      # MOVE LEFT
                print("GO LEFT")
            elif cX >= 2 * (WIDTH / 3) and HEIGHT / 3 <= cY <= 2 * (HEIGHT / 3):
                tello.send_rc_control(20, 0, 0, 0)                                                     # MOVE RIGHT
                print("GO RIGHT")
            elif cX <= WIDTH / 3 and cY <= HEIGHT / 3:
                tello.send_rc_control(-20, 0, 20, 0)                                                    # DIAGONAL UP LEFT
                print("GO DIAGONALLY UP LEFT")
            elif cX <= WIDTH / 3 and cY >= 2 * (HEIGHT / 3):
                tello.send_rc_control(-20, 0, -20, 0)                                                   # DIAGONAL DOWN LEFT
                print("GO DIAGONALLY DOWN LEFT")
            elif cX >= 2 * (WIDTH / 3) and cY <= HEIGHT / 3:
                tello.send_rc_control(20, 0, 20, 0)                                                     # DIAGONAL UP RIGHT
                print("GO DIAGONALLY UP RIGHT")
            elif cX >= 2 * (WIDTH / 3) and cY >= 2 * (HEIGHT / 3):
                tello.send_rc_control(20, 0, -20, 0)                                                    # DIAGONAL DOWN RIGHT
                print("GO DIAGONALLY DOWN RIGHT")
            else:
                # Not Detected, Move Forward -- Maybe it always goes forward no matter what
                print("NOT DETECTED: MOVE FORWARD")
                continue

        else:
            tello.send_rc_control(0, 0, 0, 0)
            print("NOT DETECTED")

    # Draw lines to split frame into ninths:
    # First line
    leftLineWidth = int(WIDTH / 3)
    cv2.line(myFrame, (leftLineWidth, 0), (leftLineWidth, HEIGHT), (255, 255, 255), 1)
    # Second line
    rightLineWidth = 2 * int(WIDTH / 3)
    cv2.line(myFrame, (rightLineWidth, 0), (rightLineWidth, HEIGHT), (255, 255, 255), 1)

    # Upper horizontal
    upperLineY = int(HEIGHT / 3)
    cv2.line(myFrame, (0, upperLineY), (WIDTH, upperLineY), (255, 255, 255), 1)
    # Lower horizontal line
    lowerLineY = 2 * int(HEIGHT / 3)
    cv2.line(myFrame, (0, lowerLineY), (WIDTH, lowerLineY), (255, 255, 255), 1)

    cv2.imshow("Frame", myFrame)
    cv2.imshow("Mask", mask)

    # Change value below for different updated video framerates
    key = cv2.waitKey(1)
    if(key == 27):
        tello.land()
        break

cv2.destroyAllWindows()