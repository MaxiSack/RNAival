
import os.path

from tkinter import Canvas
from tkinter import StringVar
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Label as ThemedLabel
from tkinter.ttk import Entry as ThemedEntry
from tkinter.ttk import Button as ThemedButton
from tkinter.filedialog import asksaveasfilename

import graphs.drawGraphics as graphLib

class InteractiveGraph:
	def __init__(self,main,parent,canvasHeight,title,safePath,colouring=None,exportFontsize=12,styles=None,positionalColouring=None,graphType="unset",
			parentCombo=None,xlab=None,ylab=None,lineColours=None,fileSuffix=None):
		#print(f"\n[IG] Creating new interactive graph {title}, Graph-height: "{height}")
		
		#---------------- object values ----------------
		self.main = main
		self.canvasHeight = canvasHeight
		self.plotWidth = 0
		self.plotHeight = 0
		self.title = title
		self.fileSuffix = title.replace(" ","_") if fileSuffix is None else fileSuffix	#appended to the comboFilename for svg export
		self.positionalColouring = positionalColouring
		self.safePath = safePath
		self.pointRadius = 10
		self.parentCombo = parentCombo
		self.graphType = graphType
		#print(f"[IG] Creating IG of parent \"{self.parentCombo.title}\" with title \"{self.title}\" and fileSuffix \"{self.fileSuffix}\"")
		
		#---------------- IG GUI def ----------------
		graphFrame = ThemedFrame(parent)
		graphFrame.pack(fill="both",expand=True,side="top")
		
		labelFrame = ThemedFrame(graphFrame)
		labelFrame.pack(fill="both")
		ThemedLabel(labelFrame,text=self.title).pack(fill="both",side="left")
		#ThemedButton(labelFrame,text="Save as File",command=self.saveAsFile).pack(fill="y",side="right")	#Save as eps using Canvas native export
		#if self.graphType=="SCATTER":	#clear all marked points
			#print("[IG] Type is SCATTER")
		ThemedButton(labelFrame,text="Clear",command=parentCombo.clearConnected).pack(fill="y",side="right")
		ThemedButton(labelFrame,text="Save As",command=self.saveAsFile).pack(fill="y",side="right")
		
		
		self.myGraphStats = StringVar()
		self.myGraphStats.set("")
		ThemedEntry(graphFrame,textvariable=self.myGraphStats,state="readonly",style="RText.TEntry").pack(fill="both")
		
		self.canvas = Canvas(graphFrame,height=self.canvasHeight,bg=self.main.graphBackgroundColour,highlightthickness=0)
		self.canvas.pack(fill="both",expand=True,side="top")
		self.canvas.bind("<Button-1>",self._handle_cursor_click)
		
		#---------------- ----------------
		
		self.graphData = None
		
		self.dataObjects = None
		self.markedBars = set()	#of indices
		self.barhighlights = dict()
		self.styles = styles
		self.lineColours = lineColours
		
		# -------- values set by the plotting lib ------
		self.xbase = None
		self.xdataToPix = None
		self.ydataToPix = None
		
		self.legend = None
		self.highlightpositions = None
		
		self.xlab=xlab
		self.ylab=ylab
		self.xLabels = None
		
		self.clickFillCol = "#88ccff"
		self.clickStrokeCol = "#2255ff"
		self.colourscale = None
		
		self.globalYScale=False
		
	def saveAsFile(self):
		
		soloExtra = "" if self.fileSuffix is "" else "_"+self.fileSuffix
		savePath = os.path.join(self.safePath,f"{self.parentCombo.fileName}{soloExtra}.svg")
		resultsPath = asksaveasfilename(initialfile=savePath,filetypes=[("Scalable Vector Graphic",".svg")],initialdir=self.safePath)
		self.parentCombo.exportAsSVG(resultsPath,self.plotWidth,self.plotHeight,1,selectedGraphName=self.title,overridePath=True)
	
	def setXLabels(self,xlabels):
		self.xLabels=xlabels
	
	def updateDesc(self,index,yindex,ypoint):	#TODO modernise this!
		#print(f"[IG][Debug] Updating Desc of {self.graphType}-{self.title}:\t{index}\t{yindex}\t{ypoint}")
		
		if self.graphType=="BAR2":
			point = self.graphData[index]
			#print("[IG][Debug] Selected: "+str(point)+" xindex: "+str(index)+" yindex: "+str(yindex))
			
			#self.myGraphStats.set("pos: "+str(point[0])+", + count: "+str(point[1])+", - count: "+str(point[2]))
			if len(point)==7:
				if yindex<0:	#TODO use legend description here and as in-graph legend!!
					self.myGraphStats.set("pos: {point[0]}, sense, covarage (all): {point[1]}, coverage (21-24): {point[3]}, coverage (21): {point[5]}")
					if (index,1) in self.markedBars:
						self.colourBar(self.dataObjects[index][4],"pink","red")
						self.colourBar(self.dataObjects[index][2],"lime","green")
						self.colourBar(self.dataObjects[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,1))
					else:
						self.colourBar(self.dataObjects[index][4],"#88ccff","#0000ff")
						self.colourBar(self.dataObjects[index][2],"#5599ff","#0000dd")
						self.colourBar(self.dataObjects[index][0],"#2266bb","#0000bb")
						self.markedBars.add((index,1))
				else:
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, count: "+str(point[2])
						+", count (19-25): "+str(point[4])+", count (21-23): "+str(point[6]))
					if (index,2) in self.markedBars:
						self.colourBar(self.dataObjects[index][5],"pink","red")
						self.colourBar(self.dataObjects[index][3],"lime","green")
						self.colourBar(self.dataObjects[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,2))
					else:
						self.colourBar(self.dataObjects[index][5],"#88ccff","#0000ff")
						self.colourBar(self.dataObjects[index][3],"#5599ff","#0000dd")
						self.colourBar(self.dataObjects[index][1],"#2266bb","#0000bb")
						self.markedBars.add((index,2))
			elif len(point)==5:	#start-end	#TODO!
				if ypoint<0:
					self.myGraphStats.set("pos: "+str(point[0])+", sense, coverage: "+str(point[3])+", coverage (esiRNA): "+str(point[1]))
					if (index,1) in self.markedBars:
						if point[0] in self.positionalColouring[0]:
							self.colourBar(self.dataObjects[index][0],self.styles[self.positionalColouring[0][point[0]]][0],
								self.styles[self.positionalColouring[0][point[0]]][1])
						else: self.colourBar(self.dataObjects[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.colourBar(self.dataObjects[index][2],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,1))
					else:
						self.colourBar(self.dataObjects[index][0],self.clickFillCol,self.clickStrokeCol)
						self.colourBar(self.dataObjects[index][2],self.clickFillCol,self.clickStrokeCol)
						self.markedBars.add((index,1))
				else:
					#self.myGraphStats.set("pos: "+str(point[0])+", antisense, 5' count: "+str(point[4])+", 3' count: "+str(point[2]))
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, coverage: "+str(point[3])+", coverage (esiRNA): "+str(point[2]))
					if (index,2) in self.markedBars:
						if point[0] in self.positionalColouring[1]:
							self.colourBar(self.dataObjects[index][1],self.styles[self.positionalColouring[1][point[0]]][0],
								self.styles[self.positionalColouring[1][point[0]]][1])
						else: self.colourBar(self.dataObjects[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.colourBar(self.dataObjects[index][3],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,2))
					else:
						self.colourBar(self.dataObjects[index][1],self.clickFillCol,self.clickStrokeCol)
						self.colourBar(self.dataObjects[index][3],self.clickFillCol,self.clickStrokeCol)
						self.markedBars.add((index,2))
			elif len(point)==3:
				if ypoint<0:
					self.myGraphStats.set("pos: "+str(point[0])+", sense, count: "+str(point[1]))
					if (index,1) in self.markedBars:
						if point[0] in self.positionalColouring[0]:
							self.colourBar(self.dataObjects[index][0],self.styles[self.positionalColouring[0][point[0]]][0],
								self.styles[self.positionalColouring[0][point[0]]][1])
						else: self.colourBar(self.dataObjects[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,1))
					else:
						self.colourBar(self.dataObjects[index][0],self.clickFillCol,self.clickStrokeCol)
						self.markedBars.add((index,1))
				else:
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, count: "+str(point[2]))
					if (index,2) in self.markedBars:
						if point[0] in self.positionalColouring[1]:
							self.colourBar(self.dataObjects[index][1],self.styles[self.positionalColouring[1][point[0]]][0],
								self.styles[self.positionalColouring[1][point[0]]][1])
						else: self.colourBar(self.dataObjects[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,2))
					else:
						self.colourBar(self.dataObjects[index][1],self.clickFillCol,self.clickStrokeCol)
						self.markedBars.add((index,2))
		
		elif self.graphType=="HEAT":
			yindex = abs(yindex)
			if yindex >= len(self.yvals):
				print("[IG] ERROR: yposition "+str(yindex)+" is outside heatmap!")
				return
			xpos = self.xvals[index]
			ypos = self.yvals[yindex]
			
			self.myGraphStats.set(f"{self.xlab}: {xpos}, {self.ylab}: {ypos}, Abundance: {self.graphData[index][yindex]}")
			
			#print(self.highlightpositions)
			
			if (index,yindex) in self.highlightpositions:
				self.clearCellHighlight(index,yindex)
			else:
				self.highlightCell(index,yindex)
			
		else:
			print("[IG] ERROR: Unknown graphtype: "+self.graphType)
	
	def selectPoint(self, pos):
		#print(f"[IG][Debug] Selection point {pos} in {self.graphType}-{self.title}")
		if self.graphType=="SCATTER":
			point = self.graphData[pos]
			self.myGraphStats.set(f"Position: {point[0]}, {self.xlab}: {point[1]}, {self.ylab}: {point[2]}")
			self.canvas.itemconfig(self.dataObjects[pos][0],outline="#ff00c6")#"#ff5700")#"#ff00c6")#"#d800df")#"#00ffff")	#ff7700
		elif self.graphType=="BAR" or (self.graphType=="BAR2" and not self.discreetX):
			point = self.graphData[pos]
			self.myGraphStats.set(f"{self.xlab}: {point[0]}, {self.ylab}: {point[1]}")
			self.barhighlights[pos] = graphLib.createBarHighlight(self,pos+1)
	
	def clearPoint(self,pos):
		if self.graphType=="SCATTER":
			self.canvas.itemconfig(self.dataObjects[pos][0],outline="")
		elif self.graphType=="BAR" or (self.graphType=="BAR2" and not self.discreetX):
			self.canvas.delete(self.barhighlights[pos])
	
	def selectPointInAll(self,pos):	#this is actually an index for the datastructure
		#print(f"[IG][Debug] Selecting all points at index {pos}")
		#print(f"[IG][Debug] connectedCombos: {len(self.parentCombo.connectedGraphs)}")
		if pos in self.parentCombo.selectedPoints:
			for comboGraph in self.parentCombo.connectedGraphs:
				comboGraph.clearPoint(pos)
		else:
			for comboGraph in self.parentCombo.connectedGraphs:
				comboGraph.selectPoint(pos)
	
	def _handle_cursor_click(self,event):
		#Use different click-selection method based on type of graph
		if self.graphType=="SCATTER":	
			self.cursorSelectPoint(event)
		else:
			self.cursorSelectBar(event)
	
	def cursorSelectPoint(self,event):	#handles finding the point (circle) that was clicked on
		for i in range(len(self.dataObjects)):
			if self.pointRadius > ((event.x-self.dataObjects[i][1])**2+(event.y-self.dataObjects[i][2])**2)**0.5:
				#point[1] and point[2] are the point's center in canvas-space. And so is the event
				#call other plots and highlight
				self.selectPointInAll(i)
	
	def cursorSelectBar(self,event):	#handles finding the bar (cell) that was clicked on
		#print("Cursor: "+str(event.x)+" "+str(event.y))	#coords in canvas-space
		if self.dataObjects is None and self.dataObjects is None:
			print("[IG] ERROR: Data has not been drawn!")
			return
		barx = event.x-self.xbase
		ypoint = event.y-self.yzero
		if barx>=0:
			if self.graphType=="HEAT" or self.discreetX:
				barIndex = int((barx / self.xdataToPix))
			else:
				barIndex = int((barx / self.xdataToPix)-0.5)
			yindex = int(ypoint / self.ydataToPix)
			#print(f"\n[IG][Debug] Selected Position(index): {barIndex} {yindex} {round(event.y,2)} / {round(self.ybase)} {round(self.yzero)} {ypoint}")
			if barIndex<len(self.graphData):
				if self.graphType=="BAR" or (self.graphType=="BAR2" and not self.discreetX):
					self.selectPointInAll(barIndex)
				else:
					self.updateDesc(barIndex,yindex,ypoint)
		
	#legend is a list of (Colour,String)
	def setData(self,graphType,graphData,legend=None,colourscale_define=None):
		#print(f"[IG] setting data for graph of type {graphType}")
		self.graphType = graphType
		if graphType=="HEAT":	#Heatmaps have a different data structure and need to be unpacked
			self.graphData,self.yvals,self.xvals=graphData	#value-matrix, list of y labels, list of x labels
		else:
			self.graphData = graphData	#list of position, value, ...
		
		if self.graphType=="HEAT":
			self.highlightpositions = set()
			self.colourscale,legendDesc = graphLib.getColourscale(self.graphData,colourscale_define)
			self.legend=("Count:",legendDesc)
			if -1 in self.yvals:self.legend[1].append(("#ff00ff","esiRNAs"))
		elif self.graphType=="BAR2" or self.graphType=="multiLine" or self.graphType=="SCATTER":	#self.graphType=="BAR" BAR is now unused!
			self.legend = legend
		else:
			print(f"\n[ERROR][IG] ERROR, could not identify graphtype!:\n{len(graphData[0])} {self.graphType}")
	
	def drawGraph(self,width,height,colouring=None,fontMultiplier=1.0,pointRadius=10):	#TODO dont re-gen the IGs all the time !
		self.canvas.delete("all")
		self.plotWidth = width
		self.plotHeight = height
		self.pointRadius = pointRadius
		if self.graphData is None:
			print("[IG] ERROR drawing graph: No graph data has been set!")
			return
		
		self.dataObjects = graphLib.canvas_createPlot(self,self.canvas,self.graphData,width,height,graphType=self.graphType,lineColour=self.main.graphLineColour,
				colourscale=self.colourscale,fontMultiplier=fontMultiplier,scaleFactor=self.main.osScaleFactor,pointRadius=pointRadius)
	
	def colourBar(self,bar,col="#ff0000",stroke="#ff0000"):
		#print("[IG] Colouring bar "+str(bar)+" with "+str(col))
		try:
			self.canvas.itemconfig(bar,fill=col,outline=stroke)
		except:
			print(f"[IG] ERROR bar highlight: {bar} {col} {stroke}")
	
	def highlightCell(self,x,y):
		try:
			self.canvas.itemconfig(self.dataObjects[x][y],outline="#ff00ff",width=4)
			self.canvas.tag_raise(self.dataObjects[x][y])
			self.highlightpositions.add((x,y))
		except:
			print(f"[IG] ERROR cell highlight: {y} {len(self.dataObjects[0])}")
	
	def clearCellHighlight(self,x,y):
		self.canvas.itemconfig(self.dataObjects[x][y],outline=None,width=0)
		self.highlightpositions.remove((x,y))

