
from tkinter import Canvas	#functions of this object are called in these functions, but no canvas is created here
#Monkey-patching these functions in so that the SVG class can just create a cricle insteat of ellipses
def _create_circle(canvas,xcenter,ycenter,radius,fill="black",outline="black",outlineThickness=1):
	return canvas.create_oval(xcenter-radius,ycenter-radius,xcenter+radius,ycenter+radius,outline=outline,width=outlineThickness,fill=fill)
Canvas.create_circle = _create_circle
def _set_styles(self,styles):
	pass
Canvas.set_styles = _set_styles
def _infer_styles(self,colourscale):
	pass
Canvas.infer_styles = _infer_styles
def _open_group(self):
	pass
Canvas.open_group = _open_group
def _close_group(self):
	pass
Canvas.close_group = _close_group
#TODO could also implement isSVG() function that returns False for canvas and True for my svg-canvas; maybe this could be helpfull...?


def svg_writeStyle(svg,name,fill,stroke,sw=1,cap="butt"):
	svg.append("<style> ."+str(name)+"{"+f"fill:{fill}; stroke:{stroke}; stroke-width:{sw}; stroke-linecap:{cap}"+"}</style>")

def svg_drawRect(svg,x,y,w,h,sw=1,stroke="#000000",fill="#ffffff",style=None):
	styledef = f"style=\"fill:{fill};stroke-width:{round(sw,3)};stroke:{stroke}" if style is None else f"class=\"{style}"
	svg.append(f"<rect {styledef}\" x=\"{round(x,3)}\" y=\"{round(y,3)}\" width=\"{round(w,3)}\" height=\"{round(h,3)}\" />")

def svg_drawLine(svg,x1,y1,x2,y2,col="black",width=1,style=None,cap="butt"):
	capdef = "" if cap=="butt" else f";stroke-linecap:{cap}"	#butt is default, so save the text
	styledef = f"style=\"stroke-width:{round(width,3)};stroke:{col}" if style is None else f"class=\"{style}"
	svg.append(f"<path {styledef}{capdef}\" d=\"M {round(x1,3)},{round(y1,3)} {round(x2,3)},{round(y2,3)}\" />")

def cleanText(text):	#replaces specific characters for the xml/svg file
	return text.replace("&","&amp;").replace("\'","&apos;").replace("\"","&quot;").replace("<","&lt;").replace(">","&gt;")

def svg_drawText(svg,x,y,text,col="black",xanchor=None,yanchor=None,rotation=None,fontsize=12):
	xal="" if xanchor == None else f" text-anchor=\"{xanchor}\""
	yal="" if yanchor == None else f" dominant-baseline=\"{yanchor}\""
	rot="" if rotation == None else f" transform=\"rotate({rotation},{x},{y})\""
	svg.append(f"<text x=\"{x}\" y=\"{y}\"{xal}{yal}{rot} style=\"font-size:{fontsize}px;font-family:Arial\" >{cleanText(text)}</text>")

capTranslate = {"butt":"butt","projecting":"square","round":"round"}
class SVG_Canvas:	#TODO use grouping better, i.e. <g stroke-width=1>, <g width=3> (?)
	#A class that implements all used TKinter canvas functions, but instead appends them as SVG-code to the svg-list
	def __init__(self,svg,startx=0,starty=0,width=500,height=500):
		self.svg=svg
		self.startx=startx
		self.starty=starty
		self.width=width
		self.height=height
		self.styles = dict()
	def set_styles(self,styleDefs):
		for key,style in styleDefs.items():
			self.styles[(style[0],style[1],style[2])] = key
			svg_writeStyle(self.svg,key,style[0],style[1],sw=style[2])
	def infer_styles(self,colourscale):
		styleDefs=dict()
		maxval = colourscale[-1][0]
		colset = set()
		print(colourscale)
		breakpoint=-1
		for p,c in colourscale:
			if p>100:
				breakpoint=p
				break
		#[Draw HEAT] Number of unique colours: 390, saves file size by using styles for the most common cell-values
		
		for i in range(int(breakpoint)):
			colset.add(getColour(i,colourscale))
		print(f"[SVG HEAT] Number of unique colours: {len(colset)}")
		for c in colset:
			styleDefs["c"+c.removeprefix("#")] = (c,"black",1)
		self.set_styles(styleDefs)
	def open_group(self):
		self.svg.append("<g>")
	def close_group(self):
		self.svg.append("</g>")
	def create_text(self,x1_y1,text="Text",anchor="center",fill="black",font="System 12",angle=0):
		x1,y1=x1_y1	#tkinter canvas wants a tuple
		xanchor="middle"
		yanchor="middle"
		if anchor!="center":				#anchor: center, n, s, w, e		#tkinter canvas
			if "n" in anchor: yanchor="hanging"	#yanchor="bottom","middle","hanging"	#svg
			if "s" in anchor: yanchor="bottom"
			if "w" in anchor: xanchor="start"	#xanchor="start","middle","end"		#svg
			if "e" in anchor: xanchor="end"
		svg_drawText(self.svg,x1,y1,text,col=fill,xanchor=xanchor,yanchor=yanchor,rotation=-1*angle,fontsize=int(font.split()[1])*2)
	def create_line(self,*args,fill="black",width=1,capstyle="butt"):	#x1,y1,x2,y2	// pointList
		#capstyle = butt / projecting / round for tkinter canvas
		if len(args)==4:
			x1,y1,x2,y2 = args
			cap = "butt" if capstyle=="butt" or not capstyle in capTranslate else capTranslate[capstyle]
			self.create_singleline(x1,y1,x2,y2,fill=fill,width=width,cap=cap)
		elif len(args)==1:
			pointList = args[0]
			self.create_polyline(pointList,fill=fill,width=width)
		else:
			print(f"[Draw SVG] Error with line args: {args}")
	def create_singleline(self,x1,y1,x2,y2,fill="black",width=1,cap="butt"):
		styleKey = (fill,fill,width)
		svg_drawLine(self.svg,x1,y1,x2,y2,col=fill,width=width,style=self.styles[styleKey] if styleKey in self.styles else None,cap=cap)
	def create_polyline(self,pointList,fill="black",width=1):
		points = " ".join([f"{round(p[0],3)},{round(p[1],3)}" for p in pointList])
		self.svg.append(f"<polyline stroke-width=\"{width}\" stroke=\"{fill}\" fill=\"none\" points=\"{points}\" />")
	def create_rectangle(self,x1,y1,x2,y2,fill="black",outline="black",width=1):
		ystart = min(y1,y2)	#rect with negative doesnt work, always top-left to bottom right
		height = abs(y2-y1)
		styleKey = (fill,outline,width)
		svg_drawRect(self.svg,x1,ystart,x2-x1,height,sw=width,stroke=outline,fill=fill,style=self.styles[styleKey] if styleKey in self.styles else None)
	def create_circle(self,xcenter,ycenter,radius,fill="black",outline="black",outlineThickness=1):
		styleKey = (fill,outline,outlineThickness)
		styledef = f"class=\"{self.styles[styleKey]}" if styleKey in self.styles else f"style=\"fill:{fill}"
		outlinedef = "" if outline=="" else f";stroke-width={outlineThickness};stroke:{outline}"
		self.svg.append(f"<circle {styledef}{outlinedef}\" cx=\"{round(xcenter,3)}\" cy=\"{round(ycenter,3)}\" r=\"{round(radius,3)}\" />")
	def create_oval(self,x1,y1,x2,y2,outline="black",width=1,fill="black"):	#now unused
		if outline=="":width=0	#in canvas width is pre set, but outline is unset for later highlighting
		t = f"<ellipse style=\"fill:{fill};stroke-width={width};stroke:{outline}\" cx=\"{round(x1+(x2-x1)/2,3)}\" cy=\"{round(y1+(y2-y1)/2,3)}\""
		t+= f" rx=\"{round((x2-x1)/2,3)}\" ry=\"{round((y2-y1)/2,3)}\" />"
		self.svg.append(t)
	def itemconfig(self,itemID,outline="#ff00ff",width="1"):
		pass	#instead of writing to list, could also write to dict and allow re-arranging of items, but it is not necessary
	def tag_raise(self,itemID):
		pass

axisspacer = 5
markerLength = 10

def canvas_createLegend(canvas,x1,y1,x2,y2,legend,vertical=True,textcolour="black",fontMultiplier=1.0):
	canvas.open_group()
	#canvas.create_rectangle(x1,y1,x2,y2,fill="#ddffee",outline="blue")
	
	x1+=10
	y1+=10
	
	legendColSize = int(26*fontMultiplier)	#Width/height of rectangle or diameter of circle
	legendYStep = int(40*fontMultiplier)
	
	canvas.create_text((x1,y1+legendColSize/2),text=str(legend[0]),anchor="w",fill=textcolour,font="System "+str(int(16*fontMultiplier)))
	for i,(col,desc) in enumerate(legend[1]):
		if desc == "esiRNAs":
			canvas.create_rectangle(
				x1, y1+(i+1)*legendYStep,
				x1+legendColSize, y1+(i+1)*legendYStep+legendColSize,
				outline=col,width=4*fontMultiplier)
		else:
			canvas.create_rectangle(
				x1, y1+(i+1)*legendYStep,
				x1+legendColSize, y1+(i+1)*legendYStep+legendColSize,
				outline=col,fill=col)
		canvas.create_text(
			(x1+legendColSize+5,y1+(i+1)*legendYStep+0.5*legendColSize),
			text=str(desc),anchor="w",fill=textcolour,font="System "+str(int(12*fontMultiplier)))
	canvas.close_group()

def canvas_createXAxis(canvas,x_xaxisStart,x_xaxisEnd,y_xaxisStart,continous=True,startv=None,endv=None,by=None,breaks=None,linewidth=2,lineColour="black",fontsize=10):
	canvas.open_group()
	font="System "+str(fontsize)
	#requires either: continous=True and startv,endv,by OR continous=False and breaks
	if continous:
		x1=x_xaxisStart
		y1=y_xaxisStart+axisspacer
		x2=x_xaxisEnd
		y2=y1
		canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth,capstyle="projecting")
		
		nbreaks=int((endv-startv)/by)+1
		binwidth = (x_xaxisEnd-x_xaxisStart)/(nbreaks-1)
		y2=y_xaxisStart+axisspacer+markerLength
		for step in range(0,nbreaks):
			x1=x_xaxisStart + binwidth*step
			x2=x1
			canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth,capstyle="projecting")
			xval = startv+by*step
			#+linewidth*2 to get some space between the line and the text
			canvas.create_text((x2,y2+linewidth),text=str(xval),anchor="n",fill=lineColour,font=font)
	else:
		nbreaks=len(breaks)
		binwidth = (x_xaxisEnd-x_xaxisStart)/(nbreaks)
		x1=x_xaxisStart + binwidth/2
		y1=y_xaxisStart+axisspacer
		x2=x_xaxisEnd - binwidth/2
		y2=y1
		canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth,capstyle="projecting")
		y2=y_xaxisStart+axisspacer+markerLength
		for step in range(0,nbreaks):
			x1=x_xaxisStart + binwidth/2 + binwidth*step
			x2=x1
			canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth,capstyle="projecting")
			xval = breaks[step]
			canvas.create_text((x2,y2+linewidth),text=str(xval),anchor="n",fill=lineColour,font=font)
	canvas.close_group()
		
def canvas_createYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,continous=True,startv=None,endv=None,by=None,linewidth=2,yaxisBuffer=20,lineColour="black",fontsize=10):
	#requires either: continous=True and startv,endv,by
	if not continous:return	#TODO
	canvas.open_group()
	x1=x_yaxisStart -axisspacer
	y1=y_yaxisStart
	x2=x1
	y2=y_yaxisEnd
	canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth,capstyle="projecting")
	
	font="System "+str(fontsize)
	#print("YAxis: "+str(endv)+" - "+str(startv)+", "+str(by))
	nbreaks=int((endv-startv)/by)+1
	#print("Breaks: "+str(nbreaks))
	binwidth = abs(y_yaxisStart-y_yaxisEnd)/(nbreaks-1)
	#print("BinWidth: "+str(binwidth))
	x1=x_yaxisStart -axisspacer -markerLength
	for step in range(0,nbreaks):
		y1=y_yaxisEnd - binwidth*step
		y2=y1
		canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth,capstyle="projecting")
		yval = startv+by*step
		#print(f"[Draw] {yval} ~ {y1}")
		canvas.create_text((x1-linewidth*2,y1),text=str(yval),anchor="e",fill=lineColour,font=font)
	canvas.close_group()

def canvas_createSplitYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,startv=None,endv=None,by=None,linewidth=2,yaxisBuffer=20,lineColour="black",fontsize=10):
	canvas.open_group()
	
	font="System "+str(fontsize)
	x1=x_yaxisStart -axisspacer
	y1=y_yaxisStart
	x2=x1
	y2=y_yaxisEnd
	splitNbreaks = (endv-startv+1)	#breaks for each part
	nbreaks = splitNbreaks*2+1		#total breaks for top and bottom + spacer line
	binwidth = abs(y_yaxisStart-y_yaxisEnd)/(nbreaks)
	#print("Split YAxis: "+str(splitNbreaks)+" "+str(nbreaks)+" "+str(binwidth)+" "+str(abs(y_yaxisStart-y_yaxisEnd)))
	canvas.create_line(
		x1,y2-(0.5)*binwidth,
		x1,y2-(splitNbreaks-0.5)*binwidth,
		fill=lineColour,width=linewidth,capstyle="projecting")
	canvas.create_line(
		x1,y2-(splitNbreaks+1.5)*binwidth,
		x1,y2-(nbreaks-0.5)*binwidth,
		fill=lineColour,width=linewidth,capstyle="projecting")
	
	x2=x_yaxisStart -axisspacer -markerLength
	for j,i in enumerate([0,splitNbreaks-1,splitNbreaks+1,nbreaks-1]):
		canvas.create_line(
			x1,y2-((i+0.5)*binwidth),
			x2,y2-((i+0.5)*binwidth),
			fill=lineColour,width=linewidth,capstyle="projecting")
		if j%2==0:
			canvas.create_text(
				(x2-linewidth*2,y2-((i+0.5)*binwidth)),
				text=str(startv),anchor="se",fill=lineColour,font=font)
		else:
			canvas.create_text(
				(x2-linewidth*2,y2-((i+0.5)*binwidth)),
				text=str(endv),anchor="ne",fill=lineColour,font=font)
	canvas.close_group()

def canvas_createXLabel(canvas,x_xLabelCenter,y_xLabelStart,xLabelText,fontsize=16,textcolour="black"):
	canvas.create_text((x_xLabelCenter,y_xLabelStart),text=str(xLabelText),anchor="n",fill=textcolour,font="System "+str(fontsize))#+" bold")
	
def canvas_createYLabel(canvas,y_yLabelCenter,x_yLabelStart,yLabelText,fontsize=16,textcolour="black"):
	canvas.create_text((x_yLabelStart,y_yLabelCenter),text=str(yLabelText),anchor="s",fill=textcolour,font="System "+str(fontsize),angle=90)
	
def canvas_createBars(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,discreetX=False,barcolours=None,lineColour="black",defBarcol="black"):
	#TODO boxBars is discreet vs continous x-axis!
	#data = [x,+,-] or [x,+,-,+,-]
	#first +,- is black/background, second is drawn ontop ~~~~
	#colouring is same but colour insted of yvalue
	#startv,endv ~ x_dataSpace
	xdataToPix = x_dataSpace/(xmax-xmin+1)
	#print(xmin,xmax,ymin,ymax)
	#ymin=-graph.ybins[1]*graph.ystep
	#ymax=graph.ybins[0]*graph.ystep
	ydataToPix = y_dataSpace/(ymax-ymin)
	
	yzero = y_dataStart + ymax * ydataToPix
	
	graph.xbase = x_dataStart
	graph.yzero = yzero
	graph.xdataToPix = xdataToPix
	graph.ydataToPix = ydataToPix
	
	if ymin<0:
		canvas.create_line(x_dataStart,yzero,x_dataStart+x_dataSpace,yzero,fill=lineColour,width=1)
	
	if barcolours is None:
		barcolours = [[lineColour]*len(data[0])-1]*len(data)
	
	
	bars = [None]*len(data)	#~~~
	barwidth = max(2,xdataToPix)
	barradius = max(1,xdataToPix/2)
	
	styleDefs=dict()
	styleDefs["b"] = (defBarcol,defBarcol,barwidth)
	canvas.set_styles(styleDefs)
	for i,point in enumerate(data):
		xcenter = x_dataStart+(point[0]-xmin)*xdataToPix	#TODO offset !!	~startv ???
		if discreetX:
			xcenter+=xdataToPix/2
			#print(str(point)+" "+str(xcenter))
		posBars = [None]*(len(point)-1)
		for j in range(len(point)-1,0,-1):
			y1 = yzero - point[j] * ydataToPix * ((j%2)*2-1)
			y2 = yzero
			bar=None
			if discreetX:
				x1 = xcenter - barradius
				x2 = xcenter + barradius
				bar = canvas.create_rectangle(x1,y1,x2,y2,fill=barcolours[i][j-1][0],outline=barcolours[i][j-1][1])
			else:
				x1 = xcenter
				x2 = x1
				bar = canvas.create_line(x1,y1,x2,y2,fill=barcolours[i][j-1][0],width=barwidth)
			posBars[j-1] = bar
		bars[i] = posBars
	return bars

def canvas_createLines(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,linewidth=2,lineColours=None,discreetX=False):
	#data = [x,+,-] or [x,+,-,+,-]
	#first +,- is black/background, second is drawn ontop ~~~~
	#colouring is same but colour insted of yvalue
	#startv,endv ~ x_dataSpace
	xdataToPix = x_dataSpace/(xmax-xmin+1)
	#print("Bounds:")
	#print(xmin,xmax,ymin,ymax)
	#ymin=-graph.ybins[1]*graph.ystep
	#ymax=graph.ybins[0]*graph.ystep
	ydataToPix = y_dataSpace/(ymax-ymin)
	
	yzero = y_dataStart + ymax * ydataToPix
	
	#graph.xbase = x_dataStart
	#graph.yzero = yzero
	#graph.xdataToPix = xdataToPix
	#graph.ydataToPix = ydataToPix
	
	if ymin<0:
		canvas.create_line(x_dataStart,yzero,x_dataStart+x_dataSpace,yzero,fill="black",width=1)
	
	if lineColours is None:
		lineColours = ["red"]*(len(data[0])-1)
	if discreetX:
		x_dataStart+=xdataToPix/2	#just affects the coords downstream
	lines = [None]*(len(data[0])-1)	#~~~
	for j in range(len(data[0])-1,0,-1):
		coords = [(x_dataStart + (p[0]-xmin) * xdataToPix,yzero - p[j] * ydataToPix * ((j%2)*2-1)) for p in data]
		lines[j-1] = canvas.create_line(coords,fill=lineColours[j-1],width=linewidth)
	return lines

def canvas_createPoints(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,pointRadius=10,discreetX=False,fillColour="#000000"):
	points = [None]*len(data)
	
	xdataToPix = x_dataSpace/(xmax-xmin)
	ydataToPix = y_dataSpace/(ymax-ymin)
	ybase = y_dataStart+y_dataSpace
	if xmin<0:
		xzero = x_dataStart-xmin*xdataToPix
		canvas.create_line(xzero,y_dataStart,xzero,y_dataStart+y_dataSpace,fill="black",width=1)
	#if ymin<0:
	#	canvas.create_line(x_dataStart,yzero,x_dataStart+x_dataSpace,yzero,fill="black",width=1)
	graph.xbase = x_dataStart
	graph.yzero = ybase
	graph.xdataToPix = xdataToPix
	graph.ydataToPix = ydataToPix
	
	outlineThickness=7
	styleDefs=dict()
	styleDefs["c"] = (fillColour,"",outlineThickness)
	canvas.set_styles(styleDefs)
	for i,point in enumerate(data):
	#cant sort by colouring, because the graph doesnt know about this hidden value behind the colouring
	#for i,point in sorted(zip(list(range(len(data))),data), key=lambda x: x[1]):
		#if i%20==0:print(point)
		xcenter = x_dataStart+(point[1]-xmin)*xdataToPix
		ycenter = ybase-(point[2]-ymin)*ydataToPix
		point = canvas.create_circle(xcenter,ycenter,pointRadius,fill=fillColour,outline="",outlineThickness=outlineThickness)
		points[i] = (point,xcenter,ycenter)	#(ovalObject,xcenter,ycenter)	#for tkinter canvas
	return points

def canvas_createHeatmap(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,colourscale,xmax,fontMultiplier=1.0):
	#------------ Data -> cells ---------------------
	cells = [[None]*len(data[0]) for i in range(len(data))]
	
	xvals=len(data)		#xaxis length
	yvals=len(data[0])	#yaxis length
	xdataToPix = x_dataSpace/xmax
	ydataToPix = y_dataSpace/yvals
	y2=y_dataStart+y_dataSpace
	x_dataStart+=xdataToPix/2
	
	graph.xbase = x_dataStart
	graph.yzero = y_dataStart+y_dataSpace
	graph.xdataToPix = xdataToPix
	graph.ydataToPix = ydataToPix
	
	print(f"[Draw HEAT] {len(data)} {len(data[0])}")
	
	canvas.infer_styles(colourscale)
	
	for x,column in enumerate(data):
		for y,value in enumerate(column):
			if (x,y) in graph.positionalColouring:continue
			cellColour = getColour(value,colourscale)
			try:
				cells[x][y] = canvas.create_rectangle(
					x_dataStart+(x)*xdataToPix, y2-(y)*ydataToPix,
					x_dataStart+(x+1)*xdataToPix, y2-(y+1)*ydataToPix,
					fill=cellColour,outline="black",width=1)
			except:
				print("[Draw] Error with cell: "+str(x)+"-"+str(y)+": "+str(value)+" "+str(cellColour))
	
	for (x,y) in graph.positionalColouring:	#draw highlighted cells later, better for SVG compatibility
		cellColour = getColour(data[x][y],colourscale)
		cells[x][y] = canvas.create_rectangle(
			x_dataStart+(x)*xdataToPix, y2-(y)*ydataToPix,
			x_dataStart+(x+1)*xdataToPix, y2-(y+1)*ydataToPix,
			fill=cellColour,outline="#ff00ff",width=3*fontMultiplier)
		graph.highlightpositions.add((x,y))
		#canvas.tag_raise(cells[x][y])	#not needed if we draw them last anyway
	return cells

def canvas_createPlot(graph,canvas,data,lineColour="black",graphType=None,colourscale=None,width=None,height=None,scaleFactor=1,fontMultiplier=1.0,
			xlabel=None,ylabel=None,legend=None,x_canvasOffset=0,y_canvasOffset=0,drawBorder=False):
	canvas.open_group()
	#TODO get dict of parametes instead of graph !
	#TODO cleanup here !
	
	#buffers depend on fontsize and screen scaling
	
	if drawBorder:
		canvas.create_rectangle(x_canvasOffset,y_canvasOffset,x_canvasOffset+width,y_canvasOffset+height,outline="#000000",width=2,fill="#ffffff")
	
	if graphType is None:graphType = graph.graphType
	
	print(f"[Draw] Drawing {graphType}")
	
	if width is None:width = graph.width	#space allowed on canvas from offset
	if height is None:height = graph.height
	
	#--------------------------------- Graph bounds ---------------------------------
	titleBuffer=0
	sideTitleBuffer=0
	xlabelBuffer=0
	xaxisBuffer=0
	ylabelBuffer=0
	yaxisBuffer=0
	legendBuffer=0
	yLegendBuffer=0
	title=False
	title=False
	sideTitle=False
	if xlabel is None: xlabel=graph.xlab
	xaxis=True
	if ylabel is None: ylabel=graph.ylab
	yaxis=True
	if legend is None: legend=graph.legend
	topLegend=False
	if title:titleBuffer=50
	if sideTitle:sideTitleBuffer	= int(200*fontMultiplier)
	if xlabel:xlabelBuffer		= int(50*fontMultiplier)
	if xaxis:xaxisBuffer		= int(40*fontMultiplier)
	if ylabel:ylabelBuffer		= int(50*fontMultiplier)
	if yaxis:yaxisBuffer		= int(120*fontMultiplier)
	if legend:legendBuffer		= int(410*fontMultiplier)
	if topLegend:yLegendBuffer	= int(50*fontMultiplier)
	
	x_leftBuffer = 10
	x_rightBuffer = 30
	y_topBuffer = 20
	y_bottomBuffer = 10
	
	x_dataStart = x_canvasOffset +x_leftBuffer +ylabelBuffer +yaxisBuffer	#all is anchored around this!
	x_dataSpace = width -x_leftBuffer -ylabelBuffer -yaxisBuffer -sideTitleBuffer -legendBuffer -x_rightBuffer
	y_dataStart = y_canvasOffset +y_topBuffer +titleBuffer +yLegendBuffer
	y_dataSpace = height -y_topBuffer -titleBuffer -yLegendBuffer -xlabelBuffer -xaxisBuffer -y_bottomBuffer
	
	x_xaxisStart = x_dataStart
	x_xaxisEnd = x_dataStart + x_dataSpace
	y_xaxisStart = y_dataStart + y_dataSpace
	x_xLabelCenter = x_dataStart + x_dataSpace/2
	y_xLabelStart = y_xaxisStart + xaxisBuffer
	
	y_yaxisStart = y_dataStart
	y_yaxisEnd = y_dataStart + y_dataSpace
	x_yaxisStart = x_dataStart			#right most anchor
	y_yLabelCenter = y_yaxisStart + y_dataSpace/2
	x_yLabelStart = x_yaxisStart -yaxisBuffer	#right most anchor
	
	if canvas is None:canvas = graph.canvas
	
	
	#--------------------------------- Data bounds ---------------------------------
	#if len(data)<50:print("\n".join([str(point) for point in data]))	#TODO cleanup!
	
	#print("graph-X: "+str(graph.xbins)+" "+str(graph.xstep)+" "+str(graph.xdataToPix))
	#print("graph-Y: "+str(graph.ybins)+" "+str(graph.ystep)+" "+str(graph.ydataToPix))
	
	discreetX = False
	if not graphType=="HEAT":
		if graphType=="SCATTER":
			maxx1 = max([point[1] for point in data])
			minx1 = min([point[1] for point in data])
			if minx1>=0:xbreaks,xstep = getAxisScale(maxx1,minValue=minx1)
			else:xbreaks,xstep = getAxisScale2(maxx1,abs(minx1))
		else:
			maxx1 = max([point[0] for point in data])
			minx1 = min([point[0] for point in data])
			xbreaks,xstep = getAxisScale(maxx1,minValue=minx1)
		
		if graphType=="SCATTER":
			maxy1 = max([point[2] for point in data])
			miny1 = abs(min([point[2] for point in data]))
			ybreaks,ystep = getAxisScale(maxy1,minValue=miny1)
			maxy2=miny1
		else:
			maxy1 = max([max([point[i] for i in range(1,len(point),2)]) for point in data])
			maxy2 = 0
			if len(data[0])>2:
				maxy2 = max([max([point[i] for i in range(2,len(point),2)]) for point in data])
			ybreaks,ystep = getAxisScale2(maxy1,maxy2)
	
		if len(data)<50:
			discreetX = True
	graph.discreetX = discreetX
	if graphType=="SCATTER":
		if minx1>0:
			xmin = int(minx1/xstep)
			xmax = xmin + xstep * xbreaks
		else:
			xmax = xstep * xbreaks[0]
			xmin = -xstep * xbreaks[1]
		#print(str(xmin)+" - "+str(xmax))
		ymin = int(miny1/xstep)
		ymax = ymin + ystep * ybreaks
	elif graphType=="HEAT":	#TODO for selections of the sequence??
		xmin = 0
		xmax = xmin + graph.xstep * graph.xbins
		xstep = graph.xstep
		ymin = graph.yvals[0]	#?
		ymax = graph.yvals[-1]	#?
		#print(graph.yvals)
		ystep = 1
	else:
		if discreetX:
			xmin = minx1
			xmax = maxx1
		else:
			xmin = int(minx1/xstep)
			xmax = xmin + xstep * xbreaks
		
		ymax = ystep * ybreaks[0]
		ymin = -ystep * ybreaks[1]
	
	#print("Proper Xdef: "+str(xmin)+" "+str(xmax)+" "+str(xstep))
	#print("Proper Ydef: "+str(ymin)+" "+str(ymax)+" "+str(ystep))
	
	#print("yaxis: "+str(height)+" "+str(y_xaxisStart))
	
	#--------------------------------- Axes ---------------------------------
	if discreetX:
		breaks = [p[0] for p in data] 
		if not graph.xLabels is None:
			breaks = [graph.xLabels[p[0]] for p in data]
		#print("\nBreaks: "+str(breaks)+"\n")
		canvas_createXAxis(canvas,x_xaxisStart,x_xaxisEnd,y_xaxisStart,continous=False,breaks=breaks,fontsize=int(10*fontMultiplier),lineColour=lineColour)
	else:
		canvas_createXAxis(canvas,x_xaxisStart,x_xaxisEnd,y_xaxisStart,continous=True,startv=xmin,endv=xmax,by=xstep,fontsize=int(10*fontMultiplier),lineColour=lineColour)
	
	if graphType=="HEAT":#split yaxis for heatmap
		canvas_createSplitYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,startv=ymin,endv=ymax,by=1,linewidth=2,yaxisBuffer=20,
			lineColour=lineColour,fontsize=int(10*fontMultiplier))
	else:
		canvas_createYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,continous=True,startv=ymin,endv=ymax,by=ystep,yaxisBuffer=yaxisBuffer,
			lineColour=lineColour,fontsize=int(10*fontMultiplier))	#Count +-, cov+- ???
	
	#--------------------------------- Legend and Labels ---------------------------------
	if not legend is None:
		canvas_createLegend(canvas,x_xaxisEnd,y_yaxisStart,x_xaxisEnd+legendBuffer,y_yaxisEnd,legend,vertical=True,textcolour=lineColour,fontMultiplier=fontMultiplier)
	
	if not xlabel is None:
		canvas_createXLabel(canvas,x_xLabelCenter,y_xLabelStart,xlabel,fontsize=int(16*fontMultiplier),textcolour=lineColour)
	
	if not ylabel is None:
		canvas_createYLabel(canvas,y_yLabelCenter,x_yLabelStart,ylabel,fontsize=int(16*fontMultiplier),textcolour=lineColour)
	
	#--------------------------------- colouring stuff ---------------------------------
	barcolours=None
	if not graphType=="HEAT" and not graph.positionalColouring is None:
		
		#TODO unify and improve the colouring of graphs
		
		barcolours=[None]*len(data)
		nbarsPerPoint=len(data[0])-1
		for i,point in enumerate(data):
			cols=[None]*nbarsPerPoint
			for j in range(0,nbarsPerPoint):
				if point[0] in graph.positionalColouring[j%2] and j<2:
					cols[j] = [graph.styles[graph.positionalColouring[j%2][point[0]]][0],graph.styles[graph.positionalColouring[j%2][point[0]]][1]]
				else:
					cols[j] = graph.styles["default"]
			barcolours[i]=cols
	
	#--------------------------------- Bounding box of Data ---------------------------------
	canvas.open_group()	#data group (for svg); could be set in each function instead and use group attributes to save on svg size
	
	#canvas.create_rectangle(x_dataStart,y_dataStart,x_dataStart+x_dataSpace,y_dataStart+y_dataSpace,fill="#ddeeff",outline="red")
	#canvas.create_text((x_dataStart,y_dataStart),text="Debug data area",anchor="nw",fill="#ff0000",font="System 16 bold")
	
	if graphType=="BAR" or graphType=="BAR2":
		bars = canvas_createBars(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,discreetX=discreetX,barcolours=barcolours,
			lineColour=lineColour,defBarcol=graph.styles["default"][0])
	
	if graphType=="multiLine":
		if graph.lineColours is None:
			lineColours = ["red","red","green","green","blue","blue"]
		else:
			lineColours = graph.lineColours
		lines = canvas_createLines(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,linewidth=5,lineColours=lineColours,discreetX=discreetX)
	
	if graphType=="SCATTER":
		points = canvas_createPoints(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,pointRadius=graph.pointRadius,discreetX=discreetX,
			fillColour=lineColour)
		
	if graphType=="HEAT":
		cells = canvas_createHeatmap(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,colourscale,xmax)	#????	#data is [x][y] = value ??
	
	canvas.close_group()	#data group end
	
	canvas.close_group()	#graph group end
	
	#--------------------------------- Return objects ---------------------------------
	if graphType=="multiLine":return lines
	if graphType=="SCATTER":return points
	if graphType=="BAR" or graphType=="BAR2":return bars
	if graphType=="HEAT": return cells
	return False

def createBarHighlight(graph,pos):	#Used to create a highlight border around bars
	x = graph.xbase+pos*graph.xdataToPix
	y = graph.ybase
	h = graph.ybins*graph.ystep*graph.ydataToPix
	r = graph.barRadius+2.5
	barHighlight = graph.canvas.create_rectangle(x-r,y, x+r,y-h, fill="",width=5,outline="#ff00c6")#ff5700")#"#ff00c6")#"#00ffff")	#ff7700
	return barHighlight

def getColour(value,colourscale):
	if value==-1: return "#ffffff"
	for i,(breakpoint,colour) in enumerate(colourscale):
		if value<=breakpoint:
			if i==0: return getHexColourTuple(colour)
			return interpolateColours(value, colourscale[i-1], colourscale[i])
	return getHexColourTuple(colourscale[-1][1])

def interpolateColours(value, point1, point2):
	r1,g1,b1 = point1[1]
	r2,g2,b2 = point2[1]
	frac = (value-point1[0])/(point2[0]-point1[0])
	r= int(r1+(r2-r1)*frac)
	g= int(g1+(g2-g1)*frac)
	b= int(b1+(b2-b1)*frac)
	return getHexColour(r,g,b)

def interpolateColoursFraction(frac, col1, col2):
	if frac<=0:return col1
	r1,g1,b1 = hexToDec(col1.lower())
	r2,g2,b2 = hexToDec(col2.lower())
	r= int(r1+(r2-r1)*frac)
	g= int(g1+(g2-g1)*frac)
	b= int(b1+(b2-b1)*frac)
	return getHexColour(r,g,b)

hexToDecDict = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"a":10,"b":11,"c":12,"d":13,"e":14,"f":15}
def hexToDec(col):
	c=col.removeprefix("#")
	return (hexToDecDict[c[0]]*16+hexToDecDict[c[1]],hexToDecDict[c[2]]*16+hexToDecDict[c[3]],hexToDecDict[c[4]]*16+hexToDecDict[c[5]])
	
def multiplyColour(frac,col):
	if frac<0: return col
	elif frac==0: return "#000000"
	elif frac<1: return interpolateColoursFraction(frac, "#000000", col) 
	elif frac==1: return col
	elif frac<2: return interpolateColoursFraction(frac-1, "#ffffff", col)
	elif frac==2: return "#ffffff"
	else: return col

def getHexColourTuple(colTuple):
	return getHexColour(colTuple[0],colTuple[1],colTuple[2])

decToHex = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
def getHexColour(r,g,b):
	return "#"+decToHex[int(r/16)]+decToHex[r%16]+decToHex[int(g/16)]+decToHex[g%16]+decToHex[int(b/16)]+decToHex[b%16]

def isHexColour(string):
	string=string.lower()
	if len(string)!=7:return False
	if not string.startswith("#"): return False
	for c in string[1:]:
		if not c in hexToDecDict:
			return False
	return True

def getAxisScale(maxValue,minValue=1):
	if maxValue<20:return int(maxValue)+1,1
	allowedSteps = [1,5,10,20,50,100,200,500,1000,2000,5000,10000,50000,100000,500000,1000000,5000000,10000000]
	targetbreaks = 9
	best_breaks = -1
	best_step = -1
	for stepSize in allowedSteps:
		nbreaks = int((maxValue-2)/stepSize)+1
		if nbreaks < 5:break	#stepSize increases, so there is nothing more
		if nbreaks >20:continue
		if abs(nbreaks-targetbreaks)<abs(best_breaks-targetbreaks):
			best_breaks = nbreaks
			best_step = stepSize
	if best_breaks==-1 or best_step==-1: print(f"[GraphLib] Error no stepsize found for {maxValue} {minValue}")
	return best_breaks,best_step

def getAxisScale2(maxValue1,maxValue2):
	allowedSteps = [1,2,5,10,20,50,100,200,500,1000,2000,5000,10000,50000,100000,500000,1000000,5000000,10000000]
	if maxValue1<2 and maxValue2<2:
		allowedSteps = [0.001,0.002,0.005,0.01,0.02,0.05,0.1,0.2,0.5]
	targetbreaks = 9
	best_nbreaks = -1
	best_step = -1
	best_breaks = (1,1)
	for stepSize in allowedSteps:
		nbreaks = int(maxValue1/stepSize)+3+int(abs(maxValue2)/stepSize)
		if nbreaks < 5:break	#stepSize increases, so there is nothing more
		if nbreaks >20:continue
		if abs(nbreaks-targetbreaks)<abs(best_nbreaks-targetbreaks):
			best_nbreaks = nbreaks
			best_step = stepSize
			best_breaks = (int(abs(maxValue1)/stepSize)+1,0 if maxValue2==0 else int(abs(maxValue2)/stepSize)+1)
	return best_breaks,best_step

