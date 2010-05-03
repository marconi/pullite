import sys, os
from PyQt4 import QtGui, QtCore
from dialogs.add_download import AddDownload

from components.file import File
from components.file_fixer import FileFixer
from components.settings import Settings

class Pullite(QtGui.QMainWindow):
  def __init__(self, parent=None, title='Pullite - Download manager, the python way'):
    super(Pullite, self).__init__(parent)

    self.setWindowTitle(title)
    self.resize(850, 650)
    
    self.initGui()
    self.initActions()
    self.initResources()
    self.initFileFixer()
    
  def initGui(self):
    
    #initialize icons
    self.icons = {"add":"images/add.png",
                  "remove":"images/remove.png",
                  "stop":"images/stop.png",
                  "resume":"images/resume.png",
                  "incomplete":"images/incomplete.png",
                  "complete":"images/complete.png",
                  "onprogress":"images/onprogress.png"}
                  
    #central widget
    central_widget = QtGui.QWidget()
    
    #categories
    self.categories = QtGui.QComboBox()
    self.categories.addItems(['All', 'Applications', 'Movies', 'Music', 'Picture', 'Others'])
    
    #main splitter
    main_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
    splitter_layout = QtGui.QHBoxLayout()
    splitter_layout.addWidget(main_splitter)
    
    #top pane
    top_tabs = QtGui.QTabWidget()
    running_tab = QtGui.QWidget()
    paused_tab = QtGui.QWidget()
    completed_tab = QtGui.QWidget()
    
    #downloads table
    self.downloads_table = QtGui.QTableWidget(0, 6)
    self.downloads_table.setAlternatingRowColors(True) 
    self.downloads_table.setHorizontalHeaderLabels(['', 'Name', 'Progress', 'Size', 'Completed', 'Created'])
    self.downloads_table.setColumnWidth(0, 30)
    self.downloads_table.setColumnWidth(1, 300)
    self.downloads_table.horizontalHeader().setStretchLastSection(True)
    self.downloads_table.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
    self.downloads_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    #self.downloads_table.setItemDelegateForColumn(2, DownloadDelegate(self))

    top_tabs.addTab(self.downloads_table, '&All')
    top_tabs.addTab(running_tab, '&Running')
    top_tabs.addTab(paused_tab, '&Paused')
    top_tabs.addTab(completed_tab, '&Completed')
    main_splitter.addWidget(top_tabs)
    
    #bottom pane
    self.download_details = QtGui.QTableWidget(0, 3)
    self.download_details.setHorizontalHeaderLabels(['Threads', 'Progress', 'Status'])
    self.download_details.setColumnWidth(0, 150)
    self.download_details.setColumnWidth(1, 300)
    self.download_details.horizontalHeader().setStretchLastSection(True)
    self.download_details.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    self.download_details.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    main_splitter.addWidget(self.download_details)
    
    central_widget.setLayout(splitter_layout)
    self.setCentralWidget(central_widget)
    
    #toolbar
    self.toolbar = self.addToolBar("Controls")
    self.toolbar.setMovable(False)
    self.toolbar.setStyleSheet("padding: 2;")
    
    self.add = QtGui.QAction(QtGui.QIcon(self.icons["add"]), "Add", self)
    self.add.setShortcut("Ctrl+A")
    self.remove = QtGui.QAction(QtGui.QIcon(self.icons["remove"]), "Remove", self)
    self.remove.setShortcut("Ctrl+R")
    self.stop = QtGui.QAction(QtGui.QIcon(self.icons["stop"]), "Stop", self)
    self.stop.setShortcut("Ctrl+S")
    self.resume = QtGui.QAction(QtGui.QIcon(self.icons["resume"]), "Resume", self)
    self.resume.setShortcut("Ctrl+S")
    
    self.toolbar.addAction(self.add)
    self.toolbar.addAction(self.remove)
    self.toolbar.addAction(self.stop)
    self.toolbar.addAction(self.resume)
  
  def initActions(self):
    self.connect(self.add, QtCore.SIGNAL("triggered()"), self.addDownloadAction)
  
  def initResources(self):
    if not os.path.isdir(Settings.download_path):
      os.mkdir(Settings.download_path)
  
  def initFileFixer(self):
      fixer = FileFixer()
      fixer.start()
  
  def addDownloadAction(self):
    add_download = AddDownload(None)
    if add_download.exec_():
      
      row = self.downloads_table.rowCount()
      self.downloads_table.insertRow(row)
      
      file = File(name=add_download.name, remote_file=add_download.url,
                  thread_count=add_download.threads, new=True)
      
      iconItem = QtGui.QTableWidgetItem(QtGui.QIcon(self.icons["onprogress"]), '')
      iconItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
      
      nameItem = QtGui.QTableWidgetItem(add_download.name)
      nameItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
      
      download_pb = QtGui.QProgressBar(self)
      download_pb.setRange(0, 99)
      download_pb.setValue(40)
      
      sizeItem = QtGui.QTableWidgetItem(File.getHumanSize(file.file_size))
      sizeItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
      sizeItem.setTextAlignment(QtCore.Qt.AlignRight)
      
      completedItem = QtGui.QTableWidgetItem('40%')
      completedItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
      completedItem.setTextAlignment(QtCore.Qt.AlignRight)
      
      createdItem = QtGui.QTableWidgetItem(file.created)
      createdItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
      createdItem.setTextAlignment(QtCore.Qt.AlignRight)
      
      self.downloads_table.setItem(row, 0, iconItem)
      self.downloads_table.setItem(row, 1, nameItem)
      self.downloads_table.setCellWidget(row, 2, download_pb)
      self.downloads_table.setItem(row, 3, sizeItem)
      self.downloads_table.setItem(row, 4, completedItem)
      self.downloads_table.setItem(row, 5, createdItem)
      
      self.downloads_table.setRowHeight(row, 20)
      
      #start download
      file.download()

if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)
  pullite = Pullite(None)
  pullite.show()
  sys.exit(app.exec_())