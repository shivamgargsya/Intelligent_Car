"""Code read the inpur from camera filter the image using canny edge detection and co
lor segmentation and then feed it to the neural network"""
import cv2
import numpy as np
import time
import serial
import json
from network import Network
cam = cv2.VideoCapture(1)

cam.set(3,160)
cam.set(4,120)

ser = serial.Serial(
    port='COM7',
    baudrate=9600,
    timeout=0,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

def capture():
    var=1
    a='8 ' 
    #f=open('trainingData/controls8.txt','w')
    k=53
    #loading neural network
    net=load("network.txt")
    while var > 0:

        minRed = 127
        maxRed = 127
        minRedGreenRange = 127
        maxRedGreenRange = 127
        minRedBlueRange = 127
        maxRedBlueRange = 127

        minLineLength = 80
        maxLineGap = 20
        ret,frame = cam.read()
        height, width, channels = frame.shape
        opImage = np.zeros((height,width,1),np.uint8)

        #finding threshols for image segmentation
        for i in range(100,height):
            for j in range(70,width-70):
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
                else:
                    opImage[i,j] = 0
                    
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
                cv2.fillConvexPoly(opImage, polyPoints, [0,0,0])

        cv2.imshow('output',opImage)
        cv2.imshow('input',frame)
        resOutput = cv2.resize(opImage,(40,30),interpolation = cv2.INTER_AREA)
        img=resOutput
        k=cv2.waitKey(1)
        if k == 27: ## 27 - ASCII for escape key
             break
            #feeding image to neural network
        img=np.array(img)
        img=img.flatten()
        
        
        img=img.tolist()
        for k in range(len(img)):
            img[k]=(float(img[k])/255)
        img=np.array(img,dtype='float32')
        img=np.reshape(img, (1200, 1))
        a=int(np.argmax(feedforward(net,img)))
        if a == 4:
            ser.write("\x34")
        elif a == 6:
            ser.write("\x36")
        elif a==8:
            ser.write("\x38")
        elif a== 5:
            ser.write("\x35")
        elif a== 2:
            ser.write("\x32")
        #feed to the zigby
        print a
        
        
        '''
        if k == 53:
            ser.write("\x35")
        else:
            if a!='5 ':
                resOutput = cv2.resize(opImage,(40,30),interpolation = cv2.INTER_AREA)
                cv2.imwrite('testImages/test'+str(var)+'.jpg',resOutput)
                cv2.imwrite('originalImages/original'+str(var)+'.jpg',frame)     
                var = var+1
                if k == 27: ## 27 - ASCII for escape key
                    break        
                if k == 52:
                    ser.write("\x34")
                    a='4 '
                elif k == 56:
                    a='8 '
                    ser.write("\x38")
                elif k == 50:
                    a='2 '
                    ser.write("\x32")
                elif k == 54:
                    a='6 '
                    ser.write("\x36")
                f.write(a)

        '''
def load(filename):
    """Load a neural network from the file ``filename``.  Returns an
    instance of Network.

    """
    f = open(filename, "r")
    data = json.load(f)
    f.close()
   
    net = Network(data["sizes"])
    net.weights = [np.array(w) for w in data["weights"]]
    net.biases = [np.array(b) for b in data["biases"]]
    return net

def feedforward(net, a):
        """Return the output of the network if ``a`` is input."""
        for b, w in zip(net.biases, net.weights):
            a = sigmoid_vec(np.dot(w, a)+b)
        return a

#### Miscellaneous functions
def sigmoid(z):
    """The sigmoid function."""
    return 1.0/(1.0+np.exp(-z))

sigmoid_vec = np.vectorize(sigmoid)


#wait for the two threads to complete
if __name__=="__main__":
    capture()

cam.release()
cv2.destroyAllWindows()
    
