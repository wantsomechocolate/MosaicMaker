
## Test that original_image is unaffected by using the various methods in the ImageMosaic class
test = mm.MosaicImage('C:/Users/wants/Projects/Code/MosaicMakerImages/Anqi/Anqi-04/Anqi-04.jpg')
original_size = test.original_image.size
test.to_thumbnail()
hasattr(test,'original_image')
hasattr(test.original_image,'filename')
original_size == test.original_image.size

## rest img and do a similar thing...
test.img = 'asdf'


## Making sure all the comparison function stuff works

## resetting the comparison function safter init for exampe. 