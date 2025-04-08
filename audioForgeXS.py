#!/usr/bin/python3
#-*- coding:utf-8 -*-


__version__ = "v2.1.0"



import argparse, sys, time, os
from tqdm import tqdm
from modules.debugLogger import DebugLogger
from modules.getAudioInfo import GetAudioInfo
from modules.pathProcessing import PathProcessing
from modules.audioBasicProcessing import AudioBasicProcessing
from modules.getTestSetAndNorm import GetTestSetAndNorm


Basic_functions_info = {"audioNorm": "音频归一化", "getInfo":"获取音频信息",
                        "getMono": "获取音频单通道", "mp3ToWav":"mp3转wav格式",
                        "pcmToWav": "pcm转wav格式", "wavHeadRepair": "wav音频头修复",
                        "getFileSize": "获取wav大小","getAllWavDuration": "获取输入所有wav的总时长"}

class AudioProcessSet:
    def __init__(self, output_root_path, debug):
        """
            功能:   初始化参数
            参数：  output_dir: 处理结果输出目录
                    Framerate: 音频采样率:  修复头和pcmToWav用到
                    SampleEncoding: 音频位宽:   修复头和pcmToWav用到
                    channels:       音频通道数: 修复头和pcmToWav用到
        """
        self.output_root_path = output_root_path


        if debug:
            self.logger = DebugLogger("debug")
        else:
            self.logger = DebugLogger("info")
        self.PathProcessing = PathProcessing(self.logger)
        self.AudioBasicProcessing = AudioBasicProcessing(self.logger)
        self.GetAudioInfo = GetAudioInfo(self.logger)



    def audio_basic_process(self, input_path, process_type="norm", input_wav_info=None):
        """
            功能:
                    * 音频基础操作处理
            参数:
                    *
            返回值:
                    * /
        """
        fun_obj_dict = {"audioNorm": self.AudioBasicProcessing.wavNorm,
                        "getInfo": self.GetAudioInfo.getWavInfor,
                        "getMono": self.AudioBasicProcessing.getMono,
                        "mp3ToWav": self.AudioBasicProcessing.mp3ToWav,
                        "wavHeadRepair": self.AudioBasicProcessing.wavHeadRepair,
                        "pcmToWav": self.AudioBasicProcessing.pcmToWav,
                        "getFileSize": self.AudioBasicProcessing.getFileSize,
                        "getAllWavDuration": self.GetAudioInfo.getWavFileDuration,
                        }

        if process_type == "pcmToWav":
            audio_path_list = self.PathProcessing.get_file_list(input_path, ".pcm$")
        elif process_type == "mp3ToWav":
            audio_path_list = self.PathProcessing.get_file_list(input_path, ".mp3$")
        else:
            audio_path_list = self.PathProcessing.get_file_list(input_path, ".wav$")

        if not audio_path_list:
            self.logger.log(f"[AudioProcessSet]: 警告! 当前输入路径下，音频数量为: 0", "warning")

        total_Duration = 0
        for audio_path in tqdm(audio_path_list, desc=f"\033[0;36;33m音频 {process_type} 处理\033[0m", ncols=150, unit="条"):
            ouput_path = os.path.join(self.output_root_path, audio_path)
            os.makedirs(os.path.dirname(ouput_path), exist_ok=True)
            res = fun_obj_dict[process_type](audio_path, ouput_path, input_wav_info)
            if process_type == "getInfo":
                self.logger.log(res, "info")
            if process_type == "getAllWavDuration":
                total_Duration += res
        if process_type == "getAllWavDuration":
            self.logger.log(f"当前输入 {input_path} 目录下，wav 总数: {len(audio_path_list)} 总时长 {total_Duration} 秒", "info")



def func_BasicMode(args):
    """
    功能:
            * 音频归一化操作入口
    参数:
            * args: 命令行参数
    返回值:
            * None
    """
    print(f"\033[0;36;33m[BasicMode]: 提示! 开始音频 {args.function} 处理\033[0m")
    if not args.inputPath:
        print("\033[0;36;31m[BasicMode]: 错误! 没有设置音频输入路径 -i/--inputPath\033[0m")
        return False

    input_wav_info = None
    if args.function in ["pcmToWav", "wavHeadRepair"]:
        input_wav_info = {}
        input_wav_info["Framerate"] = input("请输入音频采样率:")
        input_wav_info["channels"] = input("请输入音频通道数:")
        input_wav_info["SampleEncoding"] = input("请输入编码位数:")
    if args.function in ["audioNorm"]:
        input_wav_info = input("请输入音频归一化幅度值(0~1)支持浮点:")
        try:
            input_wav_info = float(input_wav_info)
        except:
            self.logger.log(f"[AudioProcessSet]: 错误! 当前输入的归一化值 {input_wav_info} 类型错误，当前只能是数字", "error")
        if input_wav_info > 1:
            self.logger.log(f"[AudioProcessSet]: 错误! 当前输入的归一化值 {input_wav_info} 范围错误，当前范围 0~1, 支持浮点", "error")


    aps = AudioProcessSet(args.output, args.debug)
    aps.audio_basic_process(args.inputPath, process_type=args.function, input_wav_info=input_wav_info)


def func_GetTestSetMode(args):
    """
    功能:
            * 获取测试集并归一化操作入口
            * 主要是测试集参与转录的前处理
    参数:
            * args: 命令行参数
    返回值:
            * None
    """
    print(f"\033[0;36;33m[BasicMode]: 提示! 开始获取参与转录测试集音频，并归一化处理\033[0m")


    if not args.inputPath:
        print("\033[0;36;31m[BasicMode]: 错误! 没有设置音频输入路径 -i/--inputPath\033[0m")
        return False

    if not args.cmdFilePath:
        print("\033[0;36;31m[BasicMode]: 错误! 没有设置指令词列表文件路径 -c/--cmdFilePath\033[0m")
        return False

    gtsan = GetTestSetAndNorm(args.output, args.debug)
    gtsan.getTestSetAndNorm(args.inputPath, args.cmdFilePath, args.number)



def main():
    update_time = "Update time: 2025-04-08\nauthor: liu-XiaoShu"
    version_info = "\nversion: " + str(__version__) + "\n" + update_time
    tool_description = "这是一个音频处理的工具，主要是对 WAV 音频的处理"
    parser = argparse.ArgumentParser(description=tool_description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '-V', '--version', action='version', version=version_info,
                        help='Print software version info')

    # 创建子命令解析器
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # 添加参数并进行验证
    def validate_function(value):
        if value not in list(Basic_functions_info.keys()):
            raise argparse.ArgumentTypeError(f"\033[0;36;31m无效的功能选择: {value} 可用功能: {', '.join(Basic_functions.keys())}\033[0m")
        return value

    def print_function_help():
        output_str = "\n"
        for key in Basic_functions_info:
            output_str += f"  \033[0;36;33m{key} :  {Basic_functions_info[key]}\033[0m\n"
        return output_str + "\n"

    cmd_BasicMode = subparsers.add_parser('BasicMode',
                                           help="对音频进行基础操作",
                                           aliases=["basicmode"],
                                            formatter_class=argparse.RawTextHelpFormatter)
    cmd_BasicMode.add_argument('-i', '--inputPath', dest="inputPath", default=None,
                               help="输入音频路径，支持文件/目录")
    cmd_BasicMode.add_argument('-o', '--output', type=str, default="OUTPUT",
                               help='处理后音频输出路径，默认路径 OUTPUT')
    cmd_BasicMode.add_argument('-f', '--function', type=validate_function,
                               help='功能选择: \n' + print_function_help())
    cmd_BasicMode.add_argument('-d', '--debug', action="store_true", default=False,
                               help="使能调试模式，默认不打开、主要调整打印等级为 debug, 输出详细打印，用于调试")
    cmd_BasicMode.set_defaults(func=func_BasicMode)


    cmd_GetTestSetMode = subparsers.add_parser('GetTestSetMode',
                                           help="获取归一化后的测试集，用于转录测试集的前处理",
                                           aliases=["gettestsetmode"],
                                            formatter_class=argparse.RawTextHelpFormatter)

    cmd_GetTestSetMode.add_argument('-i', '--inputPath', dest="inputPath", default=None,
                               help="输入音频路径，支持文件/目录")
    cmd_GetTestSetMode.add_argument('-o', '--output', type=str, default="OUTPUT",
                               help='处理后音频输出路径，默认路径 OUTPUT')
    cmd_GetTestSetMode.add_argument('-c', '--cmdFilePath', type=str, default=None,
                               help=f"""需要处理的测试集指令词列表文件 内容示例如下:

小树同学
小树小树
打开照明
关闭照明

注意: 以换行分割指令词
""")

    cmd_GetTestSetMode.add_argument('-n', '--number', type=int, default=100,
                               help='每条指令可以获取最大的测试集音频数量，默认100')
    cmd_GetTestSetMode.add_argument('-d', '--debug', action="store_true", default=False,
                               help="使能调试模式，默认不打开、主要调整打印等级为 debug, 输出详细打印，用于调试")
    cmd_GetTestSetMode.set_defaults(func=func_GetTestSetMode)



    # 设置子命令名不区分大小写任意组合
    if len(sys.argv) > 1:
        sys.argv[1] = sys.argv[1].lower()  # 将第一个参数（子命令名称）转换为小写

    # 解析命令行参数
    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
    else:
        print(args)
        args.func(args)

if __name__ == "__main__":
    main()
