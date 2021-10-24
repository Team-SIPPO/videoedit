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

def get_default_font_face():
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
        font_face = get_default_font_face()
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


def generate_mask(img_width, img_height, text, org, font_face=None, font_scale=100, color=(255, 255, 255), pos="topleft"):
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
