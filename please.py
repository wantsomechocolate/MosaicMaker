from datetime import datetime
import os
from yattag import Doc
from yattag import indent
from PIL import Image

def output_html(self):
	

	start = datetime.utcnow()
	timestamp = int(start.timestamp())

	target_image_filepath = self.target.original_image.filename
	base_save_directory = os.path.splitext(target_image_filepath)[0]
	html_save_directory = base_save_directory+'/html/html-'+str(timestamp)+'/'
	pieces_save_directory = html_save_directory+'pieces/'
	
	img_filename = base_save_directory.split('/')[-1]

	os.makedirs(html_save_directory) if not os.path.exists(html_save_directory) else None
	os.makedirs(pieces_save_directory) if not os.path.exists(pieces_save_directory) else None

	html_output_filepath = html_save_directory+img_filename+'-'+str(int(datetime.utcnow().timestamp()))+'.html'		
	css_output_filepath = html_save_directory+'mosaicStyle.css'

	doc, tag, text = Doc().tagtext()

	doc.asis('<!DOCTYPE html>')

	with tag('html', lang = 'en'):
		with tag('head'):
			doc.stag('meta', charset='utf-8')
			with tag('title'):
				text("PhotoMosaic")
			doc.stag('meta', name='description', content='PhotoMosaic Output')
			doc.stag('meta', name='author', content='James McGlynn')
			doc.stag('link', rel='stylesheet', href='mosaicStyle.css')


		with tag('body'):
			with tag('div', klass='imageContainer'):
				
				for i in range(self.h_sections):

					with tag('div', klass='row', id='row-'+str(i)):
				
						for j in range(self.w_sections):

							with tag('div', klass='col', id='cell-'+str(i)+'-'+str(j)):
								doc.stag('img', src='pieces/'+self.grid[i][j].piece.original_image.filename.split('/')[-1])
				
	
	with open(html_output_filepath, 'w') as fh:
		output = indent(doc.getvalue())
		fh.write(output)
		image_container_width = self.w_sections * 40

	css_text = '''
* {{box-sizing:border-box;}}
body {{background:black;
color:white;
padding:0;
margin:0;
border:0;}}
.imageContainer {{overflow:hidden;
border:0;
margin:0;
padding:0;
width:{image_container_width};}}
img {{padding:0px;
margin:0px;
height:40px;
width:40px;}}
.row {{width:100%;
padding:0;
margin:0;}}
/* Clear floats after image containers */
.row::after {{clear: both;
content: "";
display:block;}}
.col {{float: left;
padding: 0px;
margin:0px;
height:40px;}}'''

	css_text = css_text.format(image_container_width = image_container_width)

	with open(css_output_filepath, 'w') as fh:
		fh.write(css_text)


	for item in self.unique_pieces:
		im = Image.open(item.piece.original_image.filename)
		im_name = item.piece.original_image.filename.split('/')[-1]
		im.save(pieces_save_directory+im_name)

	return html_output_filepath