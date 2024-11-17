from concurrent.futures import ThreadPoolExecutor
import zipfile
from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtCore import Qt
from threading import Lock
import os
import sys
import re
from PyQt5.Qsci import *
import re
import keyword
from PyQt5.QtGui import *
import subprocess

from CodeEditUi import Ui_MainWindow as CodeEditUi

__all__ = ["Worker","Zip","MakeCode"]

class Worker(QtCore.QThread):
    sinOut = QtCore.pyqtSignal(object)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui = parent
        self.workName = ""
    def emit(self,*args):
        self.sinOut.emit(args[0] if len(args) == 1 else args)
    def zipWork(self,*args):
        self.workName = "Zip-Dir"
        self.work = Zip(*args)
        self.work.worker = self
        self.sinOut.connect(self.work.showInfo)
    def packWork(self,*args):
        self.workName = "Pack-Exe"
        self.work = PackExe(*args)
        self.work.worker = self
        self.sinOut.connect(self.work.showInfo)
    def run(self):
        self.work.run()
        print(" ".join(["Worker",self.workName,"Finished."]))
        if self.workName == "Zip-Dir":
            self.ui.sinMakeCode.emit()

class Zip:
    def __init__(self,ui,zipFilePath,dir,max_workers = 4):
        self.ui = ui
        self.dir = dir
        self.max_workers = max_workers
        self.zipFilePath = zipFilePath
        self.pool = ThreadPoolExecutor(self.max_workers)
        self.zipLock = Lock()
        self.zip = zipfile.ZipFile(self.zipFilePath,"w",zipfile.ZIP_DEFLATED,compresslevel = 9)
    def zipFile(self,file):
        try:
            with self.zipLock:
                self.returnInfo("打包程序压缩包 - 压缩文件: %s" % os.path.split(file)[1],float("%.2f" % (self.zipDown / len(self.file_paths) * 100)))
                self.zip.write(file,file.replace(self.dir,""))
                self.zipDown += 1
        except:
            print(traceback.format_exc())
    def showInfo(self,tv):
        self.ui.runName.setText(" ".join(["正在执行:",self.ui.cutStr(str(tv[0]),self.ui.getInsertTextLen())]))
        self.ui.progressBar.setValue(tv[1])
    def returnInfo(self,text,value):
        self.worker.emit(text,value)
    def run(self):
        self.file_paths = []
    
        # 获取指定目录下的所有文件及其子目录的路径
        self.zipAllSize = []
        sizedPool = ThreadPoolExecutor(8)
        def getSize(p):
            self.zipAllSize.append(os.path.getsize(file_path))
        for root, _, files in os.walk(self.dir):
            for file in files:
                file_path = os.path.join(root,file)
                self.file_paths.append(file_path)
                self.returnInfo("打包程序压缩包 - 搜索文件",0)
                sizedPool.submit(getSize,file_path)
        sizedPool.shutdown()
        self.ui.zipAllSize = sum(self.zipAllSize)
        
        self.zipDown = 0
        list(self.pool.map(self.zipFile,self.file_paths))
        #self.zipFile("uninst.exe")
        
        self.zip.close()
        self.returnInfo("打包程序压缩包 - 完成",100)

class PackExe:
    def __init__(self,ui):
        self.ui = ui
    def showInfo(self,args):
        if args[1] == "insert":
            self.ui.textBrowser.insertPlainText(args[0])
        else:
            self.ui.textBrowser.append(args[0])
        self.ui.progressBar.setValue(args[2])
        self.ui.runName.setText(" ".join(["正在执行:",args[3]]))
        print(args[0],flush = True)
    def returnInfo(self,text,type = "append",value = 0,state = "制作安装包程序"):
        self.worker.emit(text,type,value,state)
    def run(self):
        self.returnInfo("==================== Starting Pack Exe ====================")
        popenCwd = self.ui.buildDir
        pyPath = ".".join([self.ui.exeName,"py"])
        uiPath = "ExeUi.py"
        pyinstallerPopenCommand = ["cmd","/c",
                                   "pyinstaller39",
                                   "-F",
                                   "-w",
                                   "-i","exeicon.ico",
                                   pyPath,
                                   "--add-data","winicon.ico;.",
                                   "--add-data","pkg.zip;.",
                                   "--add-data","ExeUi.py;.",
                                   "--add-data","exeicon.ico;."]
        if os.path.exists(os.path.join(self.ui.buildDir,"image.png")):
            print("Add image.png in Exe")
            pyinstallerPopenCommand.append("--add-data")
            pyinstallerPopenCommand.append("image.png;.")
        p = subprocess.Popen(pyinstallerPopenCommand,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.STDOUT,
                             cwd = popenCwd,
                             shell = True
                             )
        while True:
            line = p.stdout.readline()
            line = line.strip()
            if line:
                self.returnInfo(line.decode("utf-8"))
            if p.poll() != None and p.returncode != None:
                break
        self.returnInfo("","insert",value = 80,state = "制作安装包程序 - 复制安装包文件")
        exeFilePath = os.path.join(self.ui.buildDir,"dist",".".join([self.ui.exeName,"exe"]))
        if os.path.exists(exeFilePath):
            with open(exeFilePath,"rb") as r:
                with open(os.path.join(self.ui.distDir,"".join([self.ui.exeName,"安装程序",".exe"])),"wb") as w:
                    w.write(r.read())
        else:
            print("Exe file Not Found.")
        
        self.returnInfo(f"制作安装包程序结束 - Returncode:{p.returncode}",value = 100,state = ("制作安装包程序 - 发生错误, 请检查输出信息!" if p.returncode else "制作安装包程序 - 完成!"))
        self.ui.doEnable()

class highlight(QsciLexerPython):
    def __init__(self,parent):
        QsciLexerPython.__init__(self,parent)
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setPointSize(12)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setColor(QtGui.QColor(0, 0, 0))
        self.setPaper(QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QColor("#00FF00"), QsciLexerPython.ClassName)
        self.setColor(QtGui.QColor("#B0171F"), QsciLexerPython.Keyword)
        self.setColor(QtGui.QColor("#00FF00"), QsciLexerPython.Comment)
        self.setColor(QtGui.QColor("#FF00FF"), QsciLexerPython.Number)
        self.setColor(QtGui.QColor("#0000FF"), QsciLexerPython.DoubleQuotedString)
        self.setColor(QtGui.QColor("#0000FF"), QsciLexerPython.SingleQuotedString)
        self.setColor(QtGui.QColor("#288B22"), QsciLexerPython.TripleSingleQuotedString)
        self.setColor(QtGui.QColor("#288B22"), QsciLexerPython.TripleDoubleQuotedString)
        self.setColor(QtGui.QColor("#0000FF"), QsciLexerPython.FunctionMethodName)
        self.setColor(QtGui.QColor("#191970"), QsciLexerPython.Operator)
        self.setColor(QtGui.QColor("#000000"), QsciLexerPython.Identifier)
        self.setColor(QtGui.QColor("#00FF00"), QsciLexerPython.CommentBlock)
        self.setColor(QtGui.QColor("#0000FF"), QsciLexerPython.UnclosedString)
        self.setColor(QtGui.QColor("#FFFF00"), QsciLexerPython.HighlightedIdentifier)
        self.setColor(QtGui.QColor("#FF8000"), QsciLexerPython.Decorator)
        self.setFont(QtGui.QFont('Courier',12,weight=QtGui.QFont.Bold),5)
        self.setFont(QtGui.QFont('Courier',12,italic=True),QsciLexerPython.Comment)

class CodeEdit(QtWidgets.QMainWindow):
    def __init__(self,parent = None):
        super(CodeEdit,self).__init__(parent)
        self.setStatusTip("请检查代码是否有误或需要增删的地方。修改后关闭窗口以保存。")
        self.resize(800,600)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(9)
        self.setFont(font)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        font.setFixedPitch(True)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.setWindowTitle("检查代码")
        
        self.codeEdit=QsciScintilla()
        self.setCentralWidget(self.codeEdit)
        
        self.codeEdit.setFont(font)
        self.codeEdit.setMarginsFont(font)
        self.codeEdit.setUtf8(True)
        self.codeEdit.setMarginWidth(0,len(str(len(self.codeEdit.text().split('\n'))))*20)
        self.codeEdit.setMarginLineNumbers(0,True)
 
        self.codeEdit.setEdgeMode(QsciScintilla.EdgeLine)
        self.codeEdit.setEdgeColumn(80)
        self.codeEdit.setEdgeColor(QColor(0,0,0))
 
        self.codeEdit.setBraceMatching(QsciScintilla.StrictBraceMatch)
 
        self.codeEdit.setIndentationsUseTabs(True)
        self.codeEdit.setIndentationWidth(4)
        self.codeEdit.setTabIndents(True)
        self.codeEdit.setAutoIndent(True)
        self.codeEdit.setBackspaceUnindents(True)
        self.codeEdit.setTabWidth(4)
 
        self.codeEdit.setCaretLineVisible(True)
        self.codeEdit.setCaretLineBackgroundColor(QColor('#FFFFCD'))
 
        self.codeEdit.setIndentationGuides(True)
 
        self.codeEdit.setFolding(QsciScintilla.PlainFoldStyle)
        self.codeEdit.setMarginWidth(2,12)
 
        self.codeEdit.markerDefine(QsciScintilla.Minus, QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.codeEdit.markerDefine(QsciScintilla.Plus, QsciScintilla.SC_MARKNUM_FOLDER)
        self.codeEdit.markerDefine(QsciScintilla.Minus, QsciScintilla.SC_MARKNUM_FOLDEROPENMID)
        self.codeEdit.markerDefine(QsciScintilla.Plus, QsciScintilla.SC_MARKNUM_FOLDEREND)
 
        self.codeEdit.setMarkerBackgroundColor(QColor("#FFFFFF"), QsciScintilla.SC_MARKNUM_FOLDEREND)
        self.codeEdit.setMarkerForegroundColor(QColor("#272727"), QsciScintilla.SC_MARKNUM_FOLDEREND)
        self.codeEdit.setMarkerBackgroundColor(QColor("#FFFFFF"), QsciScintilla.SC_MARKNUM_FOLDEROPENMID)
        self.codeEdit.setMarkerForegroundColor(QColor("#272727"),QsciScintilla.SC_MARKNUM_FOLDEROPENMID)
        self.codeEdit.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.codeEdit.setAutoCompletionCaseSensitivity(True)
        self.codeEdit.setAutoCompletionReplaceWord(False)
        self.codeEdit.setAutoCompletionThreshold(1)
        self.codeEdit.setAutoCompletionUseSingle(QsciScintilla.AcusExplicit)
        self.lexer=highlight(self.codeEdit)
        self.codeEdit.setLexer(self.lexer)
        self.__api = QsciAPIs(self.lexer)
        autocompletions = keyword.kwlist + \
            [
            "abs","all","any","str","bool","callable","chr","classmethod","compile",
            "complex","delattr","dict","dir","divmod","enumerate","eval","exec","exit",
            "filter","float","frozenset","getattr","globals","hasattr","hex","id","int",
            "isinstance","issubclass","iter","len","list","locals","map","max","min",
            "object","oct","open","ord","pow","property", "range","repr","reversed",
            "round","set","setattr","slice","sorted","staticmethod","str","sum","super",
            "tuple","type","vars","zip","print"
            ]
        for ac in autocompletions:
            self.__api.add(ac)
        self.__api.prepare()
        self.codeEdit.autoCompleteFromAll()
        
        self.codeEdit.textChanged.connect(self.changed)
    def changed(self):
        self.mod=True
        self.codeEdit.setMarginWidth(0, len(str(len(self.codeEdit.text().split('\n')))) * 20)
    def setText(self,text):
        self.codeEdit.setText(text)
    def getText(self):
        return self.codeEdit.text()

class MakeCode:
    def __init__(self,ui,app):
        self.ui = ui
        self.app = app
    def makeCode(self):
        with open("Exe.py","r",encoding = "utf-8") as f:
            code = f.read()
        replText = [
                    (self.ui.winTitleLineEidt.text(),"__title__"),
                    (self.ui.exeNameLineEdit.text(),"__NAME__"),
                    (self.ui.exeVerLineEdit.text(),"__VER__"),
                    
                    (self.ui.uiText.ui_p1Text,"__HELLO__"),
                    (self.ui.uiText.ui_p2Per,"__PER__"),
                    (self.ui.uiText.ui_p5Text,"__END__"),
                    (self.ui.uiText.ui_p1Text,"__ui_p1Text__"),
                    (self.ui.uiText.ui_p1Title,"__ui_p1Title__"),
                    (self.ui.uiText.ui_p1LastBtn,"__ui_p1LastBtn__"),
                    (self.ui.uiText.ui_p1NextBtn,"__ui_p1NextBtn__"),
                    (self.ui.uiText.ui_p1EixtBtn,"__ui_p1EixtBtn__"),
                    (self.ui.uiText.ui_p2AcceptText,"__ui_p2AcceptText__"),
                    (self.ui.uiText.ui_p2Per,"__ui_p2Per__"),
                    (self.ui.uiText.ui_p2Title,"__ui_p2Title__"),
                    (self.ui.uiText.ui_p2Text,"__ui_p2Text__"),
                    (self.ui.uiText.ui_p2LaseBtn,"__ui_p2LastBtn__"),
                    (self.ui.uiText.ui_p2NextBtn,"__ui_p2NextBtn__"),
                    (self.ui.uiText.ui_p2ExitBtn,"__ui_p2EixtBtn__"),
                    (self.ui.uiText.ui_p3InstChangeBtn,"__ui_p3InstChangeBtn__"),
                    (self.ui.uiText.ui_p3InstToText,"__ui_p3InstToText__"),
                    (self.ui.uiText.ui_p3InstPath,"__ui_p3InstPath__"),
                    (self.ui.uiText.ui_p3LastBtn,"__ui_p3LastBtn__"),
                    (self.ui.uiText.ui_p3NextBtn,"__ui_p3NextBtn__"),
                    (self.ui.uiText.ui_p3ExitBtn,"__ui_p3EixtBtn__"),
                    (self.ui.uiText.ui_p3Title,"__ui_p3Title__"),
                    (self.ui.uiText.ui_p3Text,"__ui_p3Text__"),
                    (self.ui.uiText.ui_p4Statu,"__ui_p4Statu__"),
                    (self.ui.uiText.ui_p4Title,"__ui_p4Title__"),
                    (self.ui.uiText.ui_p4ExitBtn,"__ui_p4EixtBtn__"),
                    (self.ui.uiText.ui_p5Text,"__ui_p5Text__"),
                    (self.ui.uiText.ui_p5Title,"__ui_p5Title__"),
                    (self.ui.uiText.ui_p5Finish,"__ui_p5Finish__"),
                    (self.ui.uiText.ui_p3Addsm,"__ui_p3Addsm__"),
                    (self.ui.uiText.ui_p3Adddl,"__ui_p3Adddl__"),
                    (self.ui.uiText.ui_p3Rnas,"__ui_p3Rnas__"),
                    (self.ui.uiText.ui_p3Rnname,"__ui_p3Rnname__"),
                    (self.ui.uiText.ui_p3Rnto,"__ui_p3Rnto__"),
                    (self.ui.uiText.ui_p4Text,"__ui_p4Text__"),
                    
                    (self.ui.publisher.text(),"__publisher__"),
                    (self.ui.helpLink.text(),"__helpLink__"),
                    (str(self.ui.helpTel.text()),"__helpTel__"),
                    (str(self.ui.zipAllSize),"__zipAllSize__"),
                    ]
        for new,old in replText:
            code = code.replace(old,"\n".join([new,""]))
            print(old,"->",new)
        
        self.codeEdit = CodeEdit(self.ui)
        self.codeEdit.setText(code)
        self.codeEdit.closeEvent = self.closeCodeEdit
        self.codeEdit.show()
        print("Showed CodeEdit.")
    def closeCodeEdit(self,event):
        self.writeCode(self.codeEdit.getText())
        self.codeEdit.close()
        self.ui.sinPackExe.emit()
    def writeCode(self,code):
        print("Saved Code.")
        with open(os.path.join(self.ui.buildDir,".".join([self.ui.exeName,"py"])),"w",encoding = "utf-8") as f:
            f.write(code)
'''
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    codeEdit = CodeEdit()
    codeEdit.show()
    app.exec_()'''