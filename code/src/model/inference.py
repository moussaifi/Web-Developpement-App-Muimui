from fastai.vision import *
from warnings import filterwarnings
# from io import BytesIO
import numpy as np
import cv2
from PIL import Image
import torch
from torch.autograd import Variable
from torchvision import transforms
from annoy import AnnoyIndex
from PIL import ImageFile
from person_detect import get_person
ImageFile.LOAD_TRUNCATED_IMAGES = True


filterwarnings('ignore')
scaler = transforms.Resize((512, 512))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
to_tensor = transforms.ToTensor()

# number of classes in partial kaggle train set was 228
sz = 512
emb_size = 512
data = ImageDataBunch.single_from_classes('../', range(228), size=sz
                                          ).normalize(imagenet_stats)

learn = cnn_learner(data, models.resnet34)
learn.load('stage-1')
learn.model.eval()
layer = learn.model._modules.get('1')._modules.get('5')


def pil2cv(im):
    """Converts image data"""
    return np.asarray(im)


def im_squared(im, col=[255, 255, 255]):
    """makes the image square"""
    v, h = im.shape[0], im.shape[1]
    diff = abs(h - v)
    pad = int(diff / 2)
    if v > h:
        return cv2.copyMakeBorder(im, 0, 0, pad, pad,
                                  cv2.BORDER_CONSTANT, value=col)
    else:
        return cv2.copyMakeBorder(im, pad, pad, 0, 0,
                                  cv2.BORDER_CONSTANT, value=col)


def resize(im, new_height=None, new_width=None, scale=0.5):
    """resizes images"""
    r, c, _ = im.shape

    if new_height is None and new_width is None and scale is not None:
        # keeping the same aspect ratio as original
        new_height = int(scale * r)
        new_width = int(scale * c)
    elif new_height is None and new_width is not None:
        # use the scale based on old and new width
        scale = float(new_width) / float(c)
        new_height = int(scale * r)
    elif new_height is not None and new_width is None:
        # use the scale based on old and new height
        scale = float(new_height) / float(r)
        new_width = int(scale * c)
    elif new_height is not None and new_width is not None:
        # just use the new height and old height
        pass
    else:
        return None

    imr = cv2.resize(im, (new_width, new_height))
    return imr


def get_vector(fpath):
    """gets vector of the image"""
    # img = Image.open(BytesIO(binary_data))
    img = Image.open(fpath)
    h, w = img.size
    if h != sz or w != sz:
        img = pil2cv(img)
        img = get_person(img)
        img = im_squared(img)
        img = resize(img, sz, sz)
        img = Image.fromarray(img)
        img.save(fpath + '.jpg')

    t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
    my_embedding = torch.zeros((1, 512))

    def copy_data(m, i, o):
        """copy embeddings"""
        my_embedding.copy_(o.data)

    h = layer.register_forward_hook(copy_data)
    learn.model(t_img)
    h.remove()

    return my_embedding


t = AnnoyIndex(emb_size)
t.load('../prod.ann')


def get_nn(fpath):
    """returns list of integer indexes"""
    # returns list of integer indexes
    emb = get_vector(fpath)
    return t.get_nns_by_vector(emb[0], 5, search_k=10)
