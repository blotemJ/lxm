import torch
import torchvision
import sys

# 查看Python & PyTorch & Torchvision版本兼容性
print("python:" + sys.version)
print(sys.version_info)
print("是否可用：", torch.cuda.is_available())  # 查看GPU是否可用
print("GPU数量：", torch.cuda.device_count())  # 查看GPU数量
print("torch版本：", torch.version.__version__)
print("torchvision:" + torchvision.__version__)
print("torch方法查看CUDA版本：", torch.version.cuda)  # torch方法查看CUDA版本
print("GPU索引号：", torch.cuda.current_device())  # 查看GPU索引号
print("GPU名称：", torch.cuda.get_device_name(0))  # 根据索引号得到GPU名称
