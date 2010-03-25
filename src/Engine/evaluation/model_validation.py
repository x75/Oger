'''
Created on Aug 25, 2009

@author: dvrstrae
'''
import mdp

def train_test_only(n_samples, training_fraction):
    '''
    train_test_only(n_samples, training_fraction) -> train_indices, test_indices
    
    Return indices to do simple training and testing. Only one fold is created, using training_fraction of the dataset for training and the rest for testing.
    The samples are selected randomly.
    Two lists are returned, with 1 element each.
    - train_indices contains the indices of the dataset used for training
    - test_indices contains the indices of the dataset used for testing
    '''
    # Shuffle the samples
    randperm = mdp.numx.random.permutation(n_samples)
    # Take a fraction training_fraction for training
    train_indices = [randperm[0:int(round(n_samples * training_fraction))]]
    # Use the rest for testing
    test_indices = mdp.numx.array([mdp.numx.setdiff1d(randperm, train_indices[-1])])
    return train_indices, test_indices


def leave_one_out(n_samples):
    '''
    leave_one_out(n_samples) -> train_indices, test_indices
    
    Return indices to do leave-one-out cross-validation. Per fold, one example is used for testing and the rest for training.
    Two lists are returned, with n_samples elements each.
    - train_indices contains the indices of the dataset used for training
    - test_indices contains the indices of the dataset used for testing
    '''
    train_indices, test_indices = [], []
    all_samples = range(n_samples)
    # Loop over all sample indices, using each one for testing once
    for test_index in all_samples:
        test_indices.append(mdp.numx.array([test_index]))
        train_indices.append(mdp.numx.setdiff1d(all_samples, [test_index]))
    return train_indices, test_indices


def n_fold_random(n_samples, n_folds):
    '''
    n_fold_random(n_samples, n_folds) -> train_indices, test_indices
    
    Return indices to do random n_fold cross_validation. Two lists are returned, with n_folds elements each.
    - train_indices contains the indices of the dataset used for training
    - test_indices contains the indices of the dataset used for testing
    '''
    # Create random permutation of number of samples
    randperm = mdp.numx.random.permutation(n_samples)
    train_indices, test_indices = [], []
    foldsize = mdp.numx.ceil(float(n_samples) / n_folds)
    
    for fold in range(n_folds):
        # Select the sample indices used for testing
        test_indices.append(randperm[fold * foldsize:foldsize * (fold + 1)])
        # Select the rest for training
        train_indices.append(mdp.numx.array(mdp.numx.setdiff1d(randperm, test_indices[-1])))
    return train_indices, test_indices
    

def validate(data, flow, error_measure, cross_validate_function=n_fold_random, *args, **kwargs):
    '''
    validate(data, flow, error_measure, cross_validate_function=n_fold_random *args, **kwargs)
    
    Perform  cross-validation on a flow, return the validation test_error for each fold.
    - inputs and outputs are lists of arrays
    - flow is an mdp.Flow
    - error_measure is a function which should return a scalar
    - cross_validate_function is a function which determines the type of cross-validation
      Possible values are:
          - n_fold_random (default): split dataset in n_folds parts, for each fold train on n_folds-1 parts and test on the remainder
          - leave_one_out : do cross-validation with len(inputs) folds, using a single sample for testing in each fold and the rest for training
          - train_test_only : divide dataset into train- and testset, using training_fraction as the fraction of samples used for training
    
    '''
    test_error = []
    # Get the number of samples 
    n_samples = len(data[1])
    # Get the indices of the training and testing samples for each fold by calling the 
    # cross_validate_function hook
    train_samples, test_samples = cross_validate_function(n_samples, *args, **kwargs)
    print "Performing cross-validation using " + cross_validate_function.__name__
    for fold in mdp.utils.progressinfo(range(len(train_samples)), style='timer'):
        # Get the training data from the whole data set
        train_data = data_subset(data, train_samples[fold])
        # Empty list to store test errors for current fold
        fold_error = []
        # Copy the flownode so we can re-train it for every fold
        f_copy = flow.copy()
        # train on all training samples
        f_copy.train(train_data)
        # test on all test samples
        for index in test_samples[fold]:
            test_data = data_subset(data, index)
            fold_error.append(error_measure(f_copy(test_data[0]), test_data[-1][-1]))
        test_error.append(mdp.numx.mean(fold_error))
    return test_error

def data_subset(data, data_indices):
    '''
    Return a subset of the examples in data given by data_indices.
    Data_indices can be a slice, a list of scalars or a numpy array.
    '''
    n_nodes = len(data)
    subset = []
    #print data_indices
    #reprint type(data_indices)
    for node in range(n_nodes):
        if isinstance(data_indices, slice) or isinstance(data_indices, int):
            subset.append(data[node].__getitem__(data_indices))
        else:
            tmp_data = []
            for data_index in data_indices:
                tmp_data.append(data[node][data_index])
            subset.append(tmp_data)
        #else:
        #r    subset.append([data[node].__getitem__(data_indices)])
    return subset