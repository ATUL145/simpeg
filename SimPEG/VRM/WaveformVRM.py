import numpy as np
import scipy.special as spec

###################################################
#           STEP OFF WAVEFORM
###################################################


class StepOff():

    """
Step-Off waveform for predicting VRM response.

INPUTS:

KWARGS:

t0: The start of the off-time (default is 0)
"""

    def __init__(self, t0=0.):

        self.t0 = t0

    def getCharDecay(self, fieldType, times):

        """
Characteristic decay function for step-off waveform. This function describes
the decay of the VRM response for the linear problem type. Note that the
current will be normalized by its maximum value. The maximum current in the
transmitter is specified in the source object.

INPUTS:

fieldType: must be 'dhdt' or 'dbdt'. Characteristic decay for 'h' or 'b' CANNOT
    be computed for step-off
times: Observation times. These times MUST be during the off-time.
        """

        assert fieldType in ["dhdt", "dbdt"], "For step-off, fieldType must be one of 'dhdt' or 'dbdt' and cannot be 'h' or 'b'"
        assert self.t0 < np.min(times), "Earliest time channel must be after beginning of off-time"

        t0 = self.t0

        if fieldType is "dbdt":
            mu0 = 4*np.pi*1e-7
            eta = -mu0/(times-t0)
        elif fieldType is "dhdt":
            eta = -1/(times-t0)

        return eta

    def getLogUniformDecay(self, fieldType, times, chi0, dchi, tau1, tau2):

        """
Decay function for a step-off waveform for log-uniform distribtuion of
time-relaxation constants. The output of this function is the magnetization
at each time for each cell, normalized by the inducing field.

INPUTS:

fieldType: must be 'h', 'b', 'dhdt' or 'dbdt'.
times: Observation times.
chi0: DC (zero-frequency) magnetic susceptibility
dchi: DC (zero-frequency) magnetic susceptibility attributed to VRM
tau1: Lower-bound for log-uniform distribution of time-relaxation constants
tau2: Upper-bound for log-uniform distribution of time-relaxation constants
        """

        assert fieldType in ["h", "dhdt", "b", "dbdt"], "For step-off, fieldType must be one of 'h', dhdt', 'b' or 'dbdt' "

        nT = len(times)
        nC = len(dchi)
        t0 = self.t0

        times = np.kron(np.ones((nC, 1)), times)
        chi0 = np.kron(np.reshape(chi0, newshape=(nC, 1)), np.ones((1, nT)))
        dchi = np.kron(np.reshape(dchi, newshape=(nC, 1)), np.ones((1, nT)))
        tau1 = np.kron(np.reshape(tau1, newshape=(nC, 1)), np.ones((1, nT)))
        tau2 = np.kron(np.reshape(tau2, newshape=(nC, 1)), np.ones((1, nT)))

        if fieldType is "h":
            eta = (
                0.5*(1-np.sign(times-t0))*chi0 +
                0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (spec.expi(-(times-t0)/tau2) - spec.expi(-(times-t0)/tau1))
                )
        elif fieldType is "b":
            mu0 = 4*np.pi*1e-7
            eta = (
                0.5*(1-np.sign(times-t0))*chi0 +
                0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (spec.expi(-(times-t0)/tau2) - spec.expi(-(times-t0)/tau1))
                )
            eta = mu0*eta
        elif fieldType is "dhdt":
            eta = (
                0. + 0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (np.exp(-(times-t0)/tau1)-np.exp(-(times-t0)/tau2))/(times-t0)
                )
        elif fieldType is "dbdt":
            mu0 = 4*np.pi*1e-7
            eta = (
                0. + 0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (np.exp(-(times-t0)/tau1)-np.exp(-(times-t0)/tau2))/(times-t0)
                )
            eta = mu0*eta

        return eta


###################################################
#           SQUARE PULSE WAVEFORM
###################################################


class SquarePulse():

    """
Square-pulse waveform for predicting VRM response.

INPUTS:

delt: Duration of the on-time (default is zero)

KWARGS:

t0: The start of the off-time
    """

    def __init__(self, delt, t0=0.):

        self.delt = delt
        self.t0 = t0

    def getCharDecay(self, fieldType, times):

        """
Characteristic decay function for a square-pulse waveform. This function
describes the decay of the VRM response for the linear problem type. Note that
the current will be normalized by its maximum value. The maximum current in the
transmitter is specified in the source object.

INPUTS:

fieldType: must be 'h', 'b', 'dhdt' or 'dbdt'.
times: Observation times. These times MUST be during the off-time.
        """

        assert fieldType in ["h", "dhdt", "b", "dbdt"], "For square-pulse, fieldType must be one of 'h', 'dhdt', 'b' or 'dbdt'"
        assert self.t0 < np.min(times), "Earliest time channel must be after beginning of off-time"

        t0 = self.t0
        delt = self.delt
        mu0 = 4*np.pi*1e-7

        if fieldType is "h":
            eta = np.log(1 + delt/(times-t0))
        elif fieldType is "b":
            eta = mu0*np.log(1 + delt/(times-t0))
        elif fieldType is "dhdt":
            eta = -(1/(times-t0) - 1/(times-t0+delt))
        elif fieldType is "dbdt":
            eta = -mu0*(1/(times-t0) - 1/(times-t0+delt))

        return eta

    def getLogUniformDecay(self, fieldType, times, chi0, dchi, tau1, tau2):

        """
Decay function for a square-pulse waveform for log-uniform distribtuion of
time-relaxation constants. The output of this function is the magnetization
at each time for each cell, normalized by the inducing field.

INPUTS:

fieldType: must be 'h', 'b', 'dhdt' or 'dbdt'.
times: Observation times.
chi0: DC (zero-frequency) magnetic susceptibility
dchi: DC (zero-frequency) magnetic susceptibility attributed to VRM
tau1: Lower-bound for log-uniform distribution of time-relaxation constants
tau2: Upper-bound for log-uniform distribution of time-relaxation constants
        """

        assert fieldType in ["h", "dhdt", "b", "dbdt"], "For step-off, fieldType must be one of 'h', dhdt', 'b' or 'dbdt' "

        nT = len(times)
        nC = len(dchi)
        t0 = self.t0
        delt = self.delt

        times = np.kron(np.ones((nC, 1)), times)
        chi0 = np.kron(np.reshape(chi0, newshape=(nC, 1)), np.ones((1, nT)))
        dchi = np.kron(np.reshape(dchi, newshape=(nC, 1)), np.ones((1, nT)))
        tau1 = np.kron(np.reshape(tau1, newshape=(nC, 1)), np.ones((1, nT)))
        tau2 = np.kron(np.reshape(tau2, newshape=(nC, 1)), np.ones((1, nT)))

        if fieldType is "h":
            eta = (
                (np.sign(times-t0+delt) - np.sign(times-t0))*(chi0 - dchi) +
                0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (spec.expi(-(times-t0)/tau2) -
                    spec.expi(-(times-t0)/tau1) -
                    spec.expi(-(times-t0+delt)/tau2) +
                    spec.expi(-(times-t0+delt)/tau1))
                )
        elif fieldType is "b":
            mu0 = 4*np.pi*1e-7
            eta = (
                (np.sign(times-t0+delt) - np.sign(times-t0))*(chi0 - dchi) +
                0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (spec.expi(-(times-t0)/tau2) -
                    spec.expi(-(times-t0)/tau1) -
                    spec.expi(-(times-t0+delt)/tau2) +
                    spec.expi(-(times-t0+delt)/tau1))
                )
            eta = mu0*eta
        elif fieldType is "dhdt":
            eta = (
                0. + 0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (np.exp(-(times-t0)/tau1) - np.exp(-(times-t0)/tau2))/(times-t0) -
                0.5*(1+np.sign(times-t0+delt))*(dchi/np.log(tau2/tau1)) *
                (np.exp(-(times-t0+delt)/tau1) - np.exp(-(times-t0+delt)/tau2))/(times-t0+delt)
                )
        elif fieldType is "dbdt":
            mu0 = 4*np.pi*1e-7
            eta = (
                0. + 0.5*(1+np.sign(times-t0))*(dchi/np.log(tau2/tau1)) *
                (np.exp(-(times-t0)/tau1) - np.exp(-(times-t0)/tau2))/(times-t0) -
                0.5*(1+np.sign(times-t0+delt))*(dchi/np.log(tau2/tau1)) *
                (np.exp(-(times-t0+delt)/tau1) - np.exp(-(times-t0+delt)/tau2))/(times-t0+delt)
                )
            eta = mu0*eta

        return eta

###################################################
#    ARBITRARY WAVEFORM UNIFORM DISCRETIZATION
###################################################


class ArbitraryDiscrete():

    """
Arbitrary waveform for predicting VRM response. This approach approximates the
waveform as a set of trapezoids with uniform width. The current is normalized
by its largest absolute value. The maximum current in the transmitter is
specified in the source object.

INPUTS:

t: Times for the waveform
I: Current for the waveform
    """

    def __init__(self, t, I):

        assert np.abs(I[0]) < 1e-10 and np.abs(I[-1]) < 1e-10, "Current at t0 and tmax should be 0"
        assert len(t) == len(I), "Time values and current values must have same length"

        self.t = t
        self.I = I

    def getCharDecay(self, fieldType, times):

        """
Characteristic decay function for arbitrary waveform. This function describes
the decay of the VRM response for the Linear problem type. Note that the
current will be LogUniformized by its maximum value. The maximum current in the
transmitter is specified in the source object.

INPUTS:

fieldType: must be 'h', 'b', 'dhdt' or 'dbdt'.
times: Observation times. These times must be during the off-time.
        """

        assert fieldType in ["h", "dhdt", "b", "dbdt"], "fieldType must be one of 'h', 'dhdt', 'b' or 'dbdt'"
        assert np.max(self.t) < np.min(times), "Earliest time channel must be after beginning of off-time"

        k = np.where(self.I > 1e-10)
        j = k[0][0]-1
        k = k[0][-1]+1

        twave = self.t[j:k+1]
        Iwave = self.I[j:k+1]/np.max(np.abs(self.I[j:k+1]))

        N = int(np.ceil(25*(np.max(twave)-np.min(twave))/np.min(times)))

        if N > 25000:
            N = 25000

        dt = (np.max(twave) - np.min(twave))/np.float64(N)
        tvec = np.linspace(np.min(twave), np.max(twave), N+1)

        g = np.r_[Iwave[0], np.interp(tvec[1:-1], twave, Iwave), Iwave[-1]]
        tvec = tvec[1:]

        eta = np.zeros(len(times))

        if fieldType in ["h", "b"]:
            for tt in range(0, len(eta)):
                eta[tt] = np.sum((g[1:] + (g[1:]-g[0:-1])*(times[tt]-tvec)/dt)*np.log(1 + dt/(times[tt] - tvec)) - g[1:] + g[0:-1])
        elif fieldType in ["dhdt", "dbdt"]:
            for tt in range(0, len(eta)):
                eta[tt] = np.sum((((g[1:]-g[0:-1])/dt)*np.log(1 + dt/(times[tt] - tvec)) - (g[1:] + (g[1:]-g[0:-1])*(times[tt]-tvec)/dt)*(1/(times[tt] - tvec + dt) - 1/(times[tt] - tvec))))

        if fieldType in ["b", "dbdt"]:
            mu0 = 4*np.pi*1e-7
            eta = mu0*eta

        return eta

###################################################
#    ARBITRARY WAVEFORM PIECEWISE DISCRETIZATION
###################################################


class ArbitraryPiecewise():

    """
Arbitrary waveform for predicting VRM response. This approach approximates the
waveform as a piecewise linear function. The user is encourage to discretize
the function more sparsely at the beginning of the function and more finely at
the end. The current is normalized by its largest absolute value. The maximum
current in the transmitter is specified in the source object.

INPUTS:

t: Times for the waveform
I: Current for the waveform
    """

    def __init__(self, t, I):

        assert np.abs(I[0]) < 1e-10 and np.abs(I[-1]) < 1e-10, "Current at t0 and tmax should be 0"
        assert len(t) == len(I), "Time values and current values must have same length"

        self.t = t
        self.I = I

    def getCharDecay(self, fieldType, times):

        """
Characteristic decay function for arbitrary waveform. This function describes
the decay of the VRM response for the Linear problem type. Note that the
current will be LogUniformized by its maximum value. The maximum current in the
transmitter is specified in the source object.

INPUTS:

fieldType: must be 'h', 'b', 'dhdt' or 'dbdt'.
times: Observation times. These times must be during the off-time.
        """

        assert fieldType in ["h", "dhdt", "b", "dbdt"], "fieldType must be one of 'h', 'dhdt', 'b' or 'dbdt'"
        assert np.max(self.t) < np.min(times), "Earliest time channel must be after beginning of off-time"

        k = np.where(self.I > 1e-10)
        j = k[0][0]-1
        k = k[0][-1]+1

        tvec = self.t[j:k+1]
        dt = tvec[1:] - tvec[0:-1]
        g = self.I[j:k+1]/np.max(np.abs(self.I[j:k+1]))
        tvec = tvec[1:]

        eta = np.zeros(len(times))

        if fieldType in ["h", "b"]:
            for tt in range(0, len(eta)):
                eta[tt] = np.sum((g[1:] + (g[1:]-g[0:-1])*(times[tt]-tvec)/dt)*np.log(1 + dt/(times[tt] - tvec)) - g[1:] + g[0:-1])
        elif fieldType in ["dhdt", "dbdt"]:
            for tt in range(0, len(eta)):
                eta[tt] = np.sum((((g[1:]-g[0:-1])/dt)*np.log(1 + dt/(times[tt] - tvec)) - (g[1:] + (g[1:]-g[0:-1])*(times[tt]-tvec)/dt)*(1/(times[tt] - tvec + dt) - 1/(times[tt] - tvec))))

        if fieldType in ["b", "dbdt"]:
            mu0 = 4*np.pi*1e-7
            eta = mu0*eta

        return eta

###################################################
#               CUSTOM DECAY
###################################################


class Custom():

    """
Custom decay. If you have the values of the decay at the observed times, it can
be set here to avoid recalculating for every source.

INPUTS:

t: observation times
eta: decay at observed times
    """

    def __init__(self, t, eta):

        assert len(t) == len(eta), "Observed times and decay values must be same length."

        self.t = t
        self.eta = eta

    def getCharDecay(self, fieldType, times):

        return self.eta
