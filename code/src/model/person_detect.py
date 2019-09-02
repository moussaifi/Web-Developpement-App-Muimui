from imutils.object_detection import non_max_suppression
import numpy as np
import imutils
import cv2

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

BLUR = 21
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 200
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10
MASK_COLOR = (1.0,1.0,1.0) # In BGR format


def HogDescriptor(image):

    image = imutils.resize(image, width=min(400, image.shape[1]))
    orig = image.copy()

    (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
                                            padding=(8, 8), scale=1.05)

    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    return image, pick

def crop(im, r, c, height, width):
    return im[r:r + height, c:c + width]

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

def get_foreground(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
    edges = cv2.dilate(edges, None)
    edges = cv2.erode(edges, None)
    contour_info = []
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    for c in contours:
        contour_info.append((
            c,
            cv2.isContourConvex(c),
            cv2.contourArea(c),
        ))
    contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
    max_contour = contour_info[0]
    mask = np.zeros(edges.shape)
    cv2.fillConvexPoly(mask, max_contour[0], (255));
    mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
    mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
    mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
    mask_stack = np.dstack([mask]*3)
    mask_stack  = mask_stack.astype('float32') / 255.0
    img         = img.astype('float32') / 255.0

    masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR)
    masked = (masked * 255).astype('uint8')
    return masked

def get_person(img):
    imr, bbs = HogDescriptor(img)
    try:
        bbs = [[bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]]
               for bb in bbs]
        bbs = sorted(bbs, key=lambda x: x[2] * x[3],
                     reverse=True)
        bb = bbs[0]
        if max(bb[2], bb[3]) < 200:
            return img
        imc = crop(imr, bb[1], bb[0], bb[3], bb[2])
        masked = get_foreground(imc)
        ims = im_squared(masked)
        return ims
    except:
        return img
