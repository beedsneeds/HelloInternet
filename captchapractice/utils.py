import os
from django.conf import settings

from PIL import Image
from ultralytics import YOLO
from typing import Optional
from itertools import product

from .models import ImageSlice, CaptchaImage


# CHAAAANGE TO large    model = YOLO("yolov8l-seg.pt") when in production but to nano    model = YOLO("yolov8n-seg.pt")


def validate_image_dimensions(image, filename):
    """
    Used in views
    If image dimensions are 1:1, saves the image in path 'out_path' after a bit of processing
    """
    out_path = os.path.join(
        settings.BASE_DIR,
        "captchapractice",
        "static",
        "captchapractice",
        "images",
        "prompt candidates",
    )

    pre_img = Image.open(image)
    w, h = pre_img.size
    if w != h:
        print("Not a 1:1 ratio image", w, "x", h)
        return False

    # Resize the image so we produce a standardized display
    pre_img = pre_img.resize((1200, 1200))

    # An error is thrown if the image is transparent because JPG does not support alpha (transparency) modes like RGBA & P
    # This is only a stop-gap solution to make image uploading process be more dynamic. I want to be able to use gifs
    if pre_img.mode in ("RGBA", "P"):
        pre_img = pre_img.convert("RGB")

    # The above two lines and the explicit .jpg save converts the image to .jpg
    # I wonder if there are any file formats that break this
    # If I didn't use the .jpg extension would gifs remain functional - no because gifs are many frames
    out = os.path.join(out_path, f"{filename}.jpg")
    pre_img.save(out)
    return True


def run_object_detection(filename):
    """
    Used in views
    Uses the YOLOv8 large segmentation model and saves the output in the same path.
    Returns 2 objects:
      1) 2-item list of classes (objects) identified
      2) xy coordinates of each point in the mask. This is in the form of:
          list( list_for_each_object( name_of_class , list_of_coord(2-item lists) ) )
    The size of xy coords (the 2-item lists) is massive. So for visualization, use this:
    xy_mask = [
            ["person", [ [330.0, 397.0], [328.0, 399.0], [1067.0, 311.0], ]  ],
            ["monkey", [ [330.0, 397.0], [328.0, 399.0], [1067.0, 311.0], ]  ]
        ]
    """

    model = YOLO("yolov8n-seg.pt")
    path = os.path.join(
        settings.BASE_DIR,
        "captchapractice",
        "static",
        "captchapractice",
        "images",
        "prompt candidates",
    )
    in_path = os.path.join(path, f"{filename}.jpg")
    out_path = os.path.join(path, f"{filename}_yolo.jpg")

    output = model(in_path)
    output[0].save(filename=out_path)
    output_cls = output[0].boxes.cls
    output_xy = output[0].masks.xy
    output_coords = []
    output_classes = set()

    for i, cls in enumerate(output_cls):
        cls = int(cls)
        if cls in model.names:
            output_coords.append([model.names[cls], output_xy[i].round().tolist()])
            output_classes.add((model.names[cls], model.names[cls]))

    # List conversion avoids "Object of type set is not JSON serializable"
    output_classes = list(output_classes)
    return output_coords, output_classes


# rather than use signals, I think its time to just call it directly from views. Its more transparent


def make_image_slices(
    captcha_instance: Optional[CaptchaImage], detected_coords, selected_object
):
    coords_list = get_selected_coords(coords=detected_coords, selected=selected_object)

    path = os.path.join(
        settings.BASE_DIR,
        "captchapractice",
        "static",
        "captchapractice",
        "images",
    )
    # out-path - where the individual image slices are saved
    out_path = os.path.join(path, "prompts")

    # in_path - location of processed image after validate_image_dimensions was run
    in_path = os.path.join(path, "prompt candidates")
    filename = f"{captcha_instance.image_name}.jpg"
    img = Image.open(os.path.join(in_path, filename))

    w, h = img.size

    # Divides the image into slice_count rows & columns
    slice_count = int(captcha_instance.slice_count)
    img_dim = w // slice_count

    # Builds a list containing names of each of the slices
    # Check if there's a concise way like using list comprehension
    filename_list = []
    no_of_slice_objects = (slice_count) ** 2
    for k in range(1, no_of_slice_objects + 1):
        if k <= 9:
            filename_list.append(f"{filename}_0{k}")
        else:
            filename_list.append(f"{filename}_{k}")
        print(filename_list[k - 1])

    # List 'grid' determines the position of the top-left corner of each image.
    # ((h // img_dim) * img_dim) preferred over just h for the situation when h % img_dim produces
    # a non-zero remainder (you get a sliver of row/column because of rounding issues)
    # (h - h % img_len) is also alternatively used here, but is not as intuitive to understand
    grid = product(
        range(0, ((h // img_dim) * img_dim), img_dim),
        range(0, ((w // img_dim) * img_dim), img_dim),
    )
    k = 0
    for i, j in grid:
        # Slice_vertices is a 4-tuple in the form xyxy aka (x1, y1, x2, y2) where
        #   (x1, y1) is the top-left corner & (x2, y2) is the bottom-right corner.
        # Used by PIL's Image.crop() and YOLO's boxes.xyxy (which we aren't using here)
        slice_vertices = (j, i, j + img_dim, i + img_dim)
        out = os.path.join(out_path, f"{filename_list[k]}.jpg")
        img.crop(slice_vertices).save(out)
        ImageSlice.objects.create(
            root_image=captcha_instance, slice_name=filename_list[k]
        )
        k += 1


def get_selected_coords(selected, coords):
    # xy_mask = [
    #         ["person", [ [330.0, 397.0], [328.0, 399.0], [1067.0, 311.0], ]  ],
    #         ["monkey", [ [330.0, 397.0], [328.0, 399.0], [1067.0, 311.0], ]  ]
    #     ]
    res = []
    for item in coords:
        if item[0] == selected:
            res.append(item[1])

    return res


# test: If slice isn't a 4 elem array of ints and if mask isn't a 2 elem list of lists, fail the test
# the mask list is not a mirror copy of slice like in box_overlap. Its a very long list of 2-elem lists
def mask_overlap(slice, mask):
    # Used in utils
    sensitivity_count = 5
    # func will return true only if atleast 5 points lie within a given slice
    # this is an arbitrary number but helps avoid false positives for very tiny areas present in a slice

    for point in mask:
        if slice[0] <= point[0] <= slice[2]:  # checking x coordinate
            if slice[1] <= point[1] <= slice[3]:  # checking y coordinate
                sensitivity_count -= 1
        if sensitivity_count == 0:
            return 1

    return 0
