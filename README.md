## Hi, welcome to the README
This program used to work on Windows7 and python 2.7. I recently tried to get a little more serious and started using git more and virtual environments. Now it works on Ubuntu13.10 and python3.3 and no longer works on 2.7 and Windows7 because I don't know what backwards compatibility is. I had to install some external packages so that pillow would work properly. Everything I needed was listed on the pillow site here: http://pillow.readthedocs.org/en/latest/installation.html#linux-installation. I just followed instructions for python3 and Ubuntu12.04 and it works for now. 

## Here's the idea behind the program
A base image is chosen, the image is broken into sections and RGB information is collected for each section. Search queries are chosen and returned images are analyzed. The RGB information for each queried image is compared to each section on the base image. The image with the least error is chosen for that spot. Image queries are done ahead of time and the results of the analysis of each image are saved along with the image link (the images themselves are not saved) to reduce the amount of time the program needs to run

## Some Solved Issues
Large patches of the same color were being filled with the same image. To get around this I find the 5 images with the lowest error and then pick one at random. It theoretically brings the image quality down, but I feel that it's worth it to prevent the large areas with the same image. A better way could be to let the user highlight certain areas for randomization, or intelligently pick the areas, that way other areas can still use the best match. 

## Some Semi-Solved Issues
Images in the mosaic were being resized to match the aspect ratio of the original base image. I did this as a first pass so that there would be the same number of images across and down. It is not the desired behavior. My second pass was to make all the images in the mosaic square. It looks much better than the other method but it is still not desirable. My goal for this issue is to let the user pick the aspect ratio of the images making up the mosaic (The most common likely being, square, original aspect, and aspect ratios of common paper sizes).

## Some Outstanding Issues
A related issue to the above is that the images aren't being placed in a rectangle of a certain AR, they are being stretched. It would be much better behavior to place the image in it's section without stretching, if it doesn't fit, then pick a new image? Stretch to fit? I think I might be able to filter out certain images sizes on search. The issue that arises from placing an image in a section and having some cutoff is that there becomes a best way to place the image, how do I calculate that without taking forever. It already takes 8 minutes on my computer to fill 1000 spots with a pool of 1700 images. If I also have to move the images around each spot that could go up by a lot. I guess the first pass would be to default to centering the image (like a desktop background on fill mode). But then mosaic quality would suffer because RGB data going into the selection process would no longer be used. Not having the images to analyze at mosaic creation time is becoming a real problem. Maybe I could just maintain 50 common queries with 100 up to date images in each. 5000 images doesn't seem so bad. 

It happens very often that images will no longer be available. I need to figure out how to replace these images via javascript on load and edit the original html document and the log file containing all the links and RGB data when that occurs. Brainstorm on how to select new image.

Images that have transparencies should not be used. Otherwise, the background is visible through the image. If I ever start saving some of these images, 4 channel images can just be turned into 3 channel images. 

There are more, but I can't think of them right now. 

##Straight up bugs
Picking a new name for the copy of the image that gets saved with the HTML output doesn't work as expected. I creates the new directory, and saved the image, but the auto generated name for the HTML file uses the old image name and the html file itself is saved in the wrong directory, or not at all if the directory for the original image name doesn't exit.

## Future Work
When I have a web-based version of this, free users will have limited options for the size of the query images and base images, and how many queries they can have at one time etc. This is so that bandwith doesn't get crazy. "Paid" users will have the ability to make much "larger" mosaics. 

Generate a list of unique images so that the user can scroll through and make sure that there is nothing disgusting/offensive. Save the info when a user flags an image and notify other users when they create a mosaic that has images that have been flagged by other users in the past. Take the list of links used to generate the html doc and make a set out of it, find a way to display that data. I tried it out and the set thing seems to work, I don't have the internet right now so I have to design a page to show them and then check it out. It wasn't that bad, out of a 1900 image pool, it took 80 uniques to fill 2500 spots. Definitely manageable when trying to weed out taboo images. 

Be able to mix desired preset images and fill the rest with random/ queried images. Then people could hide certain images in there. 

have a setting where you can choose to have certain images be used in the selection process (no guarantee that they will be selected), 

After mosaic creation force use of certain images by going through and finding the best spots for these special images (will be worse then images replaced, but best spot for the forced image), click on images and choose select force image with option to upload, use previously uploaded image, or link. 

Free users can "Save" a mosaic once a week, as in save the images in the mosaic so that the mosaic will be reproducable. instead of just savings the links, which they can do as much as they want. "Paid" users will be able to save as many mosaics as they want. 

Have categories for each user, once they are searched for they are available to all users, categories that are available are selectable, categories that are yet to be searched for (searches take up to 5-10 minutes for 100 images).

Redo the image selection logic. Right now there are four grains of comparison. Each spot in the base image gets compared to a queried image by averaging RGB over the entire image and the entire section. In finer grains the sections of the base image are further sectioned and average RGB values are found for these sub sections, effectively looking at the distribution of color in each section. There has to be a better way to do it than that. Maybe doing a histogram of each image and a histogram of each section and using that? It was fun to implement the sub section method, but I don't think its a good way of doing it. I didn't/don't know much about analyzing images/image similarities, though. 

I want to use Django for this. What should I focus on setting up first? Users? Image querying? something else!?

 
