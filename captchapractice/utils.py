from itertools import product
from PIL import Image
import os 


def evaluate_response(correct_choices, selected_choices):
    selected = set(selected_choices)
    correct = set(correct_choices)

    # Members that are 'correct' in the traditional sense (they occur in both sets // set intersection)
    true_positives = correct & selected  
    # Members that are not 'correct' but were selected nonetheless
    false_postives = selected - correct
    # Members that were 'correct' but weren't selected
    false_negatives = correct - selected

    # Testing for set equality (both sets have the same elements)
    if selected == correct:
        evaluation = "You are correct!"
    elif len(false_negatives) > 0 and len(false_postives) == 0:
        evaluation = 'Uh-oh! You missed an image or two.'
    else:
        evaluation = "Oops, you got it wrong!"

    return (evaluation, true_positives, false_postives, false_negatives)


def validate_dimensions(instance, dir_in, dir_out):
    filename = str(instance.image)  
    # Format of 'filename': "admin uploads/image_name.ext"
    
    pre_img = Image.open(os.path.join(dir_in, filename))
    w, h = pre_img.size
    abbrv_name = instance.image_name

    if w != h:
        print("Not a 1:1 ratio image", w, "x", h)
        return False
    
    out = os.path.join(dir_out, f'{abbrv_name}.jpg')
    pre_img.save(out)
    return True


def make_slices(filename, slice_count, dir_in, dir_out):
    img_name = f'{filename}.jpg'
    pre_img = Image.open(os.path.join(dir_in, img_name))

    # Resize the image so we produce a standardized display
    img = pre_img.resize((1200, 1200))
    w, h = img.size

    # Divides the image into slice_count rows
    s_len = w // slice_count  

    k = 1
    grid = product(range(0, h-h%s_len, s_len), range(0, w-w%s_len, s_len))
    for i, j in grid:
        box = (j, i, j+s_len, i+s_len)
        out = os.path.join(dir_out, f'{filename}_{k}.jpg')
        img.crop(box).save(out)
        k +=1


# def create_slice_objects(filename, slice_count, instance):
#     name, ext = os.path.splitext(filename)
#     no_of_slices = (slice_count)**2
#     for i in range(1, no_of_slices+1):
#         ImageSlice.objects.create(root_image=instance, slice_name=f"{name}_{i}")

