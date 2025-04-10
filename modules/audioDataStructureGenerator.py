#!/usr/bin/python3
#-*- coding:utf-8 -*-

import os, hashlib, re
import pypinyin, shutil

try:
    from modules.debugLogger import DebugLogger
    from modules.getAudioInfo import GetAudioInfo
except ImportError:
    sys.path.append("../")
    from modules.debugLogger import DebugLogger
    from modules.getAudioInfo import GetAudioInfo




class AudioDataStructureGenerator:
    """音频资料结构生成器"""
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = DebugLogger()

        #地区关键字
        self.area_keywords_dict = {}

        self.info_keywords_dict = {
                                "语速":{
                                        "fast":["快语速","快速", "fast"],
                                        "normal":["正常语速","正常", "normal"],
                                        "slow": ["慢速", "慢语速", "slow"],},
                                "采集距离":{
                                        "1m":["1m", "1米", "一米"],
                                        "2m": ["2m", "两米", "二米", "2米"],
                                        "3m": ["3m", "3米", "三米"],},
                                "性别":{
                                        "man": ["男", "/man", "man"],
                                        "woman": ["女", "/woman", "woman"]},
                                "年龄段":{
                                        "children": ["children","儿童", "小孩", "小学", "初中","幼儿园"],
                                        "youth":["青年", "年轻", "youth", "大学", "中学","高中"],
                                        "middleAge": ["adults","中年", "middleAge","成年"],
                                        "oldＡge":["老年人","oldＡge", "大爷", "大妈"],},
                                }



    def chinese_characters_to_pinyin(self, word):
        """
        ┆   功能:
                    * 汉字转拼音(不带声调)
        ┆   参数:
                    * word 汉字字符串
        ┆   返回值:
                    * str: 对应拼音(不带声调)
        """
        word = str(word)
        pinyin = ""
        for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
            pinyin += ''.join(i)
        #print(pinyin)
        return pinyin


    def is_chinese_present(self, text: str) -> bool:
        """
            功能:
                    * 检查字符串是否含中文
            参数:
                    * 输入字符串
            返回值:
                    * Bool True/False
        """
        return any('\u4e00' <= c <= '\u9fff' for c in text)




    def readLab(self, wav_path):
        """
            功能:
                    * 智能读取关联的LAB文本文件，支持多种编码格式
                        改进点:
                            1. 更全面的编码探测机制
                            2. 自动检测BOM标记
                            3. 添加字节序检测
                            4. 支持带BOM的UTF编码
                            5. 使用更高效的编码检测策略
            参数:
                    * wav 音频文件路径 wav_path
            返回值:
                    * 解析的 lab 内容
        """
        # 配置参数
        ENCODING_CANDIDATES = [
            # 带BOM的编码优先检测
            'utf-8-sig', 'utf-16', 'utf-16le', 'utf-16be',
            'utf-32', 'utf-32le', 'utf-32be',

            # 常见编码
            'utf-8', 'ascii', 'latin-1',

            # 中文编码
            'gb18030', 'gbk', 'gb2312', 'big5', 'hz',

            # 日文编码
            'shift_jis', 'euc-jp',

            # 韩文编码
            'euc-kr',

            # 国际编码
            'iso-8859-1', 'iso-8859-2', 'iso-8859-5'
        ]

        LAB_SUFFIX_VARIANTS = [
            ".lab", ".txt", ".list",
            ".wav.lab", ".wav.txt", ".wav.list",
            "_lab", "_label", "_annotation"
        ]

        # 生成候选路径
        base_path = wav_path.rsplit('.wav', 1)[0] if wav_path.endswith('.wav') else wav_path
        candidate_paths = (
            f"{base_path}{suffix}"
            for suffix in LAB_SUFFIX_VARIANTS
        )

        # 查找有效LAB文件
        lab_path = next((p for p in candidate_paths if os.path.isfile(p)), None)

        if not lab_path:
            if self.enable_log_flag:
                self.logger.log(f"[AudioDataStructureGenerator]: 错误 未找到LAB文件 {wav_path}", "error")
            return "", ""

        # 智能编码检测
        try:
            # 优先检测BOM标记
            with open(lab_path, 'rb') as f:
                raw_data = f.read(4096)  # 读取前4KB用于编码检测

                # 第一阶段：检测BOM
                bom_encodings = {
                    b'\xff\xfe\x00\x00': 'utf-32le',
                    b'\x00\x00\xfe\xff': 'utf-32be',
                    b'\xff\xfe': 'utf-16le',
                    b'\xfe\xff': 'utf-16be',
                    b'\xef\xbb\xbf': 'utf-8-sig'
                }
                for bom, encoding in bom_encodings.items():
                    if raw_data.startswith(bom):
                        return raw_data.decode(encoding).strip(), lab_path

                # 第二阶段：使用chardet检测（需要安装）
                try:
                    import chardet
                    detection = chardet.detect(raw_data)
                    if detection['confidence'] > 0.9:
                        decoded = raw_data.decode(detection['encoding'])
                        return decoded.strip(), lab_path
                except ImportError:
                    pass

                # 第三阶段：遍历候选编码
                for encoding in ENCODING_CANDIDATES:
                    try:
                        decoded = raw_data.decode(encoding, errors='strict')
                        # 验证有效性：检查是否存在异常控制字符
                        if any(0x0 <= ord(c) < 0x20 and ord(c) not in (0x09, 0x0A, 0x0D) for c in decoded):
                            continue
                        return decoded.strip(), lab_path
                    except UnicodeDecodeError:
                        continue

                # 最终回退策略
                return raw_data.decode('utf-8', errors='replace').strip(), lab_path

        except Exception as e:
            if self.enable_log_flag:
                self.logger.log(f"[AudioDataStructureGenerator]: 错误 LAB文件 {wav_path} 字符编码解码失败: {str(e)}", "error")
            return "", lab_path


    
    def get_file_md5(self, file_path, chunk_size=4096):
        """
            功能:
                    * 计算文件的 MD5 哈希值
            
            参数:
                    * file_path (str): 待计算的文件路径
                    * chunk_size (int): 每次读取的文件块大小 (单位: 字节)
            
            返回:
                    * str: 16进制格式的MD5字符串 (全小写)
            
            异常:
                FileNotFoundError: 当文件不存在时抛出
                IOError: 当文件读取失败时抛出
        """
        # 校验文件是否存在
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 初始化MD5对象
        md5_hash = hashlib.md5()
        
        try:
            # 以二进制模式打开文件
            with open(file_path, "rb") as f:
                # 分块读取文件内容并更新哈希值
                while chunk := f.read(chunk_size):
                    md5_hash.update(chunk)
        except IOError as e:
            raise IOError(f"无法读取文件: {file_path} ({str(e)})")
        
        # 返回16进制字符串
        return md5_hash.hexdigest()




    def get_keywords_info(self, input_audio_path, output_audio_path):
        """
            功能：
                    * 获取必须得关键字信息
            参数:
                    * wav 音频文件路径 input_audio_path,
            返回值:
                    * 关键字信息 keywords_info_dict
        """
    #
    #        ['yingguo',
    # 'English',
    # 'normal',
    # '1m',
    # 'woman',
    # 'youth',
    # 'NULL',
    # 'Alexa',
    # '01+MD5+7f46054768908ee475b58d509591546a.wav']
    #

        #filename = f'{keywords_info_dict["地区"]}_{keywords_info_dict["口音"]}_{keywords_info_dict["语速"]}'
        #filename += f'_{keywords_info_dict["采集距离"]}_{keywords_info_dict["性别"]}_{keywords_info_dict["年龄段"]}'
        #filename += f'_{keywords_info_dict["人编号"]}_{keywords_info_dict["指令词"]}_01+MD5+{keywords_info_dict["MD5"]}'


        keywords_info_dict = {
                            "语料来源": "未知来源",
                            "地区": "zhongguo",
                            "口音": "putonghua",
                            "语速": "normal",
                            "采集距离": "NULL",
                            "性别": "NULL",
                            "年龄段": "NULL",
                            "人编号": "NULL",
                            "指令词": "NULL",
                            "MD5":"NULL"}
        
        path_info = input_audio_path.split("/")
        lab_content = self.readLab(input_audio_path)

        #1、解析指令词信息
        if not lab_content[0]:
            self.logger.log(f"[AudioDataStructureGenerator]: 错误！ 未找 {input_audio_path} 文件的指令信息，跳过", "error")
            return False

        keywords_info_dict["指令词"] = self.chinese_characters_to_pinyin(lab_content[0])

        #2、获取文件MD5
        keywords_info_dict["MD5"] = self.get_file_md5(input_audio_path)

        #3、获取语料来源
        try:
            for single_path_content in path_info[:-1][::-1]: #从后往前匹配
                if not single_path_content:
                    continue
                if re.findall("来源", single_path_content):
                    keywords_info_dict["语料来源"] = single_path_content.strip()
                    break
        except:
            self.logger.log(f"[AudioDataStructureGenerator]: 警告！ 未找到 {input_audio_path} 文件的 语料来源 信息", "warning")

        #4、猜测地区
        if not self.is_chinese_present(lab_content[0]):
            #不包含中文(可以定义非中国)
            output_dir = os.path.join(output_audio_path, lab_content[0], keywords_info_dict["语料来源"], "欧美")
            keywords_info_dict["地区"] = "yingguo"
            keywords_info_dict["口音"] = "English"
        else:
            output_dir = os.path.join(output_audio_path, lab_content[0], keywords_info_dict["语料来源"], "中国")


        #5、其他信息
        for info_content in self.info_keywords_dict:
            try:
                for key in self.info_keywords_dict[info_content]:
                    for keyword in self.info_keywords_dict[info_content][key]:
                        if re.findall(keyword, input_audio_path, re.I):
                            keywords_info_dict[info_content] = key
                            break
            except:
                self.logger.log(f"[AudioDataStructureGenerator]: 警告！ 未找到 {input_audio_path} 文件的 {info_content} 信息", "warning")

        #获取人员编号
        try:
            keywords_info_dict["人编号"] = path_info[-2]
        except:
            self.logger.log(f"[AudioDataStructureGenerator]: 警告！ 未找到 {input_audio_path} 文件的人员编号信息", "warning")


        filename = f'{keywords_info_dict["地区"]}_{keywords_info_dict["口音"]}_{keywords_info_dict["语速"]}'
        filename += f'_{keywords_info_dict["采集距离"]}_{keywords_info_dict["性别"]}_{keywords_info_dict["年龄段"]}'
        filename += f'_{keywords_info_dict["人编号"]}_{keywords_info_dict["指令词"]}_01+MD5+{keywords_info_dict["MD5"]}.wav'
        if len(filename.split("_")) != 9:
            self.logger.log(f"[AudioDataStructureGenerator]: 错误！ {input_audio_path} 文件的结构化后 {filename} 格式错误", "error")
        new_audio_path = os.path.join(output_dir, filename)
        self.logger.log(f"[AudioDataStructureGenerator]: 路径信息解析成功: {keywords_info_dict}", "debug")
        self.logger.log(f"[AudioDataStructureGenerator]: 新路径信息: {new_audio_path}", "debug")
        return new_audio_path


    def StartStructuredAudio(self, input_audio_path, output_audio_path, fill_para=None):
        """
            功能：
                    * 整理输入文件，统一格式方便入库
            参数:
                    * str 输入音频文件路径 input_audio_path
                    * str 输出音频文件基础路径 output_audio_path
            返回值:
                    * Bool True/False
        """
        new_audio_path = self.get_keywords_info(input_audio_path, output_audio_path)
        if not new_audio_path:
            return False

        if fill_para == 1: #预览
            self.logger.log(f"[AudioDataStructureGenerator]: 预览! 处理前: {input_audio_path}", "info")
            self.logger.log(f"[AudioDataStructureGenerator]: 预览! 处理后: {new_audio_path}", "info")
        else:
            self.logger.log(f"[AudioDataStructureGenerator]: 执行! 处理前: {input_audio_path}", "debug")
            self.logger.log(f"[AudioDataStructureGenerator]: 执行! 处理后: {new_audio_path}", "debug")
            os.makedirs(os.path.dirname(new_audio_path), exist_ok=True)
            try:
                #整理文件
                shutil.move(input_audio_path, new_audio_path)
                self.logger.log(f"[AudioDataStructureGenerator]: 执行! {input_audio_path} 移动到 {new_audio_path} 成功", "debug")
            except:
                self.logger.log(f"[AudioDataStructureGenerator]: 错误! 执行! {input_audio_path} 移动到 {new_audio_path} 成功", "error")
                return False
        return True




