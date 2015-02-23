#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Here we provide the necessary imports.
# The basic GUI widgets are located in QtGui module. 
import sys
import os.path
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import httplib2 as http
import json
import urllib
#from base64 import b64encode
import base64

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

class Form(QMainWindow):
	def __init__(self):
		super(Form, self).__init__(None)
		
		#Main Layout
		mainLayout = QVBoxLayout()

		#Method content
		methodGroup = QGroupBox()
		methodGroup.setTitle("Method")

		methodDrop = QComboBox()
		methodDrop.setObjectName("methodDrop")
		methodDrop.addItem("GET")
		methodDrop.addItem("POST")
		methodDrop.addItem("PUT")
		methodDrop.addItem("DELETE")
		urlDrop = QComboBox()
		urlDrop.setObjectName("urlDrop")
		urlDrop.setProperty("editable", 1)
		urlDrop.setProperty("minimumWidth", 450)
		sendButton = QPushButton()
		sendButton.setObjectName("sendButton")
		sendButton.setText("Send")
		
		
		with open("history") as history:
			d = json.load(history)
			history.close()
			for url in d['history']:
				urlDrop.addItem(url)


		methodLayout = QHBoxLayout()
		methodLayout.addWidget(methodDrop)
		methodLayout.addWidget(urlDrop)
		methodLayout.addWidget(sendButton)
		methodGroup.setLayout(methodLayout)

		#Header content
		headerGroup = QGroupBox()
		headerGroup.setTitle("Header")

		headerText = QTextEdit()
		headerText.setObjectName("headerText")
		
		authGroup = QGroupBox()
		authGroup.setTitle("Basic Authentication")
		
		authLayout = QVBoxLayout()
		userInput = QLineEdit()
		userInput.setProperty("placeholderText", "Username")
		userInput.setObjectName("userInput")
		passInput = QLineEdit()
		passInput.setEchoMode(QLineEdit.Password);
		passInput.setProperty("placeholderText", "Password")
		passInput.setObjectName("passInput")
		addAuthButton = QPushButton()
		addAuthButton.setText("Add")
		
		authLayout.addWidget(userInput)
		authLayout.addWidget(passInput)
		authLayout.addWidget(addAuthButton)
		authGroup.setLayout(authLayout)
		
		contentLayout = QVBoxLayout()
		contentGroup = QGroupBox()
		contentGroup.setTitle("Content Type")
		
		contentDrop = QComboBox()
		contentDrop.setProperty("minimumWidth", 200)
		contentDrop.setObjectName("contentDrop")
		contentDrop.addItem("application/json")
		contentDrop.addItem("application/xml")
		addContentButton = QPushButton()
		addContentButton.setText("Add")
		
		contentLayout.addWidget(contentDrop)
		contentLayout.addWidget(addContentButton)
		contentGroup.setLayout(contentLayout)

		headerLayout = QHBoxLayout()
		headerLayout.addWidget(headerText)
		headerLayout.addWidget(authGroup)
		headerLayout.addWidget(contentGroup)

		headerGroup.setLayout(headerLayout)

		#Body content
		bodyGroup = QGroupBox()
		bodyGroup.setTitle("Body")

		bodyText = QTextEdit()
		bodyText.setObjectName("bodyText")
		bodyText.setProperty("minimumHeight", 150)

		bodyLayout = QHBoxLayout()
		bodyLayout.addWidget(bodyText)

		bodyGroup.setLayout(bodyLayout)

		#Response content
		responseTab = QTabWidget()
		responseTab.setProperty("minimumHeight", 200)		
		responseHeaderText = QListWidget()
		responseHeaderText.setObjectName("responseHeaderText")
		
		responseBodyText = QTextBrowser()
		responseBodyText.setObjectName("responseBodyText")
		responseJSONText = QTextBrowser()
		responseJSONText.setObjectName("responseJSONText")
		responseTab.addTab(responseHeaderText, "Response Header")
		responseTab.addTab(responseBodyText, "Response Body")
		responseTab.addTab(responseJSONText, "Formatted Response")

		mainLayout.addWidget(methodGroup)
		mainLayout.addWidget(headerGroup)
		mainLayout.addWidget(bodyGroup)
		mainLayout.addWidget(responseTab)
		
		mainWidget = QWidget()
		mainWidget.setLayout(mainLayout)
		self.setCentralWidget(mainWidget)
		
		self.connect(sendButton, SIGNAL("clicked()"), self.send)
		self.connect(addAuthButton, SIGNAL("clicked()"), self.addAuth)
		self.connect(addContentButton, SIGNAL("clicked()"), self.addContent)
		
		self.setWindowTitle("REST Client")
		statusLabel = QLabel()
		statusLabel.setText("Ready")
		statusLabel.setObjectName("statusLabel")
		authorLabel = QLabel()
		authorLabel.setText("Cristi Paraschiv <cristianv.paraschiv@gmail.com>")
		frame = QFrame()
		frame.setFrameStyle(QFrame.VLine)
		frame2 = QFrame()
		frame2.setFrameStyle(QFrame.VLine)
		dateLabel = QLabel()
		dateLabel.setText("2015")
		self.statusBar().addWidget(statusLabel)
		self.statusBar().addWidget(frame)
		self.statusBar().addWidget(authorLabel)
		self.statusBar().addWidget(frame2)
		self.statusBar().addWidget(dateLabel)
		self.setProperty("maximumWidth", 600)
		
	def send(self):
		self.findChild(QLabel, "statusLabel").setText("Busy")
		self.findChild(QTextBrowser, "responseBodyText").setText("")
		self.findChild(QListWidget, "responseHeaderText").clear()
		header = {}
		headers = self.findChild(QTextEdit, "headerText").toPlainText()
		headers.replace(" ", "")
		headers.replace("'", "")
		headers.replace("Basic", "Basic ")
		if headers:
			elem = headers.split('\n')
			for e in elem:
				key = e.split(':')[0]
				value = e.split(':')[1]
				key = key.toLocal8Bit().data()
				value = value.toLocal8Bit().data()
				header[key] = value
		uri = self.findChild(QComboBox, "urlDrop").currentText().toLocal8Bit().data()
		with open("history", "r+") as history:
			d = json.load(history)
			urls = d['history']
			if not uri in urls:
				urls.append(uri)
				self.findChild(QComboBox, "urlDrop").addItem(uri)
				history.seek(0)
				json.dump(d, history)
			history.close()
			
		target = urlparse(uri)
		method = self.findChild(QComboBox, "methodDrop").currentText()
		body = self.findChild(QTextEdit, "bodyText").toPlainText().toLocal8Bit().data()
		h = http.Http()
		response, content = h.request(
			target.geturl(),
			method,
			body,
			header
		)
		data = content
		dump = content
		for key in response:
			self.findChild(QListWidget, "responseHeaderText").addItem(key.title() + ': ' + response[key])
		if (self.isJson(content)):
			data = json.loads(content)
			dump = json.dumps(data, indent=4)
		self.findChild(QTextBrowser, "responseBodyText").insertPlainText(dump)
		self.findChild(QTextBrowser, "responseJSONText").setText('<pre>' + dump + '</pre>')
		self.findChild(QLabel, "statusLabel").setText("Ready")


	def addAuth(self):
		user = self.findChild(QLineEdit, "userInput").text().toLocal8Bit().data()
		passw = self.findChild(QLineEdit, "passInput").text().toLocal8Bit().data()
		auth = base64.encodestring('%s:%s' % (user, passw)).replace('\n', '')
		self.findChild(QTextEdit, "headerText").append("'Authorization': 'Basic " + auth + "'")

	def addContent(self):
		content = self.findChild(QComboBox, "contentDrop").currentText()
		self.findChild(QTextEdit, "headerText").append("'Content-Type': '" + content + "'")
		
	def isJson(self, myjson):
		try:
			json_object = json.loads(myjson)
		except ValueError:
			return False
		return True

app = QApplication(sys.argv)
if (not os.path.exists("history")):
	with open("history", "w+") as history:
		json.dump({'history':[]}, history)
		history.close()
form = Form()
form.show()
app.exec_()
