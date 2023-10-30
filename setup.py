from cx_Freeze import setup, Executable
include_files = [('E:\\1025\\main_1025\\sitpackage')]
setup(
    name="mainwindow",
    version="1.0",
    description="测试版",
    executables=[Executable("mainserver.py")],
    options={
        'build_exe': {
            'include_files': include_files
        }

    }
)