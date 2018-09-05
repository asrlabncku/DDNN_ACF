import os
from chainer_sequential.chain_view import Chain
import chainer
import chainer.serializers as S
from chainer_sequential.sequential_view import Sequential
from chainer_sequential.function import *
from chainer_sequential.link import *
from chainer_sequential.binary_link import *
from chainer import functions as F
from chainer import training
from chainer.training import extensions
from chainer.training.triggers import IntervalTrigger

print("Model define Start ! ")

folder = "models/test_cifar10"

nfilters_embeded = int(64)
nlayers_embeded = int(4)
nfilters_cloud = int(64)
nlayers_cloud = int(4)
branchweight = float(0.1)
lr = numpy.float64(0.001)
nepochs = int(80)
ent_T = numpy.float64(0.4)
name = str("cifar10_64f_4l")

input_dims = 3
output_dims = 10

model = Sequential()
for i in range(nlayers_embeded):
    if i == 0:
        nfilters = input_dims
        model.add(ConvPoolBNBST(nfilters, nfilters_embeded, 3, 1, 1, 3, 1, 1))
    else:
        nfilters = nfilters_embeded
        model.add(BinaryConvPoolBNBST(nfilters, nfilters_embeded, 3, 1, 1, 3, 1, 1))

branch = Sequential()
branch.add(BinaryLinearBNSoftmax(None, output_dims))
model.add(branch)

for i in range(nlayers_cloud):
    if i == 0:
        nfilters = nfilters_embeded
    else:
        nfilters = nfilters_cloud
    model.add(Convolution2D(nfilters, nfilters_cloud, 3, 1, 1))
    model.add(BatchNormalization(nfilters_cloud))
    model.add(Activation('relu'))
    model.add(max_pooling_2d(3,1,1))
model.add(Linear(None, output_dims))
model.build()

chain = Chain(branchweight=branchweight, ent_T=ent_T)
chain.add_sequence(model)
chain.setup_optimizers('adam', lr)

print("Model define Over ! ")

##################################Skip the training ##################################################

##################################Load the model after training by other code #########################

print("Loading model Start ! ")
#name = self.get_name(**kwargs)
#path = '{}/{}'.format(self.folder,name)
#epoch = int(kwargs.get("nepochs",2))
#fn = "{}/chain_snapshot_epoch_{:06}".format(path,epoch)
fn = "models/test_cifar10/cifar10_64f_4l/chain_snapshot_epoch_000080"

S.load_npz(fn, chain)

print("Loading model Over ! ")

##################################   Inference the model after loading ##################################

print("Inference the model from load Start ! ")

trainset, testset = chainer.datasets.get_cifar10(ndim=3)
subtestset = chainer.datasets.SubDataset(testset,0,10000)
test_iter = chainer.iterators.SerialIterator(subtestset, 1,repeat=False, shuffle=False)
chain.train = False
chain.test = True
chain.to_gpu(0)
result = extensions.Evaluator(test_iter, chain, device=0)()


#a = chain.evaluate(testset[0][0],testset[0][1])




print("Inference the model from load Over ! ")

for key, value in result.iteritems() :
    print key, value

################################## Gen Code from the model after loading #################################

#print("Gen Code Start ! ")

#save_file = "mnist_inference_4f3l.h"
#in_shape = (1,28,28)
#c_code = model.generate_c(in_shape)
#save_dir = os.path.join(os.path.split(save_file)[:-1])[0]
#if not os.path.exists(save_dir) and save_dir != '':
#    os.makedirs(save_dir)

#with open(save_file, 'w+') as fp:
#    fp.write(c_code)

#print("Gen Code Over ! ")












