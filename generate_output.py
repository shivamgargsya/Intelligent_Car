import numpy as np
import json
import cv2
from network import Network
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

def run():
    net=load("network.txt")
    #read data from cam into img and vectorize it
    s="testImages\\test"+str(900)+".jpg"
    img=cv2.imread(s,-1)
    cv2.imshow("out",img)
    img=np.array(img)
    img=img.flatten()
    
    
    img=img.tolist()
    for k in range(len(img)):
        img[k]=(float(img[k])/255)
    img=np.array(img,dtype='float32')
    img=np.reshape(img, (1200, 1))
    a=np.argmax(feedforward(net,img))
    #feed to the zigby
    print a
    if cv2.waitKey(0) == 27 :
        cam.release()
        cv2.destroyAllWindows()


if __name__=="__main__":
    run()
         
