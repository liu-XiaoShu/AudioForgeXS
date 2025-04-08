#!/usr/bin/python3
#-*- coding:utf-8 -*-

import sys, binascii, os
try:
    from modules.debugLogger import DebugLogger
except:
    sys.path.append("../")
    from modules.debugLogger import DebugLogger

__version__="1.0.1"



class GetAudioInfo:
    """ 这是一个获取音频头信息的类"""
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = DebugLogger()


    def __hex_to_dec(self, input_hex):
        """
            功能:
                    * 十六进制字符串转换为十进制整数
            参数:
                    * input_hex: 输入的十六进制字符串
            返回值:
                    * 十进制字符串
        """
        input_hex = input_hex.replace("0x", "")
        input_hex = input_hex.replace("0X", "")
        input_hex = input_hex.split(" ")
        input_hex = input_hex[::-1]
        input_hex = "".join(input_hex)
        return int(input_hex, base=16)


    def getWavInfor(self, input_wav, output_audio_path=None, fill_para=None):
        """
            功能:
                    * 读取头文件，并根据协议翻译出头信息内容
            参数:
                    * str wav文件路径 input_wav
            返回值:
                    * dict 头信息内容字典 output_head_infor_dict
        """
        data_type_size_dict = {8:1, 16:2, 24:3, 32:4}
        output_head_infor_dict = {}
        with open(input_wav, "rb") as f:
            data = f.read(44)
            hexstr = binascii.b2a_hex(data)
            hexstr = str(hexstr, "utf-8")
        head_infor_interval_dict = {"文件的数据大小":[4, 8],
                                    "区块长度": [16, 20],
                                    "音频格式(PCM音频数据的值为1)":[20, 22],
                                    "Channels":[22, 24],
                                    "Framerate":[24, 28],
                                    "每秒的数据字节数":[28, 32],
                                    "数据快对齐":[32, 34],
                                    "SampWidth":[34, 36],}
        hex_data_list = []
        hexstr_list = list(hexstr)
        tmep = ""
        for index in range(len(hexstr_list)):
            tmep = tmep + hexstr_list[index]
            if index%2:
                hex_data_list.append(tmep)
                tmep = ""

        for key in head_infor_interval_dict:
            get_data_list = hex_data_list[head_infor_interval_dict[key][0]:head_infor_interval_dict[key][-1]]
            get_data_str = " ".join(get_data_list)
            output_head_infor_dict[key] = self.__hex_to_dec(get_data_str)
        output_head_infor_dict["SampWidth"] = data_type_size_dict[output_head_infor_dict["SampWidth"]]

        data_size = os.path.getsize(input_wav)
        output_head_infor_dict["文件的数据大小"] = data_size
        output_head_infor_dict["FileDuration"] = (
                (output_head_infor_dict["文件的数据大小"] - 44)
                    /(
                        output_head_infor_dict["Channels"]
                        * output_head_infor_dict["Framerate"]
                        * output_head_infor_dict["SampWidth"])
            )
        output_head_infor_dict["SampleTime"] = 1/output_head_infor_dict["Framerate"]
        output_head_infor_dict["nFrames"] = output_head_infor_dict["Framerate"] * output_head_infor_dict["FileDuration"]
        output_head_infor_dict["文件名"] = input_wav
        self.logger.log(f"[GetAudioInfo]: 调试! 音频信息 {output_head_infor_dict}", "debug")
        return output_head_infor_dict


    def getWavFileDuration(self, input_wav, output_audio_path=None, fill_para=None):
        """
            功能:
                    * 读取头文件，并根据协议翻译出头信息内容
                    * 获取当前 wav 的时长
            参数:
                    * str wav文件路径 input_wav
            返回值:
                    * dict 头信息内容字典 output_head_infor_dict
        """
        info = self.getWavInfor(input_wav, output_audio_path=None, fill_para=None)
        return float(info["FileDuration"])



if __name__=="__main__":
    pass

