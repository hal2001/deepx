import math
import theano.tensor as T
from theano.tensor.nnet.conv import conv2d
from theano.tensor.signal.downsample import max_pool_2d

from ..node import Node

class Conv(Node):
    def __init__(self, shape_in, shape_weights, stride=1, pool_factor=2, border_mode="full"):

        channels_out, channels_in, kernel_height, kernel_width = shape_weights

        h_in, w_in, d_in = shape_in
        if border_mode == "full":
            h_out = h_in + kernel_height - 1
            w_out = w_in + kernel_width - 1

        elif border_mode == "valid":
            h_out = h_in - kernel_height + 1
            w_out = w_in - kernel_width + 1
        else:
            raise Exception("Border mode must be {full, valid}.")

        h_out = math.ceil(h_out/2.)
        w_out = math.ceil(w_out/2.)

        shape_out = (h_out, w_out, channels_out)
        super(Conv, self).__init__(shape_in, shape_out)

        self.pool_factor = pool_factor
        self.W = self.init_parameter('W', shape_weights)
        self.b = self.init_parameter('b', channels_out)



    def rectify(self, X):
        return T.nnet.relu(X)

    def _forward(self, X):
        lin     = conv2d(X, self.W, border_mode='full') + self.b.dimshuffle('x', 0, 'x', 'x')
        act     = self.rectify(lin)
        pooled  = max_pool_2d(act, (self.pool_factor, self.pool_factor))
        return pooled
