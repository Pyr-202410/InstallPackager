from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtCore import Qt
import sys,io
import os,time
import zipfile
import winshell
import pythoncom
import winreg
from ExeUi import Ui_MainWindow as ExeUi
app = QtWidgets.QApplication([])

stdFile = open("Inst.log","a",encoding = "utf-8")

class Stdout(io.TextIOBase):
    def __init__(self):
        self.content = ""
        self._type = "Info"
    def write(self,text = ""):
        self.content += text
        if text != "\n" and text:
            stdFile.write("".join([f"[{self._type}] ",text.strip(),"\n"]))
    def flush(self):
        self.content = ""
class Stderr(Stdout):
    def __init__(self):
        self.content = ""
        self._type = "Err"
sys.stdout = Stdout()
sys.stderr = Stderr()

# 解决PyQt5不显示类中函数调用无法获取报错的问题
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = except_hook
#获取压缩包路径
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

NAME = """__NAME__"""
VER = """__VER__"""
HELLO = """__HELLO__"""
PER = """__PER__"""
END = """__END__"""

def create_shortcut(target_path,
                    shortcut_path,
                    icon_path = None,
                    description = "",
                    startIn = "",
                    arguments = ""):
    try:
        pythoncom.CoInitialize()
        with winshell.shortcut(shortcut_path) as lnk:
            lnk.path = target_path
            lnk.description = description
            lnk.arguments = arguments
            lnk.icon_location = icon_path or (target_path,0)
            lnk.working_directory = startIn
        pythoncom.CoUninitialize()
    except:pass

def register_program(program_name, program_path):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_WRITE)
    new_key = winreg.CreateKey(key, program_name)
    winreg.SetValueEx(new_key, "DisplayName", 0, winreg.REG_SZ, program_name)
    winreg.SetValueEx(new_key, "UninstallString", 0, winreg.REG_SZ, program_path)
    winreg.CloseKey(new_key)
    winreg.CloseKey(key)

class UiText(ExeUi):
    def reTextUi(self):
        winicon = resource_path("./winicon.ico")
        self.setWindowIcon(QtGui.QIcon(winicon))
        self.ui_p2Icon.setPixmap(QtGui.QPixmap(winicon))
        self.ui_p3Icon.setPixmap(QtGui.QPixmap(winicon))
        self.ui_p4Icon.setPixmap(QtGui.QPixmap(winicon))
        def _translate(text):
            return text.replace("{hello}",HELLO).replace("{per}",PER).replace("{end}",END).replace("{name}",NAME).replace("{ver}",VER)
        self.setWindowTitle(r"""__title__""")
        self.ui_p1Text.setPlainText(_translate(r"""__ui_p1Text__"""))
        self.ui_p1Title.setText(_translate(r"""__ui_p1Title__"""))
        self.ui_p1LastBtn.setText(_translate(r"""__ui_p1LastBtn__"""))
        self.ui_p1NextBtn.setText(_translate(r"""__ui_p1NextBtn__"""))
        self.ui_p1EixtBtn.setText(_translate(r"""__ui_p1EixtBtn__"""))
        self.ui_p2Accept.setText(_translate(r"""__ui_p2AcceptText__""")) #
        self.ui_p2Per.setPlainText(_translate(r"""__ui_p2Per__"""))
        self.ui_p2Title.setText(_translate(r"""__ui_p2Title__"""))
        self.ui_p2Text.setText(_translate(r"""__ui_p2Text__"""))
        self.ui_p2LaseBtn.setText(_translate(r"""__ui_p2LastBtn__"""))
        self.ui_p2NextBtn.setText(_translate(r"""__ui_p2NextBtn__"""))
        self.ui_p2ExitBtn.setText(_translate(r"""__ui_p2EixtBtn__"""))
        self.ui_p3InstChangeBtn.setText(_translate(r"""__ui_p3InstChangeBtn__"""))
        self.ui_p3InstToText.setText(_translate(r"""__ui_p3InstToText__"""))
        self.ui_p3InstPath.setText(_translate(r"""__ui_p3InstPath__"""))
        self.ui_p3LastBtn.setText(_translate(r"""__ui_p3LastBtn__"""))
        self.ui_p3NextBtn.setText(_translate(r"""__ui_p3NextBtn__"""))
        self.ui_p3ExitBtn.setText(_translate(r"""__ui_p3EixtBtn__"""))
        self.ui_p3Title.setText(_translate(r"""__ui_p3Title__"""))
        self.ui_p3Text.setText(_translate(r"""__ui_p3Text__"""))
        self.ui_p4Text.setText(_translate(r"""__ui_p4Text__"""))
        self.ui_p4Statu.setText(_translate(r"""__ui_p4Statu__"""))
        self.ui_p4Title.setText(_translate(r"""__ui_p4Title__"""))
        self.ui_p4ExitBtn.setText(_translate(r"""__ui_p4EixtBtn__"""))
        self.ui_p5Text.setPlainText(_translate(r"""__ui_p5Text__"""))
        self.ui_p5Title.setText(_translate(r"""__ui_p5Title__"""))
        self.ui_p5Finish.setText(_translate(r"""__ui_p5Finish__"""))
        # 后加
        self.ui_p3Addsm.setText(_translate(r"""__ui_p3Addsm__"""))
        self.ui_p3Adddl.setText(_translate(r"""__ui_p3Adddl__"""))
        self.ui_p3Rnas.setText(_translate(r"""__ui_p3Rnas__"""))
        self.ui_p3Rnname.setText(_translate(r"""__ui_p3Rnname__"""))
        self.ui_p3Rnto.setText(_translate(r"""__ui_p3Rnto__"""))
        self.ui_p4Text.setText(_translate(r"""__ui_p4Text__"""))
class Ui(UiText,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.reTextUi()
        self.closeEvent = self.close
    def acceptPer(self):
        if self.ui_p2Accept.isChecked():
            self.ui_p2NextBtn.setEnabled(True)
        else:
            self.ui_p2NextBtn.setEnabled(False)
    def nextPage(self):
        self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() + 1)
    def lastPage(self):
        self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() - 1)
    def setInstDir(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self,"请选择安装位置","/home")
        if dir:
            print("InstDir:",dir)
            self.ui_p3InstPath.setText(dir if NAME == os.path.split(dir)[-1] == NAME else ("".join([dir,NAME]) if dir.endswith("/") else "/".join([dir,NAME])))
    def close(self,event = None):
        if self.stackedWidget.currentIndex() == 4:
            self.setVisible(False)
            app.exit()
            print("Exit")
            os._exit(0)
        if QtWidgets.QMessageBox.warning(self,"Warning","是否要退出?",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel,QtWidgets.QMessageBox.Cancel) == QtWidgets.QMessageBox.Yes:
            self.setVisible(False)
            self.stackedWidget.setCurrentIndex(4)
            ui.setVisible(True)
    def canNext(self,text):
        if os.path.exists(text) or os.path.exists("/".join((text.split("/")[:-1] if text.split("/")[-1].startswith(NAME) else "Err:can't next") if "/" in text else (text.split("\\")[:-1] if text.split("\\")[-1].startswith(NAME) else "Err:can't next"))):
            self.ui_p3NextBtn.setEnabled(True)
        else:
            self.ui_p3NextBtn.setEnabled(False)
    def inst(self):
        self.worker = Worker(self)
        self.worker.ui = self
        self.worker.sinOut.connect(self.worker.showInfo)
        self.worker.sinStatu.connect(self.worker.showStatu)
        self.worker.start()

class Worker(QtCore.QThread):
    sinOut = QtCore.pyqtSignal(int)
    sinStatu = QtCore.pyqtSignal(str)
    def __init__(self,obj,parent = None):
        super().__init__(parent)
        self.obj = obj
    def showInfo(self,value):
        self.ui.ui_p4Pb.setValue(value)
    def showStatu(self,text):
        self.ui.ui_p4Statu.setText(" ".join([self.ui.ui_p4Statu.text(),text]))
    def extract(self,i,file,outDir):
        print(file,outDir)
        while 1:
            try:
                self.zip.extract(file,outDir)
                break
            except PermissionError:
                result = QtWidgets.QMessageBox.critical(self.ui,
                                                        "错误",
                                                        "\n".join(["提取文件",file.filename,"到",outDir,"时，权限不足"]),
                                                        QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Cancel,
                                                        QtWidgets.QMessageBox.Retry)
                if result != QtWidgets.QMessageBox.Retry:
                    break
            except Exception as err:
                QtWidgets.QMessageBox.critical(self.ui,
                                               "错误",
                                               f"未知错误:\n{err}")
                os._exit(0)
        self.sinOut.emit(i / len(self.files) * 100)
    def run(self):
        self.zip = zipfile.ZipFile(resource_path("pkg.zip"))
        self.files = self.zip.infolist()
        outDir = self.ui.ui_p3InstPath.text()
        self.outDir = outDir
        self.sinStatu.emit("解压缩程序文件夹")
        list(map(lambda x:self.extract(*x,outDir),enumerate(self.files)))
        
        self.exeFile = None
        self.findExeFile()
        if self.ui.ui_p3Addsm.isChecked():
            self.sinStatu.emit("创建开始菜单项")
            self.addStartMenu()
        if self.ui.ui_p3Adddl.isChecked():
            self.sinStatu.emit("创建桌面快捷方式")
            self.addDesktopLink()
        if self.exeFile:
            self.sinStatu.emit("注册程序")
            register_program(self.exeFile,os.path.join(self.outDir,self.exeFile))
        
        self.zip.close()
        self.ui.ui_p4Pb.setValue(100)
        time.sleep(0.5)
        self.ui.nextPage()
    def addStartMenu(self):
        if self.exeFile:
            create_shortcut(os.path.join(self.outDir,self.exeFile),
                            os.path.join(winshell.programs(),".".join([NAME,"lnk"])),
                            startIn = self.outDir
                            )
    
    def addDesktopLink(self):
        if self.exeFile:
            create_shortcut(os.path.join(self.outDir,self.exeFile),
                            os.path.join(winshell.desktop(),".".join([NAME,"lnk"])),
                            startIn = self.outDir
                            )
    def findExeFile(self):
        if not self.exeFile:
            for i in os.listdir(self.outDir):
                if i.endswith(".exe"):
                    self.exeFile = i
                    return

ui = Ui()
ui.show()
while 1:
    ui.show()
    app.exec_()
