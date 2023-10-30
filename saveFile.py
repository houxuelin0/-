import ctypes

# 初始化状态
def IPB_INIT(dllobj):
    IPBNetInit = dllobj.IPBNetInit
    # 设置返回类型
    IPBNetInit.restype = ctypes.c_int
    # 设置参数类型
    IPBNetInit.argtypes = []
    # 获取初始化状态
    return IPBNetInit

#登录
def IPB_Login(dll_obj):
    IPBLoginServer = dll_obj.IPBLoginServer
    # 获取登录返回值状态
    IPBLoginServer.restype = ctypes.c_int
    # 获取登录的参数值类型
    IPBLoginServer.argtypes = [ctypes.c_uint, ctypes.c_ushort, ctypes.c_char_p, ctypes.c_char_p]
    return IPBLoginServer

# 获取数据
def IPB_voicetrans(dllobj):
    IPBStartDevVoiceTrans = dllobj.IPBStartDevVoiceTrans
    IPBStartDevVoiceTrans.restype = ctypes.c_int
    IPBStartDevVoiceTrans.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_short, ctypes.c_uint,
                                      ctypes.c_uint, ctypes.c_void_p]
    return IPBStartDevVoiceTrans

#建立连接
def IPB_sock(dllobj):
    IPBUDPCreateSock = dllobj.IPBUDPCreateSock
    IPBUDPCreateSock.restype = ctypes.c_int
    IPBUDPCreateSock.argtypes = [ctypes.c_int]
    return IPBUDPCreateSock

#发送参数
def IPB_sendata(dllobj):
    IPBUDPSendData = dllobj.IPBUDPSendData
    IPBUDPSendData.restype = ctypes.c_int
    IPBUDPSendData.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    return IPBUDPSendData

 # 接收数据
def IPB_rcvdata(dllobj):
    IPBUDPRcvData = dllobj.IPBUDPRcvData
    IPBUDPRcvData.restype = ctypes.c_int
    IPBUDPRcvData.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_uint]
    return IPBUDPRcvData

# 获取设备名
def IPB_getDevicename(allobj):
    IPBGetAllDeviceName = allobj.IPBGetAllDeviceName
    IPBGetAllDeviceName.restype = ctypes.c_int
    IPBGetAllDeviceName.argtypes = [ctypes.c_void_p, ctypes.c_int]
    return IPBGetAllDeviceName
