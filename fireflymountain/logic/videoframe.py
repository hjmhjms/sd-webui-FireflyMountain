import os

import cv2
import gradio as gr
import numpy as np
from tqdm import tqdm

from . import shared as shared


def Video2frame(srcVideoPath,outputFolder, bControlFps, nControlFps, bControlTime , nStartTimeInSec ,nEndTimeInSec,progress=gr.Progress()):
    shared.state.Begin()

    progress(0,desc="开始")
    #print("\n FireflyMountain:Video2frame 开始生成......")
    
    # 读取视频文件
    cap = cv2.VideoCapture(srcVideoPath)

    # 检查视频是否成功打开
    if not cap.isOpened():
        print("Error opening video file")
        return "Error opening video file"

    # 创建输出文件夹
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    srcFps = cap.get(cv2.CAP_PROP_FPS)
    srcTotalFrame = cap.get(cv2.CAP_PROP_FRAME_COUNT) 
    srcTotalSecond = srcTotalFrame/srcFps


    if bControlFps:
        targetFps = nControlFps
    else:
        targetFps = srcFps

    if bControlTime:
        targetStartTimeInSec = max(nStartTimeInSec,0)
        targetEndTimeInSec = min(nEndTimeInSec,srcTotalSecond)
        targetStartFrame = int(nStartTimeInSec * srcFps)
        targetEndFrame = int(nEndTimeInSec * srcFps)
    else:
        targetStartTimeInSec = 0
        targetEndTimeInSec = srcTotalSecond
        targetStartFrame = int(0)
        targetEndFrame = int(srcTotalFrame)

    targetFrameCount = int(min((targetEndTimeInSec-targetStartTimeInSec)*targetFps,srcTotalFrame))


    frame_indexes = set( np.linspace(max(targetStartFrame,0), targetEndFrame - 1, targetFrameCount , dtype=np.int))

    frame_count = 0

    print(targetStartFrame, targetEndFrame, srcTotalFrame,frame_indexes)

    for i in progress.tqdm(range(int(srcTotalFrame)),desc="转换中"):
        if shared.state.IsInterrupted():
            break

        # 读取帧并保存为图片
        ret, frame = cap.read()
        if ret:
            if i in frame_indexes:
                frame_count += 1
                # 指定输出文件名
                output_file = os.path.join(outputFolder, f'{frame_count:04d}.png')
                # print('\r geneframe:',output_file,end='')
                # 保存帧到输出文件
                #cv2.imwrite(output_file, frame)
                cv2.imencode('.png',frame)[1].tofile(output_file)

        #print(len(frame_indexes),i)

    # for i in progress.tqdm(frame_indexes,desc="转换中"):
    #     if shared.state.IsInterrupted():
    #         break
    # # 设置读取帧的位置
    #     cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    #     # 读取帧并保存为图片
    #     ret, frame = cap.read()
    #     if ret:
    #         # 指定输出文件名
    #         frame_count += 1    
    #         output_file = os.path.join(outputFolder, f'{frame_count:04d}.png')
    #         # print('\r geneframe:',output_file,end='')
    #         # 保存帧到输出文件
    #         #cv2.imwrite(output_file, frame)
    #         cv2.imencode('.png',frame)[1].tofile(output_file)

    # 释放视频对象
    cap.release()
    #print('\n FireflyMountain:Video2frame 完成!')

    return f"成功转换{frame_count}帧"
    
# -------------------------------------------------------------------------------------------------------

def Frame2video(imageDir,ouputDir,fps,mode,progress=gr.Progress()):
    #print('\n FireflyMountain:Frame2video 开始生成......')

    if not os.path.exists(ouputDir):
        os.makedirs(ouputDir)

    ret = None
    if mode =='.mp4':
        ret = Frame2videoMp4(imageDir,ouputDir,fps,progress)
    elif mode == '.avi':
        ret  = Frame2videoAvi(imageDir,ouputDir,fps,progress)
    
    #print('\n FireflyMountain:Frame2video 完成')
    return ret

def Frame2videoMp4(imageDir,ouputDir,fps,progress):
    shared.state.Begin()
    progress(0,desc="开始生成mp4")

    # 读取图像文件列表
    image_files = [f for f in os.listdir(imageDir) if f.endswith('.png') or f.endswith('.jpg')]
    image_files.sort()

    # 获取图像的宽度和高度
    #img = cv2.imread(os.path.join(imageDir, image_files[0]),cv2.IMREAD_UNCHANGED)
    img = cv2.imdecode( np.fromfile( os.path.join(imageDir, image_files[0]), dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    height, width, _ = img.shape

    # 创建输出视频对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(ouputDir+'/output.mp4', fourcc, fps, (width, height), isColor=True)
    num_images = len(image_files)
    frame_num = 0
    # 逐帧写入视频帧
    for image_file in progress.tqdm(image_files,desc="正在生成mp4"):
        if shared.state.IsInterrupted():
            break
        #print(image_file,type(image_file),str(image_file),image_files)
        image_path = os.path.join(imageDir, image_file)
        #frame = cv2.imread(image_path)
        frame = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8),cv2.IMREAD_UNCHANGED)
        out.write(frame)
        frame_num +=1
        # print('\r generating video:',f'{100*frame_num/num_images:5.2f}%',end='')

    # 释放视频对象
    out.release()

    return f"视频生成完毕，{ouputDir+'/output.mp4'}"

def Frame2videoAvi(imageDir,ouputDir,fps,progress):
    shared.state.Begin()

    progress(0,desc="开始生成avi")

    # 读取图像文件列表
    image_files = [f for f in os.listdir(imageDir) if f.endswith('.png') or f.endswith('.jpg')]
    image_files.sort()

    # 获取图像的宽度和高度
    #img = cv2.imread(os.path.join(imageDir, image_files[0]),cv2.IMREAD_UNCHANGED)
    img = cv2.imdecode(np.fromfile(os.path.join(imageDir, image_files[0]), dtype=np.uint8),cv2.IMREAD_UNCHANGED)

    height, width, _ = img.shape

    # 创建输出视频对象
    # 格式表在这里：自己查一下对照表
    # https://learn.microsoft.com/en-us/windows/win32/medfound/video-fourccs
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(ouputDir+'/output.avi', fourcc, fps, (width, height), isColor=True)
    num_images = len(image_files)
    frame_num = 0
    # 逐帧写入视频帧
    for image_file in progress.tqdm(image_files,"正在生成avi"):
        if shared.state.IsInterrupted():
            break
        image_path = os.path.join(imageDir, image_file)
        #frame = cv2.imread(image_path)
        frame = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8),cv2.IMREAD_UNCHANGED)
        out.write(frame)
        frame_num +=1
        # print('\r generating video:',f'{100*frame_num/num_images:5.2f}%',end='')

    # 释放视频对象
    out.release()
    return f"视频生成完毕，{ouputDir+'/output.avi'}"



