
from tkinter import OptionMenu
from tkinter import StringVar
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Button as ThemedButton
from tkinter.ttk import Entry as ThemedEntry

class siIPair():	# Class that implements the siI pair GUI elements and contents and manages them
	def __init__(self,main,parent,pairID=-1):
		self.main = main
		self.pairID = pairID	#used for reporting and in PM
		
		self.pairFrameBase = ThemedFrame(parent,style="wBorder.TFrame")	#base of everything, used as border, destroyed when pair gets deleted
		self.pairFrameBase.pack(fill="x",side="top",padx=self.main.frameBorderSize,pady=(self.main.frameBorderSize,0))
		
		pairFrame = ThemedFrame(self.pairFrameBase)
		pairFrame.pack(fill="x",padx=self.main.frameBorderSize,pady=self.main.frameBorderSize)
		
		self.enrichedLibs = dict()
		self.controlLibs = dict()
		self.availableLibIDs = set()
		self.selectedTPS = "-"
		
		self.select_enriched_menu = None
		self.select_control_menu = None
		
		ThemedLabel(pairFrame,text="Label:",style="TLabel").grid(column=0,row=0,columnspan=1,sticky="news",padx=(self.main.frameBorderSize,0))
		self.labelVar = StringVar(value="New pairing")
		ThemedEntry(pairFrame,textvariable=self.labelVar).grid(column=1,row=0,columnspan=1,sticky="ew")
		
		ThemedLabel(pairFrame,text="Enriched:",style="TLabel").grid(column=2,row=0,columnspan=1,sticky="news",padx=self.main.frameBorderSize*2)
		ThemedLabel(pairFrame,text="Control:").grid(column=3,row=0,columnspan=1,sticky="news",padx=self.main.frameBorderSize*2)
		
		ThemedLabel(pairFrame,text="Target:",style="TLabel").grid(column=0,row=1,columnspan=1,sticky="news",padx=(self.main.frameBorderSize,0))
		
		self.positiveLibsFrame = ThemedFrame(pairFrame)
		self.positiveLibsFrame.grid(column=2,row=1,rowspan=4,sticky="new",padx=(self.main.frameBorderSize*2,self.main.frameBorderSize))
		self.negativeLibsFrame = ThemedFrame(pairFrame)
		self.negativeLibsFrame.grid(column=3,row=1,rowspan=4,sticky="new",padx=(self.main.frameBorderSize,self.main.frameBorderSize*2))
		
		self.startVar = self.main.PM.add(f"siI-pairs_{self.pairID}-start","int","-",	#Add to PM for automatic validation and error reporting, but dont save to file
			f"Startposition for \"{self.labelVar.get()}\" needs to be an integer!","Startposition of the region of interest.",tag="siI-pairs-tmp")
		self.endVar = self.main.PM.add(f"siI-pairs_{self.pairID}-end","int","-",
			f"Endposition   for \"{self.labelVar.get()}\" needs to be an integer!","Endposition of the region of interest.",tag="siI-pairs-tmp")
		
		TPSlist = self.main.IM.getTPSList()
		if len(TPSlist)==0:	#should be impossible to occur now
			self.main.writeError("Error, please run the pipeline before selecting siI pairs.")
			return
		self.select_TPS_var = StringVar(value="-")
		self.select_TPS_menu = OptionMenu(pairFrame,self.select_TPS_var,*TPSlist,command = lambda selectedTPS: self._selectTPS(selectedTPS))
		self.select_TPS_menu.grid(column=1,row=1,columnspan=1,sticky="news")
		self.main.styleman.registredOptionMenus.append(self.select_TPS_menu)
		self.select_TPS_menu.config(
			fg=self.main.styleman.textColour,
			bg=self.main.styleman.backgroundColour,
			font=self.main.logFont,
			activeforeground=self.main.styleman.textColour,
			activebackground=self.main.styleman.textBackgroundColour)
		self.select_TPS_menu["menu"].config(
			fg=self.main.styleman.textColour,
			bg=self.main.styleman.backgroundColour,
			font=self.main.logFont,
			activeforeground=self.main.styleman.textColour,
			activebackground=self.main.styleman.textBackgroundColour)
		
		ThemedLabel(pairFrame,text="Region-start:",style="TLabel").grid(column=0,row=2,sticky="news",padx=(self.main.frameBorderSize,0))
		ThemedEntry(pairFrame,textvariable=self.startVar,width=10).grid(column=1,row=2,sticky="w")
		ThemedLabel(pairFrame,text="Region-end:",style="TLabel").grid(column=0,row=3,sticky="news",padx=(self.main.frameBorderSize,0))
		ThemedEntry(pairFrame,textvariable=self.endVar,width=10).grid(column=1,row=3,sticky="w")
		ThemedFrame(pairFrame).grid(column=0,row=4,columnspan=2,sticky="news")
		
		ThemedButton(pairFrame,image=self.main.xImage,command = self._deleteYourself,style="Exit.TButton").grid(
			column=4,row=0,rowspan=2,sticky="new",padx=(0,self.main.frameBorderSize*2),pady=self.main.frameBorderSize*2)
		
		pairFrame.rowconfigure(0,weight=0,uniform="fred")
		pairFrame.rowconfigure(1,weight=0,uniform="fred")
		pairFrame.rowconfigure(2,weight=0,uniform="fred")
		pairFrame.rowconfigure(3,weight=0,uniform="fred")
		pairFrame.rowconfigure(4,weight=1)
		
		pairFrame.columnconfigure(0,weight=1)
		pairFrame.columnconfigure(1,weight=3)
		pairFrame.columnconfigure(2,weight=4,uniform="fred")
		pairFrame.columnconfigure(3,weight=4,uniform="fred")
		pairFrame.columnconfigure(4,weight=0)
	
	def getData(self):
		if self.selectedTPS == "-":return None
		startOkay = self.main.PM.validateParameter(f"siI-pairs_{self.pairID}-start")
		endOkay = self.main.PM.validateParameter(f"siI-pairs_{self.pairID}-end")
		if not startOkay and endOkay: return None
		return (
			list(self.enrichedLibs.keys()),
			list(self.controlLibs.keys()),
			self.labelVar.get(),
			self.main.IM.getTPSTuple(self.selectedTPS),
			int(self.startVar.get()),
			int(self.endVar.get()))
	
	def loadPair(self,pairLoad):
		#(libPos,libNeg,label,TPS,regionStart,regionEnd)
		self.labelVar.set(pairLoad[2])
		self._selectTPS(self.main.IM.TPSToString(pairLoad[3]),update=False)
		if pairLoad[4]!= "-": self.startVar.set(int(pairLoad[4]))
		if pairLoad[5]!= "-": self.endVar.set(int(pairLoad[5]))
		for libID in pairLoad[0]:
			self._addLibToEnriched(libID,update=False)	#Only update the dropdowns once the pair has been fully loaded
		for libID in pairLoad[1]:
			self._addLibToControl(libID,update=False)
		self._updateAvailableLibIDs()
	
	def _deleteYourself(self):
		if self.select_TPS_menu in self.main.styleman.registredOptionMenus:
			self.main.styleman.registredOptionMenus.remove(self.select_TPS_menu)	#remove menu references from styleman
		if not self.select_enriched_menu is None and self.select_enriched_menu in self.main.styleman.registredOptionMenuButtons:
			self.main.styleman.registredOptionMenuButtons.remove(self.select_enriched_menu)
		if not self.select_control_menu is None and self.select_control_menu in self.main.styleman.registredOptionMenuButtons:
			self.main.styleman.registredOptionMenuButtons.remove(self.select_control_menu)
		self.pairFrameBase.destroy()				#destroy GUI widgets
		self.main.siI_pairList[self.pairID] = None	#"remove" self from list of pairs
		self.main.PM.deleteParameter(f"siI-pairs_{self.pairID}-start")	#remove variable from PM
		self.main.PM.deleteParameter(f"siI-pairs_{self.pairID}-end")

	def _deleteEnrichedLib(self,libID):
		self.enrichedLibs[libID].destroy()
		del self.enrichedLibs[libID]
		self.availableLibIDs.add(libID)
		self._updateAvailableLibIDs()
	
	def _deleteControlLib(self,libID):
		self.controlLibs[libID].destroy()
		del self.controlLibs[libID]
		self.availableLibIDs.add(libID)
		self._updateAvailableLibIDs()
	
	def _selectTPS(self,selectedTPS,update=True):
		if not self.main.IM.hasTPS(selectedTPS):
			self.main.writeError(f"[siI module][ERROR] Selected a TPS that doesnt exist: {selectedTPS} (how?)")
			return
		self.select_TPS_var.set(selectedTPS)
		self.selectedTPS = selectedTPS
		self.availableLibIDs = set(self.main.IM.getTPSLibIDs(selectedTPS))
		self.startVar.set(1)
		self.endVar.set(self.main.IM.getTarget(self.main.IM.getTPSTuple(selectedTPS)[0]).mainLength)
		
		#remove existing selected libIDs from GUI and storage
		for libID in list(self.enrichedLibs.keys()):
			self._deleteEnrichedLib(libID)
		for libID in list(self.controlLibs.keys()):
			self._deleteControlLib(libID)
		
		if self.select_enriched_menu is None:
			self.libPosVar = StringVar(value="+")
			self.select_enriched_menu = OptionMenu(self.positiveLibsFrame,self.libPosVar,"+",command = lambda libID:self._addLibToEnriched(libID))
			self.select_enriched_menu.pack(fill="x",anchor="nw")
			self.main.styleman.registredOptionMenuButtons.append(self.select_enriched_menu)
			self.select_enriched_menu.config(
				fg=self.main.styleman.buttonTextColour,
				bg=self.main.styleman.buttonColour,
				font=self.main.buttonTextFont,
				activeforeground=self.main.styleman.textColour,
				activebackground=self.main.styleman.buttonHighlightColour)
			self.select_enriched_menu["menu"].config(
				fg=self.main.styleman.textColour,
				bg=self.main.styleman.backgroundColour,
				font=self.main.logFont,
				activeforeground=self.main.styleman.textColour,
				activebackground=self.main.styleman.textBackgroundColour)
		
		if self.select_control_menu is None:
			libNegVar = StringVar(value="+")
			self.select_control_menu = OptionMenu(self.negativeLibsFrame,libNegVar,"+",command = lambda libID:self._addLibToEnriched(libID))
			self.select_control_menu.pack(fill="x",anchor="nw")
			self.main.styleman.registredOptionMenuButtons.append(self.select_control_menu)
			self.select_control_menu.config(
				fg=self.main.styleman.buttonTextColour,
				bg=self.main.styleman.buttonColour,
				font=self.main.buttonTextFont,
				activeforeground=self.main.styleman.textColour,
				activebackground=self.main.styleman.buttonHighlightColour)
			self.select_control_menu["menu"].config(
				fg=self.main.styleman.textColour,
				bg=self.main.styleman.backgroundColour,
				font=self.main.logFont,
				activeforeground=self.main.styleman.textColour,
				activebackground=self.main.styleman.textBackgroundColour)
			
		if update:self._updateAvailableLibIDs()
	
	def _updateAvailableLibIDs(self):
		availableLibIDList = sorted(self.availableLibIDs)
		#print(f"[siI module][Debug] Available: {availableLibIDList}")
		#print(f"[siI module][Debug] enriched: {sorted(self.enrichedLibs.keys())}")
		#print(f"[siI module][Debug] control: {sorted(self.controlLibs.keys())}")
		self.select_enriched_menu["menu"].delete(0,"end")
		self.select_control_menu["menu"].delete(0,"end")
		for avalablelibID in availableLibIDList:
			self.select_enriched_menu["menu"].add_command(label=avalablelibID,command = lambda avalablelibID=avalablelibID:self._addLibToEnriched(avalablelibID))
			self.select_control_menu["menu"].add_command(label=avalablelibID,command = lambda avalablelibID=avalablelibID:self._addLibToControl(avalablelibID))
	
	def _addLibToEnriched(self,libID,update=True):
		self.availableLibIDs.remove(libID)
		if update:self._updateAvailableLibIDs()
		container = ThemedFrame(self.positiveLibsFrame)
		container.pack(fill="x",anchor="nw")
		self.enrichedLibs[libID] = container
		ThemedLabel(container,text=libID).pack(side="left",fill="x",anchor="nw")
		ThemedButton(container,image=self.main.xImage,
			command = lambda : self._deleteEnrichedLib(libID),style="Exit.TButton").pack(side="right",anchor="ne")
	
	def _addLibToControl(self,libID,update=True):
		self.availableLibIDs.remove(libID)
		if update:self._updateAvailableLibIDs()
		container = ThemedFrame(self.negativeLibsFrame)
		container.pack(fill="x",anchor="nw")
		self.controlLibs[libID] = container
		ThemedLabel(container,text=libID).pack(side="left",fill="x",anchor="nw")
		ThemedButton(container,image=self.main.xImage,
			command = lambda : self._deleteControlLib(libID),style="Exit.TButton").pack(side="right",anchor="ne")

