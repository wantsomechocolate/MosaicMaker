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

