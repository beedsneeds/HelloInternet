import os
from django.conf import settings

from PIL import Image
from ultralytics import YOLO
from typing import Optional
from itertools import product

from .models import ImageSlice, CaptchaImage


# TODO change TO large    model = YOLO("yolov8l-seg.pt") when in production but to nano    model = YOLO("yolov8n-seg.pt")


def validate_image_dimensions(image, filename):
    """
    If image dimensions are 1:1, saves the image in 'out_path' after some processing
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

    # Resize the image to produce a standardized display
    pre_img = pre_img.resize((1200, 1200))

    # JPG format doesn't support alpha channels (RGBA & P), avoids errors with transparent images
    if pre_img.mode in ("RGBA", "P"):
        pre_img = pre_img.convert("RGB")

    # Conversion to .jpg accomplished by converting to RGB channel & using the .jpg extension
    out = os.path.join(out_path, f"{filename}.jpg")
    pre_img.save(out)
    pre_img.close()
    return True


def run_object_detection(filename):
    """
    Uses the YOLOv8 large segmentation model and saves the output in the same path.
    Returns 2 objects:
      1) 2-item list of classes (objects) identified
      2) xy coordinates of each point in the mask. This is a 4D list in the form of:
          list( list_for_each_object_detected( name_of_object , list_of_coord(2-item lists) ) )
    The size of xy coords (the 2-item lists) is massive. So for visualization, use this:
    detected_coords = [
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
    detected_coords = []
    detected_classes = set()

    for i, cls in enumerate(output_cls):
        cls = int(cls)
        if cls in model.names:
            detected_coords.append([model.names[cls], output_xy[i].round().tolist()])
            detected_classes.add((model.names[cls], model.names[cls]))

    # List conversion avoids "Set objects are not JSON serializable" errors
    return detected_coords, list(detected_classes)


def make_image_slices(
    captcha_instance: Optional[CaptchaImage], detected_coords, selected_object
):
    """
    Handles the entire logic of creating and initializing img slices.
    There's a lot to unpack here, so check each code block.
    """

    path = os.path.join(
        settings.BASE_DIR,
        "captchapractice",
        "static",
        "captchapractice",
        "images",
    )
    # out_path: path where the image slices are saved
    out_path = os.path.join(path, "prompts")
    # in_path: path of validate_image_dimensions image output
    in_path = os.path.join(path, "prompt candidates")
    filename = captcha_instance.image_name
    slice_count = int(captcha_instance.slice_count)

    img = Image.open(os.path.join(in_path, f"{filename}.jpg"))
    w, h = img.size
    sl_dim = w // slice_count  # sl_dim is the side length of an image slice

    # Builds a list containing names/labels of each slice
    filename_list = [
        f"{filename}_0{k}" if k <= 9 else f"{filename}_{k}"
        for k in range(1, (slice_count) ** 2 + 1)
    ]

    # 1. Filter & flatten the 4D list to a 2D list. Split into 2 lines for readability.
    #       See run_object_detection to understand how detected_coords is structured.
    # 2. Flattened to 2D because eval_elem_presence returns True if even one object is present
    temp_coords = [obj[1] for obj in detected_coords if obj[0] == selected_object]
    mask_coords = [xy_point for points_list in temp_coords for xy_point in points_list]

    # 1. 'grid' records the coordinates of the top-left vertex of each slice.
    # 2. ((h // sl_dim) * sl_dim) or (h - h % img_len) is picked over (h) as the former accounts
    #       for non-zero remainders produced by (h % sl_dim)
    grid = product(
        range(0, ((h // sl_dim) * sl_dim), sl_dim),
        range(0, ((w // sl_dim) * sl_dim), sl_dim),
    )

    for index, (i, j) in enumerate(grid):
        # slice_vertices: xyxy format where top-left vertex:(x1, y1), bottom-right vertex: (x2, y2)
        slice_vertices = (j, i, j + sl_dim, i + sl_dim)
        element_presence = eval_elem_presence(
            slice_vertices=slice_vertices,
            mask_coords=mask_coords,
        )
        img.crop(slice_vertices).save(
            os.path.join(out_path, f"{filename_list[index]}.jpg")
        )
        ImageSlice.objects.create(
            root_image=captcha_instance,
            slice_name=filename_list[index],
            element_presence=element_presence,
        )
    img.close()


def eval_elem_presence(slice_vertices, mask_coords):
    """
    Args Format:
    slice_vertices is a 4-tuple like (0, 0, 400, 400)
    mask_coords is a nested list with each list item being a 2-int xy point
        [ [330.0, 397.0], [328.0, 399.0], [1067.0, 311.0],.... ]

    Output:
    Return True only if atleast {sensitivity_count} points lie within a given square slice.
    {sensitivity_count} serves to avoid false positives for indiscernible overlaps
    """

    sensitivity_count = 5
    for i, point in enumerate(mask_coords):
        # Check x-coord overlap
        if slice_vertices[0] <= point[0] <= slice_vertices[2]:  
            # Check y-coord overlap
            if (slice_vertices[1] <= point[1] <= slice_vertices[3]):  
                sensitivity_count -= 1
                # Tests for mask coords that consist of long straight lines.
                # Such masks dont have as many points as curves do
                # Avoids the need choose between accuracy and sensitivty
                if point[0] == mask_coords[i-1][0] or point[1] == mask_coords[i-1][1]:
                    sensitivity_count -= 4
        if sensitivity_count <= 0:
            return 1
    return 0
