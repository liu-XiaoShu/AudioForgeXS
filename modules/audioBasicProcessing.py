#!/usr/bin/python3
#-*- coding:utf-8 -*-
import os
import wave
import soundfile as sf
from pydub import AudioSegment
import numpy as np


try:
    from modules.debugLogger import DebugLogger
    from modules.getAudioInfo import GetAudioInfo
except ImportError:
    sys.path.append("../")
    from modules.debugLogger import DebugLogger
    from modules.getAudioInfo import GetAudioInfo



class AudioBasicProcessing:

    """ 这是一个处理路径相关的类"""
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = DebugLogger()
        self.GetAudioInfo = GetAudioInfo(self.logger)

    def getMono(self, input_audio_path, output_audio_path, get_channel_index=0):
        """
        功能:
            * 支持任意采样率、比特深度和通道数的音频文件，提取指定声道并生成单声道文件
        参数:
            * input_audio_path: 输入音频路径（支持WAV、FLAC等格式）
            * output_audio_path: 输出音频路径（自动适配格式）
            * get_channel_index: 声道索引（从0开始）
        返回值:
            * bool: 成功返回True，失败返回False
        """
        get_channel_index = int(get_channel_index)
        self.logger.log(f"[AudioBasicProcessing]: 调试！提取 {input_audio_path} 的第 {get_channel_index} 音轨", "debug")
        try:
            # 使用soundfile读取音频数据及元信息（保留原始格式）
            sig, samplerate = sf.read(input_audio_path, always_2d=True)
            channels = sig.shape[1]

            # 校验声道索引有效性
            if get_channel_index >= channels:
                self.logger.log(f"[AudioBasicProcessing]: 错误！声道索引 {get_channel_index} 超出范围（总通道数：{channels}）", "error")
                return False

            # 提取目标声道数据
            mono_data = sig[:, get_channel_index]

            # 直接使用soundfile写入输出文件（自动处理格式和参数）
            sf.write(output_audio_path, mono_data, samplerate)

            self.logger.log(f"[AudioBasicProcessing]: 调试！成功提取音轨到 {output_audio_path}", "debug")
            return True
        except Exception as e:
            self.logger.log(f"[AudioBasicProcessing]: 错误！提取失败：{str(e)}", "error")
            return False



    def wavNorm(self, input_audio_path, output_audio_path, norm_number=1):
        """
            功能:
                    * wav归一化, 把音频振幅最大值拉到1
            参数:
                    * input_audio_path: 原始路径
                    * output_audio_path: 新路径
                    * norm_number 归一化数值, 范围 (0~1) 支持浮点
            返回值:
                    * bool True/False
        """
        wav_infor_dict = {}
        try:
            wav_infor_dict = self.GetAudioInfo.getWavInfor(input_audio_path)
            if wav_infor_dict['Channels'] > 1:
                #self.getMono(input_audio_path, "temp.wav", 1)
                self.getMono(input_audio_path, "temp.wav", 0)
                input_audio_path = "temp.wav"
            sig = None
            sig, fs = sf.read(input_audio_path)
            sig = sig / max(abs(sig)) * norm_number
            sf.write(output_audio_path, sig, fs)
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} 归一化到 {norm_number} 成功，新文件 {output_audio_path}", "debug")
            return True
        except Exception as e:
            self.logger.log(f"[AudioBasicProcessing]: 错误! {input_audio_path} 归一化到 {norm_number} 失败，因 {e}", "error")
            return False

    def mp3ToWav(self, input_audio_path, output_audio_path, fill_para=None):
        """
            功能:
                    * mp3 转 wav
            参数：
                    * input_audio_path: 原始路径
                    * output_audio_path: 新路径
            返回值:
                    * bool True/False
        """
        try:
            if output_audio_path.endswith(".mp3"):
                output_audio_path = output_audio_path.split(".mp3")[0] + ".wav"
            else:
                output_audio_path = output_audio_path + ".wav"

            song = AudioSegment.from_mp3(input_audio_path)
            song.export(output_audio_path, format="wav")
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} MP3->WAV {output_audio_path} 成功", "debug")
            return True
        except Exception as e:
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} MP3->WAV {output_audio_path} 失败，因 {e}", "error")
            return False


    def pcmToWav(self, input_audio_path, output_audio_path, fill_para=None):
        """
            功能:
                    * pcm 转 wav
            参数：
                    * input_audio_path: 原始路径
                    * output_audio_path: 新路径
            返回值:
                    * bool True/False
        """
        input_wav_info = fill_para

        if self.SampleEncoding % 8 != 0:
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} PCM->WAV {output_audio_path} 失败，因 bits 参数不合规范", "error")
            return False

        if output_audio_path.find(".wav") >= 0:
            output_audio_path = output_audio_path.split(".pcm")[0]
        else:
            output_audio_path = output_audio_path.split(".pcm")[0] + ".wav"
        try:
            with open(input_audio_path, "rb") as pcmf:
                pcm_data = pcmf.read()
            with wave.open(output_audio_path, 'wb') as wavf:
                wavf.setnchannels(int(input_wav_info["channels"]))
                wavf.setsampwidth(int(input_wav_info["SampleEncoding"]) // 8)
                wavf.setframerate(int(input_wav_info["Framerate"]))
                wavf.writeframes(pcm_data)
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} PCM->WAV {output_audio_path} 成功", "debug")
            return True
        except ValueError as e:
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} PCM->WAV {output_audio_path} 失败，因 {e}", "error")
            return False


    def wavHeadRepair(self, input_audio_path, output_audio_path, fill_para=None):
        """
            功能:
                    * wav 头修复
            参数:
                    * input_audio_path: 原始路径
                    * output_audio_path: 新路径
            返回值:
                    * bool True/False
        """
        input_wav_info = fill_para
        try:
            wav_data = None
            with open(input_audio_path, "rb") as fd:
                fd.seek(44)
                wav_data = fd.read()
            with wave.open(output_audio_path, 'wb') as wavf:
                wavf.setnchannels(int(input_wav_info["channels"]))
                wavf.setsampwidth(int(input_wav_info["SampleEncoding"]) // 8)
                wavf.setframerate(int(input_wav_info["Framerate"]))
                wavf.writeframes(wav_data)
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} WAV头修复 {output_audio_path} 成功", "debug")
            return True
        except Exception as e:
            self.logger.log(f"[AudioBasicProcessing]: {input_audio_path} WAV头修复 {output_audio_path} 失败，因 {e}", "error")
            return False


    def getFileSize(self, input_audio_path, output_audio_path, fill_para=None):
        """
            功能:   获取文件大小,输出需要
                    大小的文件路径
        """
        fsize = os.path.getsize(input_audio_path)
        #fsize = fsize/float(1024 * 1024)
        fsize = round(fsize/1024, 2)
        if not fsize:
            self.logger.log(f"[AudioBasicProcessing]: 文件大小: {fsize}K \t: 文件路径: {input_audio_path}", "error")
        else:
            self.logger.log(f"[AudioBasicProcessing]: 文件大小: {fsize}K \t: 文件路径: {input_audio_path}", "info")
        return fsize

if __name__=="__main__":
    pass

