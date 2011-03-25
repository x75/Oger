import Oger
import pylab
import scipy
from timeit import Timer

def test():

    """ This example demonstrates a very simple reservoir+readout setup on the 30th order NARMA task.
    """
    scipy.random.seed(1234)
    # Get the dataset
    [x, y] = Oger.datasets.narma30(sample_len=10000)

    # construct individual nodes
    #reservoir = Oger.nodes.ReservoirNode(output_dim=100, input_scaling=0.05)
    readout = Oger.nodes.RidgeRegressionNode()

    # build network with MDP framework
    flow = Oger.nodes.InspectableFlow([readout], verbose=1)

    data = [zip(x[0:-1], y[0:-1])]

    # train the flow 
    flow.train(data)

    #apply the trained flow to the training data and test data
    trainout = flow(x[0])
    testout = flow(x[-1])

    print "NRMSE: " + str(Oger.utils.nrmse(y[-1], testout))

#    nx = 4
#    ny = 1
#
#    #plot the input
#    pylab.subplot(nx, ny, 1)
#    pylab.plot(x[0])
#
#    #plot everything
#    pylab.subplot(nx, ny, 2)
#    pylab.plot(trainout, 'r')
#    pylab.plot(y[0], 'b')
#
#    pylab.subplot(nx, ny, 3)
#    pylab.plot(testout, 'r')
#    pylab.plot(y[-1], 'b')
#
#    pylab.subplot(nx, ny, 4)
#    pylab.plot(flow.inspect(reservoir))
#    pylab.show()

if __name__ == "__main__":
    t = Timer("test()", "from __main__ import test")
    print t.timeit(number=10)
