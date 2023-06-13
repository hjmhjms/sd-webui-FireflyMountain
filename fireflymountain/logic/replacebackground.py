import os

import cv2
import gradio as gr
import numpy as np
from tqdm import tqdm
import rembg
from PIL import Image as ModPILImage
from PIL import ImageColor as ModPILImageColor
from typing import List, Optional, Union
from glob import glob

from  . import shared as shared

#dictRembgConfig=
# {
#             "model": model,
#             "return_mask": return_mask,
#             "alpha_matting": alpha_matting,
#             "alpha_matting_foreground_threshold": alpha_matting_foreground_threshold,
#             "alpha_matting_background_threshold": alpha_matting_background_threshold,
#             "alpha_matting_erode_size": alpha_matting_erode_size,
#         }

class RembgProcesser:
    def __init__(self,model:str,alpha_matting:bool,alpha_matting_foreground_threshold :int,alpha_matting_background_threshold :int,alpha_matting_erode_size: int ) -> None:
        self.model = model
        self.alpha_matting = alpha_matting
        self.alpha_matting_foreground_threshold =alpha_matting_foreground_threshold
        self.alpha_matting_background_threshold =alpha_matting_background_threshold
        self.alpha_matting_erode_size = alpha_matting_erode_size

    def _ReturnMaskOne(self,srcImg:ModPILImage.Image):
        img = rembg.remove(
                srcImg,
                session=rembg.new_session(self.model),
                only_mask=True,
                alpha_matting=self.alpha_matting,
                alpha_matting_foreground_threshold=self.alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=self.alpha_matting_background_threshold,
                alpha_matting_erode_size=self.alpha_matting_erode_size,
            )
        
        return img

    def ReturnMaskOne(self,srcImgPath,tarImgPath):
        srcimg = ModPILImage.open(srcImgPath)
        img = self._ReturnMaskOne(srcimg)
        img.save(tarImgPath)
    
    def ReturnMaskOne2(self,srcImgPath,progress):
        progress(0,desc="开始")

        srcimg = ModPILImage.open(srcImgPath)
        img = self._ReturnMaskOne(srcimg)
        return img    


    def _RemoveBgOne(self,srcImg:ModPILImage.Image):
        img = rembg.remove(
                srcImg,
                session=rembg.new_session(self.model),
                only_mask=False,
                alpha_matting=self.alpha_matting,
                alpha_matting_foreground_threshold=self.alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=self.alpha_matting_background_threshold,
                alpha_matting_erode_size=self.alpha_matting_erode_size,
            )
        
        return img

    def RemoveBgOne(self,srcImgPath,tarImgPath):
        srcimg = ModPILImage.open(srcImgPath)
        img = self._RemoveBgOne(srcimg)
        img.save(tarImgPath)
    
    def RemoveBgOne2(self,srcImgPath,progress):
        progress(0,desc="开始")

        srcimg = ModPILImage.open(srcImgPath)
        img = self._RemoveBgOne(srcimg)
        return img
    


    def RemoveBg(self,srcImgDir,tarImgDir,progress):
        if not os.path.exists(tarImgDir):
            os.makedirs(tarImgDir)

        shared.state.Begin()

        progress(0,desc="开始")
        
        listImgPath = [file for ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] for file in glob(srcImgDir + '/*.' + ext.lower())]
        listImgPath.sort()

        i = 0
        for srcImgPath in progress.tqdm(listImgPath, desc="转换中"):
            if shared.state.IsInterrupted():
                break
            tarImgPath =  os.path.join(tarImgDir, os.path.basename(srcImgPath))
            self.RemoveBgOne(srcImgPath,tarImgPath)
            i=i+1
        
        return f"成功消除了背景{i}张,共{len(listImgPath)}张"


    def _ReplaceBgOne(self,srcImg:ModPILImage.Image,bgImg:ModPILImage.Image)->ModPILImage.Image:
        img = self._RemoveBgOne(srcImg)
        #img = img.convert('RGBA')
        alpha = img.split()[-1]
        mask = ModPILImage.merge('L', (alpha,))
        result = ModPILImage.composite(img, bgImg, mask)
        return result
    
    def ReplaceBgOne(self,srcImgPath,tarImgPath,bgImgPath):
        #print("ReplaceBgOne",srcImgPath,tarImgPath,bgImgPath)
        img = ModPILImage.open(srcImgPath)
        imgbg = ModPILImage.open(bgImgPath)
        result = self._ReplaceBgOne(img,imgbg)
        result.save(tarImgPath)    

    def ReplaceBgOne2(self,srcImgPath,bgImgDir,progress):
        progress(0,desc="开始")

        listImgPath = [file for ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] for file in glob(bgImgDir + '/*.' + ext.lower())]
        listImgPath.sort()
        bgImgPath = listImgPath[0]

        img = ModPILImage.open(srcImgPath)
        imgbg = ModPILImage.open(bgImgPath)
        result = self._ReplaceBgOne(img,imgbg)
        return  result

    def _ReplaceBgColorOne(self,srcImg:ModPILImage.Image,tupleColor):
        colorImg = ModPILImage.new('RGB', srcImg.size, tupleColor)
        result = self._ReplaceBgOne(srcImg,colorImg)
        return result

    def ReplaceBgColorOne(self,srcImgPath,tarImgPath,tupleColor):
        img = ModPILImage.open(srcImgPath)
        result = self._ReplaceBgColorOne(img,tupleColor)
        result.save(tarImgPath)

    def ReplaceBgColorOne2(self,srcImgPath,strColor,progress):
        progress(0,desc="开始")
        tupleColor = ModPILImageColor.getcolor(strColor,"RGB")
        img = ModPILImage.open(srcImgPath)
        result = self._ReplaceBgColorOne(img,tupleColor)
        progress(1,desc="完成")
        return result

    def ReplaceBg(self,srcImgDir,tarImgDir,bgImgDir,progress):
        if not os.path.exists(tarImgDir):
            os.makedirs(tarImgDir)        
        shared.state.Begin()

        progress(0,desc="开始")

        listImgPath = [file for ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] for file in glob(srcImgDir + '/*.' + ext.lower())]
        listImgPath.sort()

        listBgPath = [file for ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] for file in glob(bgImgDir + '/*.' + ext.lower())]
        listBgPath.sort()
        
        i = 0
        for srcImgPath in progress.tqdm(listImgPath, desc="转换中"):
            if shared.state.IsInterrupted():
                break
            if i >= len(listBgPath):
                bgPath = listBgPath[-1]
            else:
                bgPath = listBgPath[i]
            i=i+1
            tarImgPath =  os.path.join(tarImgDir, os.path.basename(srcImgPath))
            self.ReplaceBgOne(srcImgPath,tarImgPath,bgPath)
            
        return f"成功替换了背景{i}张,共{len(listImgPath)}张"


    def ReplaceBgColor(self,srcImgDir,tarImgDir,strColor,progress):
        if not os.path.exists(tarImgDir):
            os.makedirs(tarImgDir)
                    
        shared.state.Begin()

        progress(0,desc="开始")

        tupleColor = ModPILImageColor.getcolor(strColor,"RGB")
        listImgPath = [file for ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] for file in glob(srcImgDir + '/*.' + ext.lower())]
        listImgPath.sort()

        i = 0
        for srcImgPath in progress.tqdm(listImgPath, desc="转换中"):
            if shared.state.IsInterrupted():
                break
            tarImgPath =  os.path.join(tarImgDir, os.path.basename(srcImgPath))
            self.ReplaceBgColorOne(srcImgPath,tarImgPath,tupleColor)
            i=i+1
            
        return f"成功替换了背景颜色{i}张,共{len(listImgPath)}张"


    def ReturnMask(self,srcImgDir,tarImgDir,progress):
        if not os.path.exists(tarImgDir):
            os.makedirs(tarImgDir)

        shared.state.Begin()

        progress(0,desc="开始")
        
        listImgPath = [file for ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] for file in glob(srcImgDir + '/*.' + ext.lower())]
        listImgPath.sort()

        i = 0
        for srcImgPath in progress.tqdm(listImgPath, desc="转换中"):
            if shared.state.IsInterrupted():
                break
            tarImgPath =  os.path.join(tarImgDir, os.path.basename(srcImgPath))
            self.ReturnMaskOne(srcImgPath,tarImgPath)
            i=i+1
        
        return f"成功消除了背景{i}张,共{len(listImgPath)}张"
    