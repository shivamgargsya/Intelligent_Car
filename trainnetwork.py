#### Libraries
# My libraries
import mnist_loader
from network import Network
"""used to train network from the data and save it to the network.txt"""

def trainnetwork():
     
     training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
     
     network= Network([1200,30,10])
     network.SGD(training_data,30,10,.5,test_data=test_data)
     network.save("network.txt")
     
if __name__ == "__main__":
    trainnetwork()

