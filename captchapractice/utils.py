from itertools import product
from PIL import Image
import os 

def make_slices(filename, dir_in, dir_out, slice_count):
    name, ext = os.path.splitext(filename)
    pre_img = Image.open(os.path.join(dir_in, filename))
    w, h = pre_img.size

    if w != h:
        print("Not a 1:1 ratio image", w, "x", h)
        return

    img = pre_img.resize((1200, 1200))
    w, h = img.size
    print(w, "x", h)

    s_len = w // slice_count  # divides the image into slice_count rows
    print(s_len)

    k = 1
    grid = product(range(0, h-h%s_len, s_len), range(0, w-w%s_len, s_len))
    for i, j in grid:
        box = (j, i, j+s_len, i+s_len)
        out = os.path.join(dir_out, f'{name}_{k}.jpg')
        img.crop(box).save(out)
        k +=1


# cwd = "c:/Users/bkrbh/Documents/Starting Afresh/Django-4.2/prototyping/"

input_dir  = "C:/Users/bkrbh/Documents/Starting Afresh/Django-4.2/HelloInternet/captchapractice/static/captchapractice/images/prompt candidates/"
output_dir = "C:/Users/bkrbh/Documents/Starting Afresh/Django-4.2/HelloInternet/captchapractice/static/captchapractice/images/prompts/"

result = make_slices('waifu.jpeg', input_dir, output_dir, 3)
