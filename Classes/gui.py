import tkinter as tk
import math
from tkinter import NORMAL, font, Label, Toplevel, filedialog as fido
from tkinter import ttk # duplicate
from PIL import Image, ImageTk
import cv2
import os
from Classes.graph import Graph
from Classes.bonds import Bond
from Classes.bonds import CovalentBond
from Classes.bonds import SingleBond
from Classes.bonds import DoubleBond
from Classes.bonds import TripleBond
from Classes.atom import Atom
import Classes.constants as CONSTANT
from Classes.adapter_classes import translate_molecule
import Image_Recognition.Recognizer as Recognizer
import time
"""
import RPi.GPIO as GPIO
from picamera import PiCamera
from gpiozero import Button

# Sets up the PiCamera and the Pi's GPIO pins
GPIO.setmode(GPIO.BCM)
camera = PiCamera()
BUTTON_PIN = Button(16)
LED_RED_PIN = 12
LED_GREEN_PIN = 1
GPIO.setup(LED_RED_PIN, GPIO.OUT)
GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
"""

# Geometry for popups
popup_width = 300
popup_height = 100

# main class for the GUI application
class Gui_Edit_Molecule():
	def __init__(self, window: tk.Tk):
		#class-wide lists
		self.letters = []			#holds letter IDs
		self.atom_list = []			#holds atom objects for graph
		self.letterBondings = []	#parallel array for letters, holds bonded lines
									#i = letter, j = bond, k = bond info, l (only for k = 0) = parts of bond
		
		self.singleBonds = []		#holds single bond IDs
		self.doubleBonds = []		#holds double bond IDs
		self.tripleBonds = []		#holds triple bond IDs
		self.single_bond_list = []	#holds single bond objects for the graph
		self.double_bond_list = []	#holds double bond objects for the graph
		self.triple_bond_list = []	#holds triple bond objects for the graph
		#kinda sucks to have 3 lists for the bonds, but it is much easier to manage the lists this way
		self.graph = Graph([])
		
		# Fonts for the UI
		self.UIFont1 = font.Font(family = 'Ariel', size = 12)
		self.UIEFPi = font.Font(family = 'Ariel', size = 9)

		# create the frame for the GUI
		self.window = window
		self.x = self.y = 0

##################################################   Formatting for full screen Pi, full screen desktop, and test mode    ##################################################
	# Rapsberry Pi Fullscreen mode
		#self.window.geometry("800x480")
		#self.canvas = tk.Canvas(self.window, bg="white", width=(self.window.winfo_screenwidth()-112), height=(self.window.winfo_screenheight()-80))

	# Full screen desktop
		self.window.attributes('-fullscreen',True)
		self.canvas = tk.Canvas(self.window, bg="white", width=(self.window.winfo_screenwidth()-100), height=(self.window.winfo_screenheight()-100))

	# Test mode desktop
		#self.canvas = tk.Canvas(self.window, bg="white", width=(self.window.winfo_screenwidth()-500), height=(self.window.winfo_screenheight()-500))
##########################################################################################################################################################################
		#create dropdown menu for atoms
		self.atomDropDownName1 = tk.StringVar()
		self.atomDropDownName1.set("Add Atom")
		self.options = ["H", "C", "B", "N", "O", "F", "Si", "P", "S", "Cl", "Br"]
		self.dropdown1 = tk.OptionMenu(self.window, self.atomDropDownName1, *self.options, command=self.dropdown_select_option)
		self.dropdown1.config(font = self.UIFont1)
		
		# create dropdown menu for adding polyatomic atoms
		self.atomDropDownName2 = tk.StringVar()
		self.atomDropDownName2.set("Add PolyAtom")
		self.options = {
			"SO\u2084\u00B2\u207B": "SO4",
			"HSO\u2084\u207B": "HSO4",
			"SO\u2083\u00B2\u207B": "SO3",
			"NO\u2083\u207B": "NO3",
			"NO\u2082\u207B": "NO2",
			"PO\u2084\u207B\u00B3": "PO4",
			"HPO\u2084\u00B2\u207B": "HPO4",
			"H\u2082PO\u2084\u207B": "H2PO4",
			"PO\u2083\u207B\u00B3": "PO3",
			"OH\u207B": "OH",
			"ClO\u2084\u207B": "ClO4",
			"ClO\u2083\u207B": "ClO3",
			"ClO\u2082\u207B": "ClO2",
			"\u207BOCl": "OCl",
			"CN\u207B": "CN",
			"\u207BOCN": "OCN", 
			"SCN\u207B": "SCN" ,
			"CO\u2083\u00B2\u207B": "CO3",
			"C\u2082O\u2084\u207B\u00B2": "C2O4"
		}
		self.dropdown2 = tk.OptionMenu(self.window, self.atomDropDownName2, *self.options, command=self.dropdown_select_option)
		self.dropdown2.config(font = self.UIFont1)	
		
		# Intializes an empty list letters to store the Letters objects.
		self.letters = []

		# init for Input Field
		self.Comment_Field = tk.Entry(width = int((self.window.winfo_screenwidth()/8)-10), font = self.UIEFPi)
		self.Comment_Field.insert(0, "Welcome to OCRI!")

		# Initialize the buttons
		self.btn_single_bond =		tk.Button(text="Single Bond", 	wraplength = 75, 	font = self.UIFont1, command=self.create_single_bond, state = tk.DISABLED)
		self.btn_double_bond = 		tk.Button(text="Double Bond", 	wraplength = 75, 	font = self.UIFont1, command=self.create_double_bond, state = tk.DISABLED)
		self.btn_triple_bond = 		tk.Button(text="Triple Bond",	wraplength = 75, 	font = self.UIFont1, command=self.create_triple_bond, state = tk.DISABLED)
		self.is_bond_active = False
		self.btn_delete = 			tk.Button(text="Delete", 							font = self.UIFont1, command=self.activate_delete	, state = tk.DISABLED)
		self.is_delete_active = False
		self.btn_clear = 			tk.Button(text="Clear", 							font = self.UIFont1, command=self.clear				, state = tk.DISABLED)
		self.btn_import_file = 		tk.Button(text="Import", 							font = self.UIFont1, command=self.browseFiles)
		self.btn_translate_image = 	tk.Button(text="Translate Image",wraplength = 75,	font = self.UIFont1, command=self.send_image		, state = tk.DISABLED)
		self.btn_photo = 			tk.Button(text="Photo", 							font = self.UIFont1, command=self.capture_check)
		self.btn_quit = 			tk.Button(text="Exit", 								font = self.UIFont1, command=self.exit_ocri)
		
		# Place widgets on the grid
		# Full Screen App
		self.dropdown1.grid				(row = 0, column = 1, sticky = 'e')
		self.dropdown2.grid				(row = 0, column = 2)
		self.canvas.grid				(row = 1, column = 0, rowspan = 9, columnspan = 3)
		self.btn_single_bond.grid		(row = 1, column = 3, sticky = 'nesw')
		self.btn_double_bond.grid		(row = 2, column = 3, sticky = 'nesw')
		self.btn_triple_bond.grid		(row = 3, column = 3, sticky = 'nesw')
		self.btn_delete.grid			(row = 4, column = 3, sticky = 'nesw')
		self.btn_clear.grid				(row = 5, column = 3, sticky = 'nesw')
		self.btn_import_file.grid		(row = 6, column = 3, sticky = 'nesw')
		self.btn_translate_image.grid	(row = 7, column = 3, sticky = 'nesw')
		self.btn_photo.grid				(row = 8, column = 3, sticky = 'nesw')
		self.btn_quit.grid				(row = 9, column = 3, sticky = 'nesw')
		self.Comment_Field.grid			(row = 10, column = 0, sticky = 'nesw', columnspan = 4)

#############################################  ATOMS, DROPDOWN and LETTERS   #####################################################

	#for select atom dropdown
	def dropdown_select_option(self, option):
		# clear if line was clicked
		self.clear_line_creation()
		self.Comment_Field.delete(0, "end")
		self.Comment_Field.insert(0, "Click a location on the canvas to place the atom")

		self.selected_option = option
		self.canvas.bind("<Button-1>", self.place_letter)
		if self.canvas.find_all() == ():
			self.canvas_cleared()
	
	#place a letter on the canvas
	def place_letter(self, event):
		
		try:
			# append polyatomic with subscripts but WITHOUT charges
			temp_option = CONSTANT.POLYATOMIC_UNICODE_CHARGES_TO_POLYATOMIC_NO_CHARGES[self.selected_option]
			#test if letter is being placed in a letter. If it is, then change the existing letter instead
			self.textbox = self.canvas.create_text(event.x, event.y, text=temp_option, font=("Arial", 20), tags="letter")	
		except KeyError:
			# not polyatomic, change nothing
			self.textbox = self.canvas.create_text(event.x, event.y, text=self.selected_option, font=("Arial", 20), tags="letter")
			None

		self.letters.append(self.textbox)

		#add atom object
		try:
			# translate polyatomic to non-unicode for backend
			self.selected_option = CONSTANT.FRONT_END_TO_BACKEND_POLYATOMIC[self.selected_option]
		except KeyError:
			None

		atom = Atom(self.selected_option)
		self.atom_list.append(atom)
		self.graph.add_node_via_atom_obj(atom)
		self.selected_option = None
		self.letterBondings.append([])
		self.canvas.unbind("<Button-1>")
		self.canvas.tag_bind(self.textbox, '<Button-1>', self.select_textbox)
		self.canvas.tag_bind(self.textbox, '<B1-Motion>', self.move_textbox)
		self.canvas.tag_bind(self.textbox, '<ButtonRelease-1>', self.deselect_textbox)
		# reset dropdowns once letter is placed
		if self.atomDropDownName2:
			self.atomDropDownName2.set("Add PolyAtom")
		if self.atomDropDownName1:
			self.atomDropDownName1.set("Add Atom")
		self.enable_buttons()

	def select_textbox(self, event):
		self.selected = True
		self.current_x = event.x
		self.current_y = event.y
		for ID in self.letters:
			x, y = self.canvas.coords(ID)
			if event.x < x + 20 and event.x > x - 20 and event.y < y + 20 and event.y > y - 20:
				self.textbox = ID
				break

	def move_textbox(self, event):
		if self.selected:
			dx = event.x - self.current_x
			dy = event.y - self.current_y
			self.canvas.move(self.textbox, dx, dy)
			self.current_x = event.x
			self.current_y = event.y

			#move lines
			index = self.letters.index(self.textbox)
			for i in range(len(self.letterBondings[index])):
				#get anchor points for the line
				x1, y1 = self.canvas.coords(self.textbox)
				x2, y2 = self.canvas.coords(self.letterBondings[index][i][1])     
				
				#calculate points for the line
				if x1 - x2 != 0:
					angle = math.atan((y1 - y2)/(x1 - x2))
				elif y1 >= y2:
					angle = math.pi/2
				elif y1 < y2:
					angle = -math.pi/2
				if x1 >= x2:
					x1 = x1 - 20*math.cos(angle)
					x2 = x2 + 20*math.cos(angle)
					y1 = y1 - 20*math.sin(angle)
					y2 = y2 + 20*math.sin(angle)
				else:
					x1 = x1 + 20*math.cos(angle)
					x2 = x2 - 20*math.cos(angle)
					y1 = y1 + 20*math.sin(angle)
					y2 = y2 - 20*math.sin(angle)

				#update line
				for lineID in self.letterBondings[index][i][0]:
					self.canvas.coords(lineID, x1, y1, x2, y2)
		
	# sets the selected attribute to False so only one letter will be placed at a time.
	# To add another letter the Add Atom menu needs another selection of what needs added.
	def deselect_textbox(self, event):
		self.selected = False

###################################################  PICTURES, AI, and CAMERA  ###################################################

	# draws a rectangle outline for the browseFiles def
	def drawrectangle(self):
		self.canvas.bind("<ButtonPress-1>", self.on_button_press)
		self.canvas.bind("<B1-Motion>", self.on_move_press)
		self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

		self.rect = None

		self.start_x = None
		self.start_y = None

	# gets the first x and y cord and updates it for drawing the rect
	def on_button_press(self, event):
		# save mouse drag start position
		self.Comment_Field.delete(0, "end")
		self.Comment_Field.insert(0, "Release to confirm crop rectangle")

		if self.rect is not None:
			self.canvas.delete(self.rect)
			self.rect = None

		self.start_x = event.x
		self.start_y = event.y

		self.cropX = event.x
		self.cropY = event.y

		# create rectangle if not yet exist
		#if not self.rect:
		self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline="black")

	# updates the x and y as the mouse is moved while B1 is pressed
	def on_move_press(self, event):
		curX, curY = (event.x, event.y)

		# expand rectangle as you drag the mouse
		self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

	# once released unbind the mouse events for drawing a rectangle
	def on_button_release(self, event):
		self.cropX2 = event.x
		self.cropY2 = event.y
		self.Comment_Field.delete(0, "end")
		self.Comment_Field.insert(0, "Transfer image when ready or repeat cropping procedure")

	# Command for the import button
	def browseFiles(self):
		if self.canvas.find_all() == ():
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "File browser deployed")
			self.fileb_exe()
		else:
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Warning: Popup window deployed!")
			self.fileb_popup()

	# Command for Camera Capture
	def capture_check(self):
		if self.canvas.find_all() == ():
			self.camera_capture()
		else:
			self.camera_popup()


	# Command for translate image button
	def send_image(self):
		self.Comment_Field.delete(0, "end")
		self.Comment_Field.insert(0, "Image is being translated. Please wait...")

		#calculate crop dimensions
		imageWidth, imageHeight = self.PILimage.size
		xMargin = self.canvas.winfo_width()/2 - imageWidth/2
		yMargin = self.canvas.winfo_height()/2 - imageHeight/2
		self.cropX = self.cropX - xMargin
		self.cropY = self.cropY - yMargin
		self.cropX2 = self.cropX2 - xMargin
		self.cropY2 = self.cropY2 - yMargin

		#allow for any orientation of crop rectangle
		if self.cropX > self.cropX2:
			temp = self.cropX
			self.cropX = self.cropX2
			self.cropX2 = temp
		if self.cropY > self.cropY2:
			temp = self.cropY
			self.cropY = self.cropY2
			self.cropY2 = temp

		#scale crop info
		tempImage = Image.open(self.image_name)
		tempImageWidth, tempImageHeight = tempImage.size
		widthRatio = tempImageWidth / imageWidth
		heightRatio = tempImageHeight / imageHeight
		self.cropX = self.cropX * widthRatio
		self.cropX2 = self.cropX2 * widthRatio
		self.cropY = self.cropY * heightRatio
		self.cropY2 = self.cropY2 * heightRatio

		#send data to the recognizer
		self.clear_canvas()
		try:
			self.canvas.unbind("<ButtonPress-1>")
			self.canvas.unbind("<B1-Motion>")
			self.canvas.unbind("<ButtonRelease-1>")
			mapped_node_arr, mapped_edge_arr = Recognizer.recognize(self.cropX, self.cropY, self.cropX2, self.cropY2, self.image_name)
			self.graph = translate_molecule(mapped_edge_arr, mapped_node_arr)
			self.translate_enable_buttons()
			self.place_atoms_into_canvas()
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Image Recognized")
		except ValueError:
			self.canvas.unbind("<ButtonPress-1>")
			self.canvas.unbind("<B1-Motion>")
			self.canvas.unbind("<ButtonRelease-1>")
			self.translate_enable_buttons()
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Error recognizing image")

	# Creates a popup window after the filebrowser has selected an image.
	def crop_popup(self):

		self.disable_buttons()

		def accept():
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Image accepted, please translate image")
			self.btn_translate_image.configure(state = tk.NORMAL)
			self.btn_quit.configure(state = tk.NORMAL)
			popup.destroy()
			#set crop to maximum bounds
			self.cropX = 0		#undercrop will be set to zero in the recognizer
			self.cropY = 0
			self.cropX2 = self.canvas.winfo_width()		#overcrop won't matter
			self.cropY2 = self.canvas.winfo_height()

		def crop():
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Crop image by holding down the left mouse button and dragging, release when the black rectangle is around what you want to be translated")
			self.btn_translate_image.configure(state = tk.NORMAL)
			self.btn_quit.configure(state = tk.NORMAL)
			popup.destroy()
			self.drawrectangle()

		def cancel():
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Import canceled")
			self.translate_enable_buttons()
			self.canvas_cleared()
			popup.destroy()
			self.canvas.delete("all")

		popup = tk.Tk()
		popup.title("Confirm")
		# center the popup on the original canvas
		widthp = popup.winfo_screenwidth()
		heightp = popup.winfo_screenheight()
		popupx = (widthp/2) - (popup_width/2)
		popupy = (heightp/2) - (popup_height/2)
		popup.geometry('%dx%d+%d+%d' % (popup_width, popup_height, popupx, popupy))

		button_accept = ttk.Button(popup, text = "Accept", command = accept)
		button_accept.pack()

		button_crop = ttk.Button(popup, text = "Crop", command = crop)
		button_crop.pack()

		button_cancel = ttk.Button(popup, text = "Cancel", command = cancel)
		button_cancel.pack()

		popup.protocol("WM_DELETE_WINDOW", cancel)
		popup.mainloop()

	# Clear canvas popup window, will ask if they want to clear the whole canvas or not
	def clear(self):
		self.disable_buttons()
		self.Comment_Field.delete(0, "end")
		self.Comment_Field.insert(0, "Warning: Popup window deployed!")

		def yes():
			self.canvas.delete("all")
			warning.destroy()
			self.enable_buttons()
			self.canvas_cleared()

			self.empty_properties()
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Canvas cleared")

		def no():
			warning.destroy()
			self.enable_buttons()
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Clear canceled")
		
		warning = tk.Tk()
		warning.title("Warning")
		# center the popup on the original canvas
		widthp = warning.winfo_screenwidth()
		heightp = warning.winfo_screenheight()
		popupx = (widthp/2) - (popup_width/2)
		popupy = (heightp/2) - (popup_height/2)
		warning.geometry('%dx%d+%d+%d' % (popup_width, popup_height, popupx, popupy))

		warning_label = Label(warning, text = "Are you sure you want to delete all items?")
		warning_label.pack()

		button_yes = ttk.Button(warning, text = "Yes", command = yes)
		button_yes.pack()

		button_no = ttk.Button(warning, text = "No", command = no)
		button_no.pack()

		warning.protocol("WM_DELETE_WINDOW", no)
		warning.mainloop()

	# Popup for the file import button, will give the option to continue with the import and clear the screen or
	# cancel the import and keep what is on the canvas
	def fileb_popup(self):
		self.disable_buttons()

		def yes():
			self.canvas.delete("all")
			warning.destroy()
			self.enable_buttons()
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "File browser deployed")
			self.fileb_exe()

			#empty properties when clearing
			self.empty_properties()
		def no():
			warning.destroy()
			self.enable_buttons()
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Import canceled")
		
		warning = tk.Tk()
		warning.title("Warning")
		# center the popup on the original canvas
		widthp = warning.winfo_screenwidth()
		heightp = warning.winfo_screenheight()
		popupx = (widthp/2) - (popup_width/2)
		popupy = (heightp/2) - (popup_height/2)
		warning.geometry('%dx%d+%d+%d' % (popup_width, popup_height, popupx, popupy))

		warning_label = Label(warning, text = "This action will clear workspace, are you sure you want to continue?", wraplength = 200)
		warning_label.pack()

		button_yes = ttk.Button(warning, text = "Yes", command = yes)
		button_yes.pack()

		button_no = ttk.Button(warning, text = "No", command = no)
		button_no.pack()

		warning.protocol("WM_DELETE_WINDOW", no)
		warning.mainloop()
	
	# Function for opening the file browser
	def fileb_exe(self):
		self.image_name = fido.askopenfilename(title = "Pick your image")
		if self.image_name:
			self.clear_canvas()
			self.PILimage = Image.open(self.image_name)
			
			#resize image to fit in canvas
			self.showImage()
		
			# Creates popup window
			self.crop_popup()

	#shows the image on the canvas, scales it down too
	#assign self.PILimage to use
	def showImage(self):
		#resize image to fit in canvas
		imageWidth, imageHeight = self.PILimage.size
		imageProportion = imageWidth/imageHeight
		if imageHeight > self.canvas.winfo_height():
			imageHeight = self.canvas.winfo_height()
			imageWidth = imageHeight * imageProportion
		if imageWidth > self.canvas.winfo_width():
			imageWidth = self.canvas.winfo_width()
			imageHeight = imageWidth / imageProportion
		self.PILimage = self.PILimage.resize((int(imageWidth), int(imageHeight)))

		self.image = ImageTk.PhotoImage(self.PILimage)		#convert to tkinter image
		self.canvas.create_image((self.canvas.winfo_width()/2, self.canvas.winfo_height()/2), image = self.image, anchor = tk.CENTER)

	# Popup for the camera button, will give the option to continue with the capture and clear the screen or
	# cancel the capture and keep what is on the canvas
	def camera_popup(self):
		self.disable_buttons()

		def yes():
			self.canvas.delete("all")
			warning.destroy()
			self.enable_buttons()
			self.camera_capture()

			#empty properties when clearing
			self.empty_properties()
		def no():
			warning.destroy()
			self.enable_buttons()
		
		
		warning = tk.Tk()
		warning.title("Warning")
		# center the popup on the original canvas
		widthp = warning.winfo_screenwidth()
		heightp = warning.winfo_screenheight()
		popupx = (widthp/2) - (popup_width/2)
		popupy = (heightp/2) - (popup_height/2)
		warning.geometry('%dx%d+%d+%d' % (popup_width, popup_height, popupx, popupy))

		warning_label = Label(warning, text = "This action will clear workspace, are you sure you want to continue?", wraplength = 200)
		warning_label.pack()

		button_yes = ttk.Button(warning, text = "Yes", command = yes)
		button_yes.pack()

		button_no = ttk.Button(warning, text = "No", command = no)
		button_no.pack()

		warning.protocol("WM_DELETE_WINDOW", no)
		warning.mainloop()

	def camera_capture(self):

		"""
		camera.start_preview()
		time.sleep(2)
		GPIO.output(LED_GREEN_PIN, GPIO.HIGH)
		BUTTON_PIN.wait_for_press()
		GPIO.output(LED_GREEN_PIN, GPIO.LOW)

		GPIO.output(LED_RED_PIN, GPIO.HIGH)
		time.sleep(2)
		camera.capture('/home/abissell/Desktop/Github/OCRI/Test.jpg')
		camera.stop_preview()
		self.Comment_Field.delete(0, "end")
		self.Comment_Field.insert(0, "Image Captured!")
		GPIO.output(LED_RED_PIN, GPIO.LOW)

		self.clear_canvas()
		self.temp = cv2.imread('/home/abissell/Desktop/Github/OCRI/Test.jpg')
		self.temp = cv2.rotate(self.temp, cv2.ROTATE_90_CLOCKWISE)
		cv2.imwrite('Test.jpg', self.temp)
		self.PILimage = Image.open('/home/abissell/Desktop/Github/OCRI/Test.jpg')
		self.image_name = '/home/abissell/Desktop/Github/OCRI/Test.jpg'

		#resize image to fit in canvas
		self.showImage()

		#Creates popup window
		self.crop_popup()
		"""

	def exit_ocri(self):
		self.disable_buttons()
		self.btn_quit.configure(state = tk.DISABLED)
		
		def yes():
			warning.destroy()
			#GPIO.cleanup()
			self.window.destroy()
			exit()
		def no():
			warning.destroy()
			self.enable_buttons()
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Exit canceled")
		
		warning = tk.Tk()
		warning.title("Quit")
		# center the popup on the original canvas
		widthp = warning.winfo_screenwidth()
		heightp = warning.winfo_screenheight()
		popupx = (widthp/2) - (popup_width/2)
		popupy = (heightp/2) - (popup_height/2)
		warning.geometry('%dx%d+%d+%d' % (popup_width, popup_height, popupx, popupy))

		warning_label = Label(warning, text = "Are you sure you want to quit OCRI?")
		warning_label.pack()

		button_yes = ttk.Button(warning, text = "Yes", command = yes)
		button_yes.pack()

		button_no = ttk.Button(warning, text = "No", command = no)
		button_no.pack()

		warning.protocol("WM_DELETE_WINDOW", no)
		warning.mainloop()


	# Specific for the translate_image being disabled after it translates the image
	def translate_enable_buttons(self):
		self.btn_single_bond.configure(state = tk.NORMAL)
		self.btn_double_bond.configure(state = tk.NORMAL)
		self.btn_triple_bond.configure(state = tk.NORMAL)
		self.btn_delete.configure(state = tk.NORMAL)
		self.btn_clear.configure(state = tk.NORMAL)
		self.btn_import_file.configure(state = tk.NORMAL)
		self.btn_translate_image.configure(state = tk.DISABLED)
		self.btn_photo.configure(state = tk.NORMAL)
		self.btn_quit.configure(state = tk.NORMAL)
		self.dropdown1.configure(state = tk.NORMAL)
		self.dropdown2.configure(state = tk.NORMAL)

	def disable_buttons(self):
		self.btn_single_bond.configure(state = tk.DISABLED)
		self.btn_double_bond.configure(state = tk.DISABLED)
		self.btn_triple_bond.configure(state = tk.DISABLED)
		self.btn_delete.configure(state = tk.DISABLED)
		self.btn_clear.configure(state = tk.DISABLED)
		self.btn_import_file.configure(state = tk.DISABLED)
		self.btn_photo.configure(state = tk.DISABLED)
		#self.btn_quit.configure(state = tk.DISABLED)
		self.dropdown1.configure(state = tk.DISABLED)
		self.dropdown2.configure(state = tk.DISABLED)

	def enable_buttons(self):
		self.btn_single_bond.configure(state = tk.NORMAL)
		self.btn_double_bond.configure(state = tk.NORMAL)
		self.btn_triple_bond.configure(state = tk.NORMAL)
		self.btn_delete.configure(state = tk.NORMAL)
		self.btn_clear.configure(state = tk.NORMAL)
		self.btn_import_file.configure(state = tk.NORMAL)
		self.btn_photo.configure(state = tk.NORMAL)
		self.btn_quit.configure(state = tk.NORMAL)
		self.dropdown1.configure(state = tk.NORMAL)
		self.dropdown2.configure(state = tk.NORMAL)

	def canvas_cleared(self):
		self.btn_clear.configure(state = tk.DISABLED)
		self.btn_delete.configure(state = tk.DISABLED)
		self.btn_single_bond.configure(state = tk.DISABLED)
		self.btn_double_bond.configure(state = tk.DISABLED)
		self.btn_triple_bond.configure(state = tk.DISABLED)

	#Functions to place recognized molecules into the canvas, and supporting functions
	#https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
	#efficient line segment intersect function
	def ccw(self, A, B, C):
		return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

	# returns true if line segments AB and CD intersect
	def linesIntersect(self, A, B, C, D):
		return self.ccw(A,C,D) != self.ccw(B,C,D) and self.ccw(A,B,C) != self.ccw(A,B,D)
	
	#changes a numbers to subscripts, for polyatomics
	def to_subscript(self, inputString):
		
		build_string = ""
		for c in inputString:
			if c == '0':
				build_string += "\u2080"
			elif c == '1':
				build_string += "\u2081"
			elif c == '2':
				build_string += "\u2082"
			elif c == '3':
				build_string += "\u2083"
			elif c == '4':
				build_string += "\u2084"
			elif c == '5':
				build_string += "\u2085"
			elif c == '6':
				build_string += "\u2086"
			elif c == '7':
				build_string += "\u2087"
			elif c == '8':
				build_string += "\u2088"
			elif c == '9':
				build_string += "\u2089"
			else:
				build_string += c

		return build_string

	# places atoms from the graph into the canvas, only use for recognized images
	def place_atoms_into_canvas(self):
		listOfAtoms = self.graph.get_atom_list()
		listOfBonds = self.graph.get_bond_list()

		#get canvas dimensions
		canvasWidth = self.canvas.winfo_width()
		canvasHeight = self.canvas.winfo_height()
		left = .1*canvasWidth
		right = canvasWidth - .1*canvasWidth
		top = .1*canvasHeight
		bottom = canvasHeight - .1*canvasHeight
		width = right - left
		height = bottom - top

		#calculate positional conversion rates
		convertWidth = width/(self.cropX2 - self.cropX)
		convertHeight = height/(self.cropY2 - self.cropY)

		# place atoms with a position
		for atom in listOfAtoms:
			atomX, atomY = atom.get_mapped_position()
			if atomX is not None and atomY is not None:
				atomX = atomX * convertWidth
				atomY = atomY * convertHeight
				TEXT = self.to_subscript(atom.get_type())
				self.textbox = self.canvas.create_text(int(atomX), int(atomY), text=TEXT, font=("Arial", 20), tags="letter")
				#rebind mouse to move letters
				self.canvas.tag_bind(self.textbox, '<Button-1>', self.select_textbox)
				self.canvas.tag_bind(self.textbox, '<B1-Motion>', self.move_textbox)
				self.canvas.tag_bind(self.textbox, '<ButtonRelease-1>', self.deselect_textbox)
				self.letters.append(self.textbox)
				self.atom_list.append(atom)
				self.letterBondings.append([])
		
		# print the bonds of the atoms with positions to the canvas
		for bond in listOfBonds:
			atom1, atom2 = bond.get_atoms()
			x1, y1 = atom1.get_mapped_position()
			x2, y2 = atom2.get_mapped_position()
			if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
				letter1 = self.letters[self.atom_list.index(atom1)]		#get letters associated with bond
				letter2 = self.letters[self.atom_list.index(atom2)]

				#get cooridnates of associated letters
				start_x, start_y = self.canvas.coords(letter1)
				end_x, end_y = self.canvas.coords(letter2)

				#calculate line points
				if start_x - end_x != 0:
					angle = math.atan((start_y - end_y)/(start_x - end_x))
				elif start_y >= end_y:
					angle = math.pi/2
				elif start_y < end_y:
					angle = -math.pi/2

				if start_x >= end_x:
					start_x = start_x - 20*math.cos(angle)
					end_x = end_x + 20*math.cos(angle)
					start_y = start_y - 20*math.sin(angle)
					end_y = end_y + 20*math.sin(angle)
				else:
					start_x = start_x + 20*math.cos(angle)
					end_x = end_x - 20*math.cos(angle)
					start_y = start_y + 20*math.sin(angle)
					end_y = end_y - 20*math.sin(angle)

				lineStart = (start_x, start_y)
				lineEnd = (end_x, end_y)

				#draw bond and add data to class-lists
				bondType = bond.get_electron_bond_cost()
				if bondType == 1:
					sB = []
					sB.append(self.canvas.create_line(lineStart, lineEnd, width=4, tags="bond"))
					self.singleBonds.append(sB)
					self.single_bond_list.append(bond)
					self.letterBondings[self.letters.index(letter1)].append((self.singleBonds[len(self.singleBonds) - 1],  letter2))
					self.letterBondings[self.letters.index(letter2)].append((self.singleBonds[len(self.singleBonds) - 1],  letter1)) 
				elif bondType == 2:
					dB = []
					dB.append(self.canvas.create_line(lineStart, lineEnd, width=12, fill="black", tags="bond"))
					dB.append(self.canvas.create_line(lineStart, lineEnd, width=4, fill="white", tags="bond"))
					self.doubleBonds.append(dB)
					self.double_bond_list.append(bond)
					self.letterBondings[self.letters.index(letter1)].append((self.doubleBonds[len(self.doubleBonds) - 1],  letter2))
					self.letterBondings[self.letters.index(letter2)].append((self.doubleBonds[len(self.doubleBonds) - 1],  letter1))
				elif bondType == 3:
					tB = []
					tB.append(self.canvas.create_line(lineStart, lineEnd, width=20, fill="black", tags="bond"))
					tB.append(self.canvas.create_line(lineStart, lineEnd, width=12, fill="white", tags="bond"))
					tB.append(self.canvas.create_line(lineStart, lineEnd, width=4, fill="black", tags="bond"))
					self.tripleBonds.append(tB)
					self.triple_bond_list.append(bond)
					self.letterBondings[self.letters.index(letter1)].append((self.tripleBonds[len(self.tripleBonds) - 1],  letter2))
					self.letterBondings[self.letters.index(letter2)].append((self.tripleBonds[len(self.tripleBonds) - 1],  letter1))

		#get the atoms without positions (the atoms in the multiatom groups)
		for atom in listOfAtoms:
			connectedToAtom = self.graph.get_bonds_to_atom(atom)
			for bond in connectedToAtom:
				atom1, atom2 = bond.get_atoms()
				atom3 = atom1		#atom 3 is the atom connected to the current atom
				atom4 = atom2		#atom 4 is the atom with a mapped position
				if atom == atom2:
					atom3 = atom2
					atom4 = atom1
				atomX, atomY = atom3.get_mapped_position()
				# if the atom cooridnates is none, then we have to place it
				if atomX is None and atomY is None:
					atomX, atomY = atom4.get_mapped_position()
					atomX = atomX * convertWidth
					atomY = atomY * convertHeight

					# find a place to put the letter
					fits = False
					angle = math.pi/2
					i = 0
					while not fits:
						fits = True
						positionX = 60*math.cos(angle) + atomX
						positionY = 60*math.sin(angle) + atomY
						#check if new position intersects another letter
						for letter in self.letters:
							letterX, letterY = self.canvas.coords(letter)
							tl1 = (positionX - 10, positionY - 10)
							br1 = (positionX + 10, positionY + 10)
							tl2 = (letterX - 10, letterY - 10)
							br2 = (letterX + 10, letterY + 10)
							#we can reuse the rectange intersect function from Recognizer.py
							if(Recognizer.intersects(tl1, br1, tl2, br2)):
								fits = False
						#check if new position intersects with a line
						allBonds = self.singleBonds + self.doubleBonds + self.tripleBonds
						for line in allBonds:
							x1, y1, x2, y2 = self.canvas.coords(line[0])
							if self.linesIntersect((x1, y1), (x2, y2), (positionX - 20, positionY - 20), (positionX + 20, positionY - 20)):
								fits = False	#top
							elif self.linesIntersect((x1, y1), (x2, y2), (positionX - 20, positionY - 20), (positionX - 20, positionY + 20)):
								fits = False	#left
							elif self.linesIntersect((x1, y1), (x2, y2), (positionX - 20, positionY + 20), (positionX + 20, positionY + 20)):
								fits = False	#bottom
							elif self.linesIntersect((x1, y1), (x2, y2), (positionX + 20, positionY - 20), (positionX + 20, positionY + 20)):
								fits = False	#right
						#check if new position is outside the canvas
						if positionX < 10 or positionY < 10 or positionX > canvasWidth + 10 or positionY > canvasHeight + 10:
							fits = False

						# if the letter isn't touching anything, add it to the canvas
						if fits:
							self.textbox = self.canvas.create_text(int(positionX), int(positionY), text=atom3.get_type(), font=("Arial", 20), tags="letter")
							#rebind mouse to move letters
							self.canvas.tag_bind(self.textbox, '<Button-1>', self.select_textbox)
							self.canvas.tag_bind(self.textbox, '<B1-Motion>', self.move_textbox)
							self.canvas.tag_bind(self.textbox, '<ButtonRelease-1>', self.deselect_textbox)
							self.letters.append(self.textbox)
							self.atom_list.append(atom3)
							self.letterBondings.append([])
						else:
							angle = angle + math.pi/2		#try another spot, orthagonals
							i = i + 1
							if i == 4:
								angle = angle + math.pi/4	#start trying diagonals
							#if no spots available, print in spot where it doesn't fit, but not off of the canvas
							if i > 8 and positionX > 10 and positionY > 10 and positionX < canvasWidth + 10 and positionY < canvasHeight + 10:
								fits = True
								self.textbox = self.canvas.create_text(int(positionX), int(positionY), text=atom3.get_type(), font=("Arial", 20), tags="letter")
								#rebind mouse to move letters
								self.canvas.tag_bind(self.textbox, '<Button-1>', self.select_textbox)
								self.canvas.tag_bind(self.textbox, '<B1-Motion>', self.move_textbox)
								self.canvas.tag_bind(self.textbox, '<ButtonRelease-1>', self.deselect_textbox)
								self.letters.append(self.textbox)
								self.atom_list.append(atom3)
								self.letterBondings.append([])
		
		# print the bonds of the atoms to the canvas
		for bond in listOfBonds:
			atom1, atom2 = bond.get_atoms()
			x1, y1 = atom1.get_mapped_position()
			x2, y2 = atom2.get_mapped_position()
			if x1 is None or y1 is None or x2 is None or y2 is None:
				letter1 = self.letters[self.atom_list.index(atom1)]		#get letters associated with bond
				letter2 = self.letters[self.atom_list.index(atom2)]

				#get cooridnates of associated letters
				start_x, start_y = self.canvas.coords(letter1)
				end_x, end_y = self.canvas.coords(letter2)

				#calculate line points
				if start_x - end_x != 0:
					angle = math.atan((start_y - end_y)/(start_x - end_x))
				elif start_y >= end_y:
					angle = math.pi/2
				elif start_y < end_y:
					angle = -math.pi/2

				if start_x >= end_x:
					start_x = start_x - 20*math.cos(angle)
					end_x = end_x + 20*math.cos(angle)
					start_y = start_y - 20*math.sin(angle)
					end_y = end_y + 20*math.sin(angle)
				else:
					start_x = start_x + 20*math.cos(angle)
					end_x = end_x - 20*math.cos(angle)
					start_y = start_y + 20*math.sin(angle)
					end_y = end_y - 20*math.sin(angle)

				lineStart = (start_x, start_y)
				lineEnd = (end_x, end_y)

				#draw bond and add data to class-lists
				bondType = bond.get_electron_bond_cost()
				if bondType == 1:
					sB = []
					sB.append(self.canvas.create_line(lineStart, lineEnd, width=4, tags="bond"))
					self.singleBonds.append(sB)
					self.single_bond_list.append(bond)
					self.letterBondings[self.letters.index(letter1)].append((self.singleBonds[len(self.singleBonds) - 1],  letter2))
					self.letterBondings[self.letters.index(letter2)].append((self.singleBonds[len(self.singleBonds) - 1],  letter1)) 
				elif bondType == 2:
					dB = []
					dB.append(self.canvas.create_line(lineStart, lineEnd, width=12, fill="black", tags="bond"))
					dB.append(self.canvas.create_line(lineStart, lineEnd, width=4, fill="white", tags="bond"))
					self.doubleBonds.append(dB)
					self.double_bond_list.append(bond)
					self.letterBondings[self.letters.index(letter1)].append((self.doubleBonds[len(self.doubleBonds) - 1],  letter2))
					self.letterBondings[self.letters.index(letter2)].append((self.doubleBonds[len(self.doubleBonds) - 1],  letter1))
				elif bondType == 3:
					tB = []
					tB.append(self.canvas.create_line(lineStart, lineEnd, width=20, fill="black", tags="bond"))
					tB.append(self.canvas.create_line(lineStart, lineEnd, width=12, fill="white", tags="bond"))
					tB.append(self.canvas.create_line(lineStart, lineEnd, width=4, fill="black", tags="bond"))
					self.tripleBonds.append(tB)
					self.triple_bond_list.append(bond)
					self.letterBondings[self.letters.index(letter1)].append((self.tripleBonds[len(self.tripleBonds) - 1],  letter2))
					self.letterBondings[self.letters.index(letter2)].append((self.tripleBonds[len(self.tripleBonds) - 1],  letter1))
				
######################################################   DELETE BUTTON  #####################################################

	def activate_delete(self):
		self.is_delete_active = not self.is_delete_active
		if self.is_delete_active == True:
			self.disable_buttons()
			self.btn_delete.configure(state = tk.NORMAL)
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Select an item to be deleted, deleting a bonded atom will remove the bond! To exit delete press the delete button again")
			
			# Change cursor to indicate delete mode
			self.canvas.config(cursor="crosshair")
			
			# Bind click events to handle deletion
			self.canvas.bind('<ButtonPress-1>', self.delete_click)
		else:
			self.deactivate_delete()

	def deactivate_delete(self):
		
		# Reset cursor to default
		self.canvas.config(cursor="arrow")
		self.enable_buttons()
		
		# Unbind click events for deletion
		self.canvas.unbind('<ButtonPress-1>')

	def delete_click(self, event):
		# find closest x and y value that has an object
		item = self.canvas.find_closest(event.x, event.y)[0]
		self.Comment_Field.delete(0, "end")
		self.Comment_Field.insert(0, "Item deleted")
		
		# Check if item is a letter or bond object, delete that item, and return cursor back to normal.
		#if self.canvas.type(item) in ["text", "line"]:
		for i in range(len(self.tripleBonds)):
			if item in self.tripleBonds[i]:
				self.canvas.delete(self.tripleBonds[i][0])
				self.canvas.delete(self.tripleBonds[i][1])
				self.canvas.delete(self.tripleBonds[i][2])
				self.tripleBonds.pop(i)
				self.graph.remove_bond_via_bond_obj(self.triple_bond_list[i])
				self.triple_bond_list.pop(i)
				break       #the breaks in here are to fix a bug
		for i in range(len(self.doubleBonds)):
			if item in self.doubleBonds[i]:
				self.canvas.delete(self.doubleBonds[i][0])
				self.canvas.delete(self.doubleBonds[i][0])
				self.doubleBonds.pop(i)
				self.graph.remove_bond_via_bond_obj(self.double_bond_list[i])
				self.double_bond_list.pop(i)
				break       #if you pop from array, it doesn't update len(array)
		for i in range(len(self.singleBonds)):
			#delete single bond from singleBonds
			if item in self.singleBonds[i]:
				self.canvas.delete(self.singleBonds[i][0])
				self.singleBonds.pop(i)
				self.graph.remove_bond_via_bond_obj(self.single_bond_list[i])
				self.single_bond_list.pop(i)
				break
		for i in range(len(self.letters)):
			if item == self.letters[i]:
				self.canvas.delete(self.letters[i])
				#delete the lines connected to the letter
				for j in range(len(self.letterBondings[i])):
					#delete lines from canvas
					for l in range(len(self.letterBondings[i][j][0])):
						self.canvas.delete(self.letterBondings[i][j][0][l])
					#delete bonds from single, double, and triple bonds
					if self.letterBondings[i][j][0] in self.singleBonds:
						#self.graph.remove_bond_via_bond_obj(self.single_bond_list[self.singleBonds.index(self.letterBondings[i][j][0])])
						self.single_bond_list.pop(self.singleBonds.index(self.letterBondings[i][j][0]))
						self.singleBonds.remove(self.letterBondings[i][j][0])
					elif self.letterBondings[i][j][0] in self.doubleBonds:
						#self.graph.remove_bond_via_bond_obj(self.double_bond_list[self.doubleBonds.index(self.letterBondings[i][j][0])])
						self.double_bond_list.pop(self.doubleBonds.index(self.letterBondings[i][j][0]))
						self.doubleBonds.remove(self.letterBondings[i][j][0])
					elif self.letterBondings[i][j][0] in self.tripleBonds:
						#self.graph.remove_bond_via_bond_obj(self.triple_bond_list[self.tripleBonds.index(self.letterBondings[i][j][0])])
						self.triple_bond_list.pop(self.tripleBonds.index(self.letterBondings[i][j][0]))
						self.tripleBonds.remove(self.letterBondings[i][j][0])
				#delete the items from the arrays
				self.graph.delete_atom_via_atom_object(self.atom_list[i])
				self.letters.pop(i)
				self.letterBondings.pop(i)
				self.atom_list.pop(i)
				break
		#remove lines and letters from associated letterBondings
		for i in range(len(self.letterBondings)):
			for j in range(len(self.letterBondings[i])):
				if item in self.letterBondings[i][j][0] or item in self.letterBondings[i][j]:
					self.letterBondings[i].pop(j)
					break

		if self.canvas.find_all() == ():
			self.Comment_Field.delete(0, "end")
			self.Comment_Field.insert(0, "Last item deleted, returning to regular functionality")
			self.is_delete_active = False
			self.deactivate_delete()
			self.canvas_cleared()

	#clear the canvas and arrays
	def clear_canvas(self):
		self.canvas.delete("all")
		self.letters = []			#holds letter IDs
		self.atom_list = []			#holds atom objects for graph
		self.letterBondings = []	#parallel array for letters, holds bonded lines
									#i = letter, j = bond, k = bond info, l (only for k = 0) = parts of bond
		
		self.singleBonds = []		#holds single bond IDs
		self.doubleBonds = []		#holds double bond IDs
		self.tripleBonds = []		#holds triple bond IDs
		self.single_bond_list = []	#holds single bond objects for the graph
		self.double_bond_list = []	#holds double bond objects for the graph
		self.triple_bond_list = []	#holds triple bond objects for the graph
		self.graph = Graph([])

##################################################   BONDS and LINES   ##################################################
	
	# When the Single, Double or Triple Bond button is clicked it initializes
	# Single, Double, and TripleBondCreator object if one doesn't already exist. or if the current
	# SingleBondCreator object is already being used to create a bond.
	def create_single_bond(self):
		self.is_bond_active = not self.is_bond_active
		if self.is_bond_active == True:
			self.bond_type = 1
			self.create_bond()
		else:
			self.clear_line_creation()
	
	def create_double_bond(self):
		self.is_bond_active = not self.is_bond_active
		if self.is_bond_active == True:
			self.bond_type = 2
			self.create_bond()
		else:
			self.clear_line_creation()
			
	def create_triple_bond(self):
		self.is_bond_active = not self.is_bond_active
		if self.is_bond_active == True:
			self.bond_type = 3
			self.create_bond()
		else:
			self.clear_line_creation()

	def create_bond(self):
		self.disable_buttons()
		if self.bond_type == 1:
			self.btn_single_bond.configure(state = tk.NORMAL)
		elif self.bond_type == 2:
			self.btn_double_bond.configure(state = tk.NORMAL)
		elif self.bond_type == 3:
			self.btn_triple_bond.configure(state = tk.NORMAL)
		self.lineStart = None
		self.startConnected = False
		self.lineEnd = None
		self.endConnected = False
		self.line_instance = None
		#self.canvas.unbind("<B1-Motion>")
		#self.canvas.unbind("<ButtonRelease-1>")
		self.canvas.bind("<ButtonRelease-1>", self.on_click_bond)
		self.startLetter = -1
		self.endLetter = -1
		self.Comment_Field.delete(0, "end") # clears for potential bond errors
		self.Comment_Field.insert(0, "Select two atoms to make bond, select the appropriate bond button to exit bonding")

	# Checks if line instance is None. If it is, it sets "start" to the current mouse position (event.x, event.y).
	# If it isn't, it sets "end" to the current mouse position and creates a new Bond object using
	# self.canvas, self.start, self.end. Finally it resets "start" and "end" back to None.
	def on_click_bond(self, event):
		if self.line_instance is None:
			if self.lineStart is None:
				# keep mouse position so we can change it
				point_x, point_y = -1, -1

				# check if we are inside a letter
				for letter in self.letters:
					letter_x, letter_y = self.canvas.coords(letter)
					within_x_boundary: bool = event.x < letter_x + 20 and event.x > letter_x - 20
					within_y_boundary: bool = event.y < letter_y + 20 and event.y > letter_y - 20

					if within_x_boundary and within_y_boundary:
						point_x, point_y = letter_x, letter_y

						# set bonded status
						self.startLetter = letter
						self.startConnected = True
						break
				if point_x == -1 and point_y == -1:
					self.Comment_Field.delete(0, "end")
					self.Comment_Field.insert(0, "Error: Each bond must be bound to two atoms, please start over, and select two atoms")

					# clear when second click occurs (regardless of success or failure)
					self.is_bond_active = False
					self.clear_line_creation()
				else:
					# set start coordinates for bond
					self.lineStart = (point_x, point_y)
					

			else:
				point_x, point_y = event.x, event.y   # keep mouse position so we can change it
				point_x, point_y = -1, -1   # must bind to letter

				# check if we are inside a letter

				for letter in self.letters:
					x, y = self.canvas.coords(letter)

					if event.x < x + 20 and event.x > x - 20 and event.y < y + 20 and event.y > y - 20:
						point_x, point_y = x, y

						# set bonded status
						self.endLetter = letter
						self.endConnected = True
						break

				if (point_x == -1 and point_y == -1 ):
					self.Comment_Field.delete(0, "end")
					self.Comment_Field.insert(0, "Error: Each bond must be bound to two atoms, please start over, and select two atoms")
					self.is_bond_active = False
				else:
					# atom is bound to both
					self.lineEnd = (point_x, point_y)

					# calculate snap line to connected letters
					start_x, start_y = self.lineStart
					end_x, end_y = self.lineEnd

					if start_x - end_x != 0:
						angle = math.atan((start_y - end_y)/(start_x - end_x))
					elif start_y >= end_y:
						angle = math.pi/2
					elif start_y < end_y:
						angle = -math.pi/2

					if start_x >= end_x:
						start_x = start_x - 20*math.cos(angle)
						end_x = end_x + 20*math.cos(angle)
						start_y = start_y - 20*math.sin(angle)
						end_y = end_y + 20*math.sin(angle)
					else:
						start_x = start_x + 20*math.cos(angle)
						end_x = end_x - 20*math.cos(angle)
						start_y = start_y + 20*math.sin(angle)
						end_y = end_y - 20*math.sin(angle)

					# if connected to a letter, snap line to letter
					if self.startConnected:
						self.lineStart = (start_x, start_y)
					if self.endConnected:
						self.lineEnd = (end_x, end_y)

					AddLine = True

					# actions to take if both anchors are letters
					if self.startConnected and self.endConnected:
						if self.startLetter != self.endLetter:
							# don't allow the bond to be created if a bond already exists
							for j in range(len(self.letterBondings[self.letters.index(self.startLetter)])):
								if self.letterBondings[self.letters.index(self.startLetter)][j][1] == self.endLetter:
									AddLine = False

						# Prevent self bonding
						if self.startLetter == self.endLetter:
							AddLine = False
							self.Comment_Field.delete(0, "end")
							self.Comment_Field.insert(0, "Error: Cannot self bond")

						# form bonds
						try:
							if AddLine and self.startLetter != -1 and self.endLetter != -1:
								# remove (possible) error messaages that are present
								self.Comment_Field.delete(0, "end")
								self.Comment_Field.insert(0, "Bond created")

								if self.bond_type == 1:

									# create backend bond to represent
									bond = SingleBond(self.atom_list[self.letters.index(self.startLetter)], \
									self.atom_list[self.letters.index(self.endLetter)])
									self.single_bond_list.append(bond)

									# draw line  
									sB = []
									sB.append(self.canvas.create_line(self.lineStart, self.lineEnd, width=4, tags="bond"))
									self.singleBonds.append(sB)

									#add lines to letterBondings so we know the objects are supposed to be connected
									self.letterBondings[self.letters.index(self.startLetter)].append((self.singleBonds[len(self.singleBonds) - 1],  self.endLetter))
									self.letterBondings[self.letters.index(self.endLetter)].append((self.singleBonds[len(self.singleBonds) - 1], self.startLetter))

								elif self.bond_type == 2:

									# create backend bond to represent
									bond = DoubleBond(self.atom_list[self.letters.index(self.startLetter)], \
									self.atom_list[self.letters.index(self.endLetter)])
									self.double_bond_list.append(bond)

									# draw line  
									dB = []
									dB.append(self.canvas.create_line(self.lineStart, self.lineEnd, width=12, fill="black", tags="bond"))
									dB.append(self.canvas.create_line(self.lineStart, self.lineEnd, width=4, fill="white", tags="bond"))
									self.doubleBonds.append(dB)

									#add lines to letterBondings so we know the objects are supposed to be connected
									self.letterBondings[self.letters.index(self.startLetter)].append((self.doubleBonds[len(self.doubleBonds) - 1],  self.endLetter))
									self.letterBondings[self.letters.index(self.endLetter)].append((self.doubleBonds[len(self.doubleBonds) - 1], self.startLetter))    

								elif self.bond_type == 3:

									# create backend bond to represent
									bond = TripleBond(self.atom_list[self.letters.index(self.startLetter)], \
									self.atom_list[self.letters.index(self.endLetter)])
									self.triple_bond_list.append(bond)

									# draw line  
									tB = []
									tB.append(self.canvas.create_line(self.lineStart, self.lineEnd, width=20, fill="black", tags="bond"))
									tB.append(self.canvas.create_line(self.lineStart, self.lineEnd, width=12, fill="white", tags="bond"))
									tB.append(self.canvas.create_line(self.lineStart, self.lineEnd, width=4, fill="black", tags="bond"))
									self.tripleBonds.append(tB)

									#add lines to letterBondings so we know the objects are supposed to be connected
									self.letterBondings[self.letters.index(self.startLetter)].append((self.tripleBonds[len(self.tripleBonds) - 1],  self.endLetter))
									self.letterBondings[self.letters.index(self.endLetter)].append((self.tripleBonds[len(self.tripleBonds) - 1],  self.startLetter))  

								# add to graph
								self.graph.add_bond_via_bond_obj(bond)

						except NameError as err:
							self.Comment_Field.delete(0, "end")
							self.Comment_Field.insert(0, err)
							AddLine = False
							self.is_bond_active = False
				
				# clear when second click occurs (regardless of success or failure)
				self.clear_line_creation()
		
	# resets line creation
	def clear_line_creation(self):
		if self.is_bond_active == False:
			# clear when second click occurs (regardless of success or failure)
			self.startLetter = -1
			self.endLetter = -1
			self.startConnected = False
			self.endConnected = False
			self.line_instance = 1
			self.start = None
			self.end = None
			self.enable_buttons()
		else:
			self.create_bond()
	
	def empty_properties(self):
			# empty properties 
			self.graph = Graph([])
			self.letters = []			
			self.atom_list = []			
			self.letterBondings = []	
										
			self.singleBonds = []		
			self.doubleBonds = []		
			self.tripleBonds = []		
			self.single_bond_list = []	
			self.double_bond_list = []	
			self.triple_bond_list = []	