from PyQt5 import QtGui,QtCore,QtWidgets
import sys,os
from PyQt5.QtCore import Qt
from threading import Lock,Event
import gzip
import shutil
import bz2
from functools import lru_cache
import time

from packager import *
from installPackagerUi import Ui_MainWindow as installPackagerUi
from errUi import Ui_MainWindow as errUi
import subprocess

class ErrUi(errUi,QtWidgets.QMainWindow):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowTitleHint | Qt.Window)
        self.setMaximumSize(self.screen().availableGeometry().width(),self.screen().availableGeometry().height() - 40)
    def setText(self,title,message):
        self.setWindowTitle(title)
        self.message.setText(message)
        self.adjustSize()
    def exec_(self,title,message):
        self.show()
        self.setText(title,message)
        app.exec_()
def showErr(parent = None,title = "错误",message = ""):
    errUi = ErrUi(parent)
    errUi.exec_(title,message)


# 解决PyQt5不显示类中函数调用无法获取报错的问题
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = except_hook

app = QtWidgets.QApplication([])

class Ui(installPackagerUi,QtWidgets.QMainWindow):
    sinMakeCode = QtCore.pyqtSignal()
    sinPackExe = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.sinMakeCode.connect(self.makeCode)
        self.sinPackExe.connect(self.packExe)
        self.exeIconCheckBox.setChecked(True)
    def updUi(self):
        def _translate(name,text):
            vText = text.replace("{hello}",self.helloTextEdit.toPlainText()).replace("{per}",self.permissionTextEdit.toPlainText()).replace("{end}",self.endTextEdit.toPlainText()).replace("{name}",self.exeNameLineEdit.text()).replace("{ver}",self.exeVerLineEdit.text())
            if text != vText:print("Tr:",text,"->",vText,";Name:",self.exeNameLineEdit.text(),";Ver:",self.exeVerLineEdit.text())
            return QtCore.QCoreApplication.translate(name,vText)
        self.ui_p1Text.setPlainText(_translate("MainWindow",self.ui_p1Text.toPlainText()))
        self.ui_p1Title.setText(_translate("MainWindow",self.ui_p1Title.text()))
        self.ui_p1LastBtn.setText(_translate("MainWindow",self.ui_p1LastBtn.text()))
        self.ui_p1NextBtn.setText(_translate("MainWindow",self.ui_p1NextBtn.text()))
        self.ui_p1EixtBtn.setText(_translate("MainWindow",self.ui_p1EixtBtn.text()))
        self.ui_p2AcceptText.setText(_translate("MainWindow",self.ui_p2AcceptText.text()))
        self.ui_p2Per.setPlainText(_translate("MainWindow", self.ui_p2Per.toPlainText()))
        self.ui_p2Title.setText(_translate("MainWindow",self.ui_p2Title.text()))
        self.ui_p2Text.setText(_translate("MainWindow",self.ui_p2Text.text()))
        self.ui_p2LaseBtn.setText(_translate("MainWindow",self.ui_p2LaseBtn.text()))
        self.ui_p2NextBtn.setText(_translate("MainWindow",self.ui_p2NextBtn.text()))
        self.ui_p2ExitBtn.setText(_translate("MainWindow",self.ui_p2ExitBtn.text()))
        self.ui_p3InstChangeBtn.setText(_translate("MainWindow",self.ui_p3InstChangeBtn.text()))
        self.ui_p3InstToText.setText(_translate("MainWindow",self.ui_p3InstToText.text()))
        self.ui_p3InstPath.setText(_translate("MainWindow",self.ui_p3InstPath.text()))
        self.ui_p3LastBtn.setText(_translate("MainWindow",self.ui_p3LastBtn.text()))
        self.ui_p3NextBtn.setText(_translate("MainWindow",self.ui_p3NextBtn.text()))
        self.ui_p3ExitBtn.setText(_translate("MainWindow",self.ui_p3ExitBtn.text()))
        self.ui_p3Title.setText(_translate("MainWindow",self.ui_p3Title.text()))
        self.ui_p3Text.setText(_translate("MainWindow",self.ui_p3Text.text()))
        self.ui_p4Text.setText(_translate("MainWindow",self.ui_p4Text.text()))
        self.ui_p4Statu.setText(_translate("MainWindow",self.ui_p4Statu.text()))
        self.ui_p4Title.setText(_translate("MainWindow",self.ui_p4Title.text()))
        self.ui_p4ExitBtn.setText(_translate("MainWindow",self.ui_p4ExitBtn.text()))
        self.ui_p5Text.setPlainText(_translate("MainWindow",self.ui_p5Text.toPlainText()))
        self.ui_p5Title.setText(_translate("MainWindow",self.ui_p5Title.text()))
        self.ui_p5Last.setText(_translate("MainWindow",self.ui_p5Last.text()))
        self.ui_p5Finish.setText(_translate("MainWindow",self.ui_p5Finish.text()))
        self.ui_p5Exit.setText(_translate("MainWindow",self.ui_p5Exit.text()))
    def selectFile(self,title,filters):
        if filters == "Image":
            fileters = "All Supported Picture Files(*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.pcx *.ico *.cur *.ani);;JPEG (*.jpg *.jpeg);;PNG (*.png);;GIF (*.gif);;BMP (*.bmp);;TIFF (*.tiff *.tif);;PCX (*.pcx);;ICO(*.ico);;CUR (*.cur);;ANI (*.ani);;All Files (*)"
        file,_ = QtWidgets.QFileDialog.getOpenFileName(self,title,"",fileters,)
        return file
    def isQtCanOpenImage(self,file,raiseErr = True):
        try:
            QtGui.QPixmap(file)
            return True
        except Exception as err:
            if raiseErr:
                QtWidgets.QMessageBox.critical(self,"错误",f"图片类型不支持或无法读取图片，请重新选择图片！\n详细信息:\n{err}")
            return False
    def selectImage(self):
        print("SelectImage...")
        file = self.selectFile("请选择图片文件","Image")
        if file:
            if self.isQtCanOpenImage(file):
                print("SelectImage:",file)
                self.ui_imgPath.setText(f"图片路径：{file}")
        print("SelectImage-Down")
    def selectWinIcon(self):
        print("SelectWinIcon...")
        file = self.selectFile("请选择图标文件","Image")
        if file:
            if self.isQtCanOpenImage(file):
                print("SelectWinIcon:",file)
                self.winIconLineEdit.setText(file)
        print("SelectWinIcon-Down")
    def selectExeIcon(self):
        print("SelectExeIcon...")
        file = self.selectFile("请选择图标文件","Image")
        if file:
            if self.isQtCanOpenImage(file):
                print("SelectExeIcon:",file)
                self.exeIconLineEdit.setText(file)
        print("SelectExeIcon-Down")
    def selectExeDir(self):
        print("SelectExeDir...")
        dir = QtWidgets.QFileDialog.getExistingDirectory(self,"请选择程序目录文件夹","")
        if dir:
            print("SelectExeDir:",dir)
            self.exeDirLineEdit.setText(dir)
    def updateIconChecked(self):
        if self.exeIconCheckBox.isChecked():
            self.exeIconLineEdit.setEnabled(True)
            self.exeIconButton.setEnabled(True)
            self.winIconToexeIconCheckBox.setEnabled(True)
        else:
            self.exeIconLineEdit.setEnabled(False)
            self.exeIconButton.setEnabled(False)
            self.winIconToexeIconCheckBox.setEnabled(False)
        if self.winIconToexeIconCheckBox.isChecked():
            self.exeIconLineEdit.setEnabled(False)
            self.exeIconButton.setEnabled(False)
        else:
            if self.exeIconCheckBox.isChecked():
                self.exeIconLineEdit.setEnabled(True)
                self.exeIconButton.setEnabled(True)
    def outputExe(self):
        self.output_isErr = False
        def raiseErr(errmessage = "发生错误!"):
            showErr(self,message = errmessage)
            self.output_isErr = True
            
        print("OutputExe...")
        self.splitter.setEnabled(False)
        self.exeIconCheckBox.setEnabled(False)
        self.exeIconLineEdit.setEnabled(False)
        self.exeIconButton.setEnabled(False)
        self.winIconToexeIconCheckBox.setEnabled(False)
        self.exeDirLineEdit.setEnabled(False)
        self.exeDirButton.setEnabled(False)
        self.outputButton.setEnabled(False)
        
        exeName = self.exeNameLineEdit.text()
        exeVer = self.exeVerLineEdit.text()
        exeDir = self.exeDirLineEdit.text()
        self.exeName = f"{exeName}({exeVer})"
        self.buildDir = f"./build/{self.exeName}"
        self.distDir = f"./dist/{self.exeName}"
        
        if not os.path.exists(exeDir):
            raiseErr(f"输入的程序路径不存在！\n路径: {exeDir}")
        if not os.path.exists(self.buildDir):
            try:
                os.makedirs(self.buildDir)
            except PermissionError as err:
                raiseErr(f"尝试创建build文件夹失败!\n{err}")
            except Exception as err:
                raiseErr(f"尝试创建build文件夹失败!\n[未知错误]\n详细信息:\n{err}")
        if not os.path.exists(self.distDir):
            try:
                os.makedirs(self.distDir)
            except PermissionError as err:
                raiseErr(f"尝试创建dist文件夹失败!\n{err}")
            except Exception as err:
                raiseErr(f"尝试创建build文件夹失败!\n[未知错误]\n详细信息:\n{err}")
        
        if not os.path.exists(self.winIconLineEdit.text()):
            raiseErr(f"输入的窗口图标文件不存在!\n路径: {self.winIconLineEdit.text()}")
        else:
            if not self.winIconLineEdit.text().endswith(".ico"):
                raiseErr(f"窗口图标文件格式错误!\n路径: {self.winIconLineEdit.text()}")
            else:
                try:
                    shutil.copyfile(self.winIconLineEdit.text(),os.path.join(self.buildDir,"winicon.ico"))
                except Exception as err:
                    raiseErr(f"复制窗口图标文件时出错!\n详细信息:\n{err}")
        
        if not os.path.exists(self.exeIconLineEdit.text()):
            raiseErr(f"输入的程序图标文件不存在!\n路径: {self.winIconLineEdit.text()}")
        else:
            if not self.winIconLineEdit.text().endswith(".ico"):
                raiseErr(f"程序图标文件格式错误!\n路径: {self.winIconLineEdit.text()}")
            else:
                try:
                    shutil.copyfile(self.exeIconLineEdit.text(),os.path.join(self.buildDir,"exeicon.ico"))
                except Exception as err:
                    raiseErr(f"复制程序图标文件时出错!\n详细信息:\n{err}")
        
        try:
            shutil.copyfile("./ExeUi.py",os.path.join(self.buildDir,"ExeUi.py"))
        except Exception as err:
            raiseErr(f"复制窗口Ui文件时出错!\n详细信息:\n{err}")
        
        if not self.output_isErr:
            self.updUi()
            worker = Worker(self)
            worker.zipWork(self,os.path.join(self.buildDir,"pkg.zip"),exeDir,2)
            worker.start()
            print("Zipped-Dir Started.")
        else:
            self.doEnable()
            print("OutputExe - Error.")
        
        delattr(self,"output_isErr")
    def doEnable(self):
        self.splitter.setEnabled(True)
        self.exeIconCheckBox.setEnabled(True)
        self.exeIconLineEdit.setEnabled(True)
        self.exeIconButton.setEnabled(True)
        self.winIconToexeIconCheckBox.setEnabled(True)
        self.exeDirLineEdit.setEnabled(True)
        self.exeDirButton.setEnabled(True)
        self.outputButton.setEnabled(True)
    def makeCode(self):
        mc = MakeCode(ui,app)
        mc.makeCode()
    def packExe(self):
        worker = Worker(self)
        worker.packWork(self)
        worker.start()
        print("Pack-Exe Started.")
        
    def getInsertTextLen(self):
        l = self.runName.width() // 10 - 10
        if l < 3:
            l = 3
        return l
    @lru_cache
    def cutStr(self,text,max_length):
        if max_length < 3:
            raise ValueError("\"max_length\" cannot be less than 3")
        if len(text) <= max_length:
            return text
        # 计算省略号插入的位置
        insert_pos = max_length // 2
        # 分割字符串并添加省略号
        part1 = text[:insert_pos]
        part2 = text[-(max_length - insert_pos - 1):]
        return part1 + '...' + part2
    
    def closeEvent(self,event):
        self.setVisible(False)
        event.accept()
        app.exit()
        os._exit(1)
        

ui = Ui()
ui.show()
app.exec_()
