# Connector for Windows## 软件准备#### 依次安装以下软件，均使用默认配置。
	python v2.7.13.msi  	jdk-8u144-windows-x64.exe	node-v6.11.2-x64.msi	appium-desktop-Setup-1.2.1.exe
	VCForPython27.msi#### 将文件夹复制至指定位置。
##### adb	Android\android-sdk
	->
	C:\Users\你的用户名\AppData\Local\Android\android-sdk
#### maven	apache-maven-3.5.0 
	->
	C:\Program Files\apache-maven-3.5.0#### ant	apache-ant-1.10.1
	->
	C:\Program Files\apache-ant-1.10.1## 环境变量`Win + Pause/Break` 打开**系统信息**页面，右侧**高级系统设置**。在弹出的**系统属性**页面中点击右下角**环境变量**。

**注**：**系统信息**页面也可在 **控制面板-系统与安全-系统** 中找到##### 在环境变量页面中上方用户变量中检查如下变量是否正确设置。
	ANDROID_HOME		C:\Users\你的用户名\AppData\Local\Android\android-sdk	JAVA_HOME		C:\Program Files\Java\jdk1.8.0_144	M2		C:\Program Files\apache-maven-3.5.0\bin	M2_HOME		C:\Program Files\apache-maven-3.5.0**用户变量**列表中选中 **PATH** 点击 **编辑** 检查如下路径：
	C:\Python27	C:\Python27\Scripts	C:\Program Files\apache-maven-3.5.0\bin	C:\Program Files\apache-ant-1.10.1\bin	C:\Users\你的用户名\AppData\Local\Android\android-sdk\platform-tools
	C:\Users\你的用户名\AppData\Local\Android\android-sdk\build-tools\26.0.1	C:\Program Files\Java\jdk1.8.0_144\bin	C:\Users\你的用户名\AppData\Roaming\npm ##### 环境变量页面下方系统变量中检查如下变量是否正确设置。**系统变量**列表中选中 **Path** 点击 **编辑** 检查如下路径：  
	C:\ProgramData\Oracle\Java\javapath	C:\Program Files\nodejs## appium 配置复制 `Resource/appium-scripts` 文件夹下

	appium
	appium.cmd
	
至如下目录	C:\Users\你的用户名\AppData\Local\Programs\appium-desktop\resources\app\
	## Python 依赖包 + Connector 本体安装###### 推荐使用 virtualenv 虚拟环境安装.在dmc-cli 目录下，用命令行安装（win7可在dmc-cli页面 shift+鼠标右击选择 在此处打开命令窗口）	# 关闭 SSL 认证
	$> set PYTHONHTTPSVERIFY=0
	$> pip install –e .安装完成后即可全局使用相关命令：
	
	# 添加 -h 查看相关参数	dmc-server	dmc-agent	dmc-devices
	## config.ini 使用说明	
	[dmc]	INSTALL_PATH： connector 文件夹位置	API_URI：与网页端添加 connector 时输入内容一致，一般为 http://127.0.0.1:5000/api/v1	SERVER_IP： 本机 dmcserver IP，Proxy 远程连接需要	SERVER_PORT： 本机 dmcserver 端口，Proxy 远程连接需要	[cmd]	ADB： adb.exe 路径	APPIUM ：appium.cmd 脚本路径注：  
`config.ini` 位于 `connector/dmc-cli/src` 目录下  
`API_URI` 在多处用到，更改时需留意  其他常量为开发需要, 使用时暂不相关。

## dmc-desktop 使用说明

桌面版本依赖于 python 包的安装，所以请在安装完 cli 版本后再使用。
## 附录1 – 其他问题：
桌面版本 dmc-desktop 中也有 DEV\_API\_URI 。更改时需要注意。
## 附录2 – 参考链接:[Windows CMD 复制剪切命令](https://support.microsoft.com/en-us/help/240268/copy--xcopy--and-move-overwrite-functionality-changes-in-windows)
  [Windows 系统常用环境变量](http://windowsitpro.com/systems-management/what-environment-variables-are-available-windows)  
[BAT 脚本解压、压缩文件](https://stackoverflow.com/questions/28043589/how-can-i-compress-zip-and-uncompress-unzip-files-and-folders-with-bat)  
[BAT脚本路径相关](https://stackoverflow.com/questions/17063947/get-current-batchfile-directory)  