import mdp
import collections

def mackey_glass(sample_len=1000, tau=17):
    '''
    mackey_glass(sample_len=1000, tau=17) -> input
    Generate the Mackey Glass time-series. Parameters are:
        - sample_len: length of the time-series in timesteps
        - tau: delay of the MG - system. Commonly used values are tau=17 (mild 
          chaos) and tau=30 (moderate chaos) 
    '''
    delta_t = 10
    history_len = tau * delta_t 
    # Initial conditions for the history of the system
    timeseries = 1.2
    history = collections.deque(1.2 * mdp.numx.ones(history_len) + 0.2 * \
                                (mdp.numx.random.rand(history_len) - 0.5))
    # Preallocate the array for the time-series
    inp = mdp.numx.zeros([sample_len])
    
    for timestep in range(sample_len):
        for _ in range(delta_t):
            xtau = history.popleft()
            history.append(timeseries)
            timeseries = history[-1] + (0.2 * xtau / (1.0 + xtau ** 10) - \
                         0.1 * history[-1]) / delta_t
        inp[timestep] = timeseries
    
    # Squash timeseries through tanh
    inp = mdp.numx.tanh(inp - 1)
    inp.shape = (-1, 1)
    return [inp, ]

def mso(sample_len=1000):
    '''
    mso(sample_len=1000) -> input
    Generate the Multiple Sinewave Oscillator time-series, a sum of two sines
    with incommensurable periods. Parameters are:
        - sample_len: length of the time-series in timesteps
         
    '''
    x = mdp.numx.arange(0, sample_len, 1)
    x.shape += (1,)
    signal = mdp.numx.sin(0.2 * x) + mdp.numx.sin(0.311 * x) 
    return [signal, ]

def lorentz(sample_len=1000, sigma=10, rho=28, beta=8/3, step=0.01):
    """This function generates a Lorentz time series of length sample_len,
    with standard parameters sigma, rho and beta. 
    """

    x = mdp.numx.zeros([sample_len])
    y = mdp.numx.zeros([sample_len])
    z = mdp.numx.zeros([sample_len])

    # Initial conditions taken from 'Chaos and Time Series Analysis', J. Sprott
    x[0] = 0;
    y[0] = -0.01;
    z[0] = 9;

    for t in range(sample_len-1):
        x[t+1] = x[t] + sigma*(y[t]-x[t])*step
        y[t+1] = y[t] + (x[t]*(rho-z[t]) - y[t])*step
        z[t+1] = z[t] + (x[t]*y[t] - beta*z[t])*step

    x.shape += (1,)
    y.shape += (1,)
    z.shape += (1,)

    return [mdp.numx.concatenate((x,y,z),axis=1),]