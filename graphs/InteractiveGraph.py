
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
	def __init__(self,main,parent,width,height,title,safePath,colouring=None,exportFontsize=12,styles=None,positionalColouring=None,graphType="unset",
			parentCombo=None,xlab=None,ylab=None,lineColours=None):
		self.main = main
		self.width = width
		self.height = height
		self.title = title
		self.graphName = title
		self.positionalColouring = positionalColouring
		self.safePath = safePath
		#print("\n[IG] Creating new interactive graph "+str(title))
		#print("[IG] Graph-width: "+str(self.width)+" Graph-height: "+str(self.height))
		self.pointRadius = parentCombo.pointRadius
		graphFrame = ThemedFrame(parent)
		graphFrame.pack()	#TODO dont pack, just return and let extern place it ? - would be good for more complex placement, but not necessary right now
		
		labelFrame = ThemedFrame(graphFrame)
		labelFrame.pack(fill="both")
		ThemedLabel(labelFrame,text=self.title).pack(fill="both",side="left")
		#ThemedButton(labelFrame,text="Save as File",command=self.saveAsFile).pack(fill="y",side="right")	#Save as eps using Canvas native export
		if graphType=="SCATTER":	#clear all marked points
			#print("[IG] Type is SCATTER")
			ThemedButton(labelFrame,text="Clear",command=parentCombo.clearConnected).pack(fill="y",side="right")
		
		self.myGraphStats = StringVar()
		self.myGraphStats.set("")
		ThemedEntry(graphFrame,textvariable=self.myGraphStats,state="readonly").pack(fill="both")
		
		self.canvas = Canvas(graphFrame,width=self.width,height=self.height,bg=self.main.graphBackgroundColour,highlightthickness=0)
		self.canvas.pack()
		
		self.graphType = graphType
		if self.graphType=="SCATTER":
			self.canvas.bind("<Button-1>",self.cursorSelectPoint)
		else:
			self.canvas.bind("<Button-1>",self.cursorSelectBar)
		
		self.graphData = None
		self.bars = None
		
		self.xbase=120		#TODO scalefactor!
		self.axisbuffer = 5
		self.markerLength = 10
		self.ybuffer = 50
		if not xlab is None: self.ybuffer+=30
		self.ybase=self.height-self.ybuffer
		
		self.plotwidth = self.width-self.xbase	#TODO is even still used?
		self.plotheight = self.height-self.ybuffer
		
		self.xdataToPix = None
		self.ydataToPix = None
		
		self.legend = None
		self.highlightpositions = None
		
		self.exportW = self.width
		self.exportH = self.height
		
		self.markedBars = set()	#of indices
		self.styles = styles
		
		self.error=False
		self.exportFontsize = exportFontsize
		self.xlab=xlab
		self.ylab=ylab
		
		self.clickFillCol = "#88ccff"
		self.clickStrokeCol = "#2255ff"
		
		self.globalYScale=False
		self.ybins = -1
		self.ystep = -1
		
		colouroverride = None
		
		self.parentCombo = parentCombo
		self.barhighlights = dict()
		self.lineColours = lineColours
		self.xLabels = None
	
	def setXLabels(self,xlabels):
		self.xLabels=xlabels
	
	def overrideExport(self,exportW,exportH):
		self.exportW = exportW
		self.exportH = exportH
		
		self.width = self.exportW
		self.height = self.exportH
		self.ybase=self.exportH-self.ybuffer
		self.plotwidth = self.width-self.xbase
		self.plotheight = self.height-self.ybuffer
	
	def overrideColours(self,colouroverride):
		self.colouroverride = colouroverride
	
	def updateDesc(self,index,yindex,ypoint):
		#print(f"[IG][Debug] Updating Desc of {self.graphType}-{self.title}:\t{index}\t{yindex}\t{ypoint}")
		
		if self.graphType=="BAR2":
			point = self.graphData[index]
			#print("[IG][Debug] Selected: "+str(point)+" xindex: "+str(index)+" yindex: "+str(yindex))
			
			#self.myGraphStats.set("pos: "+str(point[0])+", + count: "+str(point[1])+", - count: "+str(point[2]))
			if len(point)==7:
				if yindex<0:	#TODO use legend description here and as in-graph legend!!
					self.myGraphStats.set("pos: {point[0]}, sense, covarage (all): {point[1]}, coverage (21-24): {point[3]}, coverage (21): {point[5]}")
					if (index,1) in self.markedBars:
						self.colourBar(self.bars[index][4],"pink","red")
						self.colourBar(self.bars[index][2],"lime","green")
						self.colourBar(self.bars[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,1))
					else:
						self.colourBar(self.bars[index][4],"#88ccff","#0000ff")
						self.colourBar(self.bars[index][2],"#5599ff","#0000dd")
						self.colourBar(self.bars[index][0],"#2266bb","#0000bb")
						self.markedBars.add((index,1))
				else:
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, count: "+str(point[2])
						+", count (19-25): "+str(point[4])+", count (21-23): "+str(point[6]))
					if (index,2) in self.markedBars:
						self.colourBar(self.bars[index][5],"pink","red")
						self.colourBar(self.bars[index][3],"lime","green")
						self.colourBar(self.bars[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,2))
					else:
						self.colourBar(self.bars[index][5],"#88ccff","#0000ff")
						self.colourBar(self.bars[index][3],"#5599ff","#0000dd")
						self.colourBar(self.bars[index][1],"#2266bb","#0000bb")
						self.markedBars.add((index,2))
			elif len(point)==5:	#start-end	#TODO!
				if ypoint<0:
					self.myGraphStats.set("pos: "+str(point[0])+", sense, coverage: "+str(point[3])+", coverage (esiRNA): "+str(point[1]))
					if (index,1) in self.markedBars:
						if point[0] in self.positionalColouring[0]:
							self.colourBar(self.bars[index][0],self.styles[self.positionalColouring[0][point[0]]][0],
								self.styles[self.positionalColouring[0][point[0]]][1])
						else: self.colourBar(self.bars[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.colourBar(self.bars[index][2],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,1))
					else:
						self.colourBar(self.bars[index][0],self.clickFillCol,self.clickStrokeCol)
						self.colourBar(self.bars[index][2],self.clickFillCol,self.clickStrokeCol)
						self.markedBars.add((index,1))
				else:
					#self.myGraphStats.set("pos: "+str(point[0])+", antisense, 5' count: "+str(point[4])+", 3' count: "+str(point[2]))
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, coverage: "+str(point[3])+", coverage (esiRNA): "+str(point[2]))
					if (index,2) in self.markedBars:
						if point[0] in self.positionalColouring[1]:
							self.colourBar(self.bars[index][1],self.styles[self.positionalColouring[1][point[0]]][0],
								self.styles[self.positionalColouring[1][point[0]]][1])
						else: self.colourBar(self.bars[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.colourBar(self.bars[index][3],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,2))
					else:
						self.colourBar(self.bars[index][1],self.clickFillCol,self.clickStrokeCol)
						self.colourBar(self.bars[index][3],self.clickFillCol,self.clickStrokeCol)
						self.markedBars.add((index,2))
			elif len(point)==3:
				if ypoint<0:
					self.myGraphStats.set("pos: "+str(point[0])+", sense, count: "+str(point[1]))
					if (index,1) in self.markedBars:
						if point[0] in self.positionalColouring[0]:
							self.colourBar(self.bars[index][0],self.styles[self.positionalColouring[0][point[0]]][0],
								self.styles[self.positionalColouring[0][point[0]]][1])
						else: self.colourBar(self.bars[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,1))
					else:
						self.colourBar(self.bars[index][0],self.clickFillCol,self.clickStrokeCol)
						self.markedBars.add((index,1))
				else:
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, count: "+str(point[2]))
					if (index,2) in self.markedBars:
						if point[0] in self.positionalColouring[1]:
							self.colourBar(self.bars[index][1],self.styles[self.positionalColouring[1][point[0]]][0],
								self.styles[self.positionalColouring[1][point[0]]][1])
						else: self.colourBar(self.bars[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.markedBars.remove((index,2))
					else:
						self.colourBar(self.bars[index][1],self.clickFillCol,self.clickStrokeCol)
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
			self.canvas.itemconfig(self.points[pos][0],outline="#ff00c6")#"#ff5700")#"#ff00c6")#"#d800df")#"#00ffff")	#ff7700
		elif self.graphType=="BAR":
			point = self.graphData[pos]
			self.myGraphStats.set(f"{self.xlab}: {point[0]}, {self.ylab}: {point[1]}")
			self.barhighlights[pos] = graphLib.createBarHighlight(self,pos)
	
	def clearPoint(self,pos):
		if self.graphType=="SCATTER":
			self.canvas.itemconfig(self.points[pos][0],outline="")
		elif self.graphType=="BAR":
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
	
	def cursorSelectPoint(self,event):	#handles finding the point (circle) that was clicked on
		for i in range(len(self.points)):
			if self.pointRadius > ((event.x-self.points[i][1])**2+(event.y-self.points[i][2])**2)**0.5:
				#point[1] and point[2] are the point's center in canvas-space. And so is the event
				#call other plots and highlight
				self.selectPointInAll(i)
	
	def cursorSelectBar(self,event):	#handles finding the bar (cell) that was clicked on
		#print("Cursor: "+str(event.x)+" "+str(event.y))	#coords in canvas-space
		if self.bars is None and self.map is None:
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
				if self.graphType=="BAR":
					self.selectPointInAll(barIndex)
				else:
					self.updateDesc(barIndex,yindex,ypoint)
		
	#legend is a list of (Colour,String)
	def setData(self,graphType,graphData,legend=None,colourscale=None,ybins=-1,ystep=-1):
		#print("[IG] setting data for graph of type "+graphType)
		self.graphType = graphType
		if graphType=="HEAT":
			self.xvals=graphData[2]
			self.yvals=graphData[1]
			graphData=graphData[0]
			#print(len(graphData))
		self.graphData = graphData
		
		if graphType=="SCATTER":
			xvals = [graphData[i][1] for i in range(len(graphData))]
			self.minx = min(min(xvals),0)	#TODO enforces 0,0 to be in the graph, but cant look at area further away..
			self.maxx = max(max(xvals),0)	# fix that to be more dynamic! ~works fine for volcano, but that good for diff / position
			#print("xmin "+str(min(xvals)))
			
			yvals = [graphData[i][2] for i in range(len(graphData))]
			self.miny = min(min(yvals),0)
			self.maxy = max(max(yvals),0)
			#graph.xbins[1]	#bins for graph.minx
			#graph.xbins[0]	#bins for graph.maxx
			#graph.ybins[1]	#bins for graph.miny
			#graph.ybins[0]	#bins for graph.maxy
			self.xbins,self.xstep = graphLib.getAxisScale2(abs(self.maxx),abs(self.minx))
			self.ybins,self.ystep = graphLib.getAxisScale2(abs(self.maxy),abs(self.miny))
			self.xdataToPix = self.plotwidth / (self.xstep*(sum(self.xbins)+1))	#TODO these arent used anymore and draw re-calculates them !
			self.ydataToPix = self.plotheight / (self.ystep*(sum(self.ybins)+1))	# sync this / do this here maybe....
						
			self.xzero = self.xbase+abs(self.minx*self.xdataToPix)
			self.yzero = self.ybase-abs(self.miny*self.ydataToPix)
			
			print("[IG - SCATTER] X-Axis: "+str(self.minx)+" - "+str(self.maxx)+", "+str(self.xbins)+" * "+str(self.xstep)+", "+str(self.xdataToPix))
			print("[IG - SCATTER] Y-Axis: "+str(self.miny)+" - "+str(self.maxy)+", "+str(self.ybins)+" * "+str(self.ystep)+", "+str(self.ydataToPix))
			return
		
		ndatapoints = len(graphData)
		#print(ndatapoints)
		self.xbins,self.xstep = graphLib.getAxisScale(ndatapoints)
		if self.xbins==-1 or self.xstep==-1:
			self.error=True
		#print(self.xbins)
		#print(self.xstep)
		if self.xbins==-1 or self.xstep==-1:return
		#print("Xaxis: "+str(xbins)+" "+str(xstep)+" "+str(ndatapoints))
		self.xdataToPix = self.plotwidth / (self.xstep*(self.xbins+1))
		barwidth = self.xdataToPix
		self.barRadius = max(0.001,(barwidth)/2.0)
		#print("[IG] X-Bins: "+str(self.xbins))
		
		if len(graphData[0])==2 and self.graphType=="BAR":	#x/y graph
			#print("[IG] parameter Y-Bins: "+str(ybins))
			#print("[IG] Y-Bins: "+str(self.ybins))
			if ybins==-1 or ystep==-1:
				maxy = max([y for x,y in graphData])
				self.ybins,self.ystep = graphLib.getAxisScale(maxy)
				if self.ybins==-1 or self.ystep==-1:
					self.error=True
			else:
				self.ybins = ybins
				self.ystep = ystep
			self.ydataToPix = self.plotheight / (self.ystep*(self.ybins+1))	#TODO unused
			self.yzero = self.ybase
			self.xDataOffset = min([d[0] for d in graphData])-1
			#print("[IG] X-Offset: "+str(self.xDataOffset))
			#print("[IG] Y-Bins: "+str(self.ybins))
		elif len(graphData[0])>2 and self.graphType=="BAR2":	#x/(-y&+y) graph
			if ybins==-1 or ystep==-1:
				maxy1 = max([max([point[i] for i in range(1,len(point),2)]) for point in graphData])
				maxy2 = max([max([point[i] for i in range(2,len(point),2)]) for point in graphData])	#TODO add overwrite
				self.ybins,self.ystep = graphLib.getAxisScale2(maxy1,maxy2)
				#print(graphData)
				if self.ybins==-1 or self.ystep==-1:
					self.error=True
					#print(str(maxy1)+" "+str(maxy2))
					#print("[IG] ERROR: no Axis scale found!: "+str(graphData))
					print("[IG] ERROR: no Axis scale found!: "+str(maxy1)+" "+str(maxy2))
					#+"\t".join([str(max([point[i] for point in graphData])) for i in range(1,len(graphData[0]))]))
			else:
				self.ybins = ybins
				self.ystep = ystep
			
			self.ydataToPix = self.plotheight / (self.ystep*(sum(self.ybins)+1))	#TODO for BAR2!
			
			self.yzero = self.ybase - self.ybins[1]*self.ystep*self.ydataToPix
			
			self.legend = legend
		elif self.graphType=="HEAT":
			self.highlightpositions = set()
			self.ybins = len(self.yvals)
			self.ystep = 1
			self.ydataToPix = self.plotheight / (len(self.yvals)+1)
			self.yzero = self.ybase
			allvals=list()
			for x,column in enumerate(self.graphData):
				allvals.extend(column)
			
			maxval = max([max(column) for column in self.graphData])
			sumval = sum([sum(column) for column in self.graphData])
			valcount = len(self.graphData) * len(self.graphData[0])
			
			sortedValues = sorted(allvals)
			
			colourscale_define = colourscale
			self.colourscale = list()
			legendDesc = list()
			if not colourscale_define is None:
				for point,colour in colourscale_define:
					val=-1
					if point[0]=="abs":
						val=point[1]
						legendDesc.append((graphLib.getHexColourTuple(colour),str(val)))
					elif point[0]=="rel":
						if point[1]=="av":
							val=sumval/valcount
							legendDesc.append((graphLib.getHexColourTuple(colour),str(val)+" (average)"))
						elif point[1]=="max":
							val=maxval
							legendDesc.append((graphLib.getHexColourTuple(colour),str(val)+" (max)"))
						elif point[1]=="percentile":
							val=sortedValues[int(len(sortedValues)/100*point[2])]
							legendDesc.append((graphLib.getHexColourTuple(colour),str(val)+" (p"+str(point[2])+")"))
						else:
							print("ERROR: could not find relative definition in colouscale point: "+str(point))
					else:
						print("ERROR: could not find colourscale point type: "+str(point))
					self.colourscale.append((val,colour))
			
			#print(self.colourscale)
			self.legend=("Count:",legendDesc)
			if -1 in self.yvals:self.legend[1].append(("#ff00ff","esiRNAs"))
		elif self.graphType=="multiLine":#TODO with current draw setup, nothing more is required, need to update the other parts
			self.legend = legend
		else:
			print("\n[IG] !!! ERROR !!! could not identify graphtype!:\n"+str(len(graphData[0]))+" "+self.graphType)
			return
		#print("Yaxis: "+str(ybins)+" "+str(ystep)+" "+str(maxy))
		#print("[IG] XYscale: "+str(self.xdataToPix)+" "+str(self.ydataToPix))
		
	
	def saveAsFile(self):
		filename = asksaveasfilename(initialfile=os.path.join(self.safePath,self.title+".eps"),filetypes=[("Encapsulated PostScript",".eps")],initialdir=self.safePath)
		try:
			self.canvas.postscript(file=filename)
		except:
			print(f"[IG] Error with saving as eps")
			pass
	def saveAsSVG(self,svgPath):	#write self as svg	#TODO as alternative over eps export
		print("[IG] save self as SVG is not implemented")	#implement the same way that combograph does it
		pass
	def getSVG(self,mySVG,graph_yoffset=0,graph_xoffset=0):	#add self with offsets to the svg line list
		print("[IG] get self as SVG is not implemented")
		pass
	
	def drawGraph(self,colouring=None,fontMultiplier=1.0):	#TODO add size and other parameters important for drawing, dont re-gen the IGs all the time !
		self.canvas.delete("all")
		
		if self.graphData is None:
			print("[IG] ERROR drawing graph: No graph data has been set!")
			return
		if self.error==True:
			print("[IG] ERROR drawing graph: There was an error with the graph, skipping.")
			return
		if self.graphType == "BAR":
			self.bars = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="BAR",fontMultiplier=fontMultiplier,
				width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
		elif self.graphType == "BAR2":
			self.bars = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="BAR2",fontMultiplier=fontMultiplier,
				width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
		elif self.graphType == "multiLine":
			self.bars = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="multiLine",fontMultiplier=fontMultiplier,
				width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
		elif self.graphType == "HEAT":
			self.map = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="HEAT",fontMultiplier=fontMultiplier,
				width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor,colourscale=self.colourscale)
		elif self.graphType == "SCATTER":
			self.points = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="SCATTER",fontMultiplier=fontMultiplier,
				width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
		else: print("[IG] ERROR: Unknown graphtype: "+str(self.graphType))
	
	def colourBar(self,bar,col="#ff0000",stroke="#ff0000"):
		#print("[IG] Colouring bar "+str(bar)+" with "+str(col))
		try:
			self.canvas.itemconfig(bar,fill=col,outline=stroke)
		except:
			print(f"[IG] ERROR bar highlight: {bar} {col} {stroke}")
	
	def highlightCell(self,x,y):
		try:
			self.canvas.itemconfig(self.map[x][y],outline="#ff00ff",width=4)
			self.canvas.tag_raise(self.map[x][y])
			self.highlightpositions.add((x,y))
		except:
			print(f"[IG] ERROR cell highlight: {y} {len(self.map[0])}")
	
	def clearCellHighlight(self,x,y):
		self.canvas.itemconfig(self.map[x][y],outline=None,width=0)
		self.highlightpositions.remove((x,y))
	
	def setDimensions(width,height):	#TODO unused
		self.width=width
		self.height=height

