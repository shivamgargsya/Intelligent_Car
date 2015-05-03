import cv2
import numpy as np

cam = cv2.VideoCapture(0)

cam.set(3,160)
cam.set(4,120)


#Homographic Segmentation
var=1
while var > 0:

    minRed = 255
    maxRed = 0
    minRedGreenRange = 255
    maxRedGreenRange = 0
    minRedBlueRange = 255
    maxRedBlueRange = 0

    minLineLength = 80
    maxLineGap = 20

    ret,frame = cam.read()
    height, width, channels = frame.shape
    opImage = np.zeros((height,width,1),np.uint8)
    print height,width

    #finding threshols for image segmentation
    for i in range(80,height):
        for j in range(40,width-40):
            blue = frame[i,j,0]
            green = frame[i,j,1]
            red = frame[i,j,2]

            if blue==0 and red==0 and green==0:
                continue
            
            if red < minRed:
                minRed = red
                
            if red > maxRed:
                maxRed = red
                
            redGreenRange = int(red)-int(green)
            redBlueRange = int(red)-int(blue)
            
            if redGreenRange < minRedGreenRange:
                minRedGreenRange = redGreenRange

            if redGreenRange > maxRedGreenRange:
                maxRedGreenRange = redGreenRange

            if redBlueRange < minRedBlueRange:
                minRedBlueRange = redBlueRange

            if redBlueRange > maxRedBlueRange:
                maxRedBlueRange = redBlueRange

    #colour segmentation based on calculated thresholds
    for i in range(height):
        for j in range(width):
            blue = frame[i,j,0]
            green = frame[i,j,1]
            red = frame[i,j,2]
            
            redGreen = int(red)-int(green)
            redBlue = int(red)-int(blue)

            if red > minRed and red < maxRed and redGreen > minRedGreenRange and redGreen < maxRedGreenRange and redBlue > minRedBlueRange and redBlue < maxRedBlueRange:
                opImage[i,j] = 255
                #opImage[i,j,1] = 255
                #opImage[i,j,2] = 255
            else:
                opImage[i,j] = 0
                #opImage[i,j,1] = 0
                #opImage[i,j,2] = 0            
    
    #line segmentation
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, minLineLength, maxLineGap)

    
    if lines != None:
        for i in range(len(lines[0])):
            points=[0 for j in range(4)]

            if lines[0,i,0] < lines[0,i,2]:
                points[0] = (lines[0,i,0],0)
                points[1] = (lines[0,i,2],0)
                points[2] = (lines[0,i,2],lines[0,i,3])
                points[3] = (lines[0,i,0],lines[0,i,1])
            else:
                points[0] = (lines[0,i,2],0)
                points[1] = (lines[0,i,0],0)
                points[2] = (lines[0,i,0],lines[0,i,1])
                points[3] = (lines[0,i,2],lines[0,i,3])
            polyPoints = np.array([tuple(i) for i in points],np.int32)
            cv2.fillConvexPoly(edges, polyPoints, [0,0,0])
    
    cv2.imshow('output',opImage)
    cv2.imwrite('testImages/test'+str(var)+'.jpg',opImage)
    cv2.imwrite('originalImages/original'+str(var)+'.jpg',frame)
    var = var+1

    if cv2.waitKey(1) == 27:  ## 27 - ASCII for escape key
        break

cam.release()
cv2.waitKey(0)
cv2.destroyAllWindows()
