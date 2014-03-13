import numpy as np
import scipy.sparse as sp


def isScalar(f):
    scalarTypes = [float, int, long, np.float_, np.int_]
    if type(f) in scalarTypes:
        return True
    elif type(f) == np.ndarray and f.size == 1 and type(f[0]) in scalarTypes:
        return True
    return False

def mkvc(x, numDims=1):
    """Creates a vector with the number of dimension specified

    e.g.::

        a = np.array([1, 2, 3])

        mkvc(a, 1).shape
            > (3, )

        mkvc(a, 2).shape
            > (3, 1)

        mkvc(a, 3).shape
            > (3, 1, 1)

    """
    if type(x) == np.matrix:
        x = np.array(x)

    if hasattr(x, 'tovec'):
        x = x.tovec()

    assert type(x) == np.ndarray, "Vector must be a numpy array"

    if numDims == 1:
        return x.flatten(order='F')
    elif numDims == 2:
        return x.flatten(order='F')[:, np.newaxis]
    elif numDims == 3:
        return x.flatten(order='F')[:, np.newaxis, np.newaxis]

def sdiag(h):
    """Sparse diagonal matrix"""
    return sp.spdiags(mkvc(h), 0, h.size, h.size, format="csr")

def sdInv(M):
    "Inverse of a sparse diagonal matrix"
    return sdiag(1/M.diagonal())

def speye(n):
    """Sparse identity"""
    return sp.identity(n, format="csr")


def kron3(A, B, C):
    """Three kron prods"""
    return sp.kron(sp.kron(A, B), C, format="csr")


def spzeros(n1, n2):
    """spzeros"""
    return sp.coo_matrix((n1, n2)).tocsr()


def ddx(n):
    """Define 1D derivatives, inner, this means we go from n+1 to n"""
    return sp.spdiags((np.ones((n+1, 1))*[-1, 1]).T, [0, 1], n, n+1, format="csr")


def av(n):
    """Define 1D averaging operator from nodes to cell-centers."""
    return sp.spdiags((0.5*np.ones((n+1, 1))*[1, 1]).T, [0, 1], n, n+1, format="csr")

def avExtrap(n):
    """Define 1D averaging operator from cell-centers to nodes."""
    Av = sp.spdiags((0.5*np.ones((n, 1))*[1, 1]).T, [-1, 0], n+1, n, format="csr") + sp.csr_matrix(([0.5,0.5],([0,n],[0,n-1])),shape=(n+1,n))
    return Av

def ndgrid(*args, **kwargs):
    """
    Form tensorial grid for 1, 2, or 3 dimensions.

    Returns as column vectors by default.

    To return as matrix input:

        ndgrid(..., vector=False)

    The inputs can be a list or separate arguments.

    e.g.::

        a = np.array([1, 2, 3])
        b = np.array([1, 2])

        XY = ndgrid(a, b)
            > [[1 1]
               [2 1]
               [3 1]
               [1 2]
               [2 2]
               [3 2]]

        X, Y = ndgrid(a, b, vector=False)
            > X = [[1 1]
                   [2 2]
                   [3 3]]
            > Y = [[1 2]
                   [1 2]
                   [1 2]]

    """

    # Read the keyword arguments, and only accept a vector=True/False
    vector = kwargs.pop('vector', True)
    assert type(vector) == bool, "'vector' keyword must be a bool"
    assert len(kwargs) == 0, "Only 'vector' keyword accepted"

    # you can either pass a list [x1, x2, x3] or each seperately
    if type(args[0]) == list:
        xin = args[0]
    else:
        xin = args

    # Each vector needs to be a numpy array
    assert np.all([type(x) == np.ndarray for x in xin]), "All vectors must be numpy arrays."

    if len(xin) == 1:
        return xin[0]
    elif len(xin) == 2:
        XY = np.broadcast_arrays(mkvc(xin[1], 1), mkvc(xin[0], 2))
        if vector:
            X2, X1 = [mkvc(x) for x in XY]
            return np.c_[X1, X2]
        else:
            return XY[1], XY[0]
    elif len(xin) == 3:
        XYZ = np.broadcast_arrays(mkvc(xin[2], 1), mkvc(xin[1], 2), mkvc(xin[0], 3))
        if vector:
            X3, X2, X1 = [mkvc(x) for x in XYZ]
            return np.c_[X1, X2, X3]
        else:
            return XYZ[2], XYZ[1], XYZ[0]


def ind2sub(shape, inds):
    """From the given shape, returns the subscripts of the given index"""
    if type(inds) is not np.ndarray:
        inds = np.array(inds)
    assert len(inds.shape) == 1, 'Indexing must be done as a 1D row vector, e.g. [3,6,6,...]'
    return np.unravel_index(inds, shape, order='F')


def sub2ind(shape, subs):
    """From the given shape, returns the index of the given subscript"""
    if type(subs) is not np.ndarray:
        subs = np.array(subs)
    if len(subs.shape) == 1:
        subs = subs[np.newaxis,:]
    assert subs.shape[1] == len(shape), 'Indexing must be done as a column vectors. e.g. [[3,6],[6,2],...]'
    inds = np.ravel_multi_index(subs.T, shape, order='F')
    return mkvc(inds)


def getSubArray(A, ind):
    """subArray"""
    assert type(ind) == list, "ind must be a list of vectors"
    assert len(A.shape) == len(ind), "ind must have the same length as the dimension of A"

    if len(A.shape) == 2:
        return A[ind[0], :][:, ind[1]]
    elif len(A.shape) == 3:
        return A[ind[0], :, :][:, ind[1], :][:, :, ind[2]]
    else:
        raise Exception("getSubArray does not support dimension asked.")


def inv3X3BlockDiagonal(a11, a12, a13, a21, a22, a23, a31, a32, a33, returnMatrix=True):
    """ B = inv3X3BlockDiagonal(a11, a12, a13, a21, a22, a23, a31, a32, a33)

    inverts a stack of 3x3 matrices

    Input:
     A   - a11, a12, a13, a21, a22, a23, a31, a32, a33

    Output:
     B   - inverse
     """

    a11 = mkvc(a11)
    a12 = mkvc(a12)
    a13 = mkvc(a13)
    a21 = mkvc(a21)
    a22 = mkvc(a22)
    a23 = mkvc(a23)
    a31 = mkvc(a31)
    a32 = mkvc(a32)
    a33 = mkvc(a33)

    detA = a31*a12*a23 - a31*a13*a22 - a21*a12*a33 + a21*a13*a32 + a11*a22*a33 - a11*a23*a32

    b11 = +(a22*a33 - a23*a32)/detA
    b12 = -(a12*a33 - a13*a32)/detA
    b13 = +(a12*a23 - a13*a22)/detA

    b21 = +(a31*a23 - a21*a33)/detA
    b22 = -(a31*a13 - a11*a33)/detA
    b23 = +(a21*a13 - a11*a23)/detA

    b31 = -(a31*a22 - a21*a32)/detA
    b32 = +(a31*a12 - a11*a32)/detA
    b33 = -(a21*a12 - a11*a22)/detA

    if not returnMatrix:
        return b11, b12, b13, b21, b22, b23, b31, b32, b33

    return sp.vstack((sp.hstack((sdiag(b11), sdiag(b12),  sdiag(b13))),
                      sp.hstack((sdiag(b21), sdiag(b22),  sdiag(b23))),
                      sp.hstack((sdiag(b31), sdiag(b32),  sdiag(b33)))))



def inv2X2BlockDiagonal(a11, a12, a21, a22, returnMatrix=True):
    """ B = inv2X2BlockDiagonal(a11, a12, a21, a22)

    Inverts a stack of 2x2 matrices by using the inversion formula

    inv(A) = (1/det(A)) * cof(A)^T

    Input:
    A   - a11, a12, a21, a22

    Output:
    B   - inverse
    """

    a11 = mkvc(a11)
    a12 = mkvc(a12)
    a21 = mkvc(a21)
    a22 = mkvc(a22)

    # compute inverse of the determinant.
    detAinv = 1./(a11*a22 - a21*a12)

    b11 = +detAinv*a22
    b12 = -detAinv*a12
    b21 = -detAinv*a21
    b22 = +detAinv*a11

    if not returnMatrix:
        return b11, b12, b21, b22

    return sp.vstack((sp.hstack((sdiag(b11), sdiag(b12))),
                      sp.hstack((sdiag(b21), sdiag(b22)))))

def makePropertyTensor(M, sigma):
    if sigma is None:  # default is ones
        sigma = np.ones(M.nC)

    if isScalar(sigma):
        sigma = sigma * np.ones(M.nC)

    if M.dim == 1:
        if sigma.size == M.nC:  # Isotropic!
            sigma = mkvc(sigma)  # ensure it is a vector.
            Sigma = sdiag(sigma)
        else:
            raise Exception('Unexpected shape of sigma')
    elif M.dim == 2:
        if sigma.size == M.nC:  # Isotropic!
            sigma = mkvc(sigma)  # ensure it is a vector.
            Sigma = sdiag(np.r_[sigma, sigma])
        elif sigma.size == M.nC*2:  # Diagonal tensor
            sigma = sigma.reshape((M.nC,2), order='F')
            Sigma = sdiag(np.r_[sigma[:, 0], sigma[:, 1]])
        elif sigma.size == M.nC*3:  # Fully anisotropic
            sigma = sigma.reshape((M.nC,3), order='F')
            row1 = sp.hstack((sdiag(sigma[:, 0]), sdiag(sigma[:, 2])))
            row2 = sp.hstack((sdiag(sigma[:, 2]), sdiag(sigma[:, 1])))
            Sigma = sp.vstack((row1, row2))
        else:
            raise Exception('Unexpected shape of sigma')
    elif M.dim == 3:
        if sigma.size == M.nC:  # Isotropic!
            sigma = mkvc(sigma)  # ensure it is a vector.
            Sigma = sdiag(np.r_[sigma, sigma, sigma])
        elif sigma.size == M.nC*3:  # Diagonal tensor
            sigma = sigma.reshape((M.nC,3), order='F')
            Sigma = sdiag(np.r_[sigma[:, 0], sigma[:, 1], sigma[:, 2]])
        elif sigma.size == M.nC*6:  # Fully anisotropic
            sigma = sigma.reshape((M.nC,6), order='F')
            row1 = sp.hstack((sdiag(sigma[:, 0]), sdiag(sigma[:, 3]), sdiag(sigma[:, 4])))
            row2 = sp.hstack((sdiag(sigma[:, 3]), sdiag(sigma[:, 1]), sdiag(sigma[:, 5])))
            row3 = sp.hstack((sdiag(sigma[:, 4]), sdiag(sigma[:, 5]), sdiag(sigma[:, 2])))
            Sigma = sp.vstack((row1, row2, row3))
        else:
            raise Exception('Unexpected shape of sigma')

    return Sigma


def invPropertyTensor(M, tensor, returnMatrix=False):

    T = None

    if isScalar(tensor):
        T = 1./tensor

    elif tensor.size == M.nC:  # Isotropic!
        T = 1./mkvc(tensor)  # ensure it is a vector.

    elif M.dim == 2:
        if tensor.size == M.nC*2:  # Diagonal tensor
            T = 1./tensor
        elif tensor.size == M.nC*3:  # Fully anisotropic
            tensor = tensor.reshape((M.nC,3), order='F')
            B = inv2X2BlockDiagonal(tensor[:,0], tensor[:,2],
                                    tensor[:,2], tensor[:,1],
                                    returnMatrix=False)
            b11, b12, b21, b22 = B
            T = np.r_[b11, b22, b12]
    elif M.dim == 3:
        if tensor.size == M.nC*3:  # Diagonal tensor
            T = 1./tensor
        elif tensor.size == M.nC*6:  # Fully anisotropic
            tensor = tensor.reshape((M.nC,6), order='F')
            B = inv3X3BlockDiagonal(tensor[:,0], tensor[:,3], tensor[:,4],
                                    tensor[:,3], tensor[:,1], tensor[:,5],
                                    tensor[:,4], tensor[:,5], tensor[:,2],
                                    returnMatrix=False)
            b11, b12, b13, b21, b22, b23, b31, b32, b33 = B
            T = np.r_[b11, b22, b33, b12, b13, b23]

    if T is None:
        raise Exception('Unexpected shape of tensor')

    if returnMatrix:
        return makePropertyTensor(M, T)

    return T