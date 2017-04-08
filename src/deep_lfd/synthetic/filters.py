import cv2
import numpy as np

from deep_lfd.rgbd.bgSegmentation import bgBoundsByMode, segmentBG
from deep_lfd.rgbd.basic_imaging import formatRGB, contourise, bins, deNoise, add_dim

def get_mask(img):
    lb, ub = bgBoundsByMode(img, 30)
    bin_img = segmentBG(img, lb, ub)
    return bin_img/255.0 #normalize

"""FILTERS"""
def apply_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def apply_gray_mask(img):
    mask = get_mask(img)
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return gray_img * mask

def apply_gray_mask_binned(img):
    return bins(apply_gray_mask(img), 2)

def apply_gray_mask_trace(img):
    return contourise(bins(apply_gray_mask(img), 1))

def apply_gray_mask_blur(img):
    return deNoise(apply_gray_mask(img), moreBlur = True)

def apply_rgb_mask(img):
    mask = get_mask(img)
    mask = formatRGB(mask)
    return img * mask

def apply_rgb_mask_binned(img):
    return bins(apply_rgb_mask(img), 1)

def apply_rgb_gray_mask(img):
    mask = get_mask(img)
    inv_mask = 1 - mask
    mask = formatRGB(mask)
    rgb_fore = img * mask
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray_back = inv_mask * gray
    gray_back = formatRGB(gray_back)
    return np.where(rgb_fore != 0, rgb_fore, gray_back)

"""
Use this to returns all filters (reduces number of calculations):
return format:
[gray, gray_mask, gray_mask_binned, gray_mask_trace, gray_mask_blur, rgb, rgb_mask, rgb_mask_binned, rgb_gray]
"""
def apply_all(img):
    mask = get_mask(img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    gray_masked = mask * cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    rgb_masked = formatRGB(mask) * img

    gray_binned = bins(gray_masked, 2)
    rgb_binned = bins(rgb_masked, 1)

    trace = contourise(bins(gray_masked, 1))

    format_gray_masked = add_dim(gray_masked).astype(np.uint8)
    blur = deNoise(format_gray_masked, moreBlur = True)

    inv_mask = 1 - mask
    gray_back = inv_mask * gray
    gray_back = formatRGB(gray_back)
    rgb_gray = np.where(rgb_masked != 0, rgb_masked, gray_back)

    return [gray, gray_masked, gray_binned, rgb_masked, rgb_binned, rgb_gray]
