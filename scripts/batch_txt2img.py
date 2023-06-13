import copy
import math
import os
import re
import sys
import traceback

import gradio as gr
import modules.scripts as scripts
import pandas as pd
import piexif
from modules.processing import Processed, create_infotext, process_images
from modules.script_callbacks import (ImageSaveParams,
                                      before_image_saved_callback)
from modules.sd_hijack import model_hijack
from modules.shared import cmd_opts, opts, state
from PIL import Image, ImageFilter, PngImagePlugin

re_findidx = re.compile(
    r'(?=\S)(\d+)\.(?:[P|p][N|n][G|g]?|[J|j][P|p][G|g]?|[J|j][P|p][E|e][G|g]?|[W|w][E|e][B|b][P|p]?)\b')
re_findname = re.compile(r'[\w-]+?(?=\.)')


class Script(scripts.Script):
    def title(self):
        return '[FireflyMountain] batch txt2img'

    def description(self):
        return '萤火山 批处理txt2img'

    def show(self, is_img2img):
        return not is_img2img

    def ui(self, is_img2img):
        self.max_controlnet_models = opts.data.get("control_net_max_models_num", 1)

        gr.Markdown(""" 
        使用说明：产生第1个controlnet input directory的数量的图片，其他controlnet input 可以小于第1个。产出的文件名和第1个controlnet input一样。
        """)

        outputDir = gr.Textbox(label='Output directory',placeholder='不填就默认到输出文件夹', lines=1)

        with gr.Row(visible=True) as cn_options:
            controlnetDirs = []
            with gr.Group():
                with gr.Tabs():
                    for i in range(self.max_controlnet_models):
                        with gr.Tab(f"ControlNet-{i}", open=False):
                            controlnetDirs.append(gr.Textbox(label='ControlNet input directory', lines=1))


        return [
            outputDir,
            *controlnetDirs,]

    def run(
            self,
            p,
            outputDir,
            *controlnetDirs):

        if shared.opts.data.get("control_net_allow_script_control", False):
            print("FireflyMountain 注意，没打开设置的 control_net_allow_script_control选项，该请求终止")
            return

        if outputDir:
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)

        listAllControlnetImagesPath = []
        for cn_dir in controlnetDirs:
            if cn_dir == '':
                break

            listControlnetImagesName = [f for f in os.listdir(cn_dir) if f.endswith('.png') or f.endswith('.jpg')]
            listControlnetImagesName.sort()
            listControlnetImagesPath = [os.path.join(cn_dir,filename) for filename in listControlnetImagesName ]
            listAllControlnetImagesPath.append(listControlnetImagesPath)

        #p.img_len = 1
        #p.do_not_save_grid = True
        #p.do_not_save_samples = True


        lenControlnetImage = len(listAllControlnetImagesPath[0])
        state.job_count = lenControlnetImage

        for frameNo in range(lenControlnetImage):
            if state.interrupted:
                break
            copy_p = copy.copy(p)
            copy_p.control_net_input_image = []

            if outputDir:
                copy_p.do_not_save_grid = True
                copy_p.do_not_save_samples = True

            for listOneControlnetImagePath in listAllControlnetImagesPath:
                img = Image.open(listOneControlnetImagePath[min(frameNo,len(listOneControlnetImagePath)-1)])
                print("controlnet append",listOneControlnetImagePath[min(frameNo,len(listOneControlnetImagePath)-1)],img)
                

                copy_p.control_net_input_image.append(img)

            proc = process_images(copy_p)

            if outputDir:
                img = proc.images[0]
                img.save(os.path.join(outputDir,os.path.basename(listAllControlnetImagesPath[0][frameNo]) ))

            copy_p.close()

        return proc
