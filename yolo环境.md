### events.out.tfevents文件

events.out.tfevents文件通常存储训练过程中的事件和摘要数据的文件。您可以使用TensorBoard 来可视化这些事件文件，以便更好地理解模型的训练和评估过程。

```bash
pip install tensorboard
```

在命令行中，导航到包含 events.out.tfevents 文件的目录，并运行以下命令来启动 TensorBoard：

```bash
tensorboard --logdir=.
```

# yolo使用步骤

## 环境搭建

py3.8

miniconda

anaconda

国内镜像源

清华，阿里

## yolov5，v8环境

GPU GTX1650

CUDA12.4

cudnn

cu121

pip install

pytorch

## 下载yolo源码

安装依赖包

终端使用

cmd

anaconda prompt

## 训练

labelimg，labelme

数据集datasets，train，val，test

模型n，m，s

yaml

参数

### torch安装

```bash
yolov8环境
环境	配置
硬件环境	GPU
Cuda版本	Cuda 12.4（无需配置cuDNN即可运行）
虚拟环境管理器	Anaconda
Python版本	3.8
Torch版本	torch-2.3.1-cu121-cp38，torchaudio-2.3.1-cu121, torchvsion-0.18.1

conda 命令行
conda activate yolov8
下载地址torch，trochaudio，torchvision
https://download.pytorch.org/whl/cu121
迅雷下载
torch-2.3.1+cu121-cp38-cp38-win_amd64.whl
torchaudio-2.3.1+cu121-cp38-cp38-win_amd64.whl
torchvision-0.18.1+cu121-cp38-cp38-win_amd64.whl
迅雷下载链接
https://download.pytorch.org/whl/cu121/torch-2.3.1%2Bcu121-cp38-cp38-win_amd64.whl#sha256=c45c34c482fc20a32fa03511d3e66eb73d9dde0a1e6baffe9f8794d7d9cc6d04
https://download.pytorch.org/whl/cu121/torchvision-0.18.1%2Bcu121-cp38-cp38-win_amd64.whl#sha256=54b167a0f8c17b568c0d7191aec45f77f6af4d9b0b8549e1857b34babbc5d9a6
https://download.pytorch.org/whl/cu121/torchaudio-2.3.1%2Bcu121-cp38-cp38-win_amd64.whl#sha256=b4d1588bc27447b32c9ac9e3440ad072aa35c765cd45191befee7c2300e23e6b
conda命令行安装
pip install "torch-2.3.1+cu121-cp38-cp38-win_amd64.whl" "torchaudio-2.3.1+cu121-cp38-cp38-win_amd64.whl" "torchvision-0.18.1+cu121-cp38-cp38-win_amd64.whl" -i https://pypi.tuna.tsinghua.edu.cn/simple


v2.3.1
Conda
Linux and Windows
# CUDA 12.1
conda install pytorch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 pytorch-cuda=12.1 -c pytorch -c nvidia
# CPU Only
conda install pytorch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 cpuonly -c pytorch

Wheel
Linux and Windows
# CUDA 12.1
pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121
# CPU only
pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu

#镜像
https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
```
