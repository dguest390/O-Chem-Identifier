from keras.models import load_model
from PIL import Image, ImageEnhance
#import tflite_runtime.interpreter as tflite
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt
import numpy as np

import imutils
from imutils.contours import sort_contours

from matplotlib import cm
import math

import os

from Classes.adapter_classes import mapped_edge, mapped_node
import Classes.constants as CONSTANT

#Primary recognition function
#used https://deepnote.com/@davidespalla/Recognizing-handwriting-with-Tensorflow-and-OpenCV-cfc4acf5-188e-4d3b-bdb5-a13aa463d2b0
def recognize(cropX, cropY, cropX2, cropY2, imagePath):
	crop1 = int(cropY)  #y1
	crop2 = int(cropY2) #y2
	crop3 = int(cropX)  #x1
	crop4 = int(cropX2) #x2

	#don't allow low crops, messes things up. High crops are fine though
	if crop1 < 0:
		crop1 = 0
	if crop3 < 0:
		crop3 = 0

	#loads the model with the keras load_model function
	#model_path = os.getcwd() + '\\Image_Recognition\\model_v3\\'
	#model = load_model(model_path)
	#interpreter = tflite.Interpreter(model_path=os.getcwd()+'/Image_Recognition/model.tflite')
	interpreter = tf.lite.Interpreter(model_path=os.getcwd()+'/Image_Recognition/model.tflite')
	interpreter.allocate_tensors()
	
	#image_filename = 'DanTest.jpg'
	#image_path = os.getcwd() + '\\Image_Recognition\\Images\\'

	#open image
	image = Image.open(imagePath)

	#reduce contrast
	enhancer = ImageEnhance.Contrast(image)
	lessContrast = enhancer.enhance(0.5)

	#convert to cv2
	image = np.array(lessContrast)
	image = image[:, :, ::-1].copy()

	#apply some filters and crop image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	cropped = gray[crop1:crop2, crop3:crop4]
	blurred = cv2.GaussianBlur(cropped, (5, 5), 0)

	#convert to pure black and white
	blurred = pureBlackWhite(blurred)
	blurredCopy = blurred.copy()

	#perform edge detection, find contours in the edge map, and sort the
	#resulting contours from left-to-right
	edged = cv2.Canny(blurred, 30, 250) # low_threshold, high_threshold
	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sort_contours(cnts, method="left-to_right")[0]

	chars = []
	# loop over the contours
	for c in cnts:
		# compute the bounding box of the contour and isolate ROI
		(x, y, w, h) = cv2.boundingRect(c)
		roi = cropped[y:y + h, x:x + w]
		
		#binarize image, finds threshold with OTSU method
		thresh = cv2.threshold(roi, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
		
		# resize largest dimension to input size
		(tH, tW) = thresh.shape
		if tW / tH < 28 and tH / tW < 28:  #for propper dimensions, no abnormally long or tall images
			if tW > tH:
				thresh = imutils.resize(thresh, width=28)
			# otherwise, resize along the height
			else:
				thresh = imutils.resize(thresh, height=28)

		# find how much is needed to pad
		(tH, tW) = thresh.shape
		dX = int(max(0, 28 - tW) / 2.0)
		dY = int(max(0, 28 - tH) / 2.0)
		# pad the image and force 28 x 28 dimensions
		padded = cv2.copyMakeBorder(thresh, top=dY, bottom=dY,
		left=dX, right=dX, borderType=cv2.BORDER_CONSTANT,
		value=(0, 0, 0))
		padded = cv2.resize(padded, (28, 28))
		# reshape and rescale padded image for the model
		padded = padded.astype("float32") / 255.0
		padded = np.expand_dims(padded, axis=-1)
		# append image and bounding box data in char list
		chars.append((padded, (x, y, w, h)))

	boxes = [b[1] for b in chars]
	chars = np.array([c[0] for c in chars], dtype="float32")
	#OCR the characters using our handwriting recognition model
	#preds = model.predict(chars)
	
	#apply tf lite interpreted model
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()
	preds = []
	for char in chars:
		expandedChar = np.expand_dims(char, axis=0)
		interpreter.set_tensor(input_details[0]["index"], expandedChar)
		interpreter.invoke()
		preds.append(interpreter.get_tensor(output_details[0]["index"])[0])
	

	#define the list of label names
	labelNames = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabdefghnqrt"

	image = cv2.imread(imagePath)	 				  #keep first image for testing
	grayImage = cv2.imread(imagePath, 0)		 	  #keep second image for line segment detection
	cropped = image[crop1:crop2,crop3:crop4]
	cropped2 = grayImage[crop1:crop2,crop3:crop4]     #cropped 2 will omit characters, to detect lines

	#recognize letters letter
	letterBoxes = []
	for (pred, (x, y, w, h)) in zip(preds, boxes):
		pred = modifyPreds(pred)    #only use certain characters
		
		#find the index of the label with the largest corresponding
		#probability, then extract the probability and label
		i = np.argmax(pred)
		prob = pred[i]
		label = labelNames[i]
		#draw the prediction on the image and it's probability
		label_text = f"{label}, {prob * 100:.1f}%"
		if (prob >= 0.6) and (w > 5) and (h > 8) and (h/w < 5) and (w/h < 1.10):
			cv2.rectangle(cropped, (x, y), (x + w, y + h), (0, 255, 0), 2)
			#cv2.rectangle(cropped2, (x, y), (x + w, y + h), (255, 255, 255), -1)
			cv2.putText(cropped, label_text, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
			letterBoxes.append((x, y, w, h, label))

	#find median letterBox dimensions
	heights = []
	for letterBox in letterBoxes:
		x, y, w, h, label = letterBox
		heights.append(h)
	heights.sort()

	#filter out letterBoxes are much larger than the median
	if len(heights) > 0:
		median = heights[math.floor(len(heights)/2)]
		newLetterBoxes = []
		for letterBox in letterBoxes:
			x, y, w, h, label = letterBox
			if (label != 'n' and h < 1.50*median) or (label == 'n' and h < 1.25*median):
				newLetterBoxes.append(letterBox)
				#put white rectangle over letter so it is ignored in line segment detection
				cv2.rectangle(cropped2, (x, y), (x + w, y + h), (255, 255, 255), -1)
		letterBoxes = newLetterBoxes

	WithChars = cropped     #image with characters, used for printing
	NoChars = cropped2      #image without characters, used for line segment detection

	#NoChars = pureBlackWhite(NoChars)
	NoChars = cv2.GaussianBlur(NoChars, (5, 5), 0)

	#line segment detection
	#from https://stackoverflow.com/questions/41329665/linesegmentdetector-in-opencv-3-with-python

	#create default parametrization LSD
	lsd = cv2.createLineSegmentDetector(0)  #find out what 0 means

	#Detect lines in the image
	lines = lsd.detect(NoChars)[0] #position 0 of the retuned tuple are the detected lines

	#get rid of unnessessary lines
	avgW, avgH = avgWH(letterBoxes)
	avgSquare = (avgW + avgH)/2
	lines = condenseLines(lines, avgSquare)

	# lines = minimize_extreme_edges_by_crop(crop3, crop1, crop4, crop2, lines) # x1, y1, x2, y2
	mapped_node_arr, mapped_edge_arr = mapEdges(letterBoxes, lines)

	return mapped_node_arr, mapped_edge_arr

												###### RECOGNITION FUNCTIONS ######

def minimize_extreme_edges_by_crop(crop_x1, crop_y1, crop_x2, crop_y2, lines):
	minmized_line_list = []

	# for line position, ensure far enough away from boundary (removes some artifacts)
	for line in lines:
		line_x1, line_y1, line_x2, line_y2 = line
		offset_from_crop = 5
		x1_within_boundary: bool = line_x1 > crop_x1 + offset_from_crop and line_x1 < crop_x2 - offset_from_crop
		y1_within_boundary: bool = line_y1 > crop_y1 + offset_from_crop and line_y1 < crop_y2 - offset_from_crop
		x2_within_boundary: bool = line_x2 > crop_x1 + offset_from_crop and line_x2 < crop_x2 - offset_from_crop
		y2_within_boundary: bool = line_y2 > crop_y1 + offset_from_crop and line_y2 < crop_y2 - offset_from_crop

		if x1_within_boundary and y1_within_boundary and x2_within_boundary and y2_within_boundary:
			minmized_line_list.append(line)

	return minmized_line_list

#modify odds of certain characters
def modifyPreds(pred):
	labelNames = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabdefghnqrt"

	i = np.argmax(pred)
	pred[24] += pred[13]		#O is frequently recognized as D, so add that to O
	pred[24] += pred[0]			#doing the same thing with 0 just in case

	#table of characters to modify
	pred[0] = 0                 #0
	pred[1] = 0		            #1
	pred[2] = pred[2] + .30     #2, 3, and 4 are the only common numbers
	pred[3] = pred[3] + .30     #3
	pred[4] = pred[4] + .30     #4
	pred[5] = 0		            #5
	pred[6] = 0		            #6
	pred[7] = 0		            #7
	pred[8] = 0		            #8
	pred[9] = 0		            #9
	pred[10] = 0	            #A
	pred[11] = pred[11]         #B
	pred[12] = pred[12]	+ .2   	#C  is common
	pred[13] = 0                #D  not used
	pred[14] = 0                #E  not used
	pred[15] = pred[15]         #F
	pred[16] = 0                #G  not used
	pred[17] = pred[17]	+ .2   	#H  is common
	pred[18] = pred[18]         #I  used as 'i' and 'l'
	pred[19] = 0                #J  not used
	pred[20] = 0	            #K
	pred[21] = 0		        #L
	pred[22] = 0	            #M
	pred[23] = pred[23]	+ .2   	#N is common
	pred[24] = pred[24]	+ .2	#O is common, multiply because it sucks at recognizing O
	pred[25] = pred[25]         #P
	pred[26] = 0                #Q  not used
	pred[27] = 0	            #R
	pred[28] = pred[28]	        #S
	pred[29] = 0                #T
	pred[30] = 0                #U
	pred[31] = 0                #V
	pred[32] = 0                #W
	pred[33] = 0                #X
	pred[34] = 0                #Y
	pred[35] = 0                #Z
	pred[36] = 0	            #a
	pred[37] = 0	            #b
	pred[38] = 0                #d  not used
	pred[39] = 0   	            #e
	pred[40] = 0                #f
	pred[41] = 0	            #g
	pred[42] = 0                #h  not used
	pred[43] = 0	            #n
	pred[44] = 0                #q  not used
	pred[45] = pred[45]         #r
	pred[46] = 0	            #t

	#these are the most common, so always allow them if they are the max value
	if np.argmax(pred) == 12 and pred[12] > .30:		#C
		pred[12] = pred[12] + 1
	elif np.argmax(pred) == 17 and pred[17] > .30:		#H
		pred[17] = pred[17] + 1
	elif np.argmax(pred) == 23 and pred[23] > .30:		#N
		pred[23] = pred[23] + 1
	elif np.argmax(pred) == 24 and pred[24] > .22:		#O
		pred[24] = pred[24] + 1

	return pred

#convert an image to pure black and white
def pureBlackWhite(picture):
	
	#convert cv2 to pil 
	picture = Image.fromarray(cv2.cvtColor(picture, cv2.COLOR_BGR2RGB))
	pixelMap = picture.load()

	avgColor = 0
	pixelCount = 0

	#find average color
	w, h = picture.size
	for i in range(w):
		for j in range(h):
			b, g, r = picture.getpixel((i, j))
			avgColor = (b + g + r)/3 + avgColor
			pixelCount = pixelCount + 1

	avgColor = avgColor / pixelCount
			
	#convert to pure black and white
	w, h = picture.size
	for i in range(w):
		for j in range(h):
			b, g, r = picture.getpixel((i, j))
			if (r + b + g)/3 < avgColor*0.95:
				pixelMap[i, j] = (0, 0, 0)
			else:
				pixelMap[i, j] = (255, 255, 255)

	#convert pil back to cv2
	picture = np.array(picture)
	picture = picture[:, :, ::-1].copy()

	return picture

												###### UTILITY FUNCTIONS ######

#get average width and height of each letter box (used for dummy crabons)
def avgWH(letterBoxes):

	WTotal = 0
	HTotal = 0
	for i in range(len(letterBoxes)):
		X, Y, W, H, L = letterBoxes[i]
		WTotal = WTotal + W
		HTotal = HTotal + H

	if WTotal > 0 and HTotal > 0:
		WTotal = WTotal/len(letterBoxes)
		HTotal = HTotal/len(letterBoxes)

	return WTotal, HTotal


#get average length of the lines
def avgLineLength(lines):

	totalDistance = 0
	for i in range(len(lines)):
		X1, Y1, X2, Y2 = lines[i]
		distance = math.sqrt((X1 - X2)**2 + (Y1 - Y2)**2)
		totalDistance = totalDistance + distance

	totalDistance = totalDistance / len(lines)

	return totalDistance

#Check if two rectangles intersect
# From https://www.geeksforgeeks.org/find-two-rectangles-overlap/
def intersects(TL1, BR1, TL2, BR2):
	#T = top, L = left, B = bottom, R = right;  represents 2 rectangles

	# define cooridinate indices
	x = 0
	y = 1

	overlaps = True

	# If either rectangle has 0 area, then no overlap
	if TL1[x] == BR1[x] or TL1[y] == BR1[y] or TL2[x] == BR2[x] or TL2[y] == BR2[y]:
		overlaps = False
	
	# If one rectangle is on the left side of another rectangle, then no overlap
	if TL1[x] > BR2[x] or TL2[x] > BR1[x]:
		overlaps = False

	# If one rectangle is above another rectangle, then no overlap
	if TL1[y] > BR2[y] or TL2[y] > BR1[y]:		#(0,0) is top left corner, not bottom right
		overlaps = False
	
	return overlaps

												###### MAPPING FUNCTIONS ######

#map each point of an edge to a letter box
def mapEdges(letter_boxes, lines):
	# Generate a default box size for implicit carbons (the carbons that are two lines meeting) and bond perimeters
	if len(letter_boxes) > 0:
		avgW, avgH = avgWH(letter_boxes)
	else:
		avgW = avgLineLength(lines)/2
		avgH = avgW

	# structures to organize line and node data
	mapped_node_arr: list[mapped_node] = []
	mapped_edge_arr: list[mapped_edge] = []
	for line in lines:
		# exclude lines that are in negative x/y positions
		# if line[0] > 0 and line[1] > 0 and line[2] > 0 and line[3] > 0:
		# 	mapped_edge_arr.append(mapped_edge(line[0], line[1], line[2], line[3], avgW, avgH))
		mapped_edge_arr.append(mapped_edge(line[0], line[1], line[2], line[3], avgW, avgH))

	bound_expand = 3.0    # multiplier for width and height

	# expand the bounds of the letterBoxes, then combine them if they are touching
	combinedLetterBoxes = []			#pass this to combineBoxes
	for bound_x, bound_y, bound_w, bound_h, bound_letter in letter_boxes:
		newBoundX = bound_x - 0.5 * (bound_expand - 1) * bound_w
		newBoundY = bound_y - 0.5 * (bound_expand - 1) * bound_h
		newBoundW = bound_w * bound_expand
		newBoundH = bound_h * bound_expand

		combinedLetterBoxes.append((newBoundX, newBoundY, newBoundW, newBoundH, bound_letter))

	combinedLetterBoxes = combineBoxes(combinedLetterBoxes)			#combine nearby letterboxes
	combinedLetterBoxes = filterLetterBoxes(combinedLetterBoxes)	#make sure labels are acceptable atoms

	#put the combinedLetterBoxes into the mapped_node_arr
	for bound_x, bound_y, bound_w, bound_h, bound_letter in combinedLetterBoxes:
		mapped_node_arr.append(mapped_node(bound_x, bound_y, bound_w, bound_h, bound_letter)) 

	# determine bond types
	for line_one in mapped_edge_arr:
		for line_two in mapped_edge_arr:
			if line_one != line_two:
				if line_one.contained_within_perimeter_midpoint(line_two.x_mid, line_two.y_mid):
					line_one.related_edges.add(line_two)

	# remove edges that are unrelated (but in proximity) while maintaining edges that are part of the double/triple bond structure
	for line in mapped_edge_arr:
		line.minimize_bond_list_by_midpoint()
		line.determine_type()
	
	# minimize double and triple bonds to a single line representation
	new_edge_set = dict()
	for line in mapped_edge_arr:
		try:
			new_edge_set[line]
		except KeyError:
			# DNE as key, check values
			exists_as_value = False
			for value in new_edge_set.values():
				for item in value:
					if item == line:
						exists_as_value = True
			if not exists_as_value:
				new_edge_set[line] = line.related_edges
	

	# replace with minimized edge list
	mapped_edge_arr = new_edge_set.keys()

	# Create implicit carbons
	for line in mapped_edge_arr:
		notMatched1 = True
		notMatched2 = True

		# do not create an implicit carbon if the line point is near a letter
		for node in mapped_node_arr:
			if node.contained_in_boundaries(line.x1, line.y1):
				notMatched1 = False
			if node.contained_in_boundaries(line.x2, line.y2):
				notMatched2 = False

		if notMatched1:
			mapped_node_arr.append(mapped_node(line.x1 - 1.3*avgW/2, line.y1 - 1.3*avgH/2, 1.3*avgW, 1.3*avgH, 'C'))
		if notMatched2:
			mapped_node_arr.append(mapped_node(line.x2 - 1.3*avgW/2, line.y2 - 1.3*avgH/2, 1.3*avgW, 1.3*avgH, 'C'))

	# Initialize a 2d array full of 0's
	edge_list = [['+']*len(mapped_node_arr) for i in range(len(lines))]

	# Match lines with nodes
	index_row = 0
	index_col = 0
	for line in mapped_edge_arr:
		for node in mapped_node_arr:
			if node.contained_in_boundaries(line.x1, line.y1) and node.contained_in_boundaries(line.x2, line.y2):
				pass
			elif node.contained_in_boundaries(line.x1, line.y1):
				# update node list and bond list
				line.related_nodes.add(node)
				node.related_edges.add(line)

				# 2d arr
				edge_list[index_row][index_col] = node.type_is
			elif node.contained_in_boundaries(line.x2, line.y2):
				# update node list and bond list
				line.related_nodes.add(node)
				node.related_edges.add(line)

				# 2d arr
				edge_list[index_row][index_col] = node.type_is 
			index_col += 1
		index_row += 1
		index_col = 0

	return mapped_node_arr, mapped_edge_arr

# get combine touching letterboxes to form polyatomic and multicharacter elements
def combineBoxes(letterBoxes):

	letterGroups = []			#will store data for new letterBoxes
	newLetterBoxes = []			#the new letter boxes, return value
	grouped = set()

	# get average width and height for later
	avgWidth, avgHeight = avgWH(letterBoxes)
	avgSize = avgWidth * avgHeight

	boundBoxExpand = 0.65		#we are shrinking the bounding boxes because they are too big for this part,
									#but fine for lines

	#create group for letterBox i
	for i in range(len(letterBoxes)):
		#only search rectantles that haven't been searched
		if i not in grouped:
			newGroup = []
			X1, Y1, W1, H1, L1 = letterBoxes[i]

			#make a group for rectangle i
			newGroup.append(letterBoxes[i])
			grouped.add(i)

			#check if each letterBox intersects.
			for j in range(i + 1, len(letterBoxes)):
				X2, Y2, W2, H2, L2 = letterBoxes[j]

				#shrink rectangle j's bounds
				X2 = X2 - 0.5 * (boundBoxExpand - 1) * W2
				Y2 = Y2 - 0.5 * (boundBoxExpand - 1) * H2
				W2 = W2 * boundBoxExpand
				H2 = H2 * boundBoxExpand

				#check if each member of the current group intersects rectangle j
				for k in range(len(newGroup)):
					X1, Y1, W1, H1, L1 = newGroup[k]
					#shrink rectangle i's bounds
					X1 = X1 - 0.5 * (boundBoxExpand - 1) * W1
					Y1 = Y1 - 0.5 * (boundBoxExpand - 1) * H1
					W1 = W1 * boundBoxExpand
					H1 = H1 * boundBoxExpand
					
					#if the character intersects and isn't i, make sure the new box will have appropriate dimensions
					if j not in grouped and intersects((X1, Y1), (X1 + W1, Y1 + H1), (X2, Y2), (X2 + W2, Y2 + H2)):
						cX, cY, cW, cH, cL = letterBoxes[j]
						calcX1 = [cX]
						calcY1 = [cY]
						calcX2 = [cX + cW]
						calcY2 = [cY + cH]
						for letterBox in newGroup:
							x, y, w, h, l = letterBox
							calcX1.append(x)
							calcY1.append(y)
							calcX2.append(x+w)
							calcY2.append(y+h)
						BX1 = min(calcX1)
						BY1 = min(calcY1)
						BX2 = max(calcX2)
						BY2 = max(calcY2)
						BWidth = BX2 - BX1
						BHeight = BY2 - BY1
						#if the box has appropriate dimensions, add it to the new group, otherwise skip it
						if BWidth * BHeight < 5*avgSize and BHeight < 2.5*avgHeight:
							newGroup.append(letterBoxes[j])
							grouped.add(j)
							j = i + 1			#restart loop

			letterGroups.append(newGroup)

	#now that the groups are formed, sort the characters in each group from left to right
	#I'm not making some complicated sort to sort like 4 values, we're using bubble sort
	#for each letter group
	for i in range(len(letterGroups)):
		#bubble sort
		for j in range(len(letterGroups[i])):
			for k in range(len(letterGroups[i])):
				#compare x + y values
				if letterGroups[i][j][0] < letterGroups[i][k][0]:
					temp = letterGroups[i][j]
					letterGroups[i][j] = letterGroups[i][k]
					letterGroups[i][k] = temp
	
	
	#with the letter group items now sorted, we can condense them into a single item
	for i in range(len(letterGroups)):
		labelName = ""			#label name for the new letterBox item
		TLXs = []				#rectangular bounds for the new letterBox item
		TLYs = []
		BRXs = []
		BRYs = []
		#collect letterBox info
		for j in range(len(letterGroups[i])):
			X, Y, W, H, L = letterGroups[i][j]
			labelName += L
			TLXs.append(X)
			TLYs.append(Y)
			BRXs.append(X + W)
			BRYs.append(Y + H)	
		#add the data to the newLetterBoxes
		if len(letterBoxes) > 0:
			newLetterBoxes.append((min(TLXs), min(TLYs), max(BRXs) - min(TLXs), max(BRYs) - min(TLYs), labelName))
	

	return newLetterBoxes

#make sure the letterBoxes have acceptable characters
def filterLetterBoxes(letterBoxes):
	#this shouldn't affect polyatomics
	acceptableCharacters = CONSTANT.ATOM_SYMBOL_TO_NAME_DICT.keys()

	newLetterBoxes = []
	for letterBox in letterBoxes:
		x, y, w, h, label = letterBox
		#get rid of leading numbers
		startIndex = 0
		for i in range(len(label)):
			if label[i].isnumeric():
				startIndex = i + 1
			else:
				break			#once we find a non-numeric character, leave loop
		
		label = label[startIndex:]		#no more leading numbers

		#get rid of multi-digit numbers
		newLabel = ""
		startIndex = 0
		for i in range(len(label)):
			if i != 0:
				if label[i - 1].isnumeric() and label[i].isnumeric():
					pass		#don't add character to label
				else:
					newLabel += label[i]
			else:
				newLabel += label[i]
		label = newLabel

		#go through and change recognized characters to charcters in atoms
		#we have to do this because some characters aren't recognized by the model
		#they aren't recognized because they are too similiar to other characters
		newLabel = ""
		for i in range(len(label)):
			if i != len(label) - 1:
				if label[i] == 'L' and label[i + 1] == 'I':
					newLabel += "L"
					newLabel += "i"
					i = i + 1
				elif label[i] == 'A' and label[i + 1] == 'I':
					newLabel += 'A'
					newLabel += 'i'
					i = i + 1
				elif label[i] == 'S' and label[i + 1] == 'I':
					newLabel += 'S'
					newLabel += 'i'
					i = i + 1
				elif label[i] == 'C' and label[i + 1] == 'I':
					newLabel += 'C'
					newLabel += 'i'
					i = i + 1
				elif label[i] == 'A' and label[i + 1] == 'S':
					newLabel += 'A'
					newLabel += 's'
					i = i + 1
				elif label[i] == 'B' and label[i + 1] == 'I':
					newLabel += 'B'
					newLabel += 'i'
					i = i + 1
				else:
					newLabel += label[i]
			else:
				newLabel += label[i]
				break
		label = newLabel

		newLabel = ""
		#only keep elements in the acceptable characters list
		for i in range(len(label)):
			#get 2 character pair
			if i != len(label) - 1:
				twoChar = label[i] + label[i + 1]
			else:
				twoChar = label[i]

			if twoChar in acceptableCharacters:
				newLabel += twoChar
				i = i + 1
			#if it isn't a two character element, check if its a 1 character element
			elif label[i] in acceptableCharacters:
				newLabel += label[i]
			#always add numbers, they have already been filtered
			elif label[i].isnumeric():
				newLabel += label[i]
			if i >= len(label):			#we are modifying i, so manually exit loop
				break
		label = newLabel

		#only keep the letterbox if it isn't empty or I (I is only used for multicharacter elements)
		if(len(label) > 0 and label != "I"):
			newLetterBoxes.append((x, y, w, h, label))
	
	return newLetterBoxes

# get rid of unnessessary lines
def condenseLines(linesArg, avgSquare):

	#convert lines argument into a better array
	allLines = []
	for i in range(len(linesArg)):
		allLines.append(linesArg[i][0])

	lines = []
	# get rid of short lines, anything shorter than the square's width is gotten rid of
	for i in range(len(allLines)):
		X1, Y1, X2, Y2 = allLines[i]
		distance = math.sqrt((X1 - X2)**2 + (Y1 - Y2)**2)
		if distance > avgSquare / 1.5:
			lines.append(allLines[i])

	condensedLines = []
	isPair = True
	while isPair:
		isPair = False
		distances = []
		#first line data
		for i in range(len(lines)):
			#end loop early when it should have ended anyways (python issue or something, fixes bug)
			if i >= len(lines):
				break

			#get angle of first line
			X1, Y1, X2, Y2 = lines[i]
			if X1 - X2 == 0:
				angle1 = math.pi / 2
			else:
				angle1 = math.atan((Y1 - Y2) / (X1 - X2)) 

			#find angle flipped 90 degrees (important for angles close to 90 degrees or -90 degrees)
			if Y1 - Y2 == 0:
				sideAngle1 = math.pi / 2
			else:
				sideAngle1 = math.atan((X1 - X2) / (Y1 - Y2))
			
			#second line data
			for j in range(len(lines)):

				#get angle of second line
				XX1, YY1, XX2, YY2 = lines[j]
				if XX1 - XX2 == 0:
					angle2 = math.pi / 2
				else:
					angle2 = math.atan((YY1 - YY2) / (XX1 - XX2))

				#find angle flipped 90 degrees
				if YY1 - YY2 == 0:
					sideAngle2 = math.pi / 2
				else:
					sideAngle2 = math.atan((XX1 - XX2) / (YY1 - YY2))

				#if parallel and different lines, record distance
				if ((abs(angle1 - angle2) < math.pi / 12) or (abs(sideAngle1 - sideAngle2) < math.pi / 12)) and i != j:
					isPair = True
					#get midpoints of each line to calculate distance
					midX = (X1 + X2)/2
					midY = (Y1 + Y2)/2
					midXX = (XX1 + XX2)/2
					midYY = (YY1 + YY2)/2
					#add distances between midpoints of lines to distances
					distances.append((math.sqrt((midX - midXX)**2 + (midY - midYY)**2), i, j))

		if isPair:
			#find smallest distance
			smallestDistance, ii, jj = distances[0]
			for i in range(len(distances)):
				if distances[i][0] < smallestDistance:
					smallestDistance, ii, jj = distances[i]

			#find the largest of the two lines in the pair
			X1, Y1, X2, Y2 = lines[ii]
			length = math.sqrt((X1 - X2)**2 + (Y1 - Y2)**2)
			XX1, YY1, XX2, YY2 = lines[jj]
			llength = math.sqrt((XX1 - XX2)**2 + (YY1 - YY2)**2)
			if length < llength:
				X1, Y1, X2, Y2 = XX1, YY1, XX2, YY2

			#add line to condensed lines list, and remove the original lines from the lines list
			condensedLines.append((X1, Y1, X2, Y2))
			lines.pop(jj)
			lines.pop(ii)
   
	return condensedLines











						
