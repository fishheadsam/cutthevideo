import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys

# 获取 FFmpeg 路径
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):  # 打包后
        base_dir = sys._MEIPASS  # PyInstaller 临时解压目录
    else:  # 开发环境
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "bin", "ffmpeg.exe")

def extract_video():
    input_path = entry_input.get()
    start_time = entry_start.get()
    end_time = entry_end.get()
    output_name = entry_output.get()
    output_format = format_var.get()  # 获取用户选择的格式

    if not input_path or not start_time or not end_time or not output_name:
        messagebox.showerror("错误", "请填写所有字段")
        return

    # 获取输入视频的文件夹路径
    input_dir = os.path.dirname(input_path)
    # 生成输出文件的完整路径
    output_path = os.path.join(input_dir, f"{output_name}.{output_format}")

    # 获取 FFmpeg 路径
    ffmpeg_path = get_ffmpeg_path()

    # FFmpeg 命令
    if output_format == "gif":
        # 如果是 GIF 格式，需要重新编码
        cmd = [
            ffmpeg_path,
            '-ss', start_time,    # 开始时间
            '-to', end_time,     # 结束时间
            '-i', input_path,     # 输入文件
            '-vf', 'split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',  # 设置帧率和分辨率
            '-an',               # 禁用音频
            output_path           # 输出文件
        ]
    else:
        # 如果是 MP4 或其他格式，直接复制流
        cmd = [
            ffmpeg_path,
            '-ss', start_time,    # 开始时间
            '-to', end_time,     # 结束时间
            '-i', input_path,     # 输入文件
            '-c:v', 'copy',      # 直接复制视频流
            '-c:a', 'copy',      # 直接复制音频流
            output_path           # 输出文件
        ]

    try:
        # 隐藏 FFmpeg 窗口
        if os.name == 'nt':  # Windows 系统
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(cmd, check=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
        else:  # macOS/Linux 系统
            subprocess.run(cmd, check=True)
        messagebox.showinfo("成功", f"视频提取完成！\n保存路径: {output_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("错误", f"提取失败: {e}")

# 创建 GUI 窗口
root = tk.Tk()
root.title("视频片段提取工具")

# 输入文件选择
tk.Label(root, text="输入视频:").grid(row=0, column=0)
entry_input = tk.Entry(root, width=40)
entry_input.grid(row=0, column=1)
tk.Button(root, text="浏览", command=lambda: entry_input.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

# 时间输入
tk.Label(root, text="开始时间 (HH:MM:SS):").grid(row=1, column=0)
entry_start = tk.Entry(root)
entry_start.grid(row=1, column=1)

tk.Label(root, text="结束时间 (HH:MM:SS):").grid(row=2, column=0)
entry_end = tk.Entry(root)
entry_end.grid(row=2, column=1)

# 输出文件名
tk.Label(root, text="输出文件名 (无需后缀):").grid(row=3, column=0)
entry_output = tk.Entry(root)
entry_output.grid(row=3, column=1)

# 输出格式选择
tk.Label(root, text="输出格式:").grid(row=4, column=0)
format_var = tk.StringVar(value="mp4")  # 默认格式为 MP4
format_options = ["mp4", "gif", "avi", "mkv"]  # 支持的格式
format_menu = tk.OptionMenu(root, format_var, *format_options)
format_menu.grid(row=4, column=1)

# 执行按钮
tk.Button(root, text="开始提取", command=extract_video).grid(row=5, column=1)

# 运行主循环
root.mainloop()
