# AudioForgeXS 音频锻造专家

[English Version](#README_en.md)

🔊 一款高效的批量音频处理工具，专注于WAV音频格式的深度处理与测试集生成

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 📦 功能特性

### 基础处理模式 (BasicMode)
| 功能                  | 描述                          | 适用场景                 |
|-----------------------|-----------------------------|------------------------|
| 音频归一化 (audioNorm)   | 统一音频响度标准                 | 数据集预处理              |
| 格式转换               | MP3/PCM ↔ WAV 互转           | 格式标准化               |
| 元数据提取            | 获取音频参数/时长/大小           | 质量检测                |
| 单声道转换 (getMono)    | 立体声转单声道                  | 语音识别优化            |
| 文件修复              | WAV头文件修复                 | 损坏文件恢复            |

### 测试集生成模式 (GetTestSetMode)
```shell
根据指令词列表自动生成标准化的测试数据集，支持：
- 数量限制控制
- 归一化统一幅度
- 输出结构规范化
```

## 🛠️ 安装指南

### 二进制版本（推荐）

```shell
# Linux
wget https://github.com/liu-XiaoShu/AudioForgeXS/linux_output/audioForgeXS
chmod +x audioForgeXS
```

### 源码编译

```shell
bash
git clone https://github.com/liu-XiaoShu/AudioForgeXS.git
cd AudioForgeXS
pip install -r requirements.txt
python build.py # 支持 linux/windows/macos
```

## 🚀 快速入门

### 基础处理示例

```shell
bash
# 音频归一化处理
./audioForgeXS BasicMode -f audioNorm -i ./input/ -o ./normalized/

# 批量MP3转WAV
./audioForgeXS BasicMode -f mp3ToWav -i ./mp3_files/ -o ./wav_output/
```

### 测试集生成示例

```shell
bash
# 生成照明控制测试集
./audioForgeXS GetTestSetMode -i ./raw_audio/ -c commands.txt -n 50 -o ./testset/
```

## 📄 指令文件格式

创建 `commands.txt`：

```shell
text
# 每行一个指令词
打开客厅灯
关闭卧室灯
调节灯光亮度
切换颜色模式
```

## 📜 开发文档

```python
/
```

## 🤝 贡献指南

欢迎通过 Issues 提交建议或通过 Pull Request 参与开发：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/your-feature`)
3. 提交修改 (`git commit -am 'Add some feature'`)
4. 推送分支 (`git push origin feature/your-feature`)
5. 新建 Pull Request

## MIT 许可证

Copyright (c) 2024 liu-XiaoShu
