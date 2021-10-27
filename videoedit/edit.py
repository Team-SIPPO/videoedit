import platform
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2


def _pil2cv(imgPIL):
    # imgCV_RGB = np.array(imgPIL, dtype = np.uint8)
    imgCV_BGR = np.array(imgPIL)[:, :, ::-1]
    return imgCV_BGR

def _cv2pil(imgCV):
    imgCV_RGB = imgCV[:, :, ::-1]
    imgPIL = Image.fromarray(imgCV_RGB)
    return imgPIL

def _get_default_font_face():
    pf = platform.system()
    if pf == "Windows":
        font_face = "meiryo.ttc"
    elif pf == "Darwin":
        font_face = "ipaexg.ttf"        
    elif pf == "Linux":
        font_face = "NotoSansCJK-Regular.ttc"
    else:
        raise ValueError("not supported os.")
    return font_face

def put_text(img, text, org, font_face=None, font_scale=100, color=(255, 255, 255), pos="topleft"):
    if font_face is None:
        font_face = _get_default_font_face()
    x, y = org
    b, g, r = color
    colorRGB = (r, g, b)
    imgPIL = _cv2pil(img)
    draw = ImageDraw.Draw(imgPIL)
    fontPIL = ImageFont.truetype(font = font_face, size = font_scale)
    w, h = draw.textsize(text, font = fontPIL)
    if pos == "topleft":
        x = x
        y = y
    elif pos == "center":
        x = x - w // 2
        y = y - h // 2
    elif pos == "bottomleft":
        x = x
        y = y - h
    else:
        raise ValueError("not supported pos {}".format(pos))

    # print(x, y)
    draw.text(xy = (x,y), text = text, fill = colorRGB, font = fontPIL)
    imgCV = _pil2cv(imgPIL)
    return imgCV


def generate_text_mask(img_width, img_height, text, org, font_face=None, font_scale=100, pos="topleft"):
    color=(255, 255, 255)
    # select background color
    mean_color_intensity = np.round(np.mean(color))
    if mean_color_intensity > 128:
        backgournd = (0, 0, 0)
    else:
        backgournd = (255, 255, 255)
    
    img = np.ones((img_height, img_width, 3)) * backgournd
    img = img.astype("uint8")

    text_img = put_text(img, text, org, font_face, font_scale, color, pos)
    
    str_img = text_img == np.array(color)
    str_img = np.sum(str_img, axis=-1) == 3
    # str_img_idx = np.repeat(np.expand_dims(str_img, axis=-1), 3, axis=-1)

    return str_img


def fill_color_with_mask(img, mask, color, fill_in_mask=True):
    img[mask == fill_in_mask, 0] = color[0]
    img[mask == fill_in_mask, 1] = color[1]
    img[mask == fill_in_mask, 2] = color[2]
    return img
    

def resize_mask(mask, dsize=None, fx=None, fy=None):
    expand_gbr_image = np.repeat(np.expand_dims(mask, axis=-1), 3, axis=-1).astype("uint8")
    resized_mask =  cv2.resize(expand_gbr_image, dsize=dsize, fx=fx, fy=fy)
    resized_mask = resized_mask.astype("bool")[:, :, 0]
    return resized_mask


def scale_and_crop_mask(
    mask, 
    scale_ratio=1.0, 
    mask_center_x=None, 
    mask_center_y=None, 
    crop_img_width=None, 
    crop_img_heigt=None
):
    # mask = text_mask
    # mask_center_x = 100
    # mask_center_y = 100
    # scale_ratio = 2.0
    

    mask_center_x = mask_center_x or mask.shape[1] // 2
    mask_center_y = mask_center_y or mask.shape[0] // 2

    crop_img_width = crop_img_width or mask.shape[1]
    crop_img_heigt = crop_img_heigt or mask.shape[0]
    crop_center_x = crop_img_width // 2
    crop_center_y = crop_img_heigt // 2
    crop_img = np.zeros((crop_img_heigt, crop_img_width), dtype="bool")
    
    if scale_ratio != 1.0:
        resized_mask = resize_mask(mask, fx=scale_ratio, fy=scale_ratio)
    else:
        resized_mask = mask
    
    mask_width = resized_mask.shape[1]
    mask_height = resized_mask.shape[0]
    
    left = mask_center_x - mask_width // 2
    right = mask_center_x + mask_width // 2
    top = mask_center_y - mask_height // 2
    bottom = mask_center_y + mask_height // 2

    clip_left = np.maximum(left, 0)
    clip_right = np.minimum(right, crop_img_width)
    clip_top = np.maximum(top, 0)
    clip_bottom = np.minimum(crop_img_heigt, bottom)

    zero_point = (
        mask_height // 2 - mask_center_y,
        mask_width // 2 - mask_center_x
    )
    crop_img[clip_top:clip_bottom, clip_left:clip_right ] = \
        resized_mask[clip_top + zero_point[0]:clip_bottom + zero_point[0], clip_left + zero_point[1]:clip_right + zero_point[1]]


    return crop_img