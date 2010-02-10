import sys
from PyQt4 import QtGui, QtCore

class AddDownload(QtGui.QDialog):
  def __init__(self, parent):
    super(AddDownload, self).__init__(parent)
    self.setWindowTitle('New Download')
    self.setModal(True)
    self.setFixedSize(400, 180)
    self.initGui()
    self.initActions()
    
    self.name = None
    self.url = None
    self.threads = 1
  
  def initGui(self):
    
    vbox = QtGui.QVBoxLayout()
    
    file_label = QtGui.QLabel('Name:')
    self.file_input = QtGui.QLineEdit()
    file_label.setBuddy(self.file_input)
    
    url_label = QtGui.QLabel('URL:')
    self.url_input = QtGui.QLineEdit()
    url_label.setBuddy(self.url_input)
    
    thread_label = QtGui.QLabel('Threads:')
    self.thread_input = QtGui.QSpinBox()
    self.thread_input.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter) 
    self.thread_input.setRange(1, 100)
    thread_label.setBuddy(self.thread_input)

    gl = QtGui.QGridLayout()
    gl.addWidget(file_label, 0, 0)
    gl.addWidget(self.file_input, 0, 1)
    gl.addWidget(url_label, 1, 0)
    gl.addWidget(self.url_input, 1, 1)
    gl.addWidget(thread_label, 2, 0)
    
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(self.thread_input)
    hbox.addStretch()
    gl.addLayout(hbox, 2, 1)
    
    hbox = QtGui.QHBoxLayout()
    self.ok_button = QtGui.QPushButton("&Ok")
    self.cancel_button = QtGui.QPushButton("&Cancel")
    hbox.addStretch()
    hbox.addWidget(self.ok_button)
    hbox.addWidget(self.cancel_button)
    
    vbox.addLayout(gl)
    vbox.addLayout(hbox)
    
    self.setLayout(vbox)
    
  def initActions(self):
    self.connect(self.ok_button, QtCore.SIGNAL("clicked()"), self.checkInput)
    self.connect(self.cancel_button, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))
    
  def checkInput(self):
    #TODO: validate and sanitize data
    self.name = str(self.file_input.text())
    self.url = str(self.url_input.text())
    self.threads = int(self.thread_input.value())
    self.accept()
    
if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)
  add_download = AddDownload(None)
  if add_download.exec_():
    print add_download.name
    print add_download.url
    print add_download.threads
  sys.exit(app.exec_())