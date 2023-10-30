from mainwindows import Ui_MainWindow
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMessageBox,QErrorMessage,QVBoxLayout,QGridLayout
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer,pyqtSlot
import socket
import matplotlib.pyplot as plt
import time
import wave

import common
from saveFile import *
import os
import matplotlib
import uuid
from getFDValue import *

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
# 定义 DeviceModel 类
# class Myplot for plotting with matplotlib
class Myplot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        # normalized for 中文显示和负号
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # new fig
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # activate figure window
        # super(Plot_dynamic,self).__init__(self.fig)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        # initial figure
        self.compute_initial_figure()

        # size policy
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass



#定义进程
class GetDataThread(QThread):
    data_generated = pyqtSignal(str)
    #plot_done_event = threading.Event()

    def __init__(self):
        super().__init__()
        self.total_data = []
        self.dllevent = None
        self.getvalue_devices = None

    def run(self):
        # 建立连接
        IPBUDPCreateSock = IPB_sock(self.dllevent)
        # 发送参数
        IPBUDPSendData = IPB_sendata(self.dllevent)
        # 接收数据
        IPBUDPRcvData = IPB_rcvdata(self.dllevent)

        buffer5 = self.getvalue_devices[12:16][::-1]
        buffer_id = socket.inet_aton('.'.join(map(str, buffer5)))
        nScrPort = int.from_bytes(buffer_id, byteorder='big', signed=False)
        # nScrPort = int(''.join(map(str, buffer5)))

        buffer7 = self.getvalue_devices[20:24][::-1]
        buffer7_id = socket.inet_aton('.'.join(map(str, buffer7)))
        nDstPort = int.from_bytes(buffer7_id, byteorder='big', signed=False)
        sock = IPBUDPCreateSock(nDstPort)
        len1 = IPBUDPSendData(sock, common.Server_ip, nScrPort, self.getvalue_devices, 36)

        data = (ctypes.c_ubyte * 1568)()

        dt1 = str(time.time())
        time_dt = dt1
        count = 0
        audio_array = []
        now_time = 0
        in_time = 0
        print('开始采集数据。。。。。')
        while True:
            try:
                dt2 = time.time()
                ts = dt2 - float(dt1)
                # sec = ts.total_seconds()
                if ts > 1:
                    len2 = IPBUDPSendData(sock, common.Server_ip, nScrPort, self.getvalue_devices, 36)
                    dt1 = dt2
                    # time_dt = str(dt1)

                len3 = IPBUDPRcvData(sock, data, 1568, 5)
                if len3 > 0:
                    print('采集中.......')
                    data3 = data[8:968]
                    audio_array.append(data3)
                    # audioPlayer.input_audio_data(data3)
                    # AudioSegment(data3)
                    count += 1
                # new_sec = ts.total_seconds()
            except Exception as e:
                print(e.args[0])
            if len(audio_array) == 268:
                # 设置采样率
                sample_rate = 48000

                # 创建WAV文件
                # 获取当前文件夹目录
                current_folderpath = os.path.dirname(os.path.abspath(__file__))
                # 创建当前文件夹路径
                create_folder = current_folderpath + '\\' + 'wavFiles' + '\\'
                if not os.path.exists(create_folder):
                    os.makedirs(create_folder)
                output_file = create_folder + str(uuid.uuid1()) + 'new.wav'
                with wave.open(output_file, 'w') as wavfile:
                    # 设置音频参数
                    wavfile.setnchannels(1)  # 单声道
                    wavfile.setsampwidth(2)  # 2 bytes = 16 bits
                    wavfile.setframerate(sample_rate)
                    # 将音频数据转换为字节流并写入WAV文件
                    wavfile.writeframes(np.array(audio_array).astype(np.int16).tobytes())
                common.isStart = True
                common.now_wavfilename = output_file
                ''' now_time = str(time.time())
                if float(now_time)-in_time >= 30 or in_time == 0:'''
                self.data_generated.emit(common.now_wavfilename)
                time.sleep(5)
                print(output_file)
                audio_array = []
                in_time = float(now_time)
                # AudioSegment.export(output_file,format='wav')

class dynamic_fig(Myplot):
    def __init__(self, *args, **kwargs):
        Myplot.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):

        pass

class DeviceModel:
    def __init__(self):
        self.DeviceId = 0
        self.DeviceName = ""

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        #未连接时，隐藏按钮
        self.hide_button(False)
        #设置按钮的连接事件
        self.pushButton_2.clicked.connect(self.connectDevice)
        #获取音频数据
        #self.pushButton_3.clicked.connect(self.saveVoiceData)
        self.pushButton_3.clicked.connect(self.saveVoiceData)
        #self.pushButton.clicked.connect(self.start_Draw)
        self.pushButton.clicked.connect(self.on_dynamic_plot_clicked)
        #self.fig1 = static_fig(width=5, height=3, dpi=72)
        self.fig1 = dynamic_fig(width=5, height=3, dpi=72)
        self.axes2 = self.fig1.axes.twinx()
        # add NavigationToolbar in the figure (widgets)
        self.fig_ntb2 = NavigationToolbar(self.fig1, self)
        self.gridlayout1 = QGridLayout(self.groupBox)
        self.gridlayout1.addWidget(self.fig1)
        self.gridlayout1.addWidget(self.fig_ntb2)
        # initialized flags for static/dynamic plot: on is 1,off is 0
        self._timer = QTimer(self)
        self._t = 1
        self._counts = []
        self._delay_t = []
        self._Static_on = 0
        self._update_on = 0


    def init_value(self):
        common.xfrem = []
        common.dblist = []
        common.prelist = []
        common.xtrue = []
        common.YYSeverFilename = None
        common.now_wavfilename = ''

    #设置按钮是否隐藏
    def hide_button(self,isvisible):
        self.label_3.setVisible(isvisible)
        self.comboBox.setVisible(isvisible)
        self.pushButton_3.setVisible(isvisible)

    #不可编辑状态
    def setEnable_QT(self,isenable):
        #self.num.setEnabled(isenable)
        self.num_2.setEnabled(isenable)
        self.num_3.setEnabled(isenable)
        self.num_4.setEnabled(isenable)
        self.textEdit.setEnabled(isenable)
        self.pushButton_2.setEnabled(isenable)
        self.comboBox.setEnabled(isenable)
        self.pushButton_3.setEnabled(isenable)
        #self.pushButton.setEnabled(isenable)

    #测试连接
    def connectDevice(self):
        getip = self.textEdit.toPlainText()
        #os.path.abspath(__file__)

        my_dll = ctypes.CDLL(proto_filepath)
        # 初始化状态
        IPBNetInit = IPB_INIT(my_dll)
        init_status = IPBNetInit()
        ip = '1.0.0.127'
        # 将IP转换为十六进制
        # hex_ip = int.from_bytes(socket.inet_aton(ip), byteorder='big')
        total_ip = socket.inet_aton(ip)
        inttotal_ip = int.from_bytes(total_ip, byteorder='big', signed=False)
        common.Inttotal_ip = inttotal_ip
        nServerPort = 36100
        cUserID = b"admin"
        cPassword = b"123"
        # 登录状态
        IPBLoginServer = IPB_Login(my_dll)
        login_status = IPBLoginServer(inttotal_ip, nServerPort, cUserID, cPassword)
        if login_status == 0:
            self.hide_button(True)
            getdevices = self.getDeviceName(my_dll)
            for i_devides in getdevices:
                self.comboBox.addItem(i_devides.DeviceName)
            self.pushButton_2.setEnabled(False)
        elif login_status == 1:
            self.hide_button(True)
            QMessageBox.information(self, "提示", "已经登录，请勿重复登录！！",QMessageBox.Yes)
        else:
            QMessageBox.information(self, "错误", "登录失败，请检查设备后重新登录！！",QMessageBox.Yes)

    #获取并保存为音频文件
    @pyqtSlot()
    def saveVoiceData(self):
        #禁用框体
        self._update_on = 1
        self._timer.timeout.connect(self.update_fig)
        self._timer.start(1000)  # plot after 1s delay
        #self.init_value()
        self.setEnable_QT(False)
        my_dll = ctypes.CDLL(proto_filepath)
        # 获取数据
        IPBStartDevVoiceTrans = IPB_voicetrans(my_dll)
        getvalue_devices = (ctypes.c_ubyte * 36)()
        choiceName = self.comboBox.currentText()
        choiceID = [i_dev.DeviceId for i_dev in common.saveAlldevName if i_dev.DeviceName == choiceName][0]
        dd = IPBStartDevVoiceTrans(0, 70, choiceID, 0, common.Inttotal_ip, 49002, getvalue_devices)
        print('当前设备ID为{}'.format(str(choiceID)))
        print('start IPBStartDevVoiceTrans')
        if dd < 0:
            print('接收音频失败！！')
        else:
            print('IPBStartDevVoiceTrans 成功，正在获取数据。。。。。')
            # 创建线程
            #event = threading.Event()
            self.a_thread = GetDataThread()
            self.a_thread.dllevent = my_dll
            self.a_thread.getvalue_devices = getvalue_devices
            self.a_thread.data_generated.connect(self.handle_data_generated)
            #QTimer.singleShot(30000, window.start_Draw)
            self.a_thread.start()
            #QTimer.singleShot(30000, window.start_Draw)
    #
    def handle_data_generated(self, data):
        # 处理A函数产生的数据
        print('ddd')
        if os.path.exists(common.now_wavfilename):
            self.start_Draw()

    def start_Draw(self):
        common.isdraw = False
        if os.path.exists(common.now_wavfilename):
            #将音频文件上传到云音服务器，并获取相对路径
            serverfilepath = getYYAbFilePath(common.now_wavfilename)
            #获取声源文件的频率等数值
            freq1 = self.num_2.text()
            freq2 = self.num_3.text()
            nnum = self.num_3.text()
            #获取音频解析后的数据
            getdata = getwavRedata(freq1,freq2,nnum,serverfilepath)
            #删除服务器上的文件
            isdelflag = delSeerverFile(serverfilepath)
            if isdelflag or isdelflag == 'true' or isdelflag == 'True':
                self.setEnable_QT(True)
                #QMessageBox.information(self, "提示", "获取数据成功！！", QMessageBox.Yes)
                x_true,x_arr, pre_arr, db_arr = calculateData(getdata)
                self.on_dynamic_plot_clicked()

                #self.drawFigure(x_true,x_arr, pre_arr, db_arr)

        else:
            QMessageBox.information(self, "错误", "请重新选取设备！！！", QMessageBox.Yes)

    #获取设备名
    def getDeviceName(self,my_dll):
        # 获取设备名
        IPBGetAllDeviceName = my_dll.IPBGetAllDeviceName
        IPBGetAllDeviceName.restype = ctypes.c_int
        IPBGetAllDeviceName.argtypes = [ctypes.c_void_p, ctypes.c_int]

        # 定义 SubBytes 函数
        def SubBytes(arr, start, offset, length):
            return arr[start + offset:start + offset + length]

        # 调用 IPBGetAllDeviceName 函数
        devices = (ctypes.c_ubyte * (72 * 50))()
        d2 = IPBGetAllDeviceName(devices, 72 * 50)

        totalCount = d2 // 72

        deviceIdList = []
        devList = []

        for i in range(totalCount):
            c0 = 72 * i
            # 反转
            buffer = SubBytes(devices, c0, 0, 4)[::-1]
            id = int(''.join(map(str, buffer)))  # 设备ID
            deviceIdList.append(id)

            dModel = DeviceModel()
            dModel.DeviceId = id
            name = ""  # 设备名称
            for j in range(9):
                begin = 8 + 72 * i + 2 * j

                q1 = SubBytes(devices, begin, 0, 1)
                q2 = chr(q1[0])
                name += q2

            dModel.DeviceName = name.replace("\0", "")
            devList.append(dModel)
        common.saveAlldevName = devList
        return devList

    #在画布上作图
    def drawFigure(self,x_true,x_arr, pre_arr, db_arr):
        #self.groupBox.setLayout(QVBoxLayout())
        if len(self.groupBox.children()) > 0:
            for child in self.groupBox.children():
                child.deleteLater()
        layout = QVBoxLayout()
        # 创建一个画布
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        # 将布局设置给组合框
        self.groupBox.setLayout(layout)
        self.update_canvas(x_arr, pre_arr, db_arr)
        '''
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update_canvas(x_arr, pre_arr, db_arr))
        self.timer.start(10000)
        '''
        # 将画布添加到布局中

        # 连接鼠标移动事件
        #self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def update_canvas(self,x_arr, pre_arr, db_arr):
        # 清空画布
        self.fig.clear()
        self.canvas.close()
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False
        # 在画布中展示图像
        ax = self.fig.add_subplot(111)
        ax2 = ax.twinx()
        ax.plot(np.array(x_arr), db_arr, color='green', linestyle='-',linewidth=0.3, label='能量（db）')
        # p = ax.twinx()  # 包含另一个y轴的坐标轴对象
        ax2.plot(np.array(x_arr), pre_arr, color='red', linestyle='-',linewidth=0.3, label='密度（%）')
        # 添加图例
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        # 在图像上展示数值
        # mpldatacursor.datacursor(hover=True, bbox=dict(alpha=1, fc='w'), formatter='{x},{y}'.format)
        #mplcursors.cursor(hover=True)
        self.canvas.draw()
        print(db_arr)
        print('成功！！！')



    def on_dynamic_plot_clicked(self):
        print('start dynamic ploting')
        #self.dynamic_plot.setEnabled(False)
        # start update figure every 1s; flag "update_on" : 1 is on and 0 is Off


    def update_fig(self):
        '''self._t += 1
        print(self._t)
        self._delay_t.append(self._t)
        print(self._delay_t)
        # new_counts=random.randint(100,900)
        new_counts = 2 * self._t - self._t * np.cos(self._t / 2 / np.pi * 1000)
        self._counts.append(new_counts)
        print(self._counts)'''
        self.fig1.axes.cla()
        #plt.cla()
        self.axes2.cla()
        if len(common.xfrem) != 0:
            #ax2 = self.fig1.axes.twinx()
            #ax2 = self.fig1.axes.twinx()
            self.fig1.axes.plot(np.array(common.xfrem), common.dblist, color='green', linestyle='-', linewidth=0.3, label='能量（db）')
            # p = ax.twinx()  # 包含另一个y轴的坐标轴对象
            self.axes2.plot(np.array(common.xfrem), common.prelist, color='red', linestyle='-', linewidth=0.3, label='密度（%）')
            # 添加图例
            self.fig1.axes.legend(loc='upper left')
            self.axes2.legend(loc='upper right')
        self.fig1.draw()

if __name__ == '__main__':
    proto_filepath = os.path.dirname(os.path.abspath(__file__)) + '\sitpackage\ProtocolLib.dll'
    print(proto_filepath)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())