import cv2
import numpy as np

# WEBCAM CONTOURS FILE

# Used for setting the dimensions of the frame
WIDTH = 1440
HEIGHT = 780

cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()

    # Resizing window
    # frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Improvement to reduce noise:
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Change values as necessary
    # lowColor = np.array([1, 174, 52])
    # highColor = np.array([179, 236, 255])
    lowColor = np.array([26, 84, 71])
    highColor = np.array([179, 255, 255])

    mask = cv2.inRange(hsv, lowColor, highColor)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Another improvement: only draw contours around largest object
    maxArea = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if(area > maxArea):
            maxArea = area
        # Prints area. This is used to only draw contours larger than a specified area
        # print(area)
        # print(maxArea) ##

        # Only draw contours around largest object:
        # 5000 up to 50000-75000
        # 80000 - 12500

        if maxArea > 10000:
            cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)

            # Bounding rectangle around contoured object
            if area > 10000:
                approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
                x, y, w, h = cv2.boundingRect(approx)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 4)

                # Centroid of rectangle
                M = cv2.moments(contour)
                if M['m00'] != 0:
                    cX = int(M['m10'] / M['m00'])
                    cY = int(M['m01'] / M['m00'])

            # Draw centroid of rectangle
            cv2.circle(frame, (int (cX), int (cY)), 7, (255,255,255), -1)

            # Print coordinates of centroid (the white circle)
            print("cX: " + str(cX) + " cY: " + str(cY))

            # Then, drone moves left or right based on where it is
            if WIDTH / 3 <= cX <= 2 * (WIDTH / 3) and HEIGHT / 3 <= cY <= 2 * (HEIGHT / 3):
                print("STAY CENTERED")
                continue
            elif WIDTH / 3 <= cX <= 2 * (WIDTH / 3) and cY <= HEIGHT / 3:
                print("GO DOWN")
            elif WIDTH / 3 <= cX <= 2 * (WIDTH / 3) and cY >= 2 * (HEIGHT / 3):
                print("GO UP")
            elif cX <= WIDTH / 3 and HEIGHT / 3 <= cY <= 2 * (HEIGHT / 3):
                print("GO RIGHT")
            elif cX >= 2 * (WIDTH / 3) and HEIGHT / 3 <= cY <= 2 * (HEIGHT / 3):
                print("GO LEFT")
            elif cX <= WIDTH / 3 and cY <= HEIGHT / 3:
                print("GO DIAGONALLY DOWN RIGHT")
            elif cX <= WIDTH / 3 and cY >= 2 * (HEIGHT / 3):
                print("GO DIAGONALLY UP RIGHT")
            elif cX >= 2 * (WIDTH / 3) and cY <= HEIGHT / 3:
                print("GO DIAGONALLY DOWN LEFT")
            elif cX >= 2 * (WIDTH / 3) and cY >= 2 * (HEIGHT / 3):
                print("GO DIAGONALLY UP LEFT")
            else:
                # Not Detected, Move Forward -- Maybe it always goes forward no matter what
                print("NOT DETECTED: MOVE FORWARD")
                continue

        else:
            print("NOT DETECTED")

    # Draw lines to split frame into ninths:
    # First line
    leftLineWidth = int(WIDTH / 3)
    cv2.line(frame, (leftLineWidth, 0), (leftLineWidth, HEIGHT), (255, 255, 255), 1)
    # Second line
    rightLineWidth = 2 * int(WIDTH / 3)
    cv2.line(frame, (rightLineWidth, 0), (rightLineWidth, HEIGHT), (255, 255, 255), 1)

    # Upper horizontal
    upperLineY = int(HEIGHT / 3)
    cv2.line(frame, (0, upperLineY), (WIDTH, upperLineY), (255, 255, 255), 1)
    # Lower horizontal line
    lowerLineY = 2 * int(HEIGHT / 3);
    cv2.line(frame, (0, lowerLineY), (WIDTH, lowerLineY), (255, 255, 255), 1)

    # OpenCV Windows
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    # Change value below for different updated video framerates
    key = cv2.waitKey(1)
    if(key == 27):
        break

cap.release()
cv2.destroyAllWindows()