import sys
sys.path.insert(0, '..')
import theano
from theano import tensor as T
from theano.tensor import nnet
from theano.compile import module
from theano import printing, pprint
from theano import compile

import numpy as N


class LogisticRegressionN(module.FancyModule):
    class InstanceType(module.FancyModuleInstance):
        def initialize(self, n_in, n_out, seed = None):
            #self.component is the LogisticRegressionTemplate instance that built this guy.
            rng = N.random.RandomState(seed)
            
            self.w = rng.randn(n_in, n_out)
            self.b = rng.randn(n_out)
            self.lr = 0.01
            self.__hide__ = ['params']
        def __eq__(self, other):
            if not isinstance(other.component, LogisticRegressionN) and not isinstance(other.component, LogisticRegression2):
                raise NotImplemented
         #we compare the member.
            if (N.abs(self.w-other.w)<1e-8).all() and (N.abs(self.b-other.b)<1e-8).all() and self.lr == other.lr:
                return True
            return False
        def __hash__(self):
            raise NotImplemented

    def __init__(self, x = None, targ = None):
        super(LogisticRegressionN, self).__init__() #boilerplate

        self.x = x if x is not None else T.matrix()
        self.targ = targ if targ is not None else T.lvector()

        self.w = module.Member(T.matrix())   #automatically names
        self.b = module.Member(T.vector())   #automatically names
        self.lr = module.Member(T.dscalar()) #provides an external interface to change it
        #and makes it an implicit input to any Method you build.

        self.params = [self.w, self.b]

        xent, y = nnet.crossentropy_softmax_1hot(
                T.dot(self.x, self.w) + self.b, self.targ)
        xent = T.sum(xent)

        self.y = y
        self.xent = xent

        gparams = T.grad(xent, self.params)

        self.update = module.Method([self.x, self.targ], xent,
                updates = dict((p, p - self.lr * g) for p, g in zip(self.params, gparams)))
        self.apply = module.Method([self.x], T.argmax(T.dot(self.x, self.w) + self.b, axis=1))

class LogisticRegression2(module.FancyModule):
    class InstanceType(module.FancyModuleInstance):
        def initialize(self, n_in, seed = 1827):
            #self.component is the LogisticRegressionTemplate instance that built this guy.

            rng = N.random.RandomState(seed)
            
            self.w = rng.randn(n_in, 1)
            self.b = rng.randn(1)
            self.lr = 0.01
            self.__hide__ = ['params']
        def __eq__(self, other):
            if not isinstance(other.component, LogisticRegressionN) and not isinstance(other.component, LogisticRegression2):
                raise NotImplemented
         #we compare the member.
            if (N.abs(self.w-other.w)<1e-8).all() and (N.abs(self.b-other.b)<1e-8).all() and self.lr == other.lr:
                return True
            return False
        def __hash__(self):
            raise NotImplemented 

    def __init__(self, x = None, targ = None):
        super(LogisticRegression2, self).__init__() #boilerplate

        self.x = x if x is not None else T.matrix()
        self.targ = targ if targ is not None else T.lcol()

        self.w = module.Member(T.dmatrix())   #automatically names
        self.b = module.Member(T.dvector())   #automatically names
        self.lr = module.Member(T.dscalar()) #provides an external interface to change it
        #and makes it an implicit input to any Method you build.

        self.params = [self.w, self.b]

        y = nnet.sigmoid(T.dot(self.x, self.w))
        xent_elem = -self.targ * T.log(y) - (1.0 - self.targ) * T.log(1.0 - y)
        xent = T.sum(xent_elem)

        self.y = y
        self.xent_elem = xent_elem
        self.xent = xent

        gparams = T.grad(xent, self.params)

        self.update = module.Method([self.x, self.targ], xent,
                                    updates = dict((p, p - self.lr * g) for p, g in zip(self.params, gparams)))
        self.apply = module.Method([self.x], T.argmax(T.dot(self.x, self.w) + self.b, axis=1))
        


def main():
    pprint.assign(nnet.crossentropy_softmax_1hot_with_bias_dx, printing.FunctionPrinter('xsoftmaxdx'))
    pprint.assign(nnet.crossentropy_softmax_argmax_1hot_with_bias, printing.FunctionPrinter('nll', 'softmax', 'argmax'))
    if 1:
        lrc = LogisticRegressionN()

        print '================'
        print lrc.update.pretty()
        print '================'
        print lrc.update.pretty(mode = theano.Mode('py', 'fast_run'))
        print '================'
#         print lrc.update.pretty(mode = compile.FAST_RUN.excluding('inplace'))
#         print '================'

#        sys.exit(0)

        lr = lrc.make(10, 2, mode=theano.Mode('c|py', 'fast_run'))
        #lr = lrc.make(10, 2, mode=compile.FAST_RUN.excluding('fast_run'))
        #lr = lrc.make(10, 2, mode=theano.Mode('py', 'merge')) #'FAST_RUN')

        data_x = N.random.randn(5, 10)
        data_y = (N.random.randn(5) > 0)

        for i in xrange(10000):
            lr.lr = 0.02
            xe = lr.update(data_x, data_y) 
            if i % 100 == 0:
                print i, xe

        print
        print 'TRAINED MODEL:'
        print lr

    if 0:
        lrc = LogisticRegression2()

        lr = lrc.make(10, mode=theano.Mode('c|py', 'merge')) #'FAST_RUN')

        data_x = N.random.randn(5, 10)
        data_y = (N.random.randn(5, 1) > 0)

        for i in xrange(10000):
            xe = lr.update(data_x, data_y)
            if i % 100 == 0:
                print i, xe

        print
        print 'TRAINED MODEL:'
        print lr

if __name__ == '__main__':
    main()



