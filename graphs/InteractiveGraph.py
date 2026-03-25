
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
	def __init__(self,main,parent,width,height,title,safePath,colouring=None,exportFontsize=12,styles=None,positionalColouring=None,peakGroups=None,graphType="unset",parentCombo=None,xlab=None,ylab=None,lineColours=None):#,safePath="graph"):
		self.main = main
		self.width = width
		self.height = height
		self.title = title
		self.graphName = title
		self.positionalColouring = positionalColouring
		self.safePath = safePath
		#print("\n[IG] Creating new interactive graph "+str(title))
		#print("[IG] Graph-width: "+str(self.width)+" Graph-height: "+str(self.height))
		
		graphFrame = ThemedFrame(parent)
		graphFrame.pack()	#TODO dont pack, just return and let extern place it ?
		
		labelFrame = ThemedFrame(graphFrame)
		labelFrame.pack(fill="both")
		ThemedLabel(labelFrame,text=self.title).pack(fill="both",side="left")
		#ThemedButton(labelFrame,text="Save as File",command=self.saveAsFile).pack(fill="y",side="right")
		if graphType=="SCATTER":
			print("[IG] Type is SCATTER")
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
		
		#self.graphType = "unset"
		self.graphType = graphType
		self.graphData = None
		self.peakGroups = peakGroups
		self.bars = None
		
		self.xbase=120		#TODO scalefactor!
		self.axisbuffer = 5
		self.markerLength = 10
		self.ybuffer = 50
		if not xlab is None: self.ybuffer+=30
		self.ybase=self.height-self.ybuffer
		
		self.plotwidth = self.width-self.xbase
		self.plotheight = self.height-self.ybuffer
		
		self.xdataToPix = None
		self.ydataToPix = None
		self.peakMap = None
		
		self.legend = None
		self.highlightpositions = None
		
		self.exportW = self.width
		self.exportH = self.height
		
		self.markedPeaks = set()	#of indices
		self.styles = styles
		#styles=list()		#(id,fill,stroke,stroke-width)	#TODO apply this to the other colour uses!
		#styles.append(("mybase",self.main.graphBarColour,self.main.graphLineColour,"1"))	#TODO also cleanup this!
		#styles.append(("mygreen","lime","green","1"))
		#styles.append(("myred","pink","red","1"))
		#styles.append(("myblue1","#88ccff","#0000ff","1"))	#TODO define in generall an then get from there!
		#styles.append(("myblue2","#5599ff","#0000dd","1"))
		#styles.append(("myblue3","#2266bb","#0000bb","1"))
		#styles.append(("mysky","#aaffff","#00eeee","1"))
		
		#if colouring is None:
		self.styles=styles
		#else:
		#	self.styles=[styles[i] for i in colouring]
		
		self.error=False
		self.exportFontsize = exportFontsize
		self.xlab=xlab
		self.ylab=ylab
		#print("[IG] axis labels: "+str(xlab)+" "+str(ylab))	#TODO !
		
		self.clickFillCol = "#88ccff"
		self.clickStrokeCol = "#2255ff"
		
		self.globalYScale=False
		self.ybins = -1
		self.ystep = -1
		
		#print(self.positionalColouring)
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
	
	def resetColours(self):
		#for peakIndex in self.markedPeaks:
		#	colourPeak(self,peak,col=self.main.graphBarColour)
		#self.markedPeaks = set()
		
		for bar in self.bars:
			if isinstance(bar,list):
				#for subbar in bar:
				#	self.canvas.itemconfig(subbar,self.main.graphBarColour,outline=self.main.graphBarColour)
				self.canvas.itemconfig(bar[0],fill=self.main.graphBarColour,outline=self.main.graphLineColour)
				if len(bar)>1:
					self.canvas.itemconfig(bar[1],fill=self.main.graphBarColour,outline=self.main.graphLineColour)
				if len(bar)>2:
					self.canvas.itemconfig(bar[2],fill="lime",outline="green")
					self.canvas.itemconfig(bar[3],fill="lime",outline="green")
				if len(bar)>4:
					self.canvas.itemconfig(bar[4],fill="pink",outline="red")
					self.canvas.itemconfig(bar[5],fill="pink",outline="red")
			else:
				self.canvas.itemconfig(bar,fill=self.main.graphBarColour,outline=self.main.graphLineColour)
	
	def updateDesc(self,index,yindex,ypoint):
		#TODO self.graphData[index] get group and use those values!
		#~ use list of pos -> groupIndex to access self.peakGroups
		#then also re-colour all
		#self.myGraphStats.set("pos: "+str(self.graphData[index][0])+" count: "+str(self.graphData[index][1])+" ??")
		
		if self.graphType=="BAR":
			if not self.peakGroups is None and not self.peakMap is None:
				
				peakID = self.peakMap[index]
				if peakID == -1:return
				peak = self.peakGroups[peakID]
				print("[IG] peakID: "+str(self.peakMap[index])+" Found peak: "+str(peak))
				
				self.myGraphStats.set("pos: "+str(peak[0]+self.xDataOffset)+", count: "+str(self.graphData[peak[0]-1][1]))
				
				if not self.parentCombo is None:
					self.parentCombo.main.writeTextOutput("pos: "+str(peak[0]+self.xDataOffset)+", count: "+str(self.graphData[peak[0]-1][1]))
				
				
				if peakID in self.markedPeaks:
					self.colourPeak(peak,col=self.main.graphBarColour)
					self.markedPeaks.remove(peakID)
				else:
					self.colourPeak(peak,col="#ff0000")
					self.markedPeaks.add(peakID)
			else:
				print("[IG] ERROR: Peaks not grouped!")
				return
		elif self.graphType=="BAR2":
			point = self.graphData[index]
			print("[IG] Selected: "+str(point)+" xindex: "+str(index)+" yindex: "+str(yindex))
			
			#self.myGraphStats.set("pos: "+str(point[0])+", + count: "+str(point[1])+", - count: "+str(point[2]))
			if len(point)==7:
				if yindex<0:	#TODO use legend description here and as in-graph legend!!
					#self.myGraphStats.set("pos: "+str(point[0])+", sense, count (all): "+str(point[1])+", count (21-24): "+str(point[3])+", count (21): "+str(point[5]))
					self.myGraphStats.set("pos: "+str(point[0])+", sense, covarage (all): "+str(point[1])+", coverage (21-24): "+str(point[3])+", coverage (21): "+str(point[5]))
					if (index,1) in self.markedPeaks:
						self.colourBar(self.bars[index][4],"pink","red")
						self.colourBar(self.bars[index][2],"lime","green")
						self.colourBar(self.bars[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.markedPeaks.remove((index,1))
					else:
						self.colourBar(self.bars[index][4],"#88ccff","#0000ff")
						self.colourBar(self.bars[index][2],"#5599ff","#0000dd")
						self.colourBar(self.bars[index][0],"#2266bb","#0000bb")
						self.markedPeaks.add((index,1))
				else:
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, count: "+str(point[2])
						+", count (19-25): "+str(point[4])+", count (21-23): "+str(point[6]))
					if (index,2) in self.markedPeaks:
						self.colourBar(self.bars[index][5],"pink","red")
						self.colourBar(self.bars[index][3],"lime","green")
						self.colourBar(self.bars[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.markedPeaks.remove((index,2))
					else:
						self.colourBar(self.bars[index][5],"#88ccff","#0000ff")
						self.colourBar(self.bars[index][3],"#5599ff","#0000dd")
						self.colourBar(self.bars[index][1],"#2266bb","#0000bb")
						self.markedPeaks.add((index,2))
			elif len(point)==5:	#start-end	#TODO!
				if ypoint<0:
					self.myGraphStats.set("pos: "+str(point[0])+", sense, coverage: "+str(point[3])+", coverage (esiRNA): "+str(point[1]))
					if (index,1) in self.markedPeaks:
						if point[0] in self.positionalColouring[0]:
							self.colourBar(self.bars[index][0],self.styles[self.positionalColouring[0][point[0]]][0],self.styles[self.positionalColouring[0][point[0]]][1])
						else: self.colourBar(self.bars[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.colourBar(self.bars[index][2],self.main.graphBarColour,self.main.graphLineColour)
						self.markedPeaks.remove((index,1))
					else:
						self.colourBar(self.bars[index][0],self.clickFillCol,self.clickStrokeCol)
						self.colourBar(self.bars[index][2],self.clickFillCol,self.clickStrokeCol)
						self.markedPeaks.add((index,1))
				else:
					#self.myGraphStats.set("pos: "+str(point[0])+", antisense, 5' count: "+str(point[4])+", 3' count: "+str(point[2]))
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, coverage: "+str(point[3])+", coverage (esiRNA): "+str(point[2]))
					if (index,2) in self.markedPeaks:
						if point[0] in self.positionalColouring[1]:
							self.colourBar(self.bars[index][1],self.styles[self.positionalColouring[1][point[0]]][0],self.styles[self.positionalColouring[1][point[0]]][1])
						else: self.colourBar(self.bars[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.colourBar(self.bars[index][3],self.main.graphBarColour,self.main.graphLineColour)
						self.markedPeaks.remove((index,2))
					else:
						self.colourBar(self.bars[index][1],self.clickFillCol,self.clickStrokeCol)
						self.colourBar(self.bars[index][3],self.clickFillCol,self.clickStrokeCol)
						self.markedPeaks.add((index,2))
			elif len(point)==3:
				if ypoint<0:
					self.myGraphStats.set("pos: "+str(point[0])+", sense, count: "+str(point[1]))
					if (index,1) in self.markedPeaks:
						if point[0] in self.positionalColouring[0]:
							self.colourBar(self.bars[index][0],self.styles[self.positionalColouring[0][point[0]]][0],self.styles[self.positionalColouring[0][point[0]]][1])
						else: self.colourBar(self.bars[index][0],self.main.graphBarColour,self.main.graphLineColour)
						self.markedPeaks.remove((index,1))
					else:
						self.colourBar(self.bars[index][0],self.clickFillCol,self.clickStrokeCol)
						self.markedPeaks.add((index,1))
				else:
					self.myGraphStats.set("pos: "+str(point[0])+", antisense, count: "+str(point[2]))
					if (index,2) in self.markedPeaks:
						if point[0] in self.positionalColouring[1]:
							self.colourBar(self.bars[index][1],self.styles[self.positionalColouring[1][point[0]]][0],self.styles[self.positionalColouring[1][point[0]]][1])
						else: self.colourBar(self.bars[index][1],self.main.graphBarColour,self.main.graphLineColour)
						self.markedPeaks.remove((index,2))
					else:
						self.colourBar(self.bars[index][1],self.clickFillCol,self.clickStrokeCol)
						self.markedPeaks.add((index,2))
		
		elif self.graphType=="HEAT":	#TODO is inaccurate!
			yindex = abs(yindex)
			if yindex >= len(self.yvals):
				print("[IG] ERROR: yposition "+str(yindex)+" is outside heatmap!")
				return
			xpos = self.xvals[index]
			ypos = self.yvals[yindex]	#TODO event.y ?
			
			self.myGraphStats.set("start-pos: "+str(xpos)+",  length: "+str(ypos)+", count: "+str(self.graphData[index][yindex]))
			
			#print(self.highlightpositions)
			
			if (index,yindex) in self.highlightpositions:
				self.clearCellHighlight(index,yindex)
			else:
				self.highlightCell(index,yindex)
			
		else:
			print("[IG] ERROR: Unknown graphtype: "+self.graphType)
	def cursorSelectPoint(self,event):
		#print("\n[IG] Clicked into Canvas:")
		#print("Cursor: "+str(event.x)+" "+str(event.y))	#coords in canvas-space
		
		fieldx = event.x-self.xbase
		fieldy = event.y-self.yzero
		if fieldx<0:
			print("Outside graph")
			return
		#print("Inside Canvas: "+str(fieldx)+" "+str(fieldy))
		
		#xcenter = graph.xbase + abs(graph.minx*graph.xdataToPix) + point[1]*graph.xdataToPix
		#xcoord = fieldx - abs(self.minx*self.xdataToPix)
		#ycoord = fieldy - abs(self.miny*self.ydataToPix)
		#print("Coords: "+str(xcoord)+" "+str(ycoord))
		
		#xval = xcoord / self.xdataToPix
		#yval = ycoord / self.ydataToPix
		#print("Values: "+str(xval)+" "+str(yval))
		
		self.pointRadius = 10
		#nhits=0
		#for i,point in enumerate(self.graphData):	#point vs points ?!?!
		for i in range(len(self.points)):	#point vs points ?!?!
			if self.pointRadius > ((event.x-self.points[i][1])**2+(event.y-self.points[i][2])**2)**0.5:
				
				
				#print("Found hit to point "+str(point))
				#print(str(point[1]*self.xdataToPix)+" "+str(point[2]*self.ydataToPix))
				#print(str(self.points[i][1])+" "+str(self.points[i][2]))
				#self.canvas.itemconfig(self.points[i][0],outline="#ddaa00")
				
				#self.selectPoint(i)
				
				#TODO call other plots and highlight
				if i in self.parentCombo.selectedPoints:
					for comboGraph in self.parentCombo.connectedGraphs:
						comboGraph.clearPoint(i)
				else:
					for comboGraph in self.parentCombo.connectedGraphs:
						comboGraph.selectPoint(i)
				
				
				#nhits+=1
				#if nhits>10:break
		
			#if self.pointRadius > ((xcoord-point[1]*self.xdataToPix)**2+(ycoord-point[2]*self.ydataToPix)**2)**0.5:
			#	print("Found hit to point "+str(point))
			#	print(str(point[1]*self.xdataToPix)+" "+str(point[2]*self.ydataToPix))
			#	nhits+=1
			#	if nhits>10:break
		
	
	def selectPoint(self, pos):
		if self.graphType=="SCATTER":
			point = self.graphData[pos]
			#print("Found hit to point "+str(point))
			self.myGraphStats.set("pos: "+str(point[0])+", x: "+str(point[1])+", y: "+str(point[2]))
			self.canvas.itemconfig(self.points[pos][0],outline="#ff00c6")#"#ff5700")#"#ff00c6")#"#d800df")#"#00ffff")	#ff7700
		elif self.graphType=="BAR":
			self.barhighlights[pos] = graphLib.createBarHighlight(self,pos)
	
	def clearPoint(self,pos):
		if self.graphType=="SCATTER":
			self.canvas.itemconfig(self.points[pos][0],outline="")
		elif self.graphType=="BAR":
			self.canvas.delete(self.barhighlights[pos])
	
	def cursorSelectBar(self,event):	#TODO use event.y to get y pos and therefore bar on + or minus!!!
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
			print("[IG] Selected Position(index): "+str(barIndex)+" "+str(yindex)+" "+str(event.y)+" "+str(self.ybase)+" "+str(ypoint))
			if barIndex<len(self.graphData):
				self.updateDesc(barIndex,yindex,ypoint)
				
				if barIndex in self.parentCombo.selectedPoints:
					for comboGraph in self.parentCombo.connectedGraphs:
						comboGraph.clearPoint(barIndex)
				else:
					for comboGraph in self.parentCombo.connectedGraphs:
						comboGraph.selectPoint(barIndex)
		
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
			self.maxx = max(max(xvals),0)	#TODO fix that to be more dynamic!
			#print("xmin "+str(min(xvals)))
			
			yvals = [graphData[i][2] for i in range(len(graphData))]
			self.miny = min(min(yvals),0)
			self.maxy = max(max(yvals),0)
			#graph.xbins[1]	#bins for graph.minx
			#graph.xbins[0]	#bins for graph.maxx
			#graph.ybins[1]	#bins for graph.miny
			#graph.ybins[0]	#bins for graph.maxy
			self.xbins,self.xstep = getAxisScale2(abs(self.maxx),abs(self.minx))
			self.ybins,self.ystep = getAxisScale2(abs(self.maxy),abs(self.miny))
			self.xdataToPix = self.plotwidth / (self.xstep*(sum(self.xbins)+1))
			self.ydataToPix = self.plotheight / (self.ystep*(sum(self.ybins)+1))
			
			
			self.xzero = self.xbase+abs(self.minx*self.xdataToPix)
			self.yzero = self.ybase-abs(self.miny*self.ydataToPix)
			
			print("[IG - SCATTER] X-Axis: "+str(self.minx)+" - "+str(self.maxx)+", "+str(self.xbins)+" * "+str(self.xstep)+", "+str(self.xdataToPix))
			print("[IG - SCATTER] Y-Axis: "+str(self.miny)+" - "+str(self.maxy)+", "+str(self.ybins)+" * "+str(self.ystep)+", "+str(self.ydataToPix))
			return
		
		
		if not self.peakGroups is None:
			self.peakMap = graphLib.getPeakMap(self.peakGroups,len(self.graphData))
		
		ndatapoints = len(graphData)
		#print(ndatapoints)
		self.xbins,self.xstep = getAxisScale(ndatapoints)
		if self.xbins==-1 or self.xstep==-1:
			self.error=True
		#print(self.xbins)
		#print(self.xstep)
		if self.xbins==-1 or self.xstep==-1:return
		#print("Xaxis: "+str(xbins)+" "+str(xstep)+" "+str(ndatapoints))
		self.xdataToPix = self.plotwidth / (self.xstep*(self.xbins+1))
		barwidth = self.xdataToPix
		self.barRadius = max(0.001,(barwidth)/2.0)	#TODO 1 is outline!
		#print("[IG] X-Bins: "+str(self.xbins))
		
		if len(graphData[0])==2 and self.graphType=="BAR":	#x/y graph
			#print("[IG] parameter Y-Bins: "+str(ybins))
			#print("[IG] Y-Bins: "+str(self.ybins))
			if ybins==-1 or ystep==-1:
				maxy = max([y for x,y in graphData])
				self.ybins,self.ystep = getAxisScale(maxy)
				if self.ybins==-1 or self.ystep==-1:
					self.error=True
			else:
				self.ybins = ybins
				self.ystep = ystep
			self.ydataToPix = self.plotheight / (self.ystep*(self.ybins+1))	#TODO
			self.yzero = self.ybase
			self.xDataOffset = min([d[0] for d in graphData])-1
			#print("[IG] X-Offset: "+str(self.xDataOffset))
			#print("[IG] Y-Bins: "+str(self.ybins))
		elif len(graphData[0])>2 and self.graphType=="BAR2":	#x/(-y&+y) graph
			if ybins==-1 or ystep==-1:
				maxy1 = max([max([point[i] for i in range(1,len(point),2)]) for point in graphData])
				maxy2 = max([max([point[i] for i in range(2,len(point),2)]) for point in graphData])	#TODO add overwrite
				self.ybins,self.ystep = getAxisScale2(maxy1,maxy2)
				#print(graphData)
				if self.ybins==-1 or self.ystep==-1:
					self.error=True
					#print(str(maxy1)+" "+str(maxy2))
					#print("[IG] ERROR: no Axis scale found!: "+str(graphData))
					print("[IG] ERROR: no Axis scale found!: "+str(maxy1)+" "+str(maxy2))#+"\t".join([str(max([point[i] for point in graphData])) for i in range(1,len(graphData[0]))]))
			else:
				self.ybins = ybins
				self.ystep = ystep
			
			self.ydataToPix = self.plotheight / (self.ystep*(sum(self.ybins)+1))	#TODO for BAR2!
			
			self.yzero = self.ybase - self.ybins[1]*self.ystep*self.ydataToPix
			
			self.legend = legend
		elif self.graphType=="HEAT":
			self.highlightpositions = set()
			#maxy = self.yvals[-1]
			#miny = self.yvals[0]	#only for single...
			#TODO!!!
			self.ybins = len(self.yvals)
			#print("yvals:"+str(self.ybins))
			self.ystep = 1
			#self.ydataToPix = self.plotheight / (maxy-miny+1)
			self.ydataToPix = self.plotheight / (len(self.yvals)+1)
			self.yzero = self.ybase
			#~
			#~ double heat plot for forward and revers...
			
			#maxval=0
			#sumval=0
			#valcount=0
			allvals=list()
			for x,column in enumerate(self.graphData):
				#for y,value in enumerate(column):
				#	valcount+=1
				#	sumval+=value
				#	maxval=max(maxval,value)
				allvals.extend(column)
			
			maxval = max([max(column) for column in self.graphData])
			sumval = sum([sum(column) for column in self.graphData])
			valcount = len(self.graphData) * len(self.graphData[0])
			
			sortedValues = sorted(allvals)
			
			#TODO
			#colourscale_define = [(("abs",0),(0,0,255)), (("rel","av"),(255,255,255)), (("rel","max"),(255,0,0))]
			#colourscale_define = [(("abs",0),(0,0,0)), (("abs",1),(0,0,155)), (("rel","av"),(0,255,255)), (("rel","max"),(255,0,0))]
			#colourscale_define = [(("abs",0),(0,0,0)), (("abs",1),(0,0,100)), (("rel","percentile",95),(0,255,255)), (("rel","max"),(255,0,0))]
			colourscale_define = colourscale
			self.colourscale = list()
			legendDesc = list()
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
			
			#self.legend = colourscale	#TODO
			#self.legend=("Count:",[("#000000","0"),("#000064",">0"),("#00ffff","95th percentile"),("#ff0000","max")])
			self.legend=("Count:",legendDesc)
			if -1 in self.yvals:self.legend[1].append(("#ff00ff","esiRNAs"))
		elif self.graphType=="multiLine":#TODO tmp solution...
			self.legend = legend
		else:
			print("\n[IG] !!! ERROR !!! could not identify graphtype!:\n"+str(len(graphData[0]))+" "+self.graphType)
			return
		#print("Yaxis: "+str(ybins)+" "+str(ystep)+" "+str(maxy))
		#print("[IG] XYscale: "+str(self.xdataToPix)+" "+str(self.ydataToPix))
		
	
	def saveAsFile(self):
		filename = asksaveasfilename(initialfile=os.path.join(self.safePath,self.title+".eps"),filetypes=[("Encapsulated PostScript",".eps")],initialdir=self.safePath)
		self.saveAsPostscript(filename)
	
	def saveDirectly(self):	#TODO unused because doesnt work if graph isnt beeing rendered; rely on manual saveAsFile or svg export instead
		print("[IG] Saving directlly")
		print(self.title)
		#self.saveAsPostscript(os.path.join(self.safePath,self.title+".eps"))
		self.canvas.postscript(file=os.path.join(self.safePath,self.title+".eps"))
	
	def drawGraph(self,colouring=None,fontmultiplier=1.0):	#TODO add size and other parameters important for drawing, dont re-gen the IGs all the time !
		self.canvas.delete("all")
		
		
		if self.graphData is None:
			print("[IG] ERROR drawing graph: No graph data has been set!")
			return
		if self.error==True:
			print("[IG] ERROR drawing graph: There was an error with the graph, skipping.")
			return
		if self.graphType == "BAR":
			#self.bars = graphLib.drawInteractiveBarplot(self,self.graphData,
			#	lineColour=self.main.graphLineColour,barColour=self.main.graphBarColour,barFillColour=self.main.graphBarColour,
			#	width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor,peakGroups=self.peakGroups)
			self.bars = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="BAR",fontmultiplier=fontmultiplier)
		elif self.graphType == "BAR2":
			#self.bars = graphLib.drawInteractiveBar2plot(self,self.graphData,
			#	lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
			#	width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
			self.bars = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="BAR2",fontmultiplier=fontmultiplier)
		elif self.graphType == "multiLine":
			self.bars = graphLib.canvas_createPlot(self,self.canvas,self.graphData,
				lineColour=self.main.graphLineColour,
				width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor,graphType="multiLine",fontmultiplier=fontmultiplier)
		elif self.graphType == "HEAT":
			#self.map = graphLib.drawHeatmap(self,self.graphData,	#TODO click on cell and get value for that cell! pos,length,count !!! #TODO
			#	lineColour=self.main.graphLineColour,colourscale=self.colourscale,
			#	width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
			self.map = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="HEAT",colourscale=self.colourscale,fontmultiplier=fontmultiplier)
		elif self.graphType == "SCATTER":
			#self.points = graphLib.drawInteractiveScatterplot(self,self.graphData,	#TODO click on point and get value for that cell! pos,count,foldChange !!! #TODO
			#	width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
			self.points = graphLib.canvas_createPlot(self,self.canvas,self.graphData,lineColour=self.main.graphLineColour,graphType="SCATTER",fontmultiplier=fontmultiplier)
		else: print("[IG] ERROR: Unknown graphtype: "+str(self.graphType))
	
	def colourPeak(self,peak,col="#ff0000"):
		#barcolours = graphLib.getPosColours(self.peakGroups,len(self.graphData),default=self.main.graphBarColour)
		for pos in peak:
			self.canvas.itemconfig(self.bars[pos],fill=col)#,outline=col)	#outline not supported for "line-Barplots" like these
	
	def colourBar(self,bar,col="#ff0000",stroke="#ff0000"):
		#print("[IG] Colouring bar "+str(bar)+" with "+str(col))
		try:
			self.canvas.itemconfig(bar,fill=col,outline=stroke)
		except:
			try:
				self.canvas.itemconfig(bar,fill=col,outline=stroke)
			except:
				pass
	
	#def colourCell(self,cell,col="#ff0000"):	#colouring in a heatmap is stupid ~ maybe if you utilise the borders... #TODO
	#	self.canvas.itemconfig(cell,fill=col,outline=col)
	
	def highlightBars(self,pattern=None,positionalColouring=None):
		if self.bars is None:
			print("[IG] Error, no bars set!")
			return
		if not pattern is None:
			highlightpositions = getHighlightPositions(pattern)
			if highlightpositions is None:
				print("[IG] Error with pattern decoding")
				return
			l = len(self.graphData)
			self.highlightpositions = [highlightpositions,[l-p-1 for p in highlightpositions]]
			print("Pattern "+str(pattern))
		elif not positionalColouring is None:
			try:
				#print(positionalColouring)
				self.highlightpositions = [positionalColouring[0].keys(),positionalColouring[1].keys()]
			except:
				return
		else:
			return
		#print(self.highlightpositions)
		if len(self.bars[0])==6:
			for pos in self.highlightpositions:	#TODO also highlight in SVG!!!
				#self.styles.append(("myblue1","#88ccff","#0000ff","1"))
				try:
					self.colourBar(self.bars[pos-1][4],col=self.styles[3][1],stroke=self.styles[3][2])
				except:
					print("[IG] ERROR; pos oob bars: "+str(len(self.bars))+" "+str(pos))	#TODO ~not realy an error, just a miss assumtion (l24 for a 21 construct)
			for pos in self.highlightpositions[1]:	#TODO also highlight in SVG!!!
				try:
					self.colourBar(self.bars[pos-1][5],col=self.styles[3][1],stroke=self.styles[3][2])
				except:
					print("[IG] ERROR; pos oob bars: "+str(len(self.bars))+" "+str(pos))
		else:
			for strand in [0,1]:
				xOff = min(positionalColouring[strand])
				for pos in positionalColouring[strand]:
					try:
						self.colourBar(self.bars[pos-xOff][strand],col=self.styles[3][1],stroke=self.styles[3][2])
					except:
						print("[IG] ERROR; pos oob bars: "+str(len(self.bars))+" "+str(pos))	#TODO ~not realy an error, just a miss assumtion (l24 for a 21 construct)
	
	def highlightCell(self,x,y):
		try:
			self.canvas.itemconfig(self.map[x][y],outline="#ff00ff",width=4)
			self.canvas.tag_raise(self.map[x][y])
			self.highlightpositions.add((x,y))
		except:
			print("[IG] ERROR cell highlight: "+str(y)+" "+str(len(self.map[0])))
	
	def clearCellHighlight(self,x,y):
		self.canvas.itemconfig(self.map[x][y],outline=None,width=0)
		self.highlightpositions.remove((x,y))
		
	
	def saveAsSVG(self,svgPath):	#write self as svg
		#os.path.join(self.safePath,self.title+".svg")
		if self.error==True:return
		mySVG = list()
		mySVG.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>")
		mySVG.append("<!-- Created by siRNATools, from the project DigitalPROTECT, University of Halle -->")
		mySVG.append("<svg x=\""+str(0)+"\" y=\""+str(0)+"\" width=\""+str(self.exportW)+"\" height=\""+str(self.exportH)+"\" viewbox=\"0 0 "+str(self.width)+" "+str(self.height)+"\">")
		
		if self.graphType == "BAR":
			graphLib.svg_drawBarplot(mySVG,self,self.graphData,
				lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
				width=self.exportW,height=self.exportH,scaleFactor=self.main.osScaleFactor)
		elif self.graphType == "BAR2":
			graphLib.svg_drawBar2plot(mySVG,self,self.graphData,
				lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
				width=self.exportW,height=self.exportH,scaleFactor=self.main.osScaleFactor)
		elif self.graphType == "HEAT":
			#print("SVG solo export not implemented for heatmaps!")
			graphLib.svg_drawHeatmap(mySVG,self,self.graphData,
				lineColour=self.main.graphLineColour,colourscale=self.colourscale,
				width=self.exportW,height=self.exportH,scaleFactor=self.main.osScaleFactor)
		else:
			print("[IG] wrong graphtype!: "+str(self.graphType))
		mySVG.append("</svg>")
		
		with open(svgPath,"w") as svgw:
			svgw.write("\n".join(mySVG))
	
	def getSVG(self,mySVG,graph_yoffset=0,graph_xoffset=0):	#add self with offsets to the svg line list
		if self.error==True:return
		if self.graphType == "BAR":
			#graphLib.svg_drawBarplot(mySVG,self,self.graphData,
			graphLib.svg_drawBar2plot(mySVG,self,self.graphData,
				lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
				width=self.exportW,height=self.exportH,scaleFactor=self.main.osScaleFactor,graph_yoffset=graph_yoffset,graph_xoffset=graph_xoffset)
		elif self.graphType == "BAR2":
			graphLib.svg_drawBar2plot(mySVG,self,self.graphData,
				lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
				width=self.exportW,height=self.exportH,scaleFactor=self.main.osScaleFactor,graph_yoffset=graph_yoffset,graph_xoffset=graph_xoffset)
		elif self.graphType == "HEAT":
			#print("SVG group export not implemented for heatmaps!")
			graphLib.svg_drawHeatmap(mySVG,self,self.graphData,
				lineColour=self.main.graphLineColour,colourscale=self.colourscale,
				width=self.exportW,height=self.exportH,scaleFactor=self.main.osScaleFactor,graph_yoffset=graph_yoffset,graph_xoffset=graph_xoffset)
			
			#graphLib.svg_drawBar2plot(mySVG,self,self.graphData,
			#	lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
			#	width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor,graph_yoffset=graph_yoffset,graph_xoffset=graph_xoffset)
			#lineColour=self.main.graphLineColour,colourscale=self.colourscale,
			#	width=self.width,height=self.height,scaleFactor=self.main.osScaleFactor)
		else:
			print("[IG] wrong graphtype!: "+str(self.graphType))
	
	def saveAsPostscript(self,filename):
		self.canvas.postscript(file=filename)
	
	def setDimensions(width,height):
		self.width=width
		self.height=height

def getHighlightPositions(pattern):
	parts = pattern.split("+")
	#5poffset=0
	highlightpositions=list()	#(pos,len)	#0-indexed!, used only internally for finding bars
	#shifts=list()	#(position,by)
	shifts=dict()	#position->by
	for i,part in enumerate(parts):	#this pattern deconding is just for me... "later" we get directly coordinates from the embl!
		if "x" in part:
			amount,length = part.split("x")
			length = int(length)
			currentpos = 0
			if len(highlightpositions)>0:
				currentpos = highlightpositions[-1][0]+highlightpositions[-1][1]
			while currentpos in shifts:
				currentpos+=shifts[currentpos]
			
			for i in range(int(amount)):
				highlightpositions.append((currentpos,length))
				currentpos+=length
				
		else:
			try:
				
				currentpos = 0
				if len(highlightpositions)>0:
					currentpos = highlightpositions[-1][0]+highlightpositions[-1][1]
				shifts[currentpos]=int(part)
				
				#if i==0:
				#	5poffset=int(part)	#~shifts.append((0,int(part)))
				#else:
				#	shifts.append((0,int(part)))
			except:
				print("[IG] Error with pattern "+pattern)
				return None
	#print(pattern)
	#print(highlightpositions)
	#print(shifts)
	highlightpositionsSet = set()
	for pos,length in highlightpositions:
		highlightpositionsSet.add(pos)
	return highlightpositionsSet

def getAxisScale(maxValue,minValue=1):
	#print("[IG] Getting Axis scale for maxvalue "+str(maxValue))
	if maxValue<20:return int(maxValue)+1,1
	allowedSteps = [1,5,10,20,50,100,200,500,1000,2000,5000,10000,50000,100000,500000,1000000]
	targetbins = 9
	bins = -1
	step = -1
	for stepSize in allowedSteps:
		nbins = int((maxValue-2)/stepSize)+1
		if nbins < 5:break	#stepSize increases, so there is nothing more
		if nbins >20:continue
		if abs(nbins-targetbins)<abs(bins-targetbins):
			bins = nbins
			step = stepSize
	if bins==-1 or step==-1: print("[IG] Error no stepsize found for "+str(maxValue)+" "+str(minValue))
	return bins,step

def getAxisScale2(maxValue1,maxValue2):
	
	allowedSteps = [1,2,5,10,20,50,100,200,500,1000,2000,5000,10000,50000,100000,500000,1000000,5000000,10000000]
	if maxValue1<2 and maxValue2<2:
		allowedSteps = [0.001,0.002,0.005,0.01,0.02,0.05,0.1,0.2,0.5]
	targetbins = 9
	bins = -1
	step = -1
	breaks = (-1,-1)
	for stepSize in allowedSteps:
		nbins = int(maxValue1/stepSize)+3+int(abs(maxValue2)/stepSize)	#TODO its BREAKS not bins!
		if nbins < 5:break	#stepSize increases, so there is nothing more
		if nbins >20:continue
		if abs(nbins-targetbins)<abs(bins-targetbins):
			bins = nbins
			step = stepSize
			breaks = (int(abs(maxValue1)/stepSize)+1,0 if maxValue2==0 else int(abs(maxValue2)/stepSize)+1)	#breaks[1],0,breaks[0]
	#if bins==-1 or step==-1: print("[IG] Error no stepsize found for "+str(maxValue1)+" "+str(maxValue2))
	#print("Axis scale for "+str(maxValue1)+" "+str(maxValue2)+" : "+str(breaks)+" "+str(step))
	return breaks,step
