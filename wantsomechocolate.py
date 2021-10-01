import functools
import time
from datetime import datetime
import os

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        completed_at_time = datetime.now()
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs @{completed_at_time}")
        return value
    return wrapper_timer


def path_data(path):
    '''bp - base_path, fn - filename, ep - extended path(the path resulting from removing the file_ext), 
ext - file extension, nfn - naked filename (no ext)'''
    bp,fn = os.path.split(path)
    ep,ext = os.path.splitext(path)
    nfn = os.path.splitext(fn)[0]

    return dict(    bp=bp,
                    fn=fn,
                    ep=ep,
                    ext=ext,
                    nfn=nfn,  )


#image = ImageOps.exif_transpose(im)
def rotate_based_on_exif(pil_image_obj):

    from PIL import Image, ExifTags

    try:
        #image=Image.open(filepath)

        image = pil_image_obj

        # for orientation in ExifTags.TAGS.keys():
        #    if ExifTags.TAGS[orientation]=='Orientation':
        #        break

        orientation = 274

        exif=dict(image._getexif().items())

        if exif[orientation] == 3 or exif[orientation] == 4:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6 or exif[orientation] == 5:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8 or exif[orientation] == 7:
            image=image.rotate(90, expand=True)

        return image

        #image.save(filepath)
        #image.close()
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        #print("WARNING: The image was not rotated, sorry")
        return pil_image_obj








