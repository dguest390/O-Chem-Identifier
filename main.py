import Classes.gui as GUI
import tkinter as tk

def main():
	#start GUI
	root = tk.Tk()
	root.title("OCRI Interface")
	app = GUI.Gui_Edit_Molecule(root)
	root.resizable(False,False)         
	root.mainloop()

if __name__ == "__main__":
	main()
else:
	print(__name__)
 