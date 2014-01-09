>>> import os
>>> os.getcwd()
'/home/wantsomechocolate/Code/MosaicMaker'
>>> from PIL import Image
>>> im = Image.open("test.png")
>>> imh=im.size[0]
>>> imw=im.size[1]
>>> imh
960
>>> imw
540
>>> imw,imh=im.size
>>> imw
960
>>> imwh
Traceback (most recent call last):
  File "<pyshell#10>", line 1, in <module>
    imwh
NameError: name 'imwh' is not defined
>>> imh
540
>>> if imw<=imh:
	imh=imw
else imw=imh
SyntaxError: invalid syntax
>>> if imw<=imh:
	imh=imw
else: imw=imh

>>> imw
540
>>> imh
540
>>> 960-540
420
>>> 420/2
210.0
>>> round(210,0)
210
>>> 960-210
750
>>> im.crop([210,0,750,540])
<PIL.Image._ImageCrop image mode=RGB size=540x540 at 0x7FA9FF345ED0>
>>> imcrop=im.crop([210,0,750,540])
>>> imcrop.save("asdf.png")
