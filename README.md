## Hi, welcome to the README
If you download this program, it will not work because it depends on some files that aren't in the repository. Feel free to ask me for them and I'll give probably just send them to you. 

## How the program works

## Collecting Images
Google CSE is used to collect images (100 at a time) based on search query, It typically takes about 1000 images to yeild decent fidelity in the mosaic. You can also just supply images directly without using google to curate them for you.

## Creating the Mosaic
The base or target image is broken up into sections. The rgb information is collected for each section. The pieces (images you want to use to replace the sections, essentially) are currently supplied to the program by just telling it where a directory of images live. It then goes through and compares the RGB values of all the sections and pieces in order to find the piece that is the best fit for each section. Then you can output the results as either an image file, or a collectiong of html, css, and image files. 



 