# 计算环境自动管理

v0.5.4 起，`CareerAgent_Start.bat` 会自动判断电脑是否具备 NVIDIA GPU，并安装匹配的 PyTorch 运行环境。

## 普通用户需要准备什么

- Windows 10/11；
- Python 3.11 或 3.12；
- 使用 GPU 时，需要安装可用的 NVIDIA 显卡驱动；
- 不要求手动安装完整 CUDA Toolkit。

第一次启动时，启动器会自动执行：

1. 检测 `nvidia-smi`；
2. 有 NVIDIA GPU 时从 PyTorch 官方 `cu128` 源安装 `torch + torchaudio`；
3. 没有 NVIDIA GPU 时安装 CPU 版；
4. 安装 FunASR、faster-whisper、RapidOCR 等依赖；
5. 把 PyTorch wheel 自带的 CUDA/cuDNN DLL 路径注册给 CTranslate2；
6. 检查 SenseVoiceSmall、Paraformer、Whisper 最终会使用 CPU 还是 GPU；
7. 将检测结果写入 `data/runtime/compute_environment.json`。

## 配置项

```env
CAREERAGENT_ACCELERATOR=auto
CAREERAGENT_ALLOW_CPU_FALLBACK=true
PYTORCH_CUDA_INDEX_URL=https://download.pytorch.org/whl/cu128
PYTORCH_CPU_INDEX_URL=https://download.pytorch.org/whl/cpu
```

`CAREERAGENT_ACCELERATOR`：

- `auto`：推荐；检测到 NVIDIA GPU 就使用 CUDA，否则使用 CPU；
- `cpu`：强制 CPU；
- `cuda`：强制尝试 GPU。

如果 CUDA 版安装或自检失败，`CAREERAGENT_ALLOW_CPU_FALLBACK=true` 会自动安装 CPU 版，保证采集和文本处理功能仍可启动。

## 页面检查

进入“作品转文字”，页面会显示：

- NVIDIA 显卡和驱动；
- SenseVoiceSmall 实际设备；
- Paraformer 实际设备；
- Whisper 实际设备；
- PyTorch、CTranslate2 和缺失 DLL 的诊断信息。

## 更新时为什么不会把 CUDA 版覆盖回 CPU

`requirements-asr.txt` 不再声明 `torch` 和 `torchaudio`。这两个包只由启动器根据硬件安装，避免普通 `pip install -r requirements-asr.txt` 把 CUDA 版 PyTorch 覆盖成 CPU 版。
