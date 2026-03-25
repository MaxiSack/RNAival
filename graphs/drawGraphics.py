

#from tkinter import Canvas	#functions of this are called

#def canvas_drawBar(canvas,bars,x,y,h,r=1,sw=1,stroke="#000000",fill="#ffffff"):
#	return canvas.create_rectangle(x-r,y,x+r,y-h,outline=stroke,fill=fill,width=sw)	#outline="" draws no outline

def svg_drawBarStyle(svg,style,x,y,h,r=1):
	if h>0:t = "<rect class=\""+style+"\" x=\""+str(round(x-r,3))+"\" y=\""+str(round(y-h,3))+"\" width=\""+str(round(r*2,3))+"\" height=\""+str(round(h,3))+"\" />"
	elif h<0:t = "<rect class=\""+style+"\" x=\""+str(round(x-r,3))+"\" y=\""+str(round(y,3))+"\" width=\""+str(round(r*2,3))+"\" height=\""+str(round(-h,3))+"\" />"
	else:t = "<path class=\""+style+"\" d=\"M "+str(round(x-r,3))+","+str(round(y,3))+" "+str(round(x+r,3))+","+str(round(y,3))+"\" />"
	svg.append(t)	#svg is a list of lines

def svg_drawBarCustom(svg,x,y,h,r=1,sw=1,stroke="#000000",fill="#ffffff"):
	if h>0:t = "<rect style=\"fill:"+str(fill)+";stroke-width:"+str(sw)+";stroke:"+str(stroke)+"\" x=\""+str(round(x-r,3))+"\" y=\""+str(round(y-h,3))+"\" width=\""+str(round(r*2,3))+"\" height=\""+str(round(h,3))+"\" />"
	elif h<0:t = "<rect style=\"fill:"+str(fill)+";stroke-width:"+str(sw)+";stroke:"+str(stroke)+"\" x=\""+str(round(x-r,3))+"\" y=\""+str(round(y,3))+"\" width=\""+str(round(r*2,3))+"\" height=\""+str(round(-h,3))+"\" />"
	else:t = "<path style=\"stroke-width:"+str(sw)+";stroke:"+str(stroke)+"\" d=\"M "+str(round(x-r,3))+","+str(round(y,3))+" "+str(round(x+r,3))+","+str(round(y,3))+"\" />"
	svg.append(t)

#def drawBar(x,y,h,r=1,canvas=None,svg=None,style=None,sw=1,stroke="#000000",fill="#ffffff"):
#	if not canvas is None:
#		return canvas_drawBar(canvas,x,y,h,r=r,sw=sw,stroke=stroke,fill=fill)	#returns the bar for interactivity
#	elif not svg is None:
#		if style is None:
#			svg_drawBarCustom(svg,x,y,h,r=r,sw=sw,stroke=stroke,fill=fill)	#appends a line to the svg(-list)
#		else:
#			svg_drawBarStyle(svg,style,x,y,h,r=r)
#	else:
#		print("[Draw] ERROR, neither canvas nor svg provided to drawBar function!")

#def svg_writeStyle(svg,style,sw=None):
#	if sw is None:svg.append("<style> ."+style[0]+"{fill:"+style[1]+"; stroke:"+style[2]+"; stroke-width:"+style[3]+";}</style>")
#	else:svg.append("<style> ."+style[0]+"{fill:"+style[1]+"; stroke:"+style[2]+"; stroke-width:"+str(sw)+";}</style>")
def svg_writeStyle(svg,name,fill,stroke,sw=1):
	svg.append("<style> ."+str(name)+"{fill:"+str(fill)+"; stroke:"+str(stroke)+"; stroke-width:"+str(sw)+";}</style>")

def svg_drawRect(svg,x,y,w,h,sw=1,stroke="#000000",fill="#ffffff"):
	t = "<rect style=\"fill:"+str(fill)+";stroke-width="+str(sw)+";stroke:"+stroke+"\" x=\""+str(round(x,3))+"\" y=\""+str(round(y,3))+"\" width=\""+str(round(w,3))+"\" height=\""+str(round(h,3))+"\" />"
	svg.append(t)

def svg_drawCell(svg,x,y,w,h,fill="#ffffff"):
	t = "<rect style=\"fill:"+str(fill)+"\" x=\""+str(round(x+w/2,3))+"\" y=\""+str(round(y,3))+"\" width=\""+str(round(w,3))+"\" height=\""+str(round(h,3))+"\" />"
	svg.append(t)

def svg_drawCellOutline(svg,x,y,w,h,fill="#ffffff",stroke="#ff00ff",sw=1):
	t = "<rect style=\"fill:"+str(fill)+";stroke:"+stroke+";stroke-width="+str(sw)+"\" x=\""+str(round(x+w/2,3))+"\" y=\""+str(round(y,3))+"\" width=\""+str(round(w,3))+"\" height=\""+str(round(h,3))+"\" />"
	svg.append(t)	#svg is a list of lines

#def drawLine(canvas,x1,y1,x2,y2,col="black",svg=None):
#	canvas.create_line(x1,y1,x2,y2,fill=col)
#	if not svg is None:
#		t = "<path style=\"stroke-width:1;stroke:"+str(col)+"\" d=\"M "+str(x1)+","+str(y1)+" "+str(x2)+","+str(y2)+"\" />"
#		svg.append(t)

def svg_drawLine(svg,x1,y1,x2,y2,col="black",width=1):
	#t = "<path style=\"stroke-width:"+str(width)+";stroke:"+str(col)+"\" d=\"M "+str(x1)+","+str(y1)+" "+str(x2)+","+str(y2)+"\" />"
	t = "<path style=\"stroke-width:"+str(width)+";stroke:"+str(col)+"\" d=\"M "+str(round(x1,3))+","+str(round(y1,3))+" "+str(round(x2,3))+","+str(round(y2,3))+"\" />"
	svg.append(t)

def cleanText(text):
	return text.replace("&","&amp;").replace("\'","&apos;").replace("\"","&quot;").replace("<","&lt;").replace(">","&gt;")

def svg_drawText(svg,x,y,text,col="black",xanchor=None,yanchor=None,rotation=None,fontsize=12):
	#text-anchor="start" dominant-baseline="middle" style="font-size:32px"
	xal="" if xanchor == None else " text-anchor=\""+xanchor+"\""
	yal="" if yanchor == None else " dominant-baseline=\""+yanchor+"\""
	rot="" if rotation == None else " transform=\"rotate("+str(rotation)+","+str(x)+","+str(y)+")\""
	t = "<text x=\""+str(x)+"\" y=\""+str(y)+"\""+xal+yal+rot+" style=\"font-size:"+str(fontsize)+"px;font-family:Arial\" >"+cleanText(text)+"</text>"
	svg.append(t)

#def getAxisScale(maxValue):
#	allowedSteps = [1,5,10,20,50,100,200,500,1000,2000,5000,10000,50000,100000,500000,1000000]
#	targetbins = 9
#	bins = -1
#	step = -1
#	for stepSize in allowedSteps:
#		nbins = int(maxValue/stepSize)+1
#		if nbins < 5:break	#stepSize increases, so there is nothing more
#		if nbins >20:continue
#		if abs(nbins-targetbins)<abs(bins-targetbins):
#			bins = nbins
#			step = stepSize
#	if bins==-1 or step==-1: print("Error no stepsize found for x")
#	return bins,step

axisspacer = 5
markerLength = 10

def canvas_createLegend(canvas,x1,y1,x2,y2,legend,vertical=True,textcolour="black",fontmultiplier=1.0):
	#TODO need a way to estimate text lengths	
	#if vertical: stacks the legend fields vertically, otherwise horizontally
	#	if not enough horizontal space, wraps around~~~
	
	
	#canvas.create_rectangle(x1,y1,x2,y2,fill="#ddffee",outline="blue")
	
	x1+=10
	y1+=10
	
	legendColSize = int(26*fontmultiplier)	#Width/height of rectangle or diameter of circle
	legendYStep = int(40*fontmultiplier)	#TODO measure font size	#TODO set font size base on screen size / resolution / scalefactor!
	
	canvas.create_text((x1,y1+legendColSize/2),text=str(legend[0]),anchor="w",fill=textcolour,font="System "+str(int(16*fontmultiplier)))
	for i,(col,desc) in enumerate(legend[1]):
		if desc == "esiRNAs":
			canvas.create_rectangle(
				x1, y1+(i+1)*legendYStep,
				x1+legendColSize, y1+(i+1)*legendYStep+legendColSize,
				outline=col,width=4*fontmultiplier)	#TODO separate outline colour??
		else:
			canvas.create_rectangle(
				x1, y1+(i+1)*legendYStep,
				x1+legendColSize, y1+(i+1)*legendYStep+legendColSize,
				outline=col,fill=col)	#TODO separate outline colour??
		canvas.create_text(
			(x1+legendColSize+5,y1+(i+1)*legendYStep+0.5*legendColSize),
			text=str(desc),anchor="w",fill=textcolour,font="System "+str(int(12*fontmultiplier)))
	
	

def canvas_createXAxis(canvas,x_xaxisStart,x_xaxisEnd,y_xaxisStart,continous=True,startv=None,endv=None,by=None,breaks=None,linewidth=2,lineColour="black",fontsize=10):
	#requires either: continous=True and startv,endv,by OR continous=False and breaks
	#print("XAxis: "+str(x_xaxisStart)+" "+str(x_xaxisEnd)+" "+str(y_xaxisStart))
	if continous:
		#svg_drawLine(svg,x1,y1,x2,y2,col=lineColour,width=1)	#could work with ONE function for Canvas and SVG, just need to return data-point objects for canvas
		x1=x_xaxisStart
		y1=y_xaxisStart+axisspacer
		x2=x_xaxisEnd
		y2=y1
		canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth)
		
		nbreaks=int((endv-startv)/by)+1
		binwidth = (x_xaxisEnd-x_xaxisStart)/(nbreaks-1)
		#for xval in range(startv,endv+by,by=by):
		y2=y_xaxisStart+axisspacer+markerLength
		for step in range(0,nbreaks):
			x1=x_xaxisStart + binwidth*step
			x2=x1
			canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth)
			xval = startv+by*step
			canvas.create_text((x2,y2+linewidth),text=str(xval),anchor="n",fill=lineColour,font="System "+str(fontsize))	#+linewidth to get some space between the line and the text
	else:
		nbreaks=len(breaks)
		binwidth = (x_xaxisEnd-x_xaxisStart)/(nbreaks)
		x1=x_xaxisStart + binwidth/2
		y1=y_xaxisStart+axisspacer
		x2=x_xaxisEnd - binwidth/2
		y2=y1
		canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth)
		y2=y_xaxisStart+axisspacer+markerLength
		for step in range(0,nbreaks):
			x1=x_xaxisStart + binwidth/2 + binwidth*step
			x2=x1
			canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth)
			xval = breaks[step]
			canvas.create_text((x2,y2+linewidth),text=str(xval),anchor="n",fill=lineColour,font="System "+str(fontsize))	#+linewidth to get some space between the line and the text
		
def canvas_createYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,continous=True,startv=None,endv=None,by=None,linewidth=2,yaxisBuffer=20,lineColour="black",fontsize=10):
	#requires either: continous=True and startv,endv,by OR continous=False and breaks
	#print("YAxis: "+str(y_yaxisStart)+" "+str(y_yaxisEnd))
	if continous:
		x1=x_yaxisStart -axisspacer
		y1=y_yaxisStart
		x2=x1
		y2=y_yaxisEnd
		canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth)
		
		#print("YAxis: "+str(endv)+" - "+str(startv)+", "+str(by))
		nbreaks=int((endv-startv)/by)+1
		#print("Breaks: "+str(nbreaks))
		binwidth = abs(y_yaxisStart-y_yaxisEnd)/(nbreaks-1)
		#print("BinWidth: "+str(binwidth))
		x1=x_yaxisStart -axisspacer -markerLength
		for step in range(0,nbreaks+1):
			y1=y_yaxisEnd - binwidth*step
			y2=y1
			canvas.create_line(x1,y1,x2,y2,fill=lineColour,width=linewidth)
			yval = startv+by*step
			#print(str(yval)+" ~ "+str(y1))
			canvas.create_text((x1-linewidth,y1),text=str(yval),anchor="e",fill=lineColour,font="System "+str(fontsize))	#+linewidth to get some space between the line and the text


def canvas_createSplitYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,startv=None,endv=None,by=None,linewidth=2,yaxisBuffer=20,lineColour="black",fontsize=10):
		x1=x_yaxisStart -axisspacer
		y1=y_yaxisStart
		x2=x1
		y2=y_yaxisEnd
		splitNBins = (endv-startv+1)	#Bins for each part
		nbins = splitNBins*2+1		#total bins for top and bottom + spacer line
		binwidth = abs(y_yaxisStart-y_yaxisEnd)/(nbins)
		#print("Split YAxis: "+str(splitNBins)+" "+str(nbins)+" "+str(binwidth)+" "+str(abs(y_yaxisStart-y_yaxisEnd)))
		canvas.create_line(
			x1,y2-(0.5)*binwidth,
			x1,y2-(splitNBins-0.5)*binwidth,
			fill=lineColour,width=linewidth)
		canvas.create_line(
			x1,y2-(splitNBins+1.5)*binwidth,
			x1,y2-(nbins-0.5)*binwidth,
			fill=lineColour,width=linewidth)
		
		x2=x_yaxisStart -axisspacer -markerLength
		for j,i in enumerate([0,splitNBins-1,splitNBins+1,nbins-1]):		#ylabel	#TODO !!!
			canvas.create_line(
				x1,y2-((i+0.5)*binwidth),
				x2,y2-((i+0.5)*binwidth),
				fill=lineColour,width=linewidth)
			if j%2==0:
				canvas.create_text(
					(x2-linewidth,y2-((i+0.5)*binwidth)),
					text=str(startv),anchor="se",fill=lineColour,font="System "+str(fontsize))
			else:
				canvas.create_text(
					(x2-linewidth,y2-((i+0.5)*binwidth)),
					text=str(endv),anchor="ne",fill=lineColour,font="System "+str(fontsize))

def canvas_createXLabel(canvas,x_xLabelCenter,y_xLabelStart,xLabelText,fontsize=16,textcolour="black"):
	canvas.create_text((x_xLabelCenter,y_xLabelStart),text=str(xLabelText),anchor="n",fill=textcolour,font="System "+str(fontsize))#+" bold")
	
def canvas_createYLabel(canvas,y_yLabelCenter,x_yLabelStart,yLabelText,fontsize=16,textcolour="black"):
	canvas.create_text((x_yLabelStart,y_yLabelCenter),text=str(yLabelText),anchor="s",fill=textcolour,font="System "+str(fontsize),angle=90)
	
def canvas_createBars(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,discreetX=False,barcolours=None,lineColour="black"):
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
	for i,point in enumerate(data):
		xcenter = x_dataStart+(point[0]-xmin)*xdataToPix	#TODO offset !!	~startv
		if discreetX:
			xcenter+=xdataToPix/2
			#print(str(point)+" "+str(xcenter))
		#yheight = 
		#posBars = list()
		posBars = [None]*(len(point)-1)
		for j in range(len(point)-1,0,-1):
			y1 = yzero - point[j] * ydataToPix * ((j%2)*2-1)
			y2 = yzero
			bar=None
			if discreetX:
				x1 = xcenter - barradius
				x2 = xcenter + barradius
				bar = graph.canvas.create_rectangle(x1,y1,x2,y2,fill=barcolours[i][j-1][0],outline=barcolours[i][j-1][1])
			else:
				x1 = xcenter
				x2 = x1
				bar = graph.canvas.create_line(x1,y1,x2,y2,fill=barcolours[i][j-1][0],width=barwidth)
			posBars[j-1] = bar	#posBars.append(bar)
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
	
	
	#biggerAdd = 1 if abs(xmax)+abs(xmin)>50 else 0
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
	for i,point in enumerate(data):
	#for i,point in sorted(zip(list(range(len(data))),data), key=lambda x: x[1]):	#cant sort by colouring, because the graph doesnt know about this hidden value behind the colouring
		#if i%20==0:print(point)
		xcenter = x_dataStart+(point[1]-xmin)*xdataToPix
		ycenter = ybase-(point[2]-ymin)*ydataToPix
		points[i] = (canvas.create_oval(
			xcenter-pointRadius,ycenter-pointRadius,
			xcenter+pointRadius,ycenter+pointRadius,
			outline="",#outlineColour if graph.colouroverride is None else graph.colouroverride[i], 
			width=7,
			fill=fillColour if graph.colouroverride is None else graph.colouroverride[i]),
			xcenter,ycenter)	#(ovalObject,xcenter,ycenter)
	return points

def canvas_createHeatmap(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,colourscale,xmax,fontmultiplier=1.0):	#TODO cleanup!

	#------------ Data -> cells ---------------------
	cells = [[None]*len(data[0]) for i in range(len(data))]		#TODO values in Heatmap are wrong?? startpos on axis is wrong ???
	
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
	
	for x,column in enumerate(data):
		for y,value in enumerate(column):
			#cellColour = getHexColour(int(256/yvals*y),0,int(256/xvals*x))
			cellColour = getColour(value,colourscale)
			try:
				cells[x][y] = canvas.create_rectangle(
					x_dataStart+(x)*xdataToPix, y2-(y)*ydataToPix,
					x_dataStart+(x+1)*xdataToPix, y2-(y+1)*ydataToPix,
					fill=cellColour)#outline=cellColour,
			except:
				print("[Draw] Error with cell: "+str(x)+"-"+str(y)+": "+str(value)+" "+str(cellColour))
			
			if (x,y) in graph.positionalColouring:
				canvas.itemconfig(cells[x][y],outline="#ff00ff",width=6*fontmultiplier)
				#canvas.tag_raise(cells[x][y])	#TODO doesnt do anything here, needs to be called later!
				graph.highlightpositions.add((x,y))
	for (x,y) in graph.positionalColouring:	#TODO could also just draw them later, better for SVG compatibility anyway!
		canvas.tag_raise(cells[x][y])
	return cells

def canvas_createPlot(graph,canvas,data,lineColour="black",graphType=None,colourscale=None,width=500,height=500,scaleFactor=1,fontmultiplier=1.0):
	#TODO get dict of parametes instead of graph !
	#TODO cleanup here !
	#TODO cleanup other (now unused) functions !
	#TODO modernize svg export !
	
	#TODO maybe just replace canvas with a custom class that implements all functions, but converts them into svg code?
	#~check if there are other things to consider....
	#this method gets the width and height to draw on, so can work nicely..
	#re-calclulating the x/y-scale each time shouldnt be a problem
	#scale and such could be set on the canvas object and therefore export wont overwrite the existing IG / this method can also be called form combo instead
	
	#buffers depend on fontsize and screen scaling
	
	graphType = graph.graphType
	x_canvasOffset = 0	#offset on canvas .....
	y_canvasOffset = 0	#added to all positions
	
	width = graph.width	#space allowed on canvas from offset
	height = graph.height
	#print("Height: "+str(graph.height))
	
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
	xlabel=not graph.xlab is None
	xaxis=True
	ylabel=not graph.ylab is None
	yaxis=True
	legend=not graph.legend is None
	topLegend=False
	if title:titleBuffer=50
	if sideTitle:sideTitleBuffer	= int(200*fontmultiplier)
	if xlabel:xlabelBuffer		= int(50*fontmultiplier)
	if xaxis:xaxisBuffer		= int(40*fontmultiplier)
	if ylabel:ylabelBuffer		= int(50*fontmultiplier)
	if yaxis:yaxisBuffer		= int(120*fontmultiplier)
	if legend:legendBuffer		= int(410*fontmultiplier)
	if topLegend:yLegendBuffer	= int(50*fontmultiplier)
	
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
	
	canvas = graph.canvas
	
	
	#--------------------------------- Data bounds ---------------------------------
	#TODO
	#if len(data)<50:print("\n".join([str(point) for point in data]))	#TODO cleanup!
	
	#print("graph-X: "+str(graph.xbins)+" "+str(graph.xstep)+" "+str(graph.xdataToPix))	#TODO
	#print("graph-Y: "+str(graph.ybins)+" "+str(graph.ystep)+" "+str(graph.ydataToPix))
	
	discreetX = False
	if not graphType=="HEAT":
		from graphs.InteractiveGraph import getAxisScale, getAxisScale2
		if graphType=="SCATTER":
			maxx1 = max([point[1] for point in data])
			minx1 = min([point[1] for point in data])
			if minx1>=0:xbins,xstep = getAxisScale(maxx1,minValue=minx1)
			else:xbins,xstep = getAxisScale2(maxx1,abs(minx1))
		else:
			maxx1 = max([point[0] for point in data])
			minx1 = min([point[0] for point in data])
			xbins,xstep = getAxisScale(maxx1,minValue=minx1)	#TODO improve ~ from 0 in steps
		#print(str(maxx1)+" "+str(minx1)+" "+str(xbins)+" "+str(xstep))
		#print("Xdef: "+str(minx1)+" "+str(maxx1)+" "+str(xstep))
		
		if graphType=="SCATTER":
			maxy1 = max([point[2] for point in data])
			miny1 = abs(min([point[2] for point in data]))	#TODO
			ybins,ystep = getAxisScale(maxy1,minValue=miny1)
			maxy2=miny1
		else:
			maxy1 = max([max([point[i] for i in range(1,len(point),2)]) for point in data])
			maxy2 = 0
			if len(data[0])>2:
				maxy2 = max([max([point[i] for i in range(2,len(point),2)]) for point in data])
			ybins,ystep = getAxisScale2(maxy1,maxy2)
		
		#print(str(maxy1)+" "+str(maxy2)+" "+str(ybins)+" "+str(ystep))
		#print("Ydef: "+str(-maxy2)+" "+str(maxy1)+" "+str(ystep))
	
	
		if len(data)<50:
			discreetX = True
	graph.discreetX = discreetX
	if graphType=="SCATTER":
		if minx1>0:
			xmin = int(minx1/xstep)
			xmax = xmin + xstep * xbins
		else:
			xmax = xstep * xbins[0]
			xmin = -xstep * xbins[1]
		#print(str(xmin)+" - "+str(xmax))
		ymin = int(miny1/xstep)
		ymax = ymin + ystep * ybins
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
			xmax = xmin + xstep * xbins
		
		ymax = ystep * ybins[0]
		ymin = -ystep * ybins[1]
	
	#print("Proper Xdef: "+str(xmin)+" "+str(xmax)+" "+str(xstep))
	#print("Proper Ydef: "+str(ymin)+" "+str(ymax)+" "+str(ystep))
	
	#print("yaxis: "+str(height)+" "+str(y_xaxisStart))
	#Todo fontsize & linewidth
	
	#--------------------------------- Axes ---------------------------------
	if discreetX:
		breaks = [p[0] for p in data] 
		if not graph.xLabels is None:
			breaks = [graph.xLabels[p[0]] for p in data]
		#print("\nBreaks: "+str(breaks)+"\n")
		canvas_createXAxis(canvas,x_xaxisStart,x_xaxisEnd,y_xaxisStart,continous=False,breaks=breaks,fontsize=int(10*fontmultiplier),lineColour=lineColour)
	else:
		canvas_createXAxis(canvas,x_xaxisStart,x_xaxisEnd,y_xaxisStart,continous=True,startv=xmin,endv=xmax,by=xstep,fontsize=int(10*fontmultiplier),lineColour=lineColour)
	
	
	#TODO YAxis for heatmap
	if graphType=="HEAT":
		canvas_createSplitYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,startv=ymin,endv=ymax,by=1,linewidth=2,yaxisBuffer=20,lineColour=lineColour,fontsize=int(10*fontmultiplier))
	else:
		canvas_createYAxis(canvas,y_yaxisStart,y_yaxisEnd,x_yaxisStart,continous=True,startv=ymin,endv=ymax,by=ystep,yaxisBuffer=yaxisBuffer,fontsize=int(10*fontmultiplier),lineColour=lineColour)	#Count +-, cov+-
	
	
	#--------------------------------- Legend and Labels ---------------------------------
	if not graph.legend is None:
		canvas_createLegend(canvas,x_xaxisEnd,y_yaxisStart,x_xaxisEnd+legendBuffer,y_yaxisEnd,graph.legend,vertical=True,textcolour=lineColour,fontmultiplier=fontmultiplier)
	
	if not graph.xlab is None:
		canvas_createXLabel(canvas,x_xLabelCenter,y_xLabelStart,graph.xlab,fontsize=int(16*fontmultiplier),textcolour=lineColour)
	
	if not graph.ylab is None:
		canvas_createYLabel(canvas,y_yLabelCenter,x_yLabelStart,graph.ylab,fontsize=int(16*fontmultiplier),textcolour=lineColour)
	
	#--------------------------------- colouring stuff ---------------------------------
	#TODO
	#print(str(graph.xbins)+" "+str(graph.xstep)+" "+str(graph.xdataToPix))
	barcolours=None
	if not graphType=="HEAT" and not graph.positionalColouring is None:
		#for key,val in graph.positionalColouring.items():
		#	print(str(key)+": "+str(val))
		#if discreetX:
		#	for strandDict in graph.positionalColouring:	#TODO unify!
				#print("Highlights:")
				#3: pseudoGS
				#24: esiGS
				#45: esiGS
				#66: esiGS
				#89: esiPS
				#110: esiPS
				#131: esiPS
				#152: pseudoPS
				#for key,val in strandDict.items():
				#	print(str(key)+": "+str(val))
		barcolours=[None]*len(data)
		nbarsPerPoint=len(data[0])-1
		for i,point in enumerate(data):
			cols=[None]*nbarsPerPoint
			#for j in range(nbarsPerPoint-2,nbarsPerPoint):	#currently [for coverage] bg is 3,4 while fg is 1,2
			for j in range(0,nbarsPerPoint):
				if point[0] in graph.positionalColouring[j%2] and j<2:	#TODO !!
					cols[j] = [graph.styles[graph.positionalColouring[j%2][point[0]]][0],graph.styles[graph.positionalColouring[j%2][point[0]]][1]]
				else:
					cols[j] = graph.styles["default"]
			barcolours[i]=cols
	
	#--------------------------------- Bounding box of Data ---------------------------------
	#graph.canvas.create_rectangle(x_dataStart,y_dataStart,x_dataStart+x_dataSpace,y_dataStart+y_dataSpace,fill="#ddeeff",outline="red")
	#canvas.create_text((x_dataStart,y_dataStart),text="Debug data area",anchor="nw",fill="#ff0000",font="System 16 bold")
	
	if graphType=="BAR" or graphType=="BAR2":	#TODO
		bars = canvas_createBars(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,discreetX=discreetX,barcolours=barcolours,lineColour=lineColour)
	
	if graphType=="multiLine":
		if graph.lineColours is None:	#TODO
			lineColours = ["red","red","green","green","blue","blue"]
		else:
			lineColours = graph.lineColours
		lines = canvas_createLines(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,linewidth=5,lineColours=lineColours,discreetX=discreetX)
	
	if graphType=="SCATTER":
		points = canvas_createPoints(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,xmin,xmax,ymin,ymax,pointRadius=10,discreetX=discreetX,fillColour=lineColour)
		
	if graphType=="HEAT":
		cells = canvas_createHeatmap(graph,canvas,data,x_dataStart,x_dataSpace,y_dataStart,y_dataSpace,colourscale,xmax)	#????	#data is [x][y] = value ??
		
	#--------------------------------- Return objects ---------------------------------
	if graphType=="multiLine":return lines
	if graphType=="SCATTER":return points
	if graphType=="BAR" or graphType=="BAR2":return bars
	if graphType=="HEAT": return cells
	return False

def createBarHighlight(graph,pos):
	x = graph.xbase+pos*graph.xdataToPix
	y = graph.ybase
	h = graph.ybins*graph.ystep*graph.ydataToPix
	r = graph.barRadius+2.5
	barHighlight = graph.canvas.create_rectangle(x-r,y, x+r,y-h, fill="",width=5,outline="#ff00c6")#ff5700")#"#ff00c6")#"#00ffff")	#ff7700
	#graph.canvas.tag_lower(barHighlight)
	return barHighlight

def svg_drawBarplot(svg,graph,data,lineColour="#000000",barColour="#000000",barFillColour="#000000",width=500,height=500,graph_yoffset=0,graph_xoffset=0,scaleFactor=1,peakGroups=None):
	
	
	
	#print(graph_yoffset)	#TODO fix the graph dimensions and labels and so...
	#print(graph.barRadius)
	#print(width)
	#print(len(data))
	#print(width/len(data))
	sw=1
	if graph.barRadius <1: sw=max(0.1,graph.barRadius/2)
	#print(sw)
	#print("yzero: "+str(graph.yzero))
	#svg_writeStyle(svg,graph.styles[0],sw=sw)
	#svg_writeStyle(svg,"default",graph.styles[0][0],graph.styles[0][1],sw=sw)
	#svg_drawBar(svg,x,y,height,width=3.0,barColour="#000000",barFillColour="#000000")
	#svg_drawLine(svg,x1,y1,x2,y2,col="black")
	#svg_drawText(svg,x,y,text,col="black")
	#TODO draw reckt around gaph area
	svg_drawRect(svg,graph_xoffset,graph_yoffset,w=width,h=height,stroke=lineColour,fill="none",sw=scaleFactor*2)
	
	svg_drawText(svg,
		graph_xoffset+width-20,graph_yoffset+height/2,
		str(graph.title),col=lineColour,xanchor="middle",yanchor="middle",rotation=90,fontsize=graph.exportFontsize)
	
	xDataOffset = min([point[0] for point in data])
	if xDataOffset==1:xDataOffset=0
	#---------------- axes --------------------
	svg_drawLine(svg,
		graph.xbase+graph_xoffset,graph.ybase+graph_yoffset+graph.axisbuffer,
		graph.xbase+graph_xoffset+(graph.xbins*graph.xstep*graph.xdataToPix),graph.ybase+graph_yoffset+graph.axisbuffer,
		col=lineColour,width=scaleFactor)	#xaxis
	for i in range(graph.xbins+1):	#xlabel
		svg_drawLine(svg,
			graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.axisbuffer,
			graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.markerLength+graph.axisbuffer,
			col=lineColour,width=scaleFactor)
		svg_drawText(svg,
			graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.markerLength+graph.axisbuffer+2,	#TODO +2?
			str(xDataOffset+(i)*graph.xstep),col=lineColour,xanchor="middle",yanchor="hanging",fontsize=graph.exportFontsize)
	
	svg_drawLine(svg,
		graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset,
		graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset-(graph.ybins*graph.ystep*graph.ydataToPix),
		col=lineColour,width=scaleFactor)	#yaxis
	for i in range(graph.ybins+1):		#ylabel
		svg_drawLine(svg,
			graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),
			graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),
			col=lineColour,width=scaleFactor)
		svg_drawText(svg,
			graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer-2,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),	#TODO +2?
			str(i*graph.ystep),col=lineColour,xanchor="end",yanchor="middle",fontsize=graph.exportFontsize)
	
	#------------ Data -> Bars ---------------------
	
	if not graph.colouroverride[graph.graphName] is None:	#TODO fix colours
		barcolours = graph.colouroverride[graph.graphName]	#TODO this is ugly! the graphName is set temporarily! should be a parameter!
		print(graph.graphName)
		print(graph.colouroverride.keys())
		print(barcolours[:10])
	else:
		barcolours = getPosColours(peakGroups,len(data),default=barColour)
	#barcolours = getPosColours(peakGroups,len(data),default=barColour)	#TODO
	#for bar,col in zip(self.bars,barcolours):
	#	if isinstance(bar,list):
	#		for subbar in bar:
	#			self.canvas.itemconfig(subbar,fill=col,outline=col)
	#	else:
	#		self.canvas.itemconfig(bar,fill=col,outline=col)
	for i,point in enumerate(data):
		x = graph.xbase+graph_xoffset+(point[0]-xDataOffset)*graph.xdataToPix
		y = graph.yzero+graph_yoffset
		y2= point[1]*graph.ydataToPix
		if barcolours[i] == barColour:
			svg_drawBarStyle(svg,"defBar",#graph.styles[0][0],
				x,y,y2,r=graph.barRadius)
		else:
			#svg_drawBarStyle(svg,graph.styles[0][0],
			svg_drawBarCustom(svg,
				x,y,y2,r=graph.barRadius,stroke=barcolours[i],fill=barcolours[i],sw=sw)

def svg_drawBar2plot(svg,graph,data,lineColour="#000000",barColour="#000000",barFillColour="#000000",width=500,height=500,graph_yoffset=0,graph_xoffset=0,scaleFactor=1):
	xoffset = min([point[0] for point in data])-1
	
	#for style in graph.styles:svg_writeStyle(svg,style)
	svg.append("<g>")
	
	if not graph.legend is None:	#TODO combine with the other graphs!, no redundant code!
		#print(graph.legend)
		xlegendBase = graph_xoffset+graph.xbase+(graph.xbins*graph.xstep*graph.xdataToPix)+10	#TODO
		legendColSize = graph.exportFontsize	#20	#Width/height of rectangle or diameter of circle
		ylegendBase = graph_yoffset+10	#TODO dynamic fraction of height, based on legend length
		legendYStep = graph.exportFontsize+5	#25	#TODO measure font size	#TODO set font size base on screen size / resolution / scalefactor!
		svg.append("<g>")
		svg_drawText(svg,xlegendBase,ylegendBase+legendColSize/2,str(graph.legend[0]),xanchor="start",yanchor="middle",col=lineColour,fontsize=graph.exportFontsize)
		for i,(col,desc) in enumerate(graph.legend[1]):
			svg_drawRect(svg,
				xlegendBase, ylegendBase+(i+1)*legendYStep,
				w=legendColSize, h=legendColSize,
				stroke=col,fill=col)	#TODO separate outline colour??
			svg_drawText(svg,
				xlegendBase+legendColSize+5,ylegendBase+(i+1)*legendYStep+0.5*legendColSize,
				str(desc),xanchor="start",yanchor="middle",col=lineColour,fontsize=graph.exportFontsize)
		svg.append("</g>")
	
	#svg_drawBar(svg,x,y,height,width=3.0,barColour="#000000",barFillColour="#000000")
	#svg_drawLine(svg,x1,y1,x2,y2,col="black")
	#svg_drawText(svg,x,y,text,col="black")
	#TODO draw reckt around gaph area
	svg_drawRect(svg,graph_xoffset,graph_yoffset,w=width,h=height,stroke=lineColour,fill="none",sw=scaleFactor*2)
	
	svg_drawText(svg,
		graph_xoffset+width-graph.exportFontsize,graph_yoffset+height/2,
		str(graph.graphName),col=lineColour,xanchor="middle",yanchor="middle",rotation=90,fontsize=graph.exportFontsize)
	
	if not graph.xlab is None:
		svg_drawText(svg,
			graph_xoffset+width/2,graph_yoffset+height-graph.exportFontsize,
			str(graph.xlab),col=lineColour,xanchor="middle",yanchor="middle",fontsize=graph.exportFontsize)
	if not graph.ylab is None:
		svg_drawText(svg,
			graph_xoffset+graph.exportFontsize,graph_yoffset+height/2,
			str(graph.ylab),col=lineColour,xanchor="middle",yanchor="middle",rotation=-90,fontsize=graph.exportFontsize)
	
	
	#---------------- axes --------------------
	svg.append("<g>")
	svg_drawLine(svg,
		graph.xbase+graph_xoffset,graph.ybase+graph_yoffset+graph.axisbuffer,
		graph.xbase+graph_xoffset+(graph.xbins*graph.xstep*graph.xdataToPix),graph.ybase+graph_yoffset+graph.axisbuffer,
		col=lineColour,width=scaleFactor)	#xaxis
	for i in range(graph.xbins+1):	#xlabel
		if graph.xLabels is None or i in graph.xLabels:
			if not (graph.cutOuterXLabsBool and (i==0 or i==graph.xbins)):
				svg_drawLine(svg,
					graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.axisbuffer,
					graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.markerLength+graph.axisbuffer,
					col=lineColour,width=scaleFactor)
		if graph.xLabels is None:
			if not (graph.cutOuterXLabsBool and (i==0 or i==graph.xbins)):
				svg_drawText(svg,
					graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.markerLength+graph.axisbuffer+2,	#TODO +2?
					str((xoffset+i)*graph.xstep),col=lineColour,xanchor="middle",yanchor="hanging",fontsize=graph.exportFontsize)
		elif i in graph.xLabels:
			svg_drawText(svg,
				graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.markerLength+graph.axisbuffer+2,	#TODO +2?
				str(graph.xLabels[i]),col=lineColour,xanchor="end",yanchor="middle",rotation=-90,fontsize=graph.exportFontsize)
	svg.append("</g>")
	
	if graph.ystep>0:
		svg.append("<g>")
		if not isinstance(graph.ybins,int):
			svg_drawLine(svg,
				graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset+(graph.ybins[1]*graph.ystep*graph.ydataToPix),
				graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset-(graph.ybins[0]*graph.ystep*graph.ydataToPix),
				col=lineColour,width=scaleFactor)	#yaxis
			for i in range(-graph.ybins[1],graph.ybins[0]+1):		#ylabel
				svg_drawLine(svg,
					graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),
					graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),
					col=lineColour,width=scaleFactor)
				svg_drawText(svg,
					graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer-2,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),	#TODO +2?
					str(round(i*graph.ystep,5)),col=lineColour,xanchor="end",yanchor="middle",fontsize=graph.exportFontsize)
		
		else:
			svg_drawLine(svg,
				graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset,
				graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset-(graph.ybins*graph.ystep*graph.ydataToPix),
				col=lineColour,width=scaleFactor)	#yaxis
			for i in range(graph.ybins+1):		#ylabel
				svg_drawLine(svg,
					graph.xbase+graph_xoffset-graph.axisbuffer,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),
					graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),
					col=lineColour,width=scaleFactor)
				svg_drawText(svg,
					graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer-2,graph.yzero+graph_yoffset-(i*graph.ystep*graph.ydataToPix),	#TODO +2?
					str(i*graph.ystep),col=lineColour,xanchor="end",yanchor="middle",fontsize=graph.exportFontsize)
		
		
		svg.append("</g>")
		
	
	#------------ Data -> Bars ---------------------
	if graph.ystep>0:
		svg.append("<g>")
		for i,point in enumerate(data):	#TODO i unused
			x = graph.xbase+graph_xoffset+(point[0]-xoffset)*graph.xdataToPix
			y = graph.yzero+graph_yoffset
			r = graph.barRadius
			
			if len(point)>3:
				svg_drawBarStyle(svg,"defBar",x,y,point[3]*graph.ydataToPix,r=r)
				svg_drawBarStyle(svg,"defBar",x,y,-point[4]*graph.ydataToPix,r=r)
			
			if point[0] in graph.positionalColouring[0]:
				svg_drawBarStyle(svg,graph.positionalColouring[0][point[0]],x,y,point[1]*graph.ydataToPix,r=r)
			else:	svg_drawBarStyle(svg,"defBar",x,y,point[1]*graph.ydataToPix,r=r)
			
			if point[0] in graph.positionalColouring[1]:
				svg_drawBarStyle(svg,graph.positionalColouring[1][point[0]],x,y,-point[2]*graph.ydataToPix,r=r)
			else:	svg_drawBarStyle(svg,"defBar",x,y,-point[2]*graph.ydataToPix,r=r)
		svg.append("</g>")
	svg.append("</g>")

def svg_drawHeatmap(svg,graph,data,lineColour="#000000",colourscale=None,width=500,height=500,graph_yoffset=0,graph_xoffset=0,scaleFactor=1,legend=None):
	
	svg_drawRect(svg,graph_xoffset,graph_yoffset,w=width,h=height,stroke=lineColour,fill="none",sw=scaleFactor*2)
	if legend is None:
		legend = graph.legend
	if not legend is None and not graph.legend is None:	#TODO combine with the other graphs!, no redundant code!
		xlegendBase = graph_xoffset+graph.xbase+(graph.xbins*graph.xstep*graph.xdataToPix)+10	#TODO
		legendColSize = 20	#Width/height of rectangle or diameter of circle
		ylegendBase = graph_yoffset+10	#TODO dynamic fraction of height, based on legend length
		legendYStep = 25	#TODO measure font size	#TODO set font size base on screen size / resolution / scalefactor!
		svg_drawText(svg,xlegendBase,ylegendBase+legendColSize/2,str(graph.legend[0]),xanchor="start",yanchor="middle",col=lineColour,fontsize=graph.exportFontsize)
		for i,(col,desc) in enumerate(legend[1]):#graph.legend[1]):
			if desc == "esiRNAs":
				svg_drawRect(svg,
					xlegendBase, ylegendBase+(i+1)*legendYStep,
					w=legendColSize, h=legendColSize,
					stroke=col,fill="None")	#TODO separate outline colour??
			else:
				svg_drawRect(svg,
					xlegendBase, ylegendBase+(i+1)*legendYStep,
					w=legendColSize, h=legendColSize,
					stroke=col,fill=col)	#TODO separate outline colour??
			svg_drawText(svg,
				xlegendBase+legendColSize+5,ylegendBase+(i+1)*legendYStep+0.5*legendColSize,
				str(desc),xanchor="start",yanchor="middle",col=lineColour,fontsize=graph.exportFontsize)
	svg_drawText(svg,
		graph_xoffset+20,graph_yoffset+height/2,
		str("read length"),col=lineColour,xanchor="middle",yanchor="middle",rotation=-90,fontsize=graph.exportFontsize)
	svg_drawText(svg,
		graph_xoffset+width-20,graph_yoffset+height/2,
		str(graph.title),col=lineColour,xanchor="middle",yanchor="middle",rotation=90,fontsize=graph.exportFontsize)
	
	#---------------- axes --------------------
	svg_drawLine(svg,
		graph.xbase+graph_xoffset,graph.ybase+graph_yoffset+graph.axisbuffer,
		graph.xbase+graph_xoffset+(graph.xbins*graph.xstep*graph.xdataToPix),graph.ybase+graph_yoffset+graph.axisbuffer
		,col=lineColour,width=scaleFactor)		#xaxis
	for i in range(graph.xbins+1):	#xlabel
		svg_drawLine(svg,
			graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.axisbuffer,
			graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.markerLength+graph.axisbuffer,
			col=lineColour,width=scaleFactor)
		svg_drawText(svg,
			graph.xbase+graph_xoffset+graph.xstep*i*graph.xdataToPix,graph.ybase+graph_yoffset+graph.markerLength+graph.axisbuffer+2,	#TODO +2?
			str(i*graph.xstep),col=lineColour,xanchor="middle",yanchor="hanging",fontsize=graph.exportFontsize)
	
	
	if -1 in graph.yvals:
		#print(graph.ybase+graph_yoffset)
		svg_drawLine(svg,
			graph.xbase+graph_xoffset-graph.axisbuffer,graph.ybase+graph_yoffset-(0.5)*graph.ydataToPix,
			graph.xbase+graph_xoffset-graph.axisbuffer,graph.ybase+graph_yoffset-((graph.ybins-1)/2-0.5)*graph.ydataToPix,
			col=lineColour,width=scaleFactor)
		svg_drawLine(svg,
			graph.xbase+graph_xoffset-graph.axisbuffer,graph.ybase+graph_yoffset-((graph.ybins-1)/2+1.5)*graph.ydataToPix,
			graph.xbase+graph_xoffset-graph.axisbuffer,graph.ybase+graph_yoffset-(graph.ybins-0.5)*graph.ydataToPix,
			col=lineColour,width=scaleFactor)
		for j,i in enumerate([0,int((graph.ybins-1)/2)-1,int((graph.ybins-1)/2+1),graph.ybins-1]):		#ylabel
			y=graph.ybase+graph_yoffset-((i+0.5)*graph.ystep*graph.ydataToPix)
			svg_drawLine(svg,
				graph.xbase+graph_xoffset-graph.axisbuffer,y,
				graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer,y,
				col=lineColour,width=scaleFactor)
			if j%2==0:
				svg_drawText(svg,
					graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer-2,y,	#TODO +2?
					str(graph.yvals[i]),col=lineColour,xanchor="end",yanchor="baseline",fontsize=graph.exportFontsize)
			else:
				svg_drawText(svg,
					graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer-2,y,	#TODO +2?
					str(graph.yvals[i]),col=lineColour,xanchor="end",yanchor="hanging",fontsize=graph.exportFontsize)
		
	else:
		svg_drawLine(svg,
			graph.xbase+graph_xoffset-graph.axisbuffer,graph.ybase+graph_yoffset-(0.5)*graph.ydataToPix,
			graph.xbase+graph_xoffset-graph.axisbuffer,graph.ybase+graph_yoffset-(graph.ybins-0.5)*graph.ydataToPix,
			col=lineColour,width=scaleFactor)	#yaxis
		for i in range(graph.ybins):		#ylabel
			svg_drawLine(svg,
				graph.xbase+graph_xoffset-graph.axisbuffer,graph.ybase+graph_yoffset-((i+0.5)*graph.ystep*graph.ydataToPix),
				graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer,graph.ybase+graph_yoffset-((i+0.5)*graph.ystep*graph.ydataToPix),
				col=lineColour,width=scaleFactor)
			svg_drawText(svg,
				graph.xbase+graph_xoffset-graph.markerLength-graph.axisbuffer-2,graph.ybase+graph_yoffset-((i+0.5)*graph.ystep*graph.ydataToPix),	#TODO +2?
				str(graph.yvals[i]),col=lineColour,xanchor="end",yanchor="middle",fontsize=graph.exportFontsize)
	
	#------------ Data -> cells ---------------------
	
	for x,column in enumerate(data):
		for y,value in enumerate(column):
			cellColour = getColour(value,colourscale)
			#try:
			if (x,y) in graph.positionalColouring:
				pass	#are drawn later so that they are on top
			else:
				svg_drawCell(svg,
					graph.xbase+graph_xoffset+(x)*graph.xdataToPix, graph.ybase+graph_yoffset-(y+1)*graph.ydataToPix,
					w=graph.xdataToPix, h=graph.ydataToPix,
					fill=cellColour)
			#except:
			#	print(str(x)+"-"+str(y)+": "+str(value)+" "+str(cellColour))
	for (x,y) in graph.positionalColouring:
		try:
			cellColour = getColour(data[x][y],colourscale)
			svg_drawCellOutline(svg,
				graph.xbase+graph_xoffset+(x)*graph.xdataToPix, graph.ybase+graph_yoffset-(y+1)*graph.ydataToPix,
				w=graph.xdataToPix, h=graph.ydataToPix,
				fill=cellColour,stroke="#ff00ff",sw=2)
		except:
			print("Cell coords out of bounds "+str(x)+"-"+str(y)+": "+str(value)+" "+str(cellColour))

#TODO add svg export for scatter // make svg as nice as interactive

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
	g= int(g1+(g2-g1)*frac)	#TODO ? flip if r2<r1? also use function!
	b= int(b1+(b2-b1)*frac)
	
	return getHexColour(r,g,b)

def interpolateColoursFraction(frac, col1, col2):
	if frac<=0:return col1
	r1,g1,b1 = hexToDec(col1.lower())
	r2,g2,b2 = hexToDec(col2.lower())
	
	r= int(r1+(r2-r1)*frac) if r1<r2 else int(r2+(r1-r2)*frac)
	g= int(g1+(g2-g1)*frac) if g1<g2 else int(g2+(g1-g2)*frac)
	b= int(b1+(b2-b1)*frac) if b1<b2 else int(b2+(b1-b2)*frac)
	
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


#r1,g1,b1 = getIntValuesForColour(point1[1])	#colours are alread in (r,g,b) !
#r2,g2,b2 = getIntValuesForColour(point2[1])
#hexToInt = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"a":10,"b":11,"c":12,"d":13,"e":14,"f":15}
#def getIntValuesForColour(col):
#	return hexToInt[col[0]]*16+hexToInt[col[1]], 

def getHexColourTuple(colTuple):
	return getHexColour(colTuple[0],colTuple[1],colTuple[2])

decToHex = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
def getHexColour(r,g,b):
	return "#"+decToHex[int(r/16)]+decToHex[r%16]+decToHex[int(g/16)]+decToHex[g%16]+decToHex[int(b/16)]+decToHex[b%16]

def getPosColours(maxima,seqLen,default="#000000"):
	barcolours = [default]*seqLen
	intCol = 13895909
	for peak in maxima:
		intCol = (intCol * 3 ) % 16777216
		stringCol = str(hex(intCol)).removeprefix("0x")
		peakColour = "#"+"0"*(6-len(stringCol))+stringCol
		for pos in peak:
			barcolours[pos-1] = peakColour
	return barcolours

def getPeakMap(maxima,seqLen,default=-1):
	peakMap = [default]*seqLen
	for i,peak in enumerate(maxima):
		for pos in peak:
			peakMap[pos-1] = i
	return peakMap

def isHexColour(string):
	string=string.lower()
	if len(string)!=7:return False
	if not string.startswith("#"): return False
	for c in string[1:]:
		if not c in hexToDecDict:
			return False
	return True


