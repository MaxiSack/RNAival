
import os.path
import webbrowser

from tkinter import Toplevel
from tkinter import PhotoImage

from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry

class AboutMenu():
	def __init__(self,main):
		self.main = main
		self.window = Toplevel(main.mainWindow)
		self.window.title("RNAival - About")
		self.window.protocol("WM_DELETE_WINDOW",self.closeWindow)
		self.window.bind_all("<Control-w>",lambda event:self.closeWindow())
		
		mainframeBase = ThemedFrame(self.window,style="gBorder.TFrame")
		mainframeBase.pack(fill="both",expand=True,anchor="nw")
		
		mainframe = ThemedFrame(mainframeBase,style="TFrame")
		mainframe.pack(padx=main.frameBorderSize,pady=main.frameBorderSize,fill="both",expand=True,anchor="nw")
		
		self.icon = PhotoImage(file = os.path.join(main.execPath,"sprites/IconSquished_transparent.png"))
		ThemedLabel(mainframe,image=self.icon,anchor="n").pack(anchor="n")
		
		#-------------- main text field --------------
		self.textfield = main.styleman.getStyledText(mainframe)
		self.textfield.pack(anchor="n")
		self.textfield.configure(font=main.textFont)
		self.textfield.configure(bg=main.styleman.backgroundColour)
		self.textfield.configure(width=70,height=9)
		self.textfield["state"]="normal"
		
		self.textfield.tag_configure("center",justify="center")
		self.textfield.insert("end","\nRNAival is a tool for the identification of potent siRNAs","center","\nand the evaluation of the processing of dsRNAs\n","center")
		#<Button-1> is on initial press on the tagged area
		self.textfield.tag_configure("github",foreground="#0000cc",underline=True)
		self.textfield.tag_bind("github","<Button-1>",
			lambda event,url = "https://github.com/MaxiSack/RNAival": webbrowser.open(url,new=0,autoraise=True))
		self.textfield.insert("end","\nFind the source code on ","center","github.com/MaxiSack/RNAival","github")
		
		self.textfield.tag_configure("manual",foreground="#0000cc",underline=True)
		self.textfield.tag_bind("manual","<Button-1>",
			lambda event:main.openManual())
		self.textfield.insert("end","\nOpen the ","center","Manual.pdf","manual")
		
		self.textfield.tag_configure("contact",foreground="#0000cc",underline=True,justify="center")
		self.textfield.tag_bind("contact","<Button-1>",
			lambda event,url = "https://www.informatik.uni-halle.de/arbeitsgruppen/bioinformatik/mitarbeiterinnen/sack/?lang=en": webbrowser.open(url,new=0,autoraise=True))
		self.textfield.insert("end","\nContact the main author on \n","center","www.informatik.uni-halle.de/arbeitsgruppen/bioinformatik/mitarbeiterinnen/sack","contact")
		
		self.textfield["state"]="disabled"
		
		buttonframe = ThemedFrame(mainframe,style="TFrame")
		buttonframe.pack(fill="both",expand=True,anchor="n")
		ThemedButton(buttonframe,text="Source",
			command=lambda url = "https://github.com/MaxiSack/RNAival": webbrowser.open(url,new=0,autoraise=True)
				).grid(row=0,column=0,sticky="news")
		
		ThemedButton(buttonframe,text="Manual",command=main.openManual
				).grid(row=0,column=1,sticky="news")
		
		ThemedButton(buttonframe,text="Contact",
			command=lambda url = "https://www.informatik.uni-halle.de/arbeitsgruppen/bioinformatik/mitarbeiterinnen/sack/?lang=en": webbrowser.open(url,new=0,autoraise=True)
				).grid(row=0,column=2,sticky="news")
		
		buttonframe.columnconfigure(0,weight=1,uniform="fred")
		buttonframe.columnconfigure(1,weight=1,uniform="fred")
		buttonframe.columnconfigure(2,weight=1,uniform="fred")
		
		self.window.update()	#this draws the window , making winfo available for centering
		self.center()
	
	def center(self):
		self.window.geometry(f"+{int(self.main.mainWindow.winfo_width()/2-self.window.winfo_width()/2)}+{int(self.main.mainWindow.winfo_height()/2-self.window.winfo_height()/2)}")
	
	def raisetoTop(self):
		self.window.lift()
	
	def closeWindow(self):	#removes references to self and destroys the window 
		self.main.aboutMenu = None
		self.main.styleman.removeStyledText(self.textfield)
		self.window.destroy()

	
