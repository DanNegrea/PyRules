from burp import IBurpExtender, IExtensionStateListener, IHttpListener, ITab

from javax.swing import JScrollPane, JTextPane, JTextArea, JSplitPane, BoxLayout, JPanel, JLabel, JButton, JCheckBox, GroupLayout, LayoutStyle, JScrollBar 
from javax.swing.text import SimpleAttributeSet
from java.awt import Font, Color, FlowLayout, Desktop
from java.awt.event import FocusListener, ActionListener, MouseAdapter
from java.net import URI

from pprint import pformat
from PyUtil import Strings

import base64
import traceback

class BurpExtender(IBurpExtender, IExtensionStateListener, IHttpListener, ITab, FocusListener, ActionListener, MouseAdapter):
	_version = "0.1"
	_name = "PyRules"
	_varsStorage = _name+"_vars"
	_scriptStorage = _name+"_script"
	
	_enabled = 0
	_vars = {}

	def registerExtenderCallbacks(self, callbacks):
		print "Load:"+self._name +" "+self._version 
		
		self.callbacks = callbacks
		self.helpers = callbacks.helpers
		
		#Create Tab layout
		self.jVarsPane = JTextPane()
		self.jVarsPane.setFont(Font('Monospaced', Font.PLAIN, 11))
		self.jVarsPane.addFocusListener(self)
		
		self.jMenuPanel = JPanel()
		self.jLeftUpPanel = JPanel()
		
		self.jEnable = JCheckBox()	
		self.jEnable.setFont(Font('Monospaced', Font.BOLD, 11))
		self.jEnable.setForeground(Color(0, 0, 204))
		self.jEnable.setText(self._name)
		self.jEnable.addActionListener(self)
		
		self.jDocs = JLabel()
		self.jDocs.setFont(Font('Monospaced', Font.PLAIN, 11))
		self.jDocs.setForeground(Color(51, 102, 255))
		self.jDocs.setText(Strings.docs_titel)
		self.jDocs.setToolTipText(Strings.docs_tooltip)
		self.jDocs.addMouseListener(self)
		
		self.jConsoleText = JTextArea()
		self.jConsoleText.setFont(Font('Monospaced', Font.PLAIN, 10))
		self.jConsoleText.setBackground(Color(244, 246, 247))
		self.jConsoleText.setEditable(0)
		self.jConsoleText.setWrapStyleWord(1)
		self.jConsoleText.setRows(10)
		self.jScrollConsolePane = JScrollPane()
		self.jScrollConsolePane.setViewportView(self.jConsoleText)
		#set initial text
		self.jConsoleText.setText(Strings.console_disable)
		
		self.jMenuPanelLayout = GroupLayout(self.jMenuPanel)
		self.jMenuPanel.setLayout(self.jMenuPanelLayout)
		self.jMenuPanelLayout.setHorizontalGroup(
			self.jMenuPanelLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
			.addGroup(self.jMenuPanelLayout.createSequentialGroup()
				.addComponent(self.jEnable)
				.addPreferredGap(LayoutStyle.ComponentPlacement.RELATED, 205, 32767)
				.addComponent(self.jDocs))
		)
		
		self.jMenuPanelLayout.setVerticalGroup(
			self.jMenuPanelLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
			.addGroup(self.jMenuPanelLayout.createSequentialGroup()
				.addGroup(self.jMenuPanelLayout.createParallelGroup(GroupLayout.Alignment.BASELINE)
					.addComponent(self.jEnable)
					.addComponent(self.jDocs))
				.addGap(0, 7, 32767))
		)
		
		self.jConsolePane = JPanel()		
		self.jConsoleLayout = GroupLayout(self.jConsolePane)
		self.jConsolePane.setLayout(self.jConsoleLayout)
		self.jConsoleLayout.setHorizontalGroup(
			self.jConsoleLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
			.addComponent(self.jScrollConsolePane)
		)
		self.jConsoleLayout.setVerticalGroup(
			self.jConsoleLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
			.addGroup(GroupLayout.Alignment.TRAILING, self.jConsoleLayout.createSequentialGroup()
				.addComponent(self.jScrollConsolePane, GroupLayout.DEFAULT_SIZE, 154, 32767)
				.addContainerGap())
		)
		self.jLeftUpPanelLayout = GroupLayout(self.jLeftUpPanel)
		self.jLeftUpPanel.setLayout(self.jLeftUpPanelLayout)
		self.jLeftUpPanelLayout.setHorizontalGroup(
			self.jLeftUpPanelLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
			.addComponent(self.jConsolePane, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, 32767)
			.addComponent(self.jMenuPanel, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
		)
		self.jLeftUpPanelLayout.setVerticalGroup(
			self.jLeftUpPanelLayout.createParallelGroup(GroupLayout.Alignment.LEADING)
			.addGroup(GroupLayout.Alignment.TRAILING, self.jLeftUpPanelLayout.createSequentialGroup()
				.addComponent(self.jMenuPanel, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
				.addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
				.addComponent(self.jConsolePane, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, 32767))
		)		
		
		self.jScrollpaneLeftDown = JScrollPane()
		self.jScrollpaneLeftDown.setViewportView(self.jVarsPane)
		
		self.jSplitPaneLeft = JSplitPane(JSplitPane.VERTICAL_SPLIT, self.jLeftUpPanel, self.jScrollpaneLeftDown)
		self.jSplitPaneLeft.setDividerLocation(300);		
		
		self.jScriptPane = JTextPane()
		self.jScriptPane.setFont(Font('Monospaced', Font.PLAIN, 11))
		self.jScriptPane.addMouseListener(self)
		
		self.JScrollPaneRight = JScrollPane()
		self.JScrollPaneRight.setViewportView(self.jScriptPane)
		
		self.jSplitPane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, self.jSplitPaneLeft, self.JScrollPaneRight)
		self.jSplitPane.setDividerLocation(400);
		
		
		#Load saved saved settings		
		##Load vars
		vars = callbacks.loadExtensionSetting( self._varsStorage )
		if vars:
			vars = base64.b64decode(vars)
		else:
			vars = Strings.vars_intial
		
		## initiate the persistant variables
		locals_ = {}
		exec(vars, {}, locals_)
		self._vars = locals_
		
		## update the vars screen
		self.jVarsPane.document.insertString(
			self.jVarsPane.document.length,
			vars,
			SimpleAttributeSet())
		
		##Load script
		script = callbacks.loadExtensionSetting( self._scriptStorage )
		if script:
			script = base64.b64decode(script)
		else: 
			script = Strings.script_intial
		
		## compile the rules
		self._script = script
		self._code = compile(script, '<string>', 'exec')
		
		## update the rules screen
		self.jScriptPane.document.insertString(
			self.jScriptPane.document.length,
			script,
			SimpleAttributeSet())
		

		#Register Extension
		callbacks.customizeUiComponent(self.getUiComponent())
		callbacks.addSuiteTab(self)
		callbacks.registerExtensionStateListener(self)
		callbacks.registerHttpListener(self)

		self.jScriptPane.requestFocus()

	def getUiComponent(self):
		return self.jSplitPane
		
	def getTabCaption(self):
		return self._name
	
	def actionPerformed(self, event):
		#Check box was clicked
		if self.jEnable == event.getSource():
			if self._enabled == 1:
				self._enabled = 0
				# console content shows help
				self.jConsoleText.setText(Strings.console_disable)
			else:
				self._enabled = 1
				# console content displays the current persistent variable state
				self.jConsoleText.setText(Strings.console_state)
				self.jConsoleText.append(pformat(self._vars))
				self.jConsoleText.append(Strings.extra_line)
				self.jConsoleText.append(Strings.console_log)
		return
		
	def mouseClicked(self, event):
		if event.source == self.jDocs:
			uri = URI.create("https://github.com/DanNegrea/PyRules")
			if uri and Desktop.isDesktopSupported() and Desktop.getDesktop().isSupported(Desktop.Action.BROWSE):
				Desktop.getDesktop().browse(uri)
		return
		
	def focusGained(self, event):
		
		if self.jConsolePane == event.getSource():
			pass
			#print "Status pane gained focus" #debug
		return
	
	def focusLost(self, event):
		#Reinitialize the persistent values
		if self.jVarsPane == event.getSource():
			# get the text from the pane
			end = self.jVarsPane.document.length
			vars= self.jVarsPane.document.getText(0, end)
			
			# compute the new values
			locals_ = {}
			exec(vars, {}, locals_)
			self._vars = locals_
			
			# display the new result in console
			self.jConsoleText.append(Strings.console_state)
			self.jConsoleText.append(pformat(self._vars))
			self.jConsoleText.append(Strings.extra_line)
			self.jConsoleText.append(Strings.console_log)
			
			# scroll to bottom
			verticalScrollBar = self.jScrollConsolePane.getVerticalScrollBar()
			verticalScrollBar.setValue( verticalScrollBar.getMaximum() )
		return

	def extensionUnloaded(self):
		try:
			#Save the latestest vars and script text
			## save vars
			end = self.jVarsPane.document.length
			vars= self.jVarsPane.document.getText(0, end)
			vars = base64.b64encode(vars)
			self.callbacks.saveExtensionSetting( self._varsStorage, vars )
			## save script/rules
			end = self.jScriptPane.document.length
			script= self.jScriptPane.document.getText(0, end)
			script = base64.b64encode(script)
			self.callbacks.saveExtensionSetting( self._scriptStorage, script )
		except Exception:
			traceback.print_exc(file=self.callbacks.getStderr())
		print "Unloaded" #debug
		return

	
	def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
		if self._enabled==0:
			return
	
		try:	
			locals_  = {'extender': self,
						'callbacks': self.callbacks,
						'helpers': self.helpers,
						'toolFlag': toolFlag,
						'messageIsRequest': messageIsRequest,
						'messageInfo': messageInfo,
						'log':self.log
						}
			# add the _vars as gloval variables
			locals_= dict(locals_, **self._vars);
			
			# execute the script/rules
			try:
				exec(self.getCode, {}, locals_)
			# catch exit() call insite the rule
			except SystemExit:
				pass
			
			# update the persistant variables by searching the local variables with the same name
			for key in self._vars:
				# assumption self._vars dictionary is smaller than locals_
				if key in locals_:
					self._vars[key] = locals_[key]
		except Exception:
			traceback.print_exc(file=self.callbacks.getStderr())
		return

	#Returns the compiled script
	@property
	def getCode(self):
		end = self.jScriptPane.document.length
		script = self.jScriptPane.document.getText(0, end)
		
		# if the script hasn't changed return the already compile text
		if script == self._script:
			return self._code
		self._script = script
		
		# compile, store and return the result
		self._code = compile(script, '<string>', 'exec')
		return self._code

	#Log the information into the console screen
	def log(self, obj):
		# if string just append. else use pformat from pprint
		if isinstance(obj, str):
			self.jConsoleText.append(obj + "\n")
		else:
			self.jConsoleText.append(pformat(obj) + "\n")
		# scroll to bottom
		verticalScrollBar = self.jScrollConsolePane.getVerticalScrollBar()
		verticalScrollBar.setValue( verticalScrollBar.getMaximum() )
		return
