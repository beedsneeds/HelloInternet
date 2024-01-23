from itertools import product
from PIL import Image
import os

from .models import ImageSlice


def validate_dimensions(instance, dir_in, dir_out):
    filename = str(instance.image)
    # Format of 'filename': "admin uploads/image_name.ext"

    pre_img = Image.open(os.path.join(dir_in, filename))
    w, h = pre_img.size
    if w != h:
        print("Not a 1:1 ratio image", w, "x", h)
        return False

    # An error is thrown if the image is transparent because JPG does not support alpha (transparency) modes like RGBA & P
    # This is only a stop-gap solution to make image uploading process be more dynamic. I want to be able to use gifs
    if pre_img.mode in ("RGBA", "P"):
        pre_img = pre_img.convert("RGB")

    abbrv_name = instance.image_name
    out = os.path.join(dir_out, f"{abbrv_name}.jpg")
    pre_img.save(out)
    return True


def make_image_slices(filename, slice_count, dir_in, dir_out, instance):
    img_name = f"{filename}.jpg"
    pre_img = Image.open(os.path.join(dir_in, img_name))

    # Resize the image so we produce a standardized display
    img = pre_img.resize((1200, 1200))
    w, h = img.size

    # Divides the image into slice_count rows
    img_dim = w // slice_count

    filename_list = []
    no_of_slice_objects = (slice_count) ** 2
    for k in range(1, no_of_slice_objects + 1):
        if k <= 9:
            filename_list.append(f"{filename}_0{k}")
        else:
            filename_list.append(f"{filename}_{k}")
        print(filename_list[k - 1])

    k = 0
    # Determines the the position of the top-left corner of each image. 
    # (h // img_dim) * img_dim preferred over just h for the situation when h % img_dim produces 
    # a non-zero remainder. h - h % img_len is also alternatively used here.
    grid = product(range(0, (h // img_dim) * img_dim, img_dim), range(0, (w // img_dim) * img_dim, img_dim))
    for i, j in grid:
        box = (j, i, j + img_dim, i + img_dim)
        out = os.path.join(dir_out, f"{filename_list[k]}.jpg")
        img.crop(box).save(out)
        ImageSlice.objects.create(root_image=instance, slice_name=filename_list[k])
        k += 1
