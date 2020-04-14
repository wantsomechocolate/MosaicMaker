
def rgb_avg_comparison_f_eq_1(obj1,obj2,opts=dict()):

	## reset the obj2 error just in case anything crazy happens
	obj2.error = None

	if not hasattr(obj1,"rgb_avg"):
		obj1.rgb_avg = np.mean(obj1.rgb_data, axis=(0, 1))

	if not hasattr(obj2,"rgb_avg"):
		obj2.rgb_avg = np.mean(obj2.rgb_data, axis=(0, 1))

	error = np.absolute(obj1.rgb_avg - obj2.rgb_avg).sum()
	
	obj2.error = error

	return error




## For plotting with matplotlib - only good for large granularity
def output_matplotlib(master):

    import matplotlib.pyplot as plt
    
    print("Starting to plot")

    fig, axes = plt.subplots(master.h_sections, master.w_sections) #, figsize=(master.w_sections, master.h_sections))
    for i in range(master.h_sections):
        for j in range(master.w_sections):
            dummy = axes[i,j].imshow(master.grid[i][j].currentMosaicImage.rgb_data)
            dummy = axes[i,j].axis('off')

    fig.subplots_adjust(wspace=0, hspace=0)
    fig.show()
    return fig

    ## Code for making a plot of the original but the same size as the mosaics because I like it
    if False:
        fig2, axes2 = plt.subplots(1, 1)
        dummy = axes2.imshow(master.targetImgObject.rgb_data)
        dummy = axes2.axis('off')
        fig2.subplots_adjust(wspace=0, hspace=0)
        fig2.show()



