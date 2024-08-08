#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：yolov5
@File    ：images_half.py
@Author  ：lxm
@Date    ：2022/3/2 12:03 
@Description：
'''
import cv2
import os
import os.path as osp

img_paths =[osp.join("lxm/", x) for x in os.listdir("lxm/")]
for img_path in img_paths:
    img = cv2.imread(img_path)
    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    cv2.imwrite(img_path, img)