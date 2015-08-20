import numpy as np
from numpy.testing import assert_array_almost_equal, assert_allclose
from nose.tools import assert_raises

from fatiando.seismic import conv


def test_density_matrix_input():
    "rho default and rho matrix=1, result the same"
    #model parameters
    n_samples, n_traces = [600, 500]
    rock_grid = 1500.*np.ones((n_samples, n_traces))
    rock_grid[300:,:] = 2500.
    #synthetic calculation for rho as int
    [vel_l_int, rho_l_int] = conv.depth_2_time(rock_grid, dt=2.e-3)
    rc_int=conv.reflectivity(vel_l_int,rho_l_int)
    synt_int = conv.convolutional_model(rc_int, 30., conv.rickerwave)
    #synthetic calculation for rho as matrix
    [vel_l_mat,rho_l_mat] = conv.depth_2_time(rock_grid, dt=2.e-3,
                                        rho=1.*np.ones((n_samples, n_traces)))
    rc_mat=conv.reflectivity(vel_l_mat,rho_l_mat)
    synt_mat = conv.convolutional_model(rc_mat, 30., conv.rickerwave) 
                                                
    assert_array_almost_equal(synt_int, synt_mat, 9)

def test_impulse_response():
    """
    conv.convolutional_model raises the source wavelet as result when the model
    is a centred spike, considering the dimension of the model equal to the 
    source wavelet
    """
    w=conv.rickerwave(30., 2.e-3)
    rc_test=np.zeros((w.shape[0], 20))
    rc_test[w.shape[0]/2,:]=1
    spike=conv.convolutional_model(rc_test, 30., conv.rickerwave)
    for j in range(0,rc_test.shape[1]):
        assert_array_almost_equal(spike[:,j], w, 9)

def test_rc_shorter_than_wavelet():
    """
    When the reflectivity series is shorter than the wavelength, the spike
    response is observed like in the opposite case. The difference is that the
    the ricker wavelet (or other symmetric wavelet) is shorter in the result.
    """
    w=conv.rickerwave(30., 2.e-3)
    rc_test=np.zeros((21, 20))
    rc_test[rc_test.shape[0]/2,:]=1
    spike=conv.convolutional_model(rc_test, 30., conv.rickerwave)
    for j in range(0,rc_test.shape[1]):
        assert_array_almost_equal(spike[:,j], 
    w[(w.shape[0]-rc_test.shape[0])/2:-(w.shape[0]-rc_test.shape[0])/2], 9)

def test_reflectivity_wrong_dimensions():
    """
    If velocity and density are provided as matrix to reflectivity calculation,
    conv.reflectivity they must have the same dimension.
    """
    vel=np.ones((10,10))
    dens=np.ones((11,11))
    assert_raises(ValueError, conv.reflectivity, vel, dens)
    dt=2.e-3    
    dz=1. 
    assert_raises(ValueError, conv.depth_2_time, vel, dt, dz, dens)

def test_ricker():
    """
    conv.rickerwave inputs must satisfy the condition for sampling and 
    stability, otherwise this implies in a error. 
    """
    f=50.
    dt=2.e-3
    assert_raises(AssertionError, conv.rickerwave, f, dt)


