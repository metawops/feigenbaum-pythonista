#--------------------------------------------------------------------------
# Title      : Feigenbaum
# Author     : Stefan Wolfrum (@metawops)
# Date       : 20.01.2018
# Last Update: 30.01.2018
# Version    : 0.2
# License    : MIT License, (c) 2018 Stefan Wolfrum
#--------------------------------------------------------------------------

import ui
import math
import webbrowser
from objc_util import *
from functools import partial

def select_all(textfield):
	tf = ObjCInstance(textfield).subviews()[0]
	start_pos = tf.beginningOfDocument()
	end_pos = tf.endOfDocument()
	range = tf.textRangeFromPosition_toPosition_(start_pos, end_pos)
	tf.setSelectedTextRange_(range)
	
class feigenbaumView (ui.View):

	def __init__(self):
		# This will also be called without arguments when the view is loaded from a UI file.
		# You don't have to call super. Note that this is called *before* the attributes
		# defined in the UI file are set. Implement `did_load` to customize a view after
		# it's been fully loaded from a UI file.
		self.transform = ui.Transform.translation(self.center[0], self.center[1])
		self.drawAxis = True
		self.axisColor = '#808080'
		self.drawFunction = True
		self.functionColor = '#f70'
		self.drawSpiderweb = True
		self.spiderwebColor = '#a7c6ff'
		self.drawYeX = True # Winkelhalbierende / Y=X
		self.YeXcolor = '#35ff46'
		self.maxLam = 4.0
		self.lam = 4.0
		self.maxIter = 10
		self.maxMaxIter = 200
		self.xStart = 0.7
		self.drawRibbon = False
		self.ribbonLowerBound = 0
		self.paddingTopInitial = 10
		self.paddingTopRibbon = 80
		self.paddingTop = self.paddingTopInitial
		self.paddingBottom = 10
		self.paddingLeft = 10
		self.paddingRight = 10
		self.mode = 0 # 0 = Cobweb, 1 = Feigenbaum

	def did_load(self):
		# This will be called when a view has been fully loaded from a UI file.
		self.maxx = self.bounds[2]
		self.maxy = self.bounds[3]
		self.background_color = '#404040'
							
	def draw(self):
		# This will be called whenever the view's content needs to be drawn.
		# You can use any of the ui module's drawing functions here to render
		# content into the view's visible rectangle.
		# Do not call this method directly, instead, if you need your view
		# to redraw its content, call set_needs_display().
		if (self.mode == 0):
			self.axisPath = ui.Path()
			self.functionPath = ui.Path()
			self.spiderwebPath = ui.Path()
			self.YeXpath = ui.Path()
			self.ribbonPath = ui.Path()
					
			(self.cx, self.cy) = self.bounds.center()
			#print(self.cx, ", ", self.cy)
			
			if (self.drawAxis):
				ui.set_color(self.axisColor)
				# x-Axis:
				self.axisPath.move_to(self.mapx(0), self.mapy(0))
				self.axisPath.line_to(self.mapx(1), self.mapy(0))
				# y-Axis:
				self.axisPath.move_to(self.mapx(0), self.mapy(0))
				self.axisPath.line_to(self.mapx(0), self.mapy(1))
				
				#self.axisPath.move_to(cx+self.spacing*2.0*math.pi, 0)
				#self.axisPath.line_to(cx+self.spacing*2.0*math.pi, self.height)
				self.axisPath.stroke()
				
			if (self.drawYeX):
				ui.set_color(self.YeXcolor)
				self.YeXpath.line_width = 2.0
				self.YeXpath.move_to(self.mapx(0), self.mapy(0))
				self.YeXpath.line_to(self.mapx(1), self.mapy(1))
				self.YeXpath.stroke()
							
			if (self.drawFunction):
				ui.set_color(self.functionColor)
				self.functionPath.line_width = 3.0
				t = 0.0
				max_t = 1.0
				t_step = 0.01  # t_step constant for now but should be dynamic!
				posx = posy = 0
				self.functionPath.move_to(self.mapx(posx), self.mapy(posy))
				while (t < max_t - t_step):
					t = t + t_step
					posx = self.mapx(t)
					posy = self.mapy(self.lam * t * (1-t))
					self.functionPath.line_to(posx, posy)
				# finally make sure that the end of the path lies exactly on the x-Axis:
				finalx = self.mapx(max_t)
				finaly = self.mapy(self.lam * max_t * (1-max_t))
				self.functionPath.line_to(finalx, finaly)
				self.functionPath.stroke()
				
			if (self.drawSpiderweb):
				self.spiderwebPath.line_width = 1.0
				x = self.xStart
				iter = 0
				y = self.lam * x * (1-x)
				ui.set_color(self.spiderwebColor)		
				self.spiderwebPath.move_to(self.mapx(x), self.mapy(0))
				self.spiderwebPath.line_to(self.mapx(x), self.mapy(y))
				if (self.drawRibbon and (iter >= self.ribbonLowerBound)):
					#print(self.mapx(x), ", ", self.mapy(1.0))
					ui.set_color(self.spiderwebColor)
					self.ribbonPath.move_to(self.mapx(x), self.mapy(1.02))
					self.ribbonPath.line_to(self.mapx(x), self.mapy(1.06))
				while (iter < self.maxIter):
					x = y
					ui.set_color(self.spiderwebColor)
					self.spiderwebPath.line_to(self.mapx(x), self.mapy(y))
					y = self.lam * x * (1-x)
					self.spiderwebPath.line_to(self.mapx(x), self.mapy(y))
					if (self.drawRibbon and (iter >= self.ribbonLowerBound)):
						#print(self.mapx(x), ", ", self.mapy(1.0))
						ui.set_color(self.spiderwebColor)
						self.ribbonPath.move_to(self.mapx(x), self.mapy(1.02))
						self.ribbonPath.line_to(self.mapx(x), self.mapy(1.06))
					iter += 1
				self.spiderwebPath.stroke()
				self.ribbonPath.stroke()
		elif (self.mode == 1):
			pass
			
	def mapx(self, x):
		return x * (self.maxx - (self.paddingLeft+self.paddingRight)) + self.paddingLeft
		
	def mapy(self, y):
		return self.maxy - (y * (self.maxy - (self.paddingTop+self.paddingBottom)) + self.paddingBottom)

#----------------------------------
class FeigenbaumTextFieldDelegate (object):
	
	def textfield_should_begin_editing(self, textfield):
		return True
		
	def textfield_did_begin_editing(self, textfield):
		#pass
		ui.delay(partial(select_all, textfield), 0)
		
	def textfield_did_end_editing(self, textfield):
		#pass
		feigenbaumView = v['mainView']
		if textfield.name == 'textfieldLambda':
			current = feigenbaumView.lam
			try:
				val = float(textfield.text)
			except:
				#print("Fehler bei float()!")
				val = current
				textfield.text = "{:.2f}".format(val)
			feigenbaumView.lam = val
			v['viewCobweb']['sliderLambda'].value = val / feigenbaumView.maxLam
		elif textfield.name == 'textfieldXstart':
			current = feigenbaumView.xStart
			try:
				val = float(textfield.text)
			except:
				#print("Fehler bei float()!")
				val = current
				textfield.text = "{:.6f}".format(val)
			feigenbaumView.xStart = val
			v['viewCobweb']['sliderXstart'].value = val
						
		feigenbaumView.set_needs_display()
		
	def textfield_should_return(self, textfield):
		textfield.end_editing()
		return True
		
	def textfield_should_change(self, textfield, range, replacement):
		return True
		
	def textfield_did_change(self, textfield):
		pass
		
# Sliders handling
def sliderLambdaChanged(sender):
	mainView = v['mainView']
	mainView.lam = sender.value * mainView.maxLam
	v['viewCobweb']['textfieldLambda'].text = "{:.2f}".format(mainView.lam)
	mainView.set_needs_display()

def sliderXstartChanged(sender):
	mainView = v['mainView']
	mainView.xStart = sender.value
	v['viewCobweb']['textfieldXstart'].text = "{:.6f}".format(mainView.xStart)
	mainView.set_needs_display()
	
def sliderMaxIterChanged(sender):
	mainView = v['mainView']
	mainView.maxIter = sender.value * mainView.maxMaxIter
	v['viewCobweb']['labelMaxIter'].text = "{:.0f}".format(mainView.maxIter)
	mainView.set_needs_display()

def sliderRibbonLowerBoundChanged(sender):
	mainView = v['mainView']
	mainView.ribbonLowerBound = sender.value * mainView.maxMaxIter
	v['viewCobweb']['labelRibbonLowerBound'].text = "{:.0f}".format(mainView.ribbonLowerBound)
	mainView.set_needs_display()	
	
# --- Button handling ---
def buttonMetawopsTapped(sender):
	webbrowser.open("safari-http://twitter.com/metawops")
	
def buttonShowRibbonTapped(sender):
	mainView = v['mainView']
	if (sender.value):
		mainView.paddingTop = mainView.paddingTopRibbon
		mainView.drawRibbon = True
	else:
		mainView.paddingTop = mainView.paddingTopInitial
		mainView.drawRibbon = False
	mainView.set_needs_display()
	
# --- segmented control handling ---
def segmentedControlTapped(sender):
	si = sender.selected_index
	mainView = v['mainView']
	mainView.mode = si
	if (si == 0):
		# user tapped on 1st button
		v['viewCobweb'].hidden = False
		v['viewFeigenbaum'].hidden = True
	elif (si == 1):
		# user tapped on 2nd button
		v['viewCobweb'].hidden = True
		v['viewFeigenbaum'].hidden = False
	mainView.set_needs_display()
				
# --- MAIN ---	
	
v = ui.load_view('feigenbaumview.pyui')
mainView = v['mainView']
v['viewCobweb']['sliderLambda'].value = mainView.lam / mainView.maxLam
v['viewCobweb']['textfieldLambda'].text = "{:.2f}".format(mainView.lam)
v['viewCobweb']['textfieldLambda'].keyboard_type = ui.KEYBOARD_DECIMAL_PAD
v['viewCobweb']['sliderXstart'].value = mainView.xStart
v['viewCobweb']['textfieldXstart'].text = "{:.6f}".format(mainView.xStart)
v['viewCobweb']['textfieldXstart'].keyboard_type = ui.KEYBOARD_DECIMAL_PAD
v['viewCobweb']['sliderMaxIter'].value = mainView.maxIter / mainView.maxMaxIter
v['viewCobweb']['labelMaxIter'].text = "{:.0f}".format(mainView.maxIter)
v['viewCobweb']['sliderRibbonLowerBound'].value = mainView.ribbonLowerBound / mainView.maxMaxIter
v['viewCobweb']['labelRibbonLowerBound'].text = "{:.0f}".format(mainView.ribbonLowerBound)

v['viewCobweb']['textfieldLambda'].delegate = FeigenbaumTextFieldDelegate()
v['viewCobweb']['textfieldXstart'].delegate = FeigenbaumTextFieldDelegate()

v['viewFeigenbaum'].hidden = True
v['viewFeigenbaum'].y = 109

v.present('full_screen')
