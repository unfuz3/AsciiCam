import cv2
import webbrowser
from scipy.interpolate import interp1d
import argparse
from os import getcwd
from os.path import exists

parser = argparse.ArgumentParser(description="AsciiCam - Convert media to ascii photos")

parser.add_argument("-p", "--photo", action="store_true", help="Select the photo-to-ascii mode")
parser.add_argument("-f", "--file", action="store_true", help="Select the image file input mode")
parser.add_argument("-i", "--input", type=str, help="Specify the image input file")
parser.add_argument("-o", "--output", type=str, help="Specify the output file, default is asciipic.txt")
parser.add_argument("-s", "--size", type=str, help="Specify the ascii image size, format 'WxH', ie. -s '60x40'. Default is 128x96")

args = vars(parser.parse_args())

cap = cv2.VideoCapture(0)

charset = " .:-=+*#%@"

mapper = interp1d([0,255],[0,len(charset)-1])


def resize_and_ascii(frame,size):
	# Resized original pic
	resized = cv2.resize(frame,size,interpolation=cv2.INTER_LINEAR)

	bnlist:list[str] = []

	# Converts to ascii based on each pixel's brightness
	for row in resized:
		newrow = []
		for pixel in row:
			avg = sum(pixel)//3
			char = charset[int(mapper(avg))]
			newrow.append(char)
		bnlist.append("".join(newrow))
	
	return bnlist

def open_in_browser(pic):
	webascii = []

	# Changes the space for the special character so that html doen't ignore it
	for row in pic:
		webascii.append(row.replace(" ","&nbsp;"))

	# Overwrites the index.html file with the ascii, i'm so sorry for this implementation
	with open("webphoto/index.html","w") as f:
		f.write("<link rel='stylesheet' href='style.css'>")
		f.write("<pre>")
		for row in webascii:
			f.write(row)
			f.write("\n")
		f.write("</pre>")

	# Open the index.html file
	webbrowser.open(f"file:///{getcwd()}/webphoto/index.html")


def main() -> None:
    # Checks for mode selection errors
	if not args["photo"] and not args["file"]:
		print("You need to select a mode")
		return
	elif args["photo"] and args["file"]:
		print("Select just one mode")
		return
	else:
		if args["photo"]: # Load pic from webcam
			ret,pic = cap.read()
			if not ret:
				print("There was an error with the camera")
				return
		else: # Load pic from input file
			if not args["input"]:
				print("An input file is necessary")
				return
			if not exists(args["input"]):
				print("Input file not found")
				return
			
			pic = cv2.imread(args["input"])
		
		if not args["size"]: # Establish size of the ascii pic
			size = (128,96)
		else:
			size = tuple([int(i) for i in args["size"].split("x")])
			if len(size) != 2:
				print("There was an error with the size")
				return

		asciipic = resize_and_ascii(pic,size) # Reduces the pic's size and ascii's it

		outfile = args["output"] if args["output"] else "asciipic.txt" # Establish output file

		# Write to the output file
		with open(outfile,"w") as f:
			for row in asciipic:
				f.write(row)
				f.write("\n")

		# Give chance to show in the web browser
		print(f"DONE: Photo saved in {outfile}. Do you want to open it on the web browser with format? (Y/n)")
		if not input().lower() == "n":
			open_in_browser(asciipic)
			return
		else:
			return

if __name__=="__main__":
	main()