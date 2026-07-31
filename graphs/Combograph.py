
import os.path

from tkinter import Canvas
from tkinter.ttk import Frame as ThemedFrame
from tkinter.ttk import Label as ThemedLabel

import graphs.InteractiveGraph as ig
import graphs.drawGraphics as graphLib

import gui.functions as fun

#container storing multiple graphs on the same page
#stores the data, syncs the sizes, distributes them and later displays in gui

class Combograph:
	def __init__(self,main,title,groupID,graphType=None,legend=None,positionalColouring=None,styles=None,xlab=None,ylab=None,lineColours=None,isScrollGraph=True,fileName=None,tabName=None):
		
		#when changing params: just re-draw...? ~ requires checking if the respective Combograph already exists
		
		# for pop out:
		#button on target-notebook
		#removes tab from parent
		#creates Toplevel()
		#adds all combographs onto self
		#	only change parent
		#	re-gens IGs + draws them
		
		self.title = title
		self.fileName = title.replace(" ","_") if fileName is None else fileName	
		self.tabName = title if tabName is None else tabName	
		self.groupID = groupID	#key for main.outputGroups -> notebook
		self.main = main
		#print(f"[Combo] Creating combograph \"{self.title}\", with fileName \"{self.fileName}\" and tabName \"{self.tabName}\"")
		
		self.xlab=xlab
		self.ylab=ylab
		
		self.xLabels=None
		self.xLabelSpace=0
		
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
		
		self.globalYScale=False
		self.ybins = -1
		self.ystep = -1
		
		self.connectedGraphs = set()
		self.addConnectedGraph(self)	#to update all IGS withing the same combo
		self.selectedPoints = set()
		self.hasWrittenHeader = False
		self.descriptorFields = None
		self.pointDescriptor = None
		self.axislabels=dict()
		
		self.lineColours=lineColours
		
		self.comboFrame_base = None
		
		self.isScrollGraph=isScrollGraph
	
	def setStyles(self,styles):
		self.styles=dict()	#id -> (fill,stroke,stroke-width)
		self.styles["default"]=(self.main.graphBarColour,self.main.graphLineColour,"1")
		if not styles is None:
			for key,value in styles.items():
				self.styles[key]=(value[0],value[1],value[2])
	
	def addPointDescriptor(self,descriptorFields,pointDescriptor):	#used for SCATTER ... #TODO could be used more
		self.descriptorFields = descriptorFields
		self.pointDescriptor = pointDescriptor
	
	def addData(self,data,globalYScale=False,colourscale_define=None,axislabels=None):
		#print("[Combo] Setting data for combograph "+str(self.title)+", "+str(len(data))+" sub-graphs")
		self.globalYScale=globalYScale
		self.colourscale_define=colourscale_define
		ndatapoints = len(data[0][1])
		if self.graphType=="HEAT":
			#data = [(libID,[heatmap,lengthList,posList])]
			self.xvals=data[0][1][2]
			self.yvals=data[0][1][1]
			ndatapoints = len(self.xvals)
			self.ybins = len(self.yvals)
			self.ystep = 1
			#print("[Combo] HEAT: "+str(ndatapoints)+" x "+str(self.ybins)
			self.highlightpositions = set()
			
		if not axislabels is None and len(axislabels)!=len(data):
			print(f"\n[Combo] ERROR, length missmatch!: {axislabels}")
			print(f"                   {len(axislabels)} {len(data)}")
			return
		for i,(graphName,graphData) in enumerate(data):
			self.addGraph(graphName,graphData,
				#axislabels is list of [(xlab,ylab) for each subgraph]	#(to allow for different types of scatter plots, e.g. volcano+positional)
				axislabels=(self.xlab,self.ylab) if axislabels is None else axislabels[i])
			
			if len(graphData) != ndatapoints and not self.graphType=="HEAT":
				print("[Combo] ERROR! data are not the same length!:\n\t"+str(ndatapoints)+"\t"+str(len(graphData)))
		
		if self.globalYScale:
			if self.graphType=="BAR" or self.graphType=="BAR2" or self.graphType=="multiLine":
				data_y_min = 0
				data_y_max = 0
				for i,(graphName,graphData) in enumerate(data):
					data_y_min = min(-max([max([point[i] for i in range(2,len(point),2)]) for point in graphData]) if len(graphData[0])>2 else 0,data_y_min)
					data_y_max = max(max([max([point[i] for i in range(1,len(point),2)]) for point in graphData]),data_y_max)
				
				self.axis_y_min,self.axis_y_max,self.axis_y_step = graphLib.getAxisScale3(data_y_max,minValue=data_y_min)
	
	def addGraph(self,graphName,graphData,axislabels=None):
		self.allGraphData[graphName]=graphData
		self.axislabels[graphName]=axislabels
		#print(f"[Combo] Adding sub-graph \"{graphName}\"")
	
	def setXLabels(self,xLabels,xLabelSpace):
		self.xLabels=xLabels
		self.xLabelSpace=xLabelSpace
	
	def generateIGs(self,main,resultsPath):
		#print("\n[Combo] Creating IGs for combograph "+str(self.title)+":")
		
		if self.comboFrame_base is None:
		
			self.parentnotebook = fun.addOutputGraphicsGroup(main,self.groupID,isScrollGraph=self.isScrollGraph)
			#print(f"[Combo] generating new Tab {self.groupID}")
			if self.isScrollGraph:
				self.comboFrame_base,tabCanvas,self.comboFrame = self.parentnotebook.addScrollTab(self.tabName)	#inner_frame_style="gBorder.TFrame"
			else:
				self.comboFrame_base = ThemedFrame(self.parentnotebook,style="gBorder.TFrame")
				self.parentnotebook.add(self.comboFrame_base,text=self.tabName)
				self.comboFrame = self.comboFrame_base
			
			ThemedLabel(self.comboFrame_base,text=self.title,style="Medium.TLabel").pack(fill="x",anchor="nw",side="top")
			if self.isScrollGraph:	#addScrollTab requires extra packing to allow for better customisability
				tabCanvas.pack(fill="both",expand=True,anchor="nw")
		
		#self.IGdict = dict()	#TODO dont delete Combos and IGs, just re-draw them ! (in a different function)
		#genIGs should only be called once ! or again if we pop-out the window!
		if len(self.IGdict)>0:return
		graphCanvasHeight = main.mainNotebook.winfo_height()*0.36
		if len(self.allGraphData.keys())==1:graphCanvasHeight = main.mainNotebook.winfo_height()*0.75
		
		for (graphName,graphData) in self.allGraphData.items():
			xlab,ylab = self.axislabels[graphName]
			#print("\nLABELS: "+str(self.axislabels[graphName]))
			#resultsPath is only used for the inate eps export of tkinter canvas
			newGraph = ig.InteractiveGraph(main,self.comboFrame,graphCanvasHeight,graphName,resultsPath,styles=self.styles,
				positionalColouring=self.positionalColouring,graphType = self.graphType,parentCombo=self,
				xlab=xlab,ylab=ylab,lineColours=self.lineColours)
			self.IGdict[graphName]=newGraph
			#print("[Combo] Y-bins for IG: "+str(self.ybins))
			newGraph.setXLabels(self.xLabels)
			newGraph.setData(self.graphType,graphData,legend=self.legend,colourscale_define=self.colourscale_define)#,ybins=self.ybins,ystep=self.ystep
			if self.globalYScale: 
				newGraph.globalYScale = True
				newGraph.axis_y_min,newGraph.axis_y_max,newGraph.axis_y_step = self.axis_y_min,self.axis_y_max,self.axis_y_step
	
	def drawOntoGui(self,fontMultiplier=1.0):
		#print("[Combo] Drawing IGs of combograph "+str(self.title)+" onto GUI")
		graphWidth = self.main.mainWindow.winfo_width()-self.main.frameBorderSize*4
		graphCanvasHeight = self.main.mainNotebook.winfo_height()*0.36
		if len(self.allGraphData.keys())==1:graphCanvasHeight = self.main.mainNotebook.winfo_height()*0.75
		pointRadius = 10	#TODO allow setting from GUI
		for graphName,newGraph in self.IGdict.items():
			newGraph.drawGraph(graphWidth,graphCanvasHeight,fontMultiplier=fontMultiplier,pointRadius=pointRadius)
	
	def addConnectedGraph(self,comboGraph):#can send signals to another
		self.connectedGraphs.add(comboGraph)
	
	def selectPoint(self, pos):
		#print(f"[Combo] ({self.title}) Selecting point {pos}")
		self.selectedPoints.add(pos)
		for igraph in self.IGdict.values():
			igraph.selectPoint(pos)
		
		if not self.descriptorFields is None:
			if not self.hasWrittenHeader:
				self.main.writeTextOutput("#"+"\t".join(self.descriptorFields))
				self.hasWrittenHeader = True
			self.main.writeTextOutput("\t".join([str(v) for v in self.pointDescriptor[pos]]))
	
	def clearPoint(self, pos):
		#print(f"[Combo] [{self.title}] Clearing point at position {pos} from {self.selectedPoints}")
		self.selectedPoints.remove(pos)
		for igraph in self.IGdict.values():
			igraph.clearPoint(pos)
	
	def clearSelection(self):
		#print("[Combo] Clearing selected points:\n"+str(self.selectedPoints))
		for pos in list(self.selectedPoints):
			self.clearPoint(pos)
	
	def clearConnected(self):
		#print("[Combo] Clearing all connected Graphs")
		for comboGraph in self.connectedGraphs:	#self is in connectedGraphs
			comboGraph.clearSelection()
	
	def exportAsSVG(self,resultsPath,graphWidth,graphHeight,fontMultiplier,selectedGraphName=None,overridePath=False):
		titleFontsize = int(26*fontMultiplier)
		mySVG = list()
		mySVG.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>")
		mySVG.append("<!-- Created by RNAival, from the project DigitalPROTECT, University of Halle -->")
		titleOffset = int(titleFontsize)*2
		libNameSpace = int(40*fontMultiplier)
		
		nplots = len(self.allGraphData.keys()) if selectedGraphName is None else 1
		mySVG.append("<svg x=\""+str(0)+"\" y=\""+str(0)+"\" width=\""+str(graphWidth+libNameSpace)+"\" height=\""
			+str((graphHeight+10)*nplots+titleOffset)+"\" viewbox=\"0 0 "+str(graphWidth)
			+" "+str((graphHeight+10)*nplots+titleOffset)+"\" xmlns=\"http://www.w3.org/2000/svg\">")
		graphLib.svg_drawRect(mySVG,0,0,graphWidth+libNameSpace,(graphHeight+10)*nplots+titleOffset,sw=2,stroke="#000000",fill="#ffffff")
		graphLib.svg_drawText(mySVG,graphWidth/2,titleFontsize,self.title,fontsize=int(titleFontsize),xanchor="middle",yanchor="middle")
		
		for i,(graphName,graphData) in enumerate(self.allGraphData.items()):
			if not selectedGraphName is None:
				if graphName!=selectedGraphName: continue
				else: i=0
			graphLib.svg_drawText(mySVG,graphWidth+int(7*fontMultiplier),(graphHeight+10)*i + titleOffset+graphHeight/2,str(graphName),
				xanchor="middle",yanchor="bottom",rotation=90,fontsize=int(22*fontMultiplier))
			canvas = graphLib.SVG_Canvas(mySVG,startx=0,starty=(graphHeight+10)*i + titleOffset,width=500,height=500)
			if self.graphType == "HEAT":
				graphData=graphData[0]
				colourscale,legend = getColourScale(graphData,self.colourscale_define)
			else:
				colourscale=None
				legend=self.legend
			canvas.set_styles(self.styles)
			xlab,ylab = self.axislabels[graphName]
			graphLib.canvas_createPlot(self,canvas,graphData,width=graphWidth,height=graphHeight,lineColour=self.main.graphLineColour,graphType=self.graphType,
				colourscale=colourscale,fontMultiplier=fontMultiplier,
				xlabel=xlab,ylabel=ylab,legend=legend,x_canvasOffset=0,y_canvasOffset=(graphHeight+10)*i + titleOffset,drawBorder=True,pointRadius=4,
				highlightpos=self.selectedPoints,highlightColour="#ff00ff")
		
		mySVG.append("</svg>")
		soloExtra = "" if (selectedGraphName is None or selectedGraphName=="") else "_"+selectedGraphName
		savePath = resultsPath if overridePath else os.path.join(resultsPath,f"{self.fileName}{soloExtra}.svg")
		with open(savePath,"w") as svgw:
			svgw.write("\n".join(mySVG))

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
				print("ERROR: could not find relative definition in colourscale point: "+str(point))
		else:
			print("ERROR: could not find colourscale point type: "+str(point))
		colourscale.append((val,colour))
	#print(colourscale)
	legend=("Count:",legendDesc)
	return colourscale,legend
