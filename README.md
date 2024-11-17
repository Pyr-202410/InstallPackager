​
最近，由于有一些将可执行程序打包成安装程序的需求，自己花了两周做了一个安装包打包程序。

# 首次更新
## 程序简介
| 名称 | 暂时叫InstallPackager |
|---------|--------------------|
| 编程语言（包括最终制作的安装包，下同） | 均为Python（注：使用时无需学习python） |
| 程序界面 | PyQt5 |
| 所需环境 | 需要下载Python |
| 功能 | 将一个程序文件夹制作成安装包 |

## 使用
### 1.安装python
​
> 注：用的是Python3.9.4）
> 
> 参考浏览器搜索第一条：[超详细的Python安装和环境搭建教程_python安装教程-CSDN博客](https://blog.csdn.net/qq_53280175/article/details/121107748 "python安装教程")

### 2.下载InstallPackager
将此项目下载下来就可以了
![下载方法](​)
或者也可以`git clone`一下
### 3.安装库
使用python自带的pip安装项目所需库（先切换到InstallPackager目录里）：

pip install -r requirements.txt
4.运行！
双击installPackager.py就可以看到主界面（如果python和库安装正确）



 如果不想改代码的话可以直接把代码框关了，程序就会进行下一步开始将python打包成最终exe格式的安装程序。


最后
制作的安装包程序在“InstallPackager/build/dist”中，双击即可运行。


2024.11.17更新


​
