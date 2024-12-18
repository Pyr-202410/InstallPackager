from __future__ import print_function
from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtCore import Qt
import sys,io
import os,time
import zipfile
import winshell
import pythoncom
import winreg
import base64
from PIL import Image
import hashlib
import random
import json
import ctypes
import datetime
from ExeUi import Ui_MainWindow as ExeUi
app = QtWidgets.QApplication([])

# 高分屏适配
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

# 必须以管理员权限运行 (检测机制)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
if is_admin():
    pass
else:
    ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,sys.argv[0],None,0)
    sys.exit(0)

# 解决PyQt5不显示类中函数调用无法获取报错的问题
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = except_hook
#获取压缩包路径
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 图片转base64
def image_to_base64(image_path):
    with open(image_path,"rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def generate_sha256(input_string):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf8'))
    return str(sha256_hash.hexdigest())


NAME = """__NAME__""".strip()
VER = """__VER__""".strip()
HELLO = """__HELLO__""".strip()
PER = """__PER__""".strip()
END = """__END__""".strip()

instDataList = {"name":NAME,
                "ver":VER,
                "icon":None,
                "image":None,
                "instDir":None,
                "sha256":None,
                "startMenu":False,
                "desktopLink":False
                }

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

def register_program(program_name,program_path,icon,sha256,instDir,publisher,helpLink,helpTel,size):
    topKey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    sha256_ = sha256
    while True:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"\\".join([topKey,sha256_]))
            sha256_ = sha256 + str(random.random())
        except:
            break
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,topKey, 0, winreg.KEY_WRITE)
    new_key = winreg.CreateKey(key,sha256)
    winreg.SetValueEx(new_key, "DisplayName", 0, winreg.REG_SZ, program_name)
    winreg.SetValueEx(new_key, "UninstallString", 0, winreg.REG_SZ,f"start /D \"{instDir}\" \"{os.path.join(instDir,'uninst.exe')}\" /B")
    winreg.SetValueEx(new_key, "Publisher", 0, winreg.REG_SZ,publisher)
    winreg.SetValueEx(new_key, "DisplayVersion", 0, winreg.REG_SZ,VER)
    winreg.SetValueEx(new_key, "DisplayIcon", 0, winreg.REG_SZ,os.path.join(program_path,icon))
    winreg.SetValueEx(new_key, "sha256", 0, winreg.REG_SZ,sha256)
    winreg.SetValueEx(new_key, "InstallLocation", 0, winreg.REG_SZ,instDir) # 安装路径
    winreg.SetValueEx(new_key, "HelpLink", 0, winreg.REG_SZ,helpLink) # 帮助链接
    winreg.SetValueEx(new_key, "HelpTelephone", 0, winreg.REG_SZ,helpTel) # 帮助电话
    winreg.SetValueEx(new_key, "InstallDate", 0, winreg.REG_SZ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) # 安装日期
    winreg.SetValueEx(new_key, "EstimatedSize", 0, winreg.REG_DWORD,size) # 程序预计大小
    winreg.CloseKey(new_key)
    winreg.CloseKey(key)

class UiText(ExeUi):
    def reTextUi(self):
        winicon = resource_path("./winicon.ico")
        self.setWindowIcon(QtGui.QIcon(winicon))
        self.ui_p2Icon.setPixmap(QtGui.QPixmap(winicon))
        self.ui_p3Icon.setPixmap(QtGui.QPixmap(winicon))
        self.ui_p4Icon.setPixmap(QtGui.QPixmap(winicon))
        
        instDataList["icon"] = image_to_base64(winicon)
        if "image.png" in os.listdir(resource_path("./")):
            image = resource_path("./image.png")
            print("Found image",image)
            self.ui_p1Image.setPixmap(QtGui.QPixmap(image))
            self.ui_p5Image.setPixmap(QtGui.QPixmap(image))
            instDataList["image"] = image_to_base64(image)
            del image
        
        def _translate(text):
            return text.replace("{hello}",HELLO).replace("{per}",PER).replace("{end}",END).replace("{name}",NAME).replace("{ver}",VER).strip()
        self.setWindowTitle(r"""__title__""".strip())
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
        self.ui.ui_p4Statu.setText(" ".join(["状态:",text]))
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
        outDir = os.path.abspath(self.ui.ui_p3InstPath.text())
        self.outDir = outDir
        if not os.path.exists(self.outDir):
            os.makedirs(self.outDir)
        with open(resource_path("./exeicon.ico"),"rb") as r:
            with open(os.path.join(self.outDir,"ExeIcon.ico"),"wb") as w:
                w.write(r.read())
        
        instDataList["instDir"] = self.outDir
        instDataList["sha256"] = generate_sha256(",".join([instDataList["name"],
                                                           instDataList["ver"],
                                                           instDataList["instDir"],
                                                           str(time.time()),
                                                           str(random.randint(0,2147483648))
                                                           ]))
        
        self.sinStatu.emit("解压缩程序文件夹")
        list(map(lambda x:self.extract(*x,outDir),enumerate(self.files)))
        
        self.exeFile = None
        self.findExeFile()
        if self.ui.ui_p3Addsm.isChecked():
            self.sinStatu.emit("创建开始菜单项")
            while 1:
                try:
                    self.addStartMenu()
                    break
                except:
                    result = QtWidgets.QMessageBox.critical(self.ui,
                                                        "错误",
                                                        "\n".join(["创建桌面快捷方式失败!"]),
                                                        QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Cancel,
                                                        QtWidgets.QMessageBox.Retry)
                    if result != QtWidgets.QMessageBox.Retry:
                        break
            instDataList["startMenu"] = True
        if self.ui.ui_p3Adddl.isChecked():
            self.sinStatu.emit("创建桌面快捷方式")
            while 1:
                try:
                    self.addDesktopLink()
                    break
                except:
                    result = QtWidgets.QMessageBox.critical(self.ui,
                                                        "错误",
                                                        "\n".join(["创建桌面快捷方式失败!"]),
                                                        QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Cancel,
                                                        QtWidgets.QMessageBox.Retry)
                    if result != QtWidgets.QMessageBox.Retry:
                        break
            
            instDataList["desktopLink"] = True
        if self.exeFile:
            self.sinStatu.emit("注册程序")
            while 1:
                try:
                    register_program(self.exeFile,
                                     os.path.join(self.outDir,self.exeFile),
                                     os.path.join(self.outDir,"ExeIcon.ico"),
                                     instDataList["sha256"],
                                     self.outDir,
                                     """__publisher__""".strip(),
                                     """__helpLink__""".strip(),
                                     """__helpTel__""".strip(),
                                     int("""__zipAllSize__""".strip())
                                     )
                    break
                except Exception as err:
                    result = QtWidgets.QMessageBox.critical(self.ui,
                                                        "错误",
                                                        "\n".join(["注册程序失败!","","详细信息:",str(err)]),
                                                        QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Cancel,
                                                        QtWidgets.QMessageBox.Retry)
                    if result != QtWidgets.QMessageBox.Retry:
                        break
        
        self.zip.close()
        
        self.sinStatu.emit("写入安装配置")
        with open(os.path.join(self.outDir,"inst"),"w",encoding = "utf-8") as f:
            f.write(json.dumps(instDataList,ensure_ascii = False))
        
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
#pyuic5 -o C:\Users\Administrator\Desktop\PYExe\2024项目\工具\installPackager2.0\ExeUi.py C:\Users\Administrator\Desktop\PYExe\2024项目\工具\installPackager2.0\ExeUi.ui