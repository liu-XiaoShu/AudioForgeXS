#!/usr/bin/python3
#-*- coding:utf-8 -*-
import os
from tqdm import tqdm

try:
    from modules.debugLogger import DebugLogger
    from modules.getAudioInfo import GetAudioInfo
    from modules.audioBasicProcessing import AudioBasicProcessing
    from modules.pathProcessing import PathProcessing
except ImportError:
    sys.path.append("../")
    from modules.debugLogger import DebugLogger
    from modules.getAudioInfo import GetAudioInfo
    from modules.audioBasicProcessing import AudioBasicProcessing
    from modules.pathProcessing import PathProcessing



class GetTestSetAndNorm:

    """ 这是处理转录测试集相关的类"""

    def __init__(self, output_root_path, debug, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = DebugLogger()
        self.GetAudioInfo = GetAudioInfo(self.logger)
        self.AudioBasicProcessing = AudioBasicProcessing(self.logger)
        self.PathProcessing = PathProcessing(self.logger)

        #一级，仅选定
        self.only_set_list = []
        #二级，需排除
        self.non_set_list = []

        self.output_root_path = output_root_path


    def __GetTestSetAndNorm(self, input_audio_path, kws_cmd, set_max_num):
        """
            功能:
                    * 具体操作根据指令/唤醒词列表,选择最大数量不超
                    * 指定数量的测试集并且归一化该指令下的音频
            参数：
                    * input_audio_path: 输入总路径，语料均在下面
                    * kws_cmd_path:   指令/唤醒词列表
                    * set_max_num:    设置每个指令/唤醒词　最大数量
            返回值:
                    * /
        """
        try:
            flist = []
            input_test_set_path = os.path.join(input_audio_path, kws_cmd)
            flist = self.PathProcessing.get_file_list(input_test_set_path, ".wav")
            print("\n")
            self.logger.log(f"[GetTestSetAndNorm]: 提示！已获取测试集音频总数 {len(flist)}", "info")

            if not flist:
                return False

            wav_path_dict = {}
            for wav_path in flist:
                people_number = os.path.basename(wav_path).split("_")[-3]
                if people_number not in wav_path_dict:
                    wav_path_dict[people_number] = []
                wav_path_dict[people_number].append(wav_path)

            test_set_list = []
            while True:
                existence_test_set_flag = 0
                for key in wav_path_dict:
                    if wav_path_dict[key]:
                        existence_test_set_flag = 1
                        test_set_list.append(wav_path_dict[key].pop())
                if not existence_test_set_flag:
                    break
            is_non_set = 0
            no_only_set = 0
            is_test_set_num = 0
            for original_file in test_set_list:
                if is_test_set_num >= set_max_num:
                    break
                #仅选定
                for only_set in self.only_set_list:
                    if not re.findall(only_set, original_file):
                        no_only_set = 1
                if no_only_set:
                    no_only_set = 0
                    continue

                #排除
                for non_set in self.non_set_list:
                    #if original_file.find(non_set) >= 0:
                    if re.findall(non_set, original_file):
                        self.logger.log(f"[GetTestSetAndNorm]: 注意！已设置排除: {original_file}", "warning")
                        is_non_set = 1
                if is_non_set:
                    is_non_set = 0
                    continue

                new_file = os.path.join(self.output_root_path, original_file)
                new_dir = new_file.split(os.path.basename(new_file))[0]
                if not os.path.isdir(new_dir):
                    os.makedirs(new_dir)

                if self.AudioBasicProcessing.wavNorm(original_file, new_file, norm_number=1):
                    is_test_set_num += 1
                else:
                    continue

            new_kws_cmd_dir = os.path.join(self.output_root_path, input_test_set_path)
            new_kws_cmd_norm_dir = f"{new_kws_cmd_dir}_norm_{len(self.PathProcessing.get_file_list(new_kws_cmd_dir, '.wav'))}"
            if os.path.isdir(new_kws_cmd_norm_dir):
                self.logger.log(f"[GetTestSetAndNorm]: 注意！{new_kws_cmd_norm_dir} 该目录已经存在, 删除以前处理记录", "warning")
                os.system("rm -r " + str(new_kws_cmd_norm_dir))
            mvCmd = "mv " + str(new_kws_cmd_dir) + " " + str(new_kws_cmd_norm_dir)
            if os.system(mvCmd):
                return False
            return True
        except:
            return False




    def getTestSetAndNorm(self, input_audio_path, kws_cmd_path, set_max_num):
        """
            功能:
                    * 根据指令/唤醒词列表,选择最大数量不超指定数量的测试集
                    * 并且归一化该指令下的音频
            参数：
                    * input_audio_path: 输入总路径，语料均在下面
                    * kws_cmd_path:   指令/唤醒词列表
                    * set_max_num:    设置每个指令/唤醒词　最大数量
            返回值:
                    /
        """
        self.logger.log(f"[GetTestSetAndNorm]: 提示！获取指定数量的测试集并归一化", "info")

        kws_cmd_list = []
        if os.path.isfile(kws_cmd_path):
            with open(kws_cmd_path, "r") as f:
                kws_cmd_list = f.readlines()
                kws_cmd_list = [x.strip() for x in kws_cmd_list]
        else:
            kws_cmd_list.append(kws_cmd_path)

        defect_error_kws_cmd_list = []
        #for kws_cmd in kws_cmd_list:
        for kws_cmd in tqdm(kws_cmd_list, desc=f"\033[0;36;33m指令测试集处理\033[0m", ncols=150, unit="条"):
            if not self.__GetTestSetAndNorm(input_audio_path, kws_cmd, set_max_num):
                defect_error_kws_cmd_list.append(kws_cmd)
        if defect_error_kws_cmd_list:
            self.logger.log(f"[GetTestSetAndNorm]: 错误！{input_audio_path} 路径下缺失如下测试集 {defect_error_kws_cmd_list} 请检查", "error")


if __name__=="__main__":
    pass

