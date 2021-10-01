## Hi, welcome to the README
If you download this program, it will not work because it depends on some files that aren't in the repository.

## How the program works
A base image is chosen, the image is broken into sections and rgb information is collected for each section. Search queries are chosen and returned images are analyzed. The rgb information for each query image is compared to each section on the base image. The image with the least error is chosen for that spot. 

## Problems
Large patches of the same color will be filled with the same image. To get around this I find the 5 images with the lowest error and then pick one at random. It theoretically brings the image quallity down, but I feel that it's worth it to prevent the large areas with the same image. A better way would be to let the user highlight certain areas for randomization, or intelligently pick the areas, that way other areas can still use the best match. 

Images in the mosaic are currently being resized to match the aspect ratio of the original base image. I did this as a first pass so that there would be the same number of images across and down. It is not the desired behavior. I think I might solve this one by allowing the user to choose. The three options that come to mind are the current setup (match aspect ratio to base image), square, 8.5x11 (for printing really large mosaics. 

A related issue to the above is that the images aren't being placed in a rectangle of a certain AR, they are being stretched. It would be much better behavior to place the image in it's section without stretching, if it doesn't fit, then pick a new image? Stretch to fit? I think I might be able to filter out certain images sizes on search. The issue that arises from placing an image in a section and having some cutoff is that there becomes a best way to place the image, how do I calculate that without taking forever. It already takes 8 minutes on my computer to fill 1000 spots with a pool of 1700 images. If I also have to move the images around each spot that could go up by a lot. I guess the first pass would be to default to centering the image (like a desktop background on fill mode).

It happens very often that images will no longer be available. I need to figure out how to replace these images via javascript on load and edit the original html document and the log file containing all the links and rgb data when that occurs. Brainstorm on how to select new image.

Images that have transparencies should not be used. Otherwise, the background is visible through the image. If I ever start saving some of these images, 4 channel images can just be turned into 3 channel images, or I can make the mosaic background white, but I shouldn't have to rely on that. 

There are more, but I can't think of them right now. 

## Future Work
When I have a web-based version of this, free users will have limited options for the size of the query images and base images, and how many queries they can have at one time etc. This is so that bandwith doesn't get crazy. Paid users will have the ability to make much "larger" mosaics. 

Generate a list of unique images so that the user can scroll through and make sure that there is nothing disgusting/offensive. Save the info when a user flags an image and notify other users when they create a mosaic that has images that have been flagged by other users in the past. - This should be easy find. Take the list of links used to generate the html doc and make a set out of it, find a way to display that data. I tried it out and the set thing seems to work, I don't have the internet right now so I have to design a page to show them and then check it out. It wasn't that bad, out of a 1900 image pool, it took 80 uniques to fill 2500 spots. Definitely manageable when trying to weed out taboo images. 

Be able to mix desired preset images and fill the rest with random/ queried images. Then people could hide certain images in there. have a setting where you can choose to have certain images be used in the selection process (no guarantee that they will be selected), After the fact go through and find the best spots for these special images (will be worse then images replace, but best spot for the forced image), click on images and choose select force image with option to upload, use previously uploaded image, or link. 

Free users can "Save" a mosaic once a week, as in save the images in the mosaic so that the mosaic will be reproducable. instead of just savings the links, which they can do as much as they want. Paid users will be able to save as many mosaics as they want. 

Have categories for each user, once they are searched for they are available to all users, categories that are avaiable are selectable, categories that are yet to be searched for (searches take up to 5-10 minutes for 100 images).
I can swing only savings data for the most find grained because I can derive the rest from that?

I want to use Django for this. Should I pay for a host or experiment with a Wamp/Lamp server first to save money?
I will use wamp for now and try really hard to Django it up. The first steps from the web side are to have users? a home page?

 