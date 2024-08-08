# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project Name: yolov5
File Name: window.py.py
Author: 陆小马
Description：图形化界面，可以检测摄像头、视频和图片文件
-------------------------------------------------
"""
import copy
import os
# 导入库
import shutil
import PyQt5.QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import threading
import sys
from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn
import os.path as osp

from ui.common import DetectMultiBackend
from ui.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from ui.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from ui.plots import Annotator, colors, save_one_box
from ui.torch_utils import select_device, time_sync
import time
import numpy as np


# 在原先的基础上输出实际的信息堆积对
# 添加历史记录功能。
class MainWindow(QTabWidget):
    # 基本配置不动，然后只动第三个界面
    def __init__(self):
        # 初始化界面
        super().__init__()
        self.setWindowTitle('Target detection system')
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("../images/UI/logo.png"))
        self.output_size = 480
        self.img2predict = ""
        self.device = 'cpu'
        self.init_vid_id = '0'
        # self.vid_source = int(self.init_vid_id)
        self.vid_source = self.init_vid_id
        self.stopEvent = threading.Event()
        self.webcam = True
        self.stopEvent.clear()
        self.model = self.model_load(weights="../runs/train/exp9/weights/best.pt",
                                     device=self.device)  # todo 指明模型加载的位置的设备
        self.conf_thres = 0.25  # confidence threshold
        self.iou_thres = 0.45  # NMS IOU thresholdv
        self.vid_gap = 30  # 摄像头视频帧保存间隔。

        self.initUI()
        self.reset_vid()

    # 模型初始化
    @torch.no_grad()
    def model_load(self, weights="",  # model.pt path(s)
                   device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
                   half=False,  # use FP16 half-precision inference
                   dnn=False,  # use OpenCV DNN for ONNX inference
                   ):
        device = select_device(device)
        half &= device.type != 'cpu'  # half precision only supported on CUDA
        model = DetectMultiBackend(weights, device=device, dnn=dnn)
        stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
        # Half
        half &= pt and device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
        if pt:
            model.model.half() if half else model.model.float()
        # print(model.onnx)
        print("模型加载完成，模型信息如上!")
        return model

    '''
    ***界面初始化***
    '''

    def initUI(self):
        # 图片检测界面
        font_title = QFont('楷体', 16)
        font_main = QFont('楷体', 14)
        img_detection_widget = QWidget()
        img_detection_layout = QVBoxLayout()
        img_detection_title = QLabel("图片识别功能")
        img_detection_title.setFont(font_title)
        mid_img_widget = QWidget()
        mid_img_layout = QHBoxLayout()
        self.left_img = QLabel()
        self.right_img = QLabel()
        self.left_img.setPixmap(QPixmap("../images/UI/up.jpeg"))
        self.right_img.setPixmap(QPixmap("../images/UI/right.jpeg"))
        self.left_img.setAlignment(Qt.AlignCenter)
        self.right_img.setAlignment(Qt.AlignCenter)
        mid_img_layout.addWidget(self.left_img)
        # todo 统一变化为更新左图
        self.img_num_label = QLabel("当前数量：待检测")
        self.img_num_label.setFont(font_main)
        mid_img_widget.setLayout(mid_img_layout)
        up_img_button = QPushButton("上传图片")
        det_img_button = QPushButton("开始检测")
        up_img_button.clicked.connect(self.upload_img)
        det_img_button.clicked.connect(self.detect_img)
        up_img_button.setFont(font_main)
        det_img_button.setFont(font_main)
        up_img_button.setStyleSheet("QPushButton{color:white}"
                                    "QPushButton:hover{background-color: rgb(2,110,180);}"
                                    "QPushButton{background-color:rgb(48,124,208)}"
                                    "QPushButton{border:2px}"
                                    "QPushButton{border-radius:5px}"
                                    "QPushButton{padding:5px 5px}"
                                    "QPushButton{margin:5px 5px}")
        det_img_button.setStyleSheet("QPushButton{color:white}"
                                     "QPushButton:hover{background-color: rgb(2,110,180);}"
                                     "QPushButton{background-color:rgb(48,124,208)}"
                                     "QPushButton{border:2px}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{padding:5px 5px}"
                                     "QPushButton{margin:5px 5px}")
        img_detection_layout.addWidget(img_detection_title, alignment=Qt.AlignCenter)
        img_detection_layout.addWidget(mid_img_widget, alignment=Qt.AlignCenter)
        img_detection_layout.addWidget(self.img_num_label)
        img_detection_layout.addWidget(up_img_button)
        img_detection_layout.addWidget(det_img_button)
        img_detection_widget.setLayout(img_detection_layout)

        # 视频识别子页面
        vid_detection_widget = QWidget()
        vid_detection_layout = QVBoxLayout()
        vid_title = QLabel("视频检测功能")
        vid_title.setFont(font_title)
        self.vid_img = QLabel()
        self.vid_img.setPixmap(QPixmap("../images/UI/up.jpeg"))
        vid_title.setAlignment(Qt.AlignCenter)
        self.vid_img.setAlignment(Qt.AlignCenter)
        self.webcam_detection_btn = QPushButton("摄像头实时监测")
        self.mp4_detection_btn = QPushButton("视频文件检测")
        self.vid_stop_btn = QPushButton("停止检测")
        self.webcam_detection_btn.setFont(font_main)
        self.mp4_detection_btn.setFont(font_main)
        self.vid_stop_btn.setFont(font_main)
        self.webcam_detection_btn.setStyleSheet("QPushButton{color:white}"
                                                "QPushButton:hover{background-color: rgb(2,110,180);}"
                                                "QPushButton{background-color:rgb(48,124,208)}"
                                                "QPushButton{border:2px}"
                                                "QPushButton{border-radius:5px}"
                                                "QPushButton{padding:5px 5px}"
                                                "QPushButton{margin:5px 5px}")
        self.mp4_detection_btn.setStyleSheet("QPushButton{color:white}"
                                             "QPushButton:hover{background-color: rgb(2,110,180);}"
                                             "QPushButton{background-color:rgb(48,124,208)}"
                                             "QPushButton{border:2px}"
                                             "QPushButton{border-radius:5px}"
                                             "QPushButton{padding:5px 5px}"
                                             "QPushButton{margin:5px 5px}")
        self.vid_stop_btn.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton:hover{background-color: rgb(2,110,180);}"
                                        "QPushButton{background-color:rgb(48,124,208)}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:5px}"
                                        "QPushButton{padding:5px 5px}"
                                        "QPushButton{margin:5px 5px}")
        self.webcam_detection_btn.clicked.connect(self.open_cam)
        self.mp4_detection_btn.clicked.connect(self.open_mp4)
        self.vid_stop_btn.clicked.connect(self.close_vid)
        vid_detection_layout.addWidget(vid_title)
        vid_detection_layout.addWidget(self.vid_img)
        # todo 添加摄像头检测标签逻辑
        self.vid_num_label = QLabel("当前数量：{}".format("等待检测"))
        self.vid_num_label.setFont(font_main)
        vid_detection_layout.addWidget(self.vid_num_label)
        vid_detection_layout.addWidget(self.webcam_detection_btn)
        vid_detection_layout.addWidget(self.mp4_detection_btn)
        vid_detection_layout.addWidget(self.vid_stop_btn)
        vid_detection_widget.setLayout(vid_detection_layout)

        # 主页面
        about_widget = QWidget()
        about_layout = QVBoxLayout()
        about_title = QLabel('欢迎使用基于YOLOV5的目标检测系统\n'
                             '（调试关注: 陆小马公众号）')  # todo 修改欢迎词语
        about_title.setFont(QFont('楷体', 18))
        about_title.setAlignment(Qt.AlignCenter)
        about_img = QLabel()
        about_img.setPixmap(QPixmap('../images/UI/logo1.jpg'))
        record_button = QPushButton("查看历史记录")
        record_button.setFont(font_main)
        record_button.clicked.connect(self.check_record)
        record_button.setStyleSheet("QPushButton{color:white}"
                                        "QPushButton:hover{background-color: rgb(2,110,180);}"
                                        "QPushButton{background-color:rgb(48,124,208)}"
                                        "QPushButton{border:2px}"
                                        "QPushButton{border-radius:5px}"
                                        "QPushButton{padding:5px 5px}"
                                        "QPushButton{margin:5px 5px}")
        about_img.setAlignment(Qt.AlignCenter)
        label_super = QLabel()  # todo 更换作者信息
        label_super.setText("<a href='https://blotemj.blog.csdn.net'>找到我-->陆小马</a>")
        label_super.setFont(QFont('楷体', 16))
        label_super.setOpenExternalLinks(True)
        label_super.setAlignment(Qt.AlignRight)
        about_layout.addWidget(about_title)
        about_layout.addStretch()
        about_layout.addWidget(about_img)
        about_layout.addStretch()
        about_layout.addWidget(record_button)
        about_layout.addWidget(label_super)
        about_widget.setLayout(about_layout)
        self.left_img.setAlignment(Qt.AlignCenter)

        self.addTab(about_widget, '主页')
        self.addTab(img_detection_widget, '图片检测')
        self.addTab(vid_detection_widget, '视频检测')

        self.setTabIcon(0, QIcon('../images/UI/logo.png'))
        self.setTabIcon(1, QIcon('../images/UI/logo.png'))
        self.setTabIcon(2, QIcon('../images/UI/logo.png'))

    # 图片上传
    def upload_img(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.jpg *.png *.tif *.jpeg')
        if fileName:
            suffix = fileName.split(".")[-1]
            save_path = osp.join("../images/tmp", "tmp_upload." + suffix)
            shutil.copy(fileName, save_path)
            im0 = cv2.imread(save_path)
            resize_scale = self.output_size / im0.shape[0]
            im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
            cv2.imwrite("../images/tmp/upload_show_result.jpg", im0)
            self.img2predict = fileName
            self.left_img.setPixmap(QPixmap("../images/tmp/upload_show_result.jpg"))
            # todo 上传图片之后右侧的图片重置，
            # self.right_img.setPixmap(QPixmap("../images/UI/right.jpeg"))
            self.img_num_label.setText("当前数量：待检测")
            # QLabel()

    # 图片检测
    def detect_img(self):
        txt_results = []
        model = self.model
        output_size = self.output_size
        source = self.img2predict  # file/dir/URL/glob, 0 for webcam
        imgsz = [640, 640]  # inference size (pixels)
        conf_thres = self.conf_thres  # confidence threshold
        iou_thres = self.iou_thres  # NMS IOU threshold
        max_det = 1000  # maximum detections per image
        # device = self.device  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img = False  # show results
        save_txt = False  # save results to *.txt
        save_conf = False  # save confidences in --save-txt labels
        save_crop = False  # save cropped prediction boxes
        nosave = False  # do not save images/videos
        classes = None  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms = False  # class-agnostic NMS
        augment = False  # ugmented inference
        visualize = False  # visualize features
        line_thickness = 3  # bounding box thickness (pixels)
        hide_labels = False  # hide labels
        hide_conf = False  # hide confidences
        half = False  # use FP16 half-precision inference
        dnn = False  # use OpenCV DNN for ONNX inference
        print(source)
        if source == "":
            QMessageBox.warning(self, "请上传", "请先上传图片再进行检测")
        else:
            source = str(source)
            device = select_device(self.device)
            webcam = False
            stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
            imgsz = check_img_size(imgsz, s=stride)  # check image size
            save_img = not nosave and not source.endswith('.txt')  # save inference images
            # Dataloader
            if webcam:
                view_img = check_imshow()
                cudnn.benchmark = True  # set True to speed up constant image size inference
                dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt and not jit)
                bs = len(dataset)  # batch_size
            else:
                dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit)
                bs = 1  # batch_size
            vid_path, vid_writer = [None] * bs, [None] * bs
            # Run inference
            if pt and device.type != 'cpu':
                model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
            dt, seen = [0.0, 0.0, 0.0], 0
            for path, im, im0s, vid_cap, s in dataset:
                t1 = time_sync()
                im = torch.from_numpy(im).to(device)
                im = im.half() if half else im.float()  # uint8 to fp16/32
                im /= 255  # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim
                t2 = time_sync()
                dt[0] += t2 - t1
                pred = model(im, augment=augment, visualize=visualize)
                t3 = time_sync()
                dt[1] += t3 - t2
                # NMS
                pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
                dt[2] += time_sync() - t3
                for i, det in enumerate(pred):  # per image
                    seen += 1
                    if webcam:  # batch_size >= 1
                        p, im0, frame = path[i], im0s[i].copy(), dataset.count
                        s += f'{i}: '
                    else:
                        p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)
                    p = Path(p)  # to Path
                    s += '%gx%g ' % im.shape[2:]  # print string
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                    imc = im0.copy() if save_crop else im0  # for save_crop
                    annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                    if len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()
                        # Print results
                        for c in det[:, -1].unique():
                            n = (det[:, -1] == c).sum()  # detections per class
                            s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                        # Write results
                        for *xyxy, conf, cls in reversed(det):
                            # todo 记录坐标信息
                            location = list(torch.tensor(xyxy).view(1, 4).cpu().numpy()[0])
                            re = [names[int(cls)], conf.cpu().numpy()] + location
                            txt_results.append(re)
                            if save_txt:  # Write to file
                                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(
                                    -1).tolist()  # normalized xywh
                                line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                            if save_img or save_crop or view_img:  # Add bbox to image
                                c = int(cls)  # integer class
                                label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                                annotator.box_label(xyxy, label, color=colors(c, True))
                    LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')
                    im0 = annotator.result()
                    im_record = copy.deepcopy(im0)
                    resize_scale = output_size / im0.shape[0]
                    im0 = cv2.resize(im0, (0, 0), fx=resize_scale, fy=resize_scale)
                    cv2.imwrite("../images/tmp/single_result.jpg", im0)
                    # self.right_img.setPixmap(QPixmap("../images/tmp/single_result.jpg"))
                    self.left_img.setPixmap(QPixmap("../images/tmp/single_result.jpg"))
                    # 把这里的结果进行保存，按照时间进行保存
                    time_re = str(time.strftime('result_%Y-%m-%d_%H-%M-%S_%A'))
                    cv2.imwrite("record/img/{}.jpg".format(time_re), im_record)
                    # 保存txt记录文件
                    np.savetxt('record/img/{}.txt'.format(time_re), np.array(txt_results), fmt="%s %s %s %s %s %s",
                               delimiter="\n")
                    QMessageBox.information(self, "检测成功", "日志已保存！")
                    self.img_num_label.setText("当前数量：{}".format(len(txt_results)))

    def check_record(self):
        os.startfile(osp.join(os.path.abspath(os.path.dirname(__file__)),"record"))

    # 摄像头检测
    def open_cam(self):
        self.webcam_detection_btn.setEnabled(False)
        self.mp4_detection_btn.setEnabled(False)
        self.vid_stop_btn.setEnabled(True)
        self.vid_source = '0'
        self.webcam = True
        th = threading.Thread(target=self.detect_vid)
        th.start()

    # 视频文件检测
    def open_mp4(self):
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.mp4 *.avi')
        if fileName:
            self.webcam_detection_btn.setEnabled(False)
            self.mp4_detection_btn.setEnabled(False)
            self.vid_source = fileName
            self.webcam = False
            th = threading.Thread(target=self.detect_vid)
            th.start()

    # 视频检测主函数
    def detect_vid(self):
        model = self.model
        output_size = self.output_size
        imgsz = [640, 640]  # inference size (pixels)
        conf_thres = self.conf_thres  # confidence threshold
        iou_thres = self.iou_thres  # NMS IOU threshold
        max_det = 1000  # maximum detections per image
        # device = self.device  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img = False  # show results
        save_txt = False  # save results to *.txt
        save_conf = False  # save confidences in --save-txt labels
        save_crop = False  # save cropped prediction boxes
        nosave = False  # do not save images/videos
        classes = None  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms = False  # class-agnostic NMS
        augment = False  # ugmented inference
        visualize = False  # visualize features
        line_thickness = 3  # bounding box thickness (pixels)
        hide_labels = False  # hide labels
        hide_conf = False  # hide confidences
        half = False  # use FP16 half-precision inference
        dnn = False  # use OpenCV DNN for ONNX inference
        source = str(self.vid_source)
        webcam = self.webcam
        # print(source)
        # print(webcam)
        device = select_device(self.device)
        stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
        imgsz = check_img_size(imgsz, s=stride)  # check image size
        save_img = not nosave and not source.endswith('.txt')  # save inference images
        if webcam:
            view_img = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt and not jit)
            # 如果是cam，应该设置rlease
            bs = len(self.dataset)  # batch_size
        else:
            self.dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit)
            bs = 1  # batch_size
        vid_path, vid_writer = [None] * bs, [None] * bs
        # Run inference
        if pt and device.type != 'cpu':
            model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
        dt, seen = [0.0, 0.0, 0.0], 0
        for path, im, im0s, vid_cap, s in self.dataset:
            t1 = time_sync()
            im = torch.from_numpy(im).to(device)
            im = im.half() if half else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim
            t2 = time_sync()
            dt[0] += t2 - t1
            # Inference
            pred = model(im, augment=augment, visualize=visualize)
            t3 = time_sync()
            dt[1] += t3 - t2
            # NMS
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
            dt[2] += time_sync() - t3
            # Process predictions
            for i, det in enumerate(pred):  # per image
                txt_results = []
                seen += 1
                if webcam:  # batch_size >= 1
                    p, im0, frame = path[i], im0s[i].copy(), self.dataset.count
                    s += f'{i}: '
                else:
                    p, im0, frame = path, im0s.copy(), getattr(self.dataset, 'frame', 0)
                p = Path(p)  # to Path
                s += '%gx%g ' % im.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                imc = im0.copy() if save_crop else im0  # for save_crop
                annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()
                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        location = list(torch.tensor(xyxy).view(1, 4).cpu().numpy()[0])
                        re = [names[int(cls)], conf.cpu().numpy()] + location
                        txt_results.append(re)
                        if save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(
                                -1).tolist()  # normalized xywh
                            line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                        if save_img or save_crop or view_img:  # Add bbox to image
                            c = int(cls)  # integer class
                            label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                            annotator.box_label(xyxy, label, color=colors(c, True))
                LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')
                im0 = annotator.result()
                im_record = copy.deepcopy(im0)
                frame = im0
                resize_scale = output_size / frame.shape[0]
                frame_resized = cv2.resize(frame, (0, 0), fx=resize_scale, fy=resize_scale)

                cv2.imwrite("../images/tmp/single_result_vid.jpg", frame_resized)
                self.vid_img.setPixmap(QPixmap("../images/tmp/single_result_vid.jpg"))
                self.vid_num_label.setText("当前数量：{}".format(len(txt_results)))


                # todo 摄像头逻辑保存
                # 把这里的结果进行保存，按照时间进行保存
                if i%self.vid_gap == 0:
                    time_re = str(time.strftime('result_%Y-%m-%d_%H-%M-%S_%A'))
                    cv2.imwrite("record/vid/{}.jpg".format(time_re), im_record)
                    # 保存txt记录文件
                    if len(txt_results) > 0:
                        np.savetxt('record/vid/{}.txt'.format(time_re), np.array(txt_results), fmt="%s %s %s %s %s %s",
                                   delimiter="\n")
                    print("视频日志已保存")
                    # QMessageBox.information(self, "检测成功", "日志已保存！")

            if cv2.waitKey(25) & self.stopEvent.is_set() == True:
                self.stopEvent.clear()
                self.webcam_detection_btn.setEnabled(True)
                self.mp4_detection_btn.setEnabled(True)
                if self.dataset.cap != None:
                    self.dataset.cap.release()
                self.reset_vid()
                break

    # 摄像头重置
    def reset_vid(self):
        self.webcam_detection_btn.setEnabled(True)
        self.mp4_detection_btn.setEnabled(True)
        self.vid_img.setPixmap(QPixmap("../images/UI/up.jpeg"))
        self.vid_source = self.init_vid_id
        self.webcam = True
        self.vid_num_label.setText("当前数量：{}".format("等待检测"))

    # 视频线程关闭
    def close_vid(self):
        self.stopEvent.set()
        self.reset_vid()

    # 界面关闭
    def closeEvent(self, event):
        reply = QMessageBox.question(self,
                                     'quit',
                                     "Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            event.accept()
        else:
            event.ignore()


# todo 屏蔽主页，只展示主要部分
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
