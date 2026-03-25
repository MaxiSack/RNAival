
import os.path

from tkinter import Canvas
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Label as ThemedLabel

import graphs.InteractiveGraph as ig
import graphs.drawGraphics as graphLib
from functions.baseFunctions import getLocalMaxima	#TODO cleanup !

import gui.functions as fun

#container storing multiple graphs on the same page
#stores the data, syncs the sizes, distributes them and later displays in gui

class Combograph:
	def __init__(self,main,title,groupID,graphType=None,legend=None,positionalColouring=None,styles=None,xlab=None,ylab=None,lineColours=None):
		#TODO cleanup parent frame reference & and make setter + re-gen IGs for pop-out
		#when popping out: re-gen IGs (info-bar and canvas), then draw graph from IG onto canvas
		#when changing params: just re-draw...?
		#what if size changed between??? ~ change size of existing canvas?
		#canvas.config(width=,height=)
		#and then clear the canvas !	canvas.delete("all")
		#TODO cleanout graph sizes; set only when display is called (and then shared / synced across graphs if necessary)
		
		#TODO for pop out:
		#button on target-notebook
		#removes tab from parent
		#creates Toplevel()
		#adds all combographs onto self
		#	only change parent
		#	re-gens IGs + draws them
		
		#TODO who manages notebook tabs for combos right now?
		
		self.title = title
		self.groupID = groupID	#key for main.outputGroups -> notebook
		self.main = main
		print("\n[Combo] Creating combograph "+str(self.title))
		
		
		
		self.xlab=xlab
		self.ylab=ylab
		
		self.xLabels=None
		self.xLabelSpace=0
		self.cutOuterXLabsBool=False
		
		#self.graphDataList = list()	#list of (graphName,graphData)
		self.allGraphData = dict()		#dict of graphName -> graphData
		#graphData can be:
		# list of [x,y1,y2,y3,...]	-> (multi-)barplot	BAR
		# list of list of [z]		-> heatmap		MAP
		self.IGdict = dict()		#of interactiveGraph s
		
		self.combo_x_min = None
		self.combo_x_max = None
		self.combo_y_min = None
		self.combo_y_max = None
		self.graphType = graphType
		
		self.legend = legend
		
		if positionalColouring is None:
			self.positionalColouring = [dict(),dict()]
		else:
			self.positionalColouring = positionalColouring	# [0,1] * {xval:style}
		self.setStyles(styles)
		
		self.stacked=False	#TODO
		
		self.peakGroups = dict()	#TODO remove this stuff...
		self.globalYScale=False
		self.ybins = -1
		self.ystep = -1
		self.colouroverride = dict()
		
		self.connectedGraphs = list()
		self.addConnectedGraph(self)	#to update all IGS withing the same combo
		self.selectedPoints = set()
		self.hasWrittenHeader = False
		self.descriptorFields = None
		self.pointDescriptor = None
		self.axislabels=dict()
		
		self.lineColours=lineColours
		
		self.graphFrame = None
	
	def setStyles(self,styles):
		self.styles=dict()	#id -> (fill,stroke,stroke-width)
		self.styles["default"]=(self.main.graphBarColour,self.main.graphLineColour,"1")
		if not styles is None:
			for key,value in styles.items():
				self.styles[key]=(value[0],value[1],"1")
	
	def addPointDescriptor(self,descriptorFields,pointDescriptor):	#used for SCATTER ... #TODO could be used more
		self.descriptorFields = descriptorFields
		self.pointDescriptor = pointDescriptor
	
	def addData(self,data,globalYScale=False,colourscale=None,colouroverride=None,axislabels=None,peakGroups=None):
		#print("[Combo] Setting data for combograph "+str(self.title)+", "+str(len(data))+" sub-graphs")
		self.globalYScale=globalYScale
		self.colourscale_define=colourscale
		ndatapoints = len(data[0][1])
		if self.graphType=="HEAT":
			#data = [(libID,[heatmap,lengthList,posList])]
			self.xvals=data[0][1][2]
			self.yvals=data[0][1][1]
			ndatapoints = len(self.xvals)
			self.ybins = len(self.yvals)
			self.ystep = 1	#needs to be 1, for some reason...
			#print("[Combo] HEAT: "+str(ndatapoints)+" x "+str(self.ybins))
			
			self.highlightpositions = set()	#TODO
			
		if not axislabels is None and len(axislabels)!=len(data):
			print(f"\nERROR, length missmatch!: {axislabels}")
			print(f"{len(axislabels)} {len(data)}")
			return
		for i,(graphName,graphData) in enumerate(data):
			self.addGraph(graphName,graphData,
				colouroverride=None if colouroverride is None else colouroverride[i],
				#axislabels is list of [(xlab,ylab) for each subgraph]	#(to allow for different types of scatter plots, e.g. volcano+positional)
				axislabels=(self.xlab,self.ylab) if axislabels is None else axislabels[i],
				peakGroups=None if peakGroups is None else peakGroups[i])
			
			if len(graphData) != ndatapoints and not self.graphType=="HEAT":
				print("[Combo] ERROR! data are not the same length!:\n\t"+str(ndatapoints)+"\t"+str(len(graphData)))
		
		if self.graphType=="SCATTER":
			return
		
		self.xbins,self.xstep = ig.getAxisScale(ndatapoints)	#TODO gets re-calculated when drawing anyway...
		if self.xbins==-1 or self.xstep==-1:
			self.error=True
		#print("[Combo] Xaxis: "+str(self.xbins)+" "+str(self.xstep)+" "+str(ndatapoints))
		
		if self.globalYScale:
			if self.graphType=="HEAT":
				pass
			else:
				maxy1=0
				maxy2=0
				
				for i,(graphName,graphData) in enumerate(data):
					maxy1 = max(max([max([point[i] for i in range(1,len(point),2)]) for point in graphData]),maxy1)
					if len(graphData[0])>2:
						maxy2 = max(max([max([point[i] for i in range(2,len(point),2)]) for point in graphData]),maxy2)
				
				if len(graphData[0])>2:
					self.ybins,self.ystep = ig.getAxisScale2(maxy1,maxy2)	#TODO currently overriden when drawing
				else:
					self.ybins,self.ystep = ig.getAxisScale(maxy1)
				if self.ybins==-1 or self.ystep==-1:
					self.error=True
					#print(str(maxy1)+" "+str(maxy2))
					print("[Combo] ERROR: No step size found for "+str(graphName)+": "+"\t".join([str(max([point[i] for point in graphData])) for i in range(1,len(graphData[0]))]))
				print("[Combo] Global Y-Bins calculated: "+str(self.ybins))
		#print("\n[DEBUG] graph Data bounds:")
		#if len(graphData[0])<10:
		#	print("[DEBUG] "+str(graphData[0])+" "+str(graphData[-1]))
		#else:
		#	print("[DEBUG] "+str(len(graphData[0]))+" x "+str(len(graphData[0][0])))
	
	def addGraph(self,graphName,graphData,colouroverride=None,axislabels=None,peakGroups=None):
		self.allGraphData[graphName]=graphData
		self.colouroverride[graphName]=colouroverride	#TODO instead store all this in one parameter dict to then pass onto the drawfunciton... ?
		self.axislabels[graphName]=axislabels
		if self.graphType=="BAR":
			if peakGroups is None:
				self.peakGroups[graphName] = getLocalMaxima(self.allGraphData[graphName])
			else:
				self.peakGroups[graphName] = peakGroups
			pass
		else:
			self.peakGroups[graphName] = None
	
	def getPeakGroups(self,graphNames):
		return [self.peakGroups[graphName] for graphName in graphNames]	
	
	def setXLabels(self,xLabels,xSpace):
		self.xLabels=xLabels
		self.xLabelSpace=xSpace
	
	#def setXYLab(self,xlab=None,ylab=None):	#not needed, labels are only set on graph creation/data load!	
	#	if not xlab is None:self.xlab=xlab	#but maybe could be set later.... ! ......
	#	if not ylab is None:self.ylab=ylab
	
	def cutOuterXLabs(self):
		self.cutOuterXLabsBool=True
	
	#def genPeakGroups(self):
	#	peakGroups=list()
	#	for i,(graphName,graphData) in enumerate(self.allGraphData.items()):
	#		peakGroups.append( esi.getLocalMaxima(self.graphData))	#TODO set from elsewhere
	
	
	def generateIGs(self,main,resultsPath):	#TODO set aprent frame for combo and then gen IGs onto that... ~~ split generate from draw??
		
		
		
		
		#print("\n[Combo] Creating IGs for combograph "+str(self.title)+":")
		
		#self.graphCanvas = Canvas(basegui.outputGraphicsNotebook)#,bg=self.backgroundColour,highlightthickness=0)
		#basegui.outputGraphicsScrollCanvasList.append(self.graphCanvas)
		#basegui.outputGraphicsNotebook.add(self.graphCanvas,text=self.title)
		#self.graphCanvas["yscrollcommand"] = basegui.outputGraphicsScrollbar.set
		#self.graphCanvas.pack(side="left",fill="y")
		#self.graphFrame = ThemedFrame(self.graphCanvas)
		#self.graphCanvas.create_window((0,0),window=self.graphFrame,anchor="nw")
		#self.graphFrame.bind_all("<Button-4>",self.mouseWheelScroll)
		#self.graphFrame.bind_all("<Button-5>",self.mouseWheelScroll)	#TODO extra function for graph scroll
		
		if self.graphFrame is None:	#TODO also add extra label with (full) title !!
			notebook,scrollbar,scrollList = fun.addOutputGraphicsGroup(main,self.groupID)
			self.graphFrame = ThemedFrame(notebook,style="TEST.TFrame")
			notebook.add(self.graphFrame,text=self.title)
			
			self.graphCanvas = Canvas(self.graphFrame)#,bg=self.backgroundColour,highlightthickness=0)
			scrollList.append(self.graphCanvas)
			self.graphCanvas["yscrollcommand"] = scrollbar.set
			self.graphCanvas.pack(fill="both",expand=True,anchor="nw")
			self.graphFrame2 = ThemedFrame(self.graphCanvas,style="TEST.TFrame")
			self.graphCanvas.create_window((0,0),window=self.graphFrame2,anchor="nw")
			
			ThemedLabel(self.graphFrame2,text=self.title,style="Medium.TLabel").pack(fill="x",anchor="nw",expand=True)
			
			#fitCanvasWidthGraph(self,canvas)
			main.mainWindow.after(1000,lambda canvas=self.graphCanvas: main.fitCanvasWidthGraph(canvas))	#TODO ??? even neccessary? ~~yeah...
		#else:
		#	for child in graphFrame2.winfo_children():child.destroy()
			#TODO make it so that IG just re-draws itself insted of requiring reletiong of the objects !
		
		#self.IGdict = dict()	#TODO dont delete IGs, just re-draw them ! (in a different function)
		#genIGs should only be called once ! or again if we pop-out the window!
		if len(self.IGdict)>0:return
		
		#graphWidth = basegui.mainNotebook.winfo_width()
		graphWidth = main.mainNotebook.winfo_width()-30	#TODO refer to combo parentframe ! #TODO re-calc when displaying...?
		#graphHeight = basegui.mainNotebook.winfo_height()*0.80/len(self.allGraphData.keys())
		graphHeight = main.mainNotebook.winfo_height()*0.4
		#if graphHeightlen(self.allGraphData.keys())==1: = basegui.mainNotebook.winfo_height()*0.80/len(self.allGraphData.keys())
		if len(self.allGraphData.keys())==1:graphHeight = main.mainNotebook.winfo_height()*0.80
		for (graphName,graphData) in self.allGraphData.items():
			xlab,ylab = self.axislabels[graphName]
			#print("\nLABELS: "+str(self.axislabels[graphName]))
			newGraph = ig.InteractiveGraph(main,self.graphFrame2,graphWidth,graphHeight,graphName,resultsPath,styles=self.styles,
				positionalColouring=self.positionalColouring,peakGroups=self.peakGroups[graphName],graphType = self.graphType,parentCombo=self,
				xlab=xlab,ylab=ylab,lineColours=self.lineColours
				)#,colouring=self.colouring)#TODO resultsfolder, do properly!
			self.IGdict[graphName]=newGraph
			#print("[Combo] Y-bins for IG: "+str(self.ybins))
			newGraph.setXLabels(self.xLabels)
			newGraph.setData(self.graphType,graphData,legend=self.legend,ybins=self.ybins,ystep=self.ystep,colourscale=self.colourscale_define)
			if graphName in self.colouroverride:
				newGraph.overrideColours(self.colouroverride[graphName])
	
	def drawOntoGui(self,fontmultiplier=1.0):
		print("\n[Combo] Drawing IGs of combograph "+str(self.title)+" onto GUI")
		for graphName,newGraph in self.IGdict.items():
			newGraph.drawGraph(fontmultiplier=fontmultiplier)
	
	def addConnectedGraph(self,comboGraph):
		#TODO can send signals to another
		self.connectedGraphs.append(comboGraph)
	
	def selectPoint(self, pos):
		#print("[Combo] Selecting point "+str(pos))
		self.selectedPoints.add(pos)
		for igraph in self.IGdict.values():
			igraph.selectPoint(pos)
		
		if not self.descriptorFields is None:
			if not self.hasWrittenHeader:
				self.main.writeTextOutput("\t".join(self.descriptorFields))
				self.hasWrittenHeader = True
			self.main.writeTextOutput("\t".join([str(v) for v in self.pointDescriptor[pos]]))
	
	def clearPoint(self, pos):
		#print("[Combo] Clearing point "+str(pos))
		self.selectedPoints.remove(pos)
		for igraph in self.IGdict.values():
			igraph.clearPoint(pos)
	
	def clearSelection(self):
		print("[Combo] Clearing selected points:\n"+str(self.selectedPoints))
		for pos in list(self.selectedPoints):
			self.clearPoint(pos)
			#for igraph in self.IGdict.values():
			#	igraph.clearPoint(pos)
		#self.selectedPoints = set()
	
	def clearConnected(self):	#TODO !
		print("[Combo] Clearing all connected Graphs")
		if combo in self.selectedPoints:	#TODO shold be: for combo in self.connectedgraphs
			combo.clearSelection()
	
#	def highlight(self,pattern=None):
#		print("\n[Combo] Highlighting IGs for combograph "+str(self.title)+":")
#		#if not pattern is None:
#		#	for graphName,newGraph in self.IGdict.items():
#		#		newGraph.highlightBars(pattern=pattern)
#		if not self.highlights is None:
#			for graphName,newGraph in self.IGdict.items():
#				#print("Highlighting! "+str(self.highlights))
#				#newGraph.highlightBars(highlights=self.highlights)
#				#TODO
#				print("[IG] HIGHLIGHTING EXTRA NOT CURRENTLY SUPPORTED!")
	
	def exportAsSVG(self,resultsPath,exportW,exportH,exportFontsize):	#TODO specify libraries and make this the function from the IG for self-export (with libID in the defaultname)
		if self.graphType=="SCATTER":return	#TODO implement this
		titleOffset = int(exportFontsize)*2
		print("\n[Combo] Exporting combograph "+str(self.title))
		#print("[Combo] Legend: "+str(self.legend))
		mySVG = list()
		mySVG.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>")
		mySVG.append("<!-- Created by RNAival, from the project DigitalPROTECT, University of Halle -->")
		tw=int(graphWidth) if exportW is None else int(exportW)
		if not self.legend is None: tw+=int(exportFontsize)*13
		th=(int(graphHeight) if exportH is None else int(exportH)+10)+self.xLabelSpace
		mySVG.append("<svg x=\""+str(0)+"\" y=\""+str(0)+"\" width=\""+str(tw)+"\" height=\""
			+str(th*len(self.allGraphData.keys())+titleOffset)+"\" viewbox=\"0 0 "+str(tw)
			+" "+str(th*len(self.allGraphData.keys())+titleOffset)+"\" xmlns=\"http://www.w3.org/2000/svg\">")
		
		
		for key,style in self.styles.items():graphLib.svg_writeStyle(mySVG,key,style[0],style[1],sw=1)
		
		self.exportFontsize = exportFontsize
		#TODO combograph title!!
		graphLib.svg_drawText(mySVG,tw/2,exportFontsize,self.title,fontsize=int(exportFontsize*1.3),xanchor="middle",yanchor="middle")
		
		for i,(graphName,graphData) in enumerate(self.allGraphData.items()):
			graph_yoffset=th*i + titleOffset
			graph_xoffset=0
			
			
			self.width = exportW
			self.height = th	#exportH
			self.xbase=exportFontsize*4 if self.ylab is None else exportFontsize*6		#TODO scalefactor!
			self.axisbuffer = 5
			self.markerLength = 10
			self.ybuffer = exportFontsize*1.5 if self.xlab is None else exportFontsize*3.5
			self.ybuffer += self.xLabelSpace
			self.ybase=self.height-self.ybuffer
			self.plotwidth = self.width-self.xbase
			self.plotheight = self.height-self.ybuffer
			
			self.graphData = graphData
			
			
			
			#maxy1 = max([point[-2] for point in graphData])
			#maxy2 = max([point[-1] for point in graphData])
			if self.globalYScale:
				#print("[Combo] Using global Yscale: "+str(self.ybins)+"x"+str(self.ystep)+"p")
				pass
			else:
				maxy1 = max([max([point[i] for i in range(1,len(point),2)]) for point in graphData])
				if len(graphData[0])>2:
					maxy2 = max([max([point[i] for i in range(2,len(point),2)]) for point in graphData])
					self.ybins,self.ystep = ig.getAxisScale2(maxy1,maxy2)
				else:
					self.ybins,self.ystep = ig.getAxisScale(maxy1)
				if self.ybins==-1 or self.ystep==-1:
					self.error=True
					#print(str(maxy1)+" "+str(maxy2))
					print("[Combo] ERROR: No step size found for "+str(graphName)+": "+"\t".join([str(max([point[i] for point in graphData])) for i in range(1,len(graphData[0]))]))
				print("[Combo] Y-Bins: "+str(self.ybins))
			self.xdataToPix = self.plotwidth / (self.xstep*(self.xbins+1))
			
			self.graphName = graphName
			self.width = tw	#TODO!
			
			if self.graphType == "BAR" or self.graphType == "BAR2":
			
				barwidth = self.xdataToPix
				self.barRadius = max(0.001,(barwidth)/2.0)
				sw=1
				if self.barRadius <1: sw=max(0.1,self.barRadius/2)
				self.styles["defBar"]=(self.main.graphBarColour,self.main.graphLineColour,str(sw))
				#self.styles["defBar"]=(self.main.graphBarColour,self.main.graphLineColour,str(sw))	#TODO ????
				graphLib.svg_writeStyle(mySVG,"defBar",self.styles["defBar"][0],self.styles["defBar"][1],sw=self.styles["defBar"][2])	#TODO define earlier ~ all graphs have same x!!!
				
				if len(graphData[0])>2:	#TODO unify in the function!
					self.ydataToPix = self.plotheight / (self.ystep*(sum(self.ybins)+1))
					self.yzero = self.ybase - self.ybins[1]*self.ystep*self.ydataToPix
					graphLib.svg_drawBar2plot(mySVG,self,self.allGraphData[graphName],
						lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
						width=tw,height=exportH+self.xLabelSpace,scaleFactor=self.main.osScaleFactor,graph_yoffset=graph_yoffset,graph_xoffset=graph_xoffset)
				else:
					self.ydataToPix = self.plotheight / (self.ystep*(self.ybins))
					self.yzero = self.ybase# - self.ybins*self.ystep*self.ydataToPix
					#print("yzeroCalc")
					#print(self.ybase)
					#print(self.ybins)
					#print(self.ybins*self.ystep*self.ydataToPix)
					#print(self.graphName)
					#print(self.colouroverride.keys())
					#print(self.colouroverride[graphName][:10])
					graphLib.svg_drawBarplot(mySVG,self,self.allGraphData[graphName],
						lineColour=self.main.graphLineColour,barColour=self.main.graphLineColour,barFillColour=self.main.graphBarColour,
						width=tw,height=exportH+self.xLabelSpace,scaleFactor=self.main.osScaleFactor,graph_yoffset=graph_yoffset,graph_xoffset=graph_xoffset,peakGroups=self.peakGroups[graphName])
			
			elif self.graphType == "HEAT":
				self.ydataToPix = self.plotheight / (len(self.yvals)+1)
				self.yzero = self.ybase
				
				#print("\t[COMBO] HEAT export")
				#print(str(len(self.allGraphData[graphName][0]))+" "+str(len(self.allGraphData[graphName][0][0])))
				colourscale,legend = getColourScale(self.allGraphData[graphName][0],self.colourscale_define)
				#print(colourscale)
				#print(legend)
				graphLib.svg_drawHeatmap(mySVG,self,self.allGraphData[graphName][0],
					lineColour=self.main.graphLineColour,colourscale=colourscale,
					width=exportW,height=exportH,scaleFactor=self.main.osScaleFactor,
					graph_yoffset=graph_yoffset,graph_xoffset=graph_xoffset,legend=legend)
				pass
			
		mySVG.append("</svg>")
		
		with open(os.path.join(resultsPath,self.title+".svg"),"w") as svgw:
			svgw.write("\n".join(mySVG))
	
	
	
	def calcGraphBounds(self,graphType=None):
		if not graphType is None: self.graphType=graphType
		if self.graphType is None:
			print("ERROR: graphtype not set!")
			return
		if self.graphType=="BAR":
			for graphName,graphData in self.graphDataList:
				minx=min([point[0] for point in graphData])
				maxx=max([point[0] for point in graphData])
				
				if self.combo_x_min is None:self.combo_x_min=minx
				elif self.combo_x_min==minx:pass
				else:
					print("ERROR: inconsistent graphData: min X: "+str(self.combo_x_min)+" "+str(minx))
					self.combo_x_min=min(self.combo_x_min,minx)
				
				if self.combo_x_max is None:self.combo_x_max=maxx
				elif self.combo_x_max==maxx:pass
				else:
					print("ERROR: inconsistent graphData: max X: "+str(self.combo_x_max)+" "+str(maxx))
					self.combo_x_max=max(self.combo_x_max,maxx)
				
				miny=min([min([v*(-1 if i%2==1 else 1) for i,v in enumerate(point[1:])]) for point in graphData])
				maxy=max([max([v*(-1 if i%2==1 else 1) for i,v in enumerate(point[1:])]) for point in graphData])
				
				if self.combo_y_min is None:self.combo_y_min=miny
				elif self.combo_y_min==maxy:pass
				else:
					#print("ERROR: inconsistent graphData: min Y: "+str(self.combo_y_min)+" "+str(miny))
					self.combo_y_min=min(self.combo_y_min,miny)
				
				if self.combo_y_max is None:self.combo_y_max=maxy
				elif self.combo_y_max==maxy:pass
				else:
					#print("ERROR: inconsistent graphData: max Y: "+str(self.combo_y_max)+" "+str(maxy))
					self.combo_y_max=max(self.combo_y_max,maxy)
					
		if self.graphType=="Map":
			#for graphData in self.graphDataList:
				#TODO chck that dimensions match
			pass	#axis labels need to be set differently or special map... map is x*[y*[z]]
				#need extra lists for xpos and xpos, then calc "bounds" (axis labels) from those
		
		print("[Combo] "+self.title+"-Bounds: "+str(self.combo_x_min)+"-"+str(self.combo_x_max)+"x"+str(self.combo_y_min)+"-"+str(self.combo_y_max))
	
	def setGraphBounds(self,minx=None,maxx=None,miny=None,maxy=None):	#overwrite bounds AFTER calculating them from the data
		if not minx is None: self.combo_x_min=minx
		if not maxx is None: self.combo_x_max=maxx
		if not miny is None: self.combo_y_min=miny
		if not maxy is None: self.combo_y_max=maxy
		print("[Combo] "+self.title+"-Bounds: "+str(self.combo_x_min)+"-"+str(self.combo_x_max)+"x"+str(self.combo_y_min)+"-"+str(self.combo_y_max))
	
	#----------------------- GUI related funcitons ------------------------------
	def setGuiSpace(self,parent,xspace,yspace):
		self.parent=parent
		self.xspace=xspace
		self.yspace=yspace	#TODO may be unlimited with a scrollbar ~~
	
	def setGUIStoragePath(self,guipath):
		self.guipath=guipath

def getColourScale(graphData,colourscale_define):
	
	maxval = max([max(column) for column in graphData])
	sumval = sum([sum(column) for column in graphData])
	valcount = len(graphData) * len(graphData[0])
	
	allvals = [v for col in graphData for v in col]
	sortedValues = sorted(allvals)
	
	colourscale = list()
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
				legendDesc.append((graphLib.getHexColourTuple(colour),str(val)+" (p"+str(round(point[2],0))+")"))
			else:
				print("ERROR: could not find relative definition in colouscale point: "+str(point))
		else:
			print("ERROR: could not find colourscale point type: "+str(point))
		colourscale.append((val,colour))
	#print(colourscale)
	legend=("Count:",legendDesc)
	#if -1 in self.yvals:self.legend[1].append(("#ff00ff","esiRNAs"))	#TODO legend addition for marled cells! (also mark cells)
	return colourscale,legend
