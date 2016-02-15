import math

from .. import backend as T

from ..node import Node
from .full import Relu

class Convolution(Node):
    def __init__(self, shape_in, kernel=None, border_mode="same"):
        super(Convolution, self).__init__()

        self.shape_in, self.kernel = shape_in, kernel

        if kernel is None:
            self.shape_weights = shape_in
        else:
            self.shape_in = shape_in
            self.shape_weights = kernel

        self.border_mode = border_mode

    def copy(self, keep_parameters=False):
        node = self.__class__(self.shape_in, kernel=self.kernel, border_mode=self.border_mode)
        if keep_parameters:
            node.parameters = self.parameters
        return node

    def initialize(self):
        channels_out, kernel_height, kernel_width = self.shape_weights
        self.W = self.init_parameter('W', (channels_out, self.channels_in, kernel_height, kernel_width))
        self.b = self.init_parameter('b', channels_out)

    def _infer(self, shape_in):
        self.channels_in = shape_in[0]
        channels_out, kernel_height, kernel_width = self.shape_weights
        d_in, h_in, w_in = shape_in
        if self.border_mode == "same":
            h_out = h_in
            w_out = w_in
        elif self.border_mode == "valid":
            h_out = h_in - kernel_height + 1
            w_out = w_in - kernel_width + 1
        else:
            raise Exception("Border mode must be {same, valid}.")
        return channels_out, h_out, w_out

    def rectify(self, X):
        return T.relu(X)

    def _forward(self, X):
        return (T.conv2d(X, self.W, border_mode=self.border_mode)
                + T.expand_dims(T.expand_dims(T.expand_dims(self.b, 0), 2), 3))

class Pool(Node):

    def __init__(self, kernel=(2, 2), stride=2, pool_type='max'):
        super(Pool, self).__init__()
        self.kernel = kernel
        self.stride = stride
        self.pool_type = pool_type

    def _infer(self, shape_in):
        channels_in, h_in, w_in = shape_in
        k_h, k_w = self.kernel
        return (
            channels_in,
            int(math.ceil(h_in/float(k_h))),
            int(math.ceil(w_in/float(k_w))),
        )

    def _forward(self, X):
        return T.pool2d(X, self.kernel, strides=(self.stride, self.stride))

    def copy(self, keep_parameters=False):
        node = self.__class__(kernel=self.kernel, stride=self.stride, pool_type=self.pool_type)
        if keep_parameters:
            node.parameters = self.parameters
        return node

def Conv(conv_kernel, pool_kernel=(2, 2), pool_stride=2, border_mode='same', pool_type='max', activation=Relu):
    return Convolution(conv_kernel, border_mode=border_mode) >> activation() >> Pool(kernel=pool_kernel, stride=pool_stride)
