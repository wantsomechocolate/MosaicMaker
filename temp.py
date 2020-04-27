from random import random


	def choose_match(self, coordinates, pieces, random_max, neighborhood_size, blocklist=None, opts = dict() ):
		'''Choose the closest match that doesn't violate the neighbor constraint'''
		
		## Sort in the beginning because I think it makes later things faster. 
		pieces.sort(key=lambda x: (x.error is None, x.error))

		neighbors = self.get_neighbors(coordinates, neighborhood_size) if neighborhood_size != 0 else []

		## get_neighbors returns a list of mosaicmaker image objects so blocklist must also contain those, foo.
		## there isn't a special object for the section of a mosaic grid. 
		for item in blocklist:
			neighbors.append(item)

		## Change variable name?
		for neighbor in neighbors:
					
			## does neighbor have a mosaic object chosen for itself yet?
			if hasattr(neighbor,'piece'):
				neighbor_mosaic_image = neighbor.piece

				## Find where the neighbor's piece is in the pieces list. Straight from SO baby. 
				piece = next((x for x in pieces if x.original_image.filename == neighbor_mosaic_image.original_image.filename), None)

				## Update it's error to be nothing (and properly handle None on sort)
				## I'm not particularly happy about how I'm handling this atm. 
				piece.error = None

		## Sort the list again, this time there will be some None - https://stackoverflow.com/a/18411610/1937423
		pieces.sort(key=lambda x: (x.error is None, x.error))		
		
		## Take the best match (or perhaps with a random offset)
		self.grid[coordinates[0]][coordinates[1]].piece = pieces[ int(random()*random_max) ]




	def update_all_instances_of(self,piece,piece_list,opts = dict()):
		
		## get all the sections that have this piece - this uses filename - do something better
		sections=[]
		piece_file_name = piece.original_image.filename.split('/')[-1]
		for i in range(self.h_sections):
			for j in range(self.w_sections):
				if self.grid[i][j].piece.original_image.filename.split('/')[-1] == piece_file_name:
					self.grid[i][j].coordinates = (i,j)
					sections.append(self.grid[i][j])

		## the items are pieces
		for section in sections:
			for i in range(len(piece_list.pieces)):
				self.comparison_function(section,piece_list.pieces[i],f=self.f)

			self.choose_match(section.coordinates, piece_list.pieces, self.random_max, self.neighborhood_size, blocklist=[section.piece], opts=opts )


		return sections