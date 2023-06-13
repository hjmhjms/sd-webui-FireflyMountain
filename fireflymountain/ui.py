
import gradio as gr
import modules.ui_common as ui_common

from .logic import replacebackground, shared, videoframe


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as mainInterface:
        with gr.Row().style(equal_height=False): 
            with gr.Tabs():
                with gr.TabItem("视转图"):
                    Video2FrameUI()
                with gr.TabItem("抠图"):
                    KouTuUI()    
                with gr.TabItem("图转视"):
                    Frame2VideoUI()
                with gr.TabItem("关于"):
                    AboutUI()

    return [(mainInterface,"FireflyMountain","fireflymountain")]

        
def AboutUI():
    gr.Markdown("""
    
### 常用网站
- [civitai模型网站](https://civitai.com/)
- [arthub 别人的prompt](https://arthub.ai/)
- [huggingface 社区](https://huggingface.co/) 
- [咒语生成器](https://www.wujieai.com/tag-generator)
---

### 抖音号：
- 萤火山  (FireflyM)

### 视频号
- 萤火山唯美观

### 微信公众号
- 萤火山AI(FireflyMountainAI)

### sd-webui-FireflyMountain 是 stable diffusion webui的一个插件
```
git clone https://github.com/hjmhjms/sd-webui-FireflyMountain
```                    
""")

def Video2FrameUI():
    video_input_dir = gr.Video(lable='上传视频',source='upload',interactive=True)
    video_input_dir.style(width=300)
    with gr.Row(variant='panel'):
        aim_fps_checkbox = gr.Checkbox(label="启用输出帧率控制")
        aim_fps = gr.Slider(
                            minimum=1,
                            maximum=60,
                            step=1,
                            label='输出帧率',
                            value=30,interactive=True)
        
    with gr.Row(variant='panel'):
        time_range_checkbox = gr.Checkbox(label="启用时间段裁剪")
        aim_start_time = gr.Number(value=0,label="裁剪起始时间(s)",)
        aim_end_time = gr.Number(value=0,label="裁剪停止时间(s)")
        
    frame_output_dir = gr.Textbox(label='图片输出文件夹路径', lines=1,placeholder='output\\folder')

    with gr.Row():
        btn = gr.Button(value="开始拆帧")
        btnInterupt = gr.Button(value="中断")

    out = gr.Textbox(label="log info",interactive=False,visible=True,placeholder="output log")

    btn.click(videoframe.Video2frame, inputs=[video_input_dir, frame_output_dir,aim_fps_checkbox,aim_fps,time_range_checkbox,aim_start_time,aim_end_time],outputs=out)
    btnInterupt.click(fn=lambda: shared.state.Interrupt(),inputs=[],outputs=[])


def Frame2VideoUI():
    with gr.Row(variant='panel'):
        with gr.Column(variant='panel'):
            fps = gr.Slider(
                            minimum=1,
                            maximum=60,
                            step=1,
                            label='FPS',
                            value=30)
            
            frame_input_dir = gr.Textbox(label='图片输入目录', lines=1,placeholder='input\\folder')
            video_output_dir = gr.Textbox(label='视频输出目录', lines=1,placeholder='output\\folder')
            f2v_mode = gr.Dropdown(
                                label="video out",
                                choices=[
                                '.mp4',
                                '.avi',
                                ],
                                value='.mp4')
            
            with gr.Row():
                btn1 = gr.Button(value="生成视频")
                btnInterupt = gr.Button(value="中断")

            out1 = gr.Textbox(label="log info",interactive=False,visible=True,placeholder="output log")
            btn1.click(videoframe.Frame2video, inputs=[frame_input_dir, video_output_dir,fps,f2v_mode],outputs=out1)    
            btnInterupt.click(fn=lambda: shared.state.Interrupt(),inputs=[],outputs=[])


listRemoveBackgroundModels = [
    "None",
    "u2net",
    "u2netp",
    "u2net_human_seg",
    "u2net_cloth_seg",
    "silueta",
]

def KouTuUI():
    with gr.Column():
        with gr.Column(variant='panel'):
            gr.Markdown(""" 
            ## 图片背景消除
            """)

            with gr.Row(variant = 'compact'):
                unetModel = gr.Dropdown(label="消除算法", choices=listRemoveBackgroundModels, value="u2net")
                #return_mask = gr.Checkbox(label="Return mask", value=False)
                alpha_matting = gr.Checkbox(label="Alpha matting", value=False)

            with gr.Row(variant = 'compact',visible=False) as alpha_mask_row:
                alpha_matting_erode_size = gr.Slider(label="Erode size", minimum=0, maximum=40, step=1, value=10)
                alpha_matting_foreground_threshold = gr.Slider(label="Foreground threshold", minimum=0, maximum=255, step=1, value=240)
                alpha_matting_background_threshold = gr.Slider(label="Background threshold", minimum=0, maximum=255, step=1, value=10)

            alpha_matting.change(
                fn=lambda x: gr.update(visible=x),
                inputs=[alpha_matting],
                outputs=[alpha_mask_row],
            )

            # ------------------------------------
            modeDropdown = gr.Dropdown(
                label="图片输出模式",
                choices=[
                    "生成遮罩",
                    "透明背景",
                    "白色背景",
                    "纯色背景",
                    "自定义背景",],
                value="透明背景")
                            
            colorPicker = gr.ColorPicker(label="color",value='#646464',visible=False)
            bgDirInput = gr.Textbox(label="背景图片目录（输入图片和背景图片会一一对应，输入图片比背景图片多出的将会用最后一张背景图，如果只有一张背景是就等于固定背景了）",lines=1,placeholder='input\\folder',visible=False)

            def OnModeChange(choices):
                if choices == "纯色背景" :
                    return gr.update(visible=True),gr.update(visible=False)
                elif choices == "自定义背景":
                    return gr.update(visible=False),gr.update(visible=True)
                else:
                    return gr.update(visible=False),gr.update(visible=False)
            modeDropdown.change(fn = OnModeChange,inputs=[modeDropdown], outputs=[colorPicker,bgDirInput]) 

        with gr.Row():
            with gr.Column(variant='panel'):
                gr.Markdown(""" 
                ## 批量生产
                """)
                frameInputDir = gr.Textbox(label='图片输入目录',lines=1,placeholder='input\\folder')
                frameOutputDir = gr.Textbox(label='图片输出目录',lines=1,placeholder='output\\folder',value='./outputs/FireflyMountain_output')

                with gr.Row():
                    btnGen = gr.Button(value="批量生成")
                    btnInterupt = gr.Button(value="中断")
                    
                textboxOutput = gr.Textbox(label="log info",interactive=False,visible=True,placeholder="output log")
                btnGen.click(Gen,inputs=[
                                            unetModel,alpha_matting,alpha_matting_foreground_threshold,alpha_matting_background_threshold,alpha_matting_erode_size,
                                            modeDropdown,colorPicker,bgDirInput,frameInputDir,frameOutputDir
                                        ],
                                        outputs=textboxOutput)
                
                btnInterupt.click(fn=lambda: shared.state.Interrupt(),inputs=[],outputs=[])
            
            with gr.Column(variant='panel'):
                gr.Markdown(""" 
                ## 单图生产
                """)
                single_image_input_path = gr.Image(source='upload',type='filepath')
                btnGenSingle = gr.Button(value="生成单图")
                image_show_path = gr.Image(label='output images',interactive=False).style(height=512)
                #image_show_path = gr.Gallery(label='output images').style(grid=1,height=512,maxheight)
                btnGenSingle.click(fn=GenSingle,
                                        inputs=[
                                                    unetModel,alpha_matting,alpha_matting_foreground_threshold,alpha_matting_background_threshold,alpha_matting_erode_size,
                                                    modeDropdown,colorPicker,bgDirInput,single_image_input_path,image_show_path
                                                ],
                                        outputs=[image_show_path])

                #deforum_gallery, generation_info, html_info, html_log = ui_common.create_output_panel("FireflyMountain", "img2img")



def Gen(model:str,alpha_matting:bool,alpha_matting_foreground_threshold :int,alpha_matting_background_threshold :int,alpha_matting_erode_size: int,
        modeDropdown,colorPicker,bgDirInput,frameInputDir,frameOutputDir,progress=gr.Progress()):
    p = replacebackground.RembgProcesser(model=model,
                                    alpha_matting=alpha_matting,
                                    alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                                    alpha_matting_background_threshold=alpha_matting_background_threshold,
                                    alpha_matting_erode_size=alpha_matting_erode_size)
    if modeDropdown == "生成遮罩":
        return p.ReturnMask(frameInputDir,frameOutputDir,progress)
    elif modeDropdown == "透明背景":
        return p.RemoveBg(frameInputDir,frameOutputDir,progress)
    elif modeDropdown == "白色背景":
        return p.ReplaceBgColor(frameInputDir,frameOutputDir,"#ffffff" ,progress)
    elif modeDropdown == "纯色背景":
        return p.ReplaceBgColor(frameInputDir,frameOutputDir,colorPicker,progress)
    elif modeDropdown == "自定义背景":
        return p.ReplaceBg(frameInputDir,frameOutputDir,bgDirInput,progress)


def GenSingle(model:str,alpha_matting:bool,alpha_matting_foreground_threshold :int,alpha_matting_background_threshold :int,alpha_matting_erode_size: int,
        modeDropdown,colorPicker,bgDirInput,single_image_input_path,image_show_path,progress=gr.Progress()):
    p = replacebackground.RembgProcesser(model=model,
                                    alpha_matting=alpha_matting,
                                    alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                                    alpha_matting_background_threshold=alpha_matting_background_threshold,
                                    alpha_matting_erode_size=alpha_matting_erode_size)
    if modeDropdown == "生成遮罩":
        return p.ReturnMaskOne2(single_image_input_path,progress)
    elif modeDropdown == "透明背景":
        return p.RemoveBgOne2(single_image_input_path,progress)
    elif modeDropdown == "白色背景":
        return p.ReplaceBgColorOne2(single_image_input_path,"#ffffff" ,progress)
    elif modeDropdown == "纯色背景":
        return p.ReplaceBgColorOne2(single_image_input_path,colorPicker,progress)
    elif modeDropdown == "自定义背景":
        return p.ReplaceBgOne2(single_image_input_path,bgDirInput,progress)
