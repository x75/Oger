import Oger
import mdp
import pylab
import scipy as sp
import random

def loss_01_time(x,y):
    # This custom error function is used to optimize the regularization parameter of the ridge regression node below
    return Oger.utils.loss_01(sp.argmax(mdp.numx.atleast_2d(mdp.numx.mean(x, axis=0))),sp.argmax(mdp.numx.mean(y, axis=0)))

if __name__ == "__main__":

    n_subplots_x, n_subplots_y = 2, 1
    train_frac = .9

    [inputs, outputs] = Oger.datasets.analog_speech(indir="../datasets/Lyon_decimation_128")
    
    n_samples = len(inputs)
    n_train_samples = int(round(n_samples * train_frac))
    n_test_samples = int(round(n_samples * (1 - train_frac)))
    
    # Shuffle the data randomly
    data = zip(inputs, outputs)
    random.shuffle(data)
    inputs, outputs = zip(*data)
    
    input_dim = inputs[0].shape[1]

    # construct individual nodes
    reservoir = Oger.nodes.LeakyReservoirNode(input_dim=input_dim, output_dim=30, input_scaling=.1, leak_rate=1)
    readout = Oger.nodes.RidgeRegressionNode()
    
    flow = Oger.nodes.InspectableFlow([reservoir, readout])
    
    # Plot an example input to the reservoir 
    pylab.subplot(n_subplots_x, n_subplots_y, 1)
    pylab.imshow(inputs[0].T, aspect='auto', interpolation='nearest')
    pylab.title("Cochleogram (input to reservoir)")
    pylab.ylabel("Channel")
    
    
    print "Training..."
    flow.train([[], zip(inputs[0:n_train_samples], outputs[0:n_train_samples])])

    ytest = []

    print "Applying to testset..."
    for xtest in inputs[n_train_samples:]:
        ytest.append(flow(xtest))
        
    pylab.subplot(n_subplots_x, n_subplots_y, 2)
    pylab.plot(flow.inspect(reservoir))
    pylab.title("Sample reservoir states")
    pylab.xlabel("Timestep")
    pylab.ylabel("Activation")
     
    print "Error without optimization of regularization parameter: " + str(mdp.numx.mean([loss_01_time(sample,target) for (sample,target) in zip(ytest,outputs[n_train_samples:])]))
    
    
    #Create a new, untrained readout
    readout2 = Oger.nodes.RidgeRegressionNode()
    
    # Build a flow with the same reservoir as before 
    flow2 = Oger.nodes.InspectableFlow([reservoir, readout2])
    
    # Determine the range over which the regularization parameter should be optimized
    gridsearch_params = {readout:{'ridge_param':mdp.numx.concatenate((mdp.numx.array([0]),mdp.numx.power(10., mdp.numx.arange(-15, 0, .5))))}}
    cross_validate_function = Oger.evaluation.n_fold_random
    error_measure = loss_01_time
    n_folds = 5
    Oger.utils.optimize_parameters(Oger.nodes.RidgeRegressionNode, gridsearch_parameters=gridsearch_params, cross_validate_function=cross_validate_function, error_measure=error_measure, n_folds=5, progress = False)
 
    print "Training..."
    flow2.train([[], zip(inputs[0:n_train_samples], outputs[0:n_train_samples])])
    
    ytest = []
    print "Applying to testset..."
    for xtest in inputs[n_train_samples:]:
        ytest.append(flow2(xtest))
    print "Error with optimization of regularization parameter:" + str(mdp.numx.mean([loss_01_time(sample,target) for (sample,target) in zip(ytest,outputs[n_train_samples:])]))
    print readout2.ridge_param
    pylab.show()