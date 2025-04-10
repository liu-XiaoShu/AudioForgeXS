------

# AudioForgeXS Audio Forging Expert

🔊 A high-efficiency batch audio processing tool specialized in WAV manipulation and testset generation

## 📦 Features

### Basic Processing Mode

| Function            | Description                   | Use Case               |
| ------------------- | ----------------------------- | ---------------------- |
| Audio Normalization | Standardize audio loudness    | Dataset preprocessing  |
| Format Conversion   | MP3/PCM ↔ WAV Transcoding     | Format standardization |
| Metadata Extraction | Get audio specs/duration/size | Quality inspection     |
| Mono Conversion     | Stereo to Mono                | ASR optimization       |
| File Repair         | WAV header recovery           | Corrupted file repair  |
|File Path Formatting |Standardize naming conventions & hierarchy|File organization|

### Testset Generation Mode

```shell
Automatically generate standardized test datasets based on the instruction word list, supporting:
-Quantity limit control
-Normalized unified amplitude
-Standardization of output structure
```

## 🛠️ Installation

### Pre-built Binaries (Recommended)

```shell
# Linux
wget https://github.com/liu-XiaoShu/AudioForgeXS/linux_output/audioForgeXS
chmod +x audioForgeXS
```

### Build from Source

```shell
git clone https://github.com/liu-XiaoShu/AudioForgeXS.git
cd AudioForgeXS
pip install -r requirements.txt
python build.py # supports linux/windows/macos
```

## 🚀 Quick Start

### Basic Processing Example

```shell
# Audio normalization
./audioForgeXS BasicMode -f audioNorm -i ./input/ -o ./normalized/

# Batch MP3 to WAV
./audioForgeXS BasicMode -f mp3ToWav -i ./mp3_files/ -o ./wav_output/
```

### Testset Generation Example

```shell
# Generate lighting control testset
./audioForgeXS GetTestSetMode -i ./raw_audio/ -c commands.txt -n 50 -o ./testset/
```

## 📄 Command File Format

Create `commands.txt`:

```shell
# One command per line
Turn on living room light
Turn off bedroom light
Adjust brightness
Change color mode
```

## 📜 Documentation

```python
/
```

## 🤝 Contributing

Welcome to submit suggestions via Issues or contribute through Pull Requests:

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -am 'Add some feature'`)
4. Push branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## MIT License

Copyright (c) 2024 liu-XiaoShu
