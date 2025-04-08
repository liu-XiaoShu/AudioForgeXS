import sys, subprocess
import platform

def run_cmd(full_cmd):
    print(full_cmd)
    subprocess.call(full_cmd, shell=True)

print("开始打包 ...")
dir_name = sys.platform + "_output"
if sys.platform == 'win32': # windows
    run_cmd('pyinstaller -F audioForgeXS.py --clean')
    run_cmd("mkdir " + dir_name)
    mvcmd = "mv dist/app.exe dist/audioForgeXS" + str(sys.platform) + ".exe"
    run_cmd(mvcmd)
    run_cmd("copy dist " + dir_name)
    run_cmd("del /F /S /Q __pycache__ build dist *.spec")
    run_cmd("rd /S /Q __pycache__ build dist")

elif sys.platform == 'linux': # linux
    run_cmd('pyinstaller -F audioForgeXS.py --clean')
    mvcmd = "mv dist/app dist/audioForgeXS_" + str(sys.platform) + "_" + str(platform.architecture()[0])
    run_cmd(mvcmd)
    run_cmd("mkdir " + dir_name)
    run_cmd("cp dist/* " + dir_name)
    run_cmd("rm -rf __pycache__ build dist *.spec")

elif sys.platform == 'darwin': # Mac OS
    run_cmd('sudo pyinstaller -F audioForgeXS.py  --clean')
    mvcmd = "mv dist/app dist/audioForgeXS_" + str(sys.platform)
    run_cmd(mvcmd)
    run_cmd("mkdir " + dir_name)
    run_cmd("cp dist/* " + dir_name)
    run_cmd("sudo rm -r __pycache__ build dist *.spec")
else:
    print("The system is not supported!")

print("打包完成 ...........")
