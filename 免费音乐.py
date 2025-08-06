import os
import tkinter as tk
import webbrowser
import requests
import tkinter.messagebox as mes_box
import PySimpleGUI as sg
from tkinter import ttk
from retrying import retry


class SetUI(object):
    """
    音乐弹框界面
    """

    def __init__(self, weight=1000, height=600):
        self.ui_weight = weight
        self.ui_height = height
        self.title = " 音乐破解软件"
        self.ui_root = tk.Tk(className=self.title)
        self.ui_url = tk.StringVar()
        self.ui_var = tk.IntVar()
        self.ui_var.set(1)
        self.show_result = None
        self.song_num = None
        self.response_data = None
        self.song_url = None
        self.song_name = None
        self.song_author = None

    def set_ui(self):
        """
        设置简易UI界面
        :return:
        """
        # Frame空间
        frame_1 = tk.Frame(self.ui_root)
        frame_2 = tk.Frame(self.ui_root)
        frame_3 = tk.Frame(self.ui_root)
        frame_4 = tk.Frame(self.ui_root)

        # ui界面中菜单设计
        ui_menu = tk.Menu(self.ui_root)
        self.ui_root.config(menu=ui_menu)
        file_menu = tk.Menu(ui_menu, tearoff=0)
        ui_menu.add_cascade(label='菜单', menu=file_menu)
        file_menu.add_command(label='使用说明', command=lambda: webbrowser.open('www.baidu.com'))
        file_menu.add_command(label='关于作者', command=lambda: webbrowser.open('www.baidu.com'))
        file_menu.add_command(label='退出', command=self.ui_root.quit)

        # 控件内容设置
        choice_passageway = tk.Label(frame_1, text='请选择音乐搜索通道：', padx=10, pady=10)
        passageway_button_1 = tk.Radiobutton(frame_1, text='酷我', variable=self.ui_var, value=1, width=10, height=3)
        passageway_button_2 = tk.Radiobutton(frame_1, text='网易云', variable=self.ui_var, value=2, width=10, height=3)
        passageway_button_3 = tk.Radiobutton(frame_1, text='QQ音乐', variable=self.ui_var, value=3, width=10, height=3)
        passageway_button_4 = tk.Radiobutton(frame_1, text='酷狗', variable=self.ui_var, value=4, width=10, height=3)
        input_link = tk.Label(frame_2, text="请输入歌曲名或歌手：")
        entry_style = tk.Entry(frame_2, textvariable=self.ui_url, highlightcolor='Fuchsia', highlightthickness=1,
                               width=35)
        label2 = tk.Label(frame_2, text=" ")
        play_button = tk.Button(frame_2, text="搜索", font=('楷体', 11), fg='Purple', width=2, height=1,
                                command=self.get_KuWoMusic)
        label3 = tk.Label(frame_2, text=" ")
        # 表格样式
        columns = ("序号", "歌手", "歌曲", "专辑")
        self.show_result = ttk.Treeview(frame_3, height=20, show="headings", columns=columns)
        # 下载
        download_button = tk.Button(frame_4, text="下载", font=('楷体', 11), fg='Purple', width=6, height=1, padx=5,
                                    pady=5, command=self.download_music)

        # 控件布局
        frame_1.pack()
        frame_2.pack()
        frame_3.pack()
        frame_4.pack()
        choice_passageway.grid(row=0, column=0)
        passageway_button_1.grid(row=0, column=1)
        passageway_button_2.grid(row=0, column=2)
        passageway_button_3.grid(row=0, column=3)
        passageway_button_4.grid(row=0, column=4)
        input_link.grid(row=0, column=0)
        entry_style.grid(row=0, column=1)
        label2.grid(row=0, column=2)
        play_button.grid(row=0, column=3, ipadx=10, ipady=10)
        label3.grid(row=0, column=4)
        self.show_result.grid(row=0, column=4)
        download_button.grid(row=0, column=5)

        # 设置表头
        self.show_result.heading("序号", text="序号")
        self.show_result.heading("歌手", text="歌手")
        self.show_result.heading("歌曲", text="歌曲")
        self.show_result.heading("专辑", text="专辑")
        # 设置列
        self.show_result.column("序号", width=100, anchor='center')
        self.show_result.column("歌手", width=200, anchor='center')
        self.show_result.column("歌曲", width=200, anchor='center')
        self.show_result.column("专辑", width=300, anchor='center')

        # 鼠标点击
        self.show_result.bind('<ButtonRelease-1>', self.get_song_url)

    @retry(stop_max_attempt_number=5)
    def get_KuWoMusic(self):
        """
        获取音乐数据 - 使用第三方API
        :return:
        """
        # 清空treeview表格数据
        for item in self.show_result.get_children():
            self.show_result.delete(item)

        # 使用���简单的headers，避免复杂的反爬虫检测
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        search_input = self.ui_url.get()
        if len(search_input) > 0:
            # 使用网易云音乐的公开API接口
            search_url = 'https://music.163.com/api/search/get/web'
            search_data = {
                's': search_input,
                'type': '1',
                'offset': '0',
                'total': 'true',
                'limit': '30'
            }
            try:
                response = requests.get(search_url, params=search_data, headers=headers, timeout=20)
                self.response_data = response.json()

                # 判断返回数据结构 - 网易云API的数据结构
                if not self.response_data or 'result' not in self.response_data or 'songs' not in self.response_data['result']:
                    # 如果网易云失败，尝试使用备用API
                    self.try_backup_api(search_input, headers)
                    return

                songs_data = self.response_data['result']['songs']
                if len(songs_data) <= 0:
                    mes_box.showerror(title='错误', message='搜索: {} 不存在.'.format(search_input))
                else:
                    for i in range(len(songs_data)):
                        # 适配网易云API的数据结构
                        artist_names = ', '.join([artist['name'] for artist in songs_data[i]['artists']])
                        album_name = songs_data[i]['album']['name'] if 'album' in songs_data[i] else '未知专辑'
                        self.show_result.insert('', i, values=(i + 1, artist_names, songs_data[i]['name'], album_name))

            except Exception as e:
                print(f"网易云API失败: {e}")
                # 使用备用API
                self.try_backup_api(search_input, headers)
        else:
            mes_box.showerror(title='错误', message='未输入需查询的歌曲或歌手，请输入后搜索！')

    def try_backup_api(self, search_input, headers):
        """
        备用API - 使用QQ音乐API
        """
        try:
            # QQ音乐搜索接口
            search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
            search_data = {
                'ct': '24',
                'qqmusic_ver': '1298',
                'new_json': '1',
                'remoteplace': 'txt.yqq.center',
                'searchid': '71600303645193523',
                't': '0',
                'aggr': '1',
                'cr': '1',
                'catZhida': '1',
                'lossless': '0',
                'flag_qc': '0',
                'p': '1',
                'n': '20',
                'w': search_input,
                'g_tk': '5381',
                'format': 'json',
                'inCharset': 'utf8',
                'outCharset': 'utf-8'
            }

            response = requests.get(search_url, params=search_data, headers=headers, timeout=20)
            qq_data = response.json()

            if 'data' in qq_data and 'song' in qq_data['data'] and 'list' in qq_data['data']['song']:
                songs_data = qq_data['data']['song']['list']
                self.response_data = {'result': {'songs': []}}  # 统一数据格式

                if len(songs_data) <= 0:
                    mes_box.showerror(title='错误', message='搜索: {} 不存在.'.format(search_input))
                else:
                    for i in range(len(songs_data)):
                        # 适配QQ音乐API的数据结构
                        artist_names = ', '.join([singer['name'] for singer in songs_data[i]['singer']])
                        album_name = songs_data[i]['album']['name'] if 'album' in songs_data[i] else '未知专辑'
                        song_name = songs_data[i]['name']

                        # 构造统一格式的数据
                        unified_song = {
                            'name': song_name,
                            'artists': [{'name': artist_names}],
                            'album': {'name': album_name},
                            'id': songs_data[i]['mid']  # 使用mid作为ID
                        }
                        self.response_data['result']['songs'].append(unified_song)

                        self.show_result.insert('', i, values=(i + 1, artist_names, song_name, album_name))
            else:
                mes_box.showerror(title='错误', message='所有音乐接口都无法获取数据，请稍后重试。')

        except Exception as e:
            print(f"备用API也失败: {e}")
            mes_box.showerror(title='错误', message='网络异常或接口暂不可用，请稍后重试。')

    def get_song_url(self, event):
        """
        获取下载歌曲的地址
        :return:
        """
        # treeview中的左键单击
        for item in self.show_result.selection():
            item_text = self.show_result.item(item, "values")
            # 获取
            self.song_num = int(item_text[0])

        # 获取下载歌曲的地址
        if self.song_num is not None:
            try:
                songs_data = self.response_data['result']['songs']
                selected_song = songs_data[self.song_num - 1]

                # 获取歌曲基本信息
                self.song_name = selected_song['name']
                self.song_author = ', '.join([artist['name'] for artist in selected_song['artists']])

                # 由于版权限制，很多音乐无法直接下载
                # 这里提供一个演示用的占位URL
                self.song_url = "https://example.com/demo.mp3"  # 演示URL

                mes_box.showinfo(title='提示', message=f'已选择歌曲：{self.song_name} - {self.song_author}\n注意：由于版权保护，实际下载功能可能受限。')

            except Exception as e:
                print(f"获取歌曲信息失败: {e}")
                mes_box.showerror(title='错误', message='获取歌曲信息失败，请重新选择')
        else:
            mes_box.showerror(title='错误', message='未选择要下载的歌曲，请选择')

    def download_music(self):
        """
        下载音乐 - 技术学习版本
        :return:
        """
        if not os.path.exists('./qqMusic'):
            os.mkdir("./qqMusic/")

        if self.song_num is not None and self.song_name and self.song_author:
            # 显示技术学习选项
            choice = mes_box.askyesnocancel(
                title='下载选项',
                message=f'选择下载方式：\n是(Yes) - 保存歌曲信息\n否(No) - 尝试技术学习方案\n取消 - 退出'
            )

            if choice is True:
                # 原有的信息保存功能
                self.save_song_info()
            elif choice is False:
                # 技术学习方案
                self.try_technical_download()
            # choice is None 表示取消，不执行任何操作
        else:
            mes_box.showerror(title='错误', message='未选择要下载的歌曲，请先搜索并选择歌曲')

    def save_song_info(self):
        """保存歌曲信息"""
        song_name = self.song_name + '--' + self.song_author + ".txt"
        try:
            save_path = os.path.join('./qqMusic/{}'.format(song_name)).replace('\\', '/')
            true_path = os.path.abspath(save_path)

            song_info = f"""歌曲信息:
歌曲名: {self.song_name}
演唱者: {self.song_author}
搜索时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

注意: 由于版权保护，无法提供实际的音频下载功能。
这个文件仅作为搜索结果的记录。
如需听歌，请使用正版音乐平台。"""

            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(song_info)

            mes_box.showinfo(title='保存成功', message=f'歌曲信息已保存：{self.song_name}\n保存地址：{true_path}')

        except Exception as e:
            print(f"保存失败: {e}")
            mes_box.showerror(title='错误', message='保存歌曲信息失败')

    def try_technical_download(self):
        """
        技术学习方案 - 仅供学习研究
        警告：请遵守版权法和相关法律法规
        """
        try:
            # 方案1：生成演示音频
            demo_path = self.create_demo_audio()
            if demo_path:
                mes_box.showinfo(title='技术演示', message=f'已生成演示音频文件：\n{demo_path}\n注意：这只是技术演示，非真实音乐文件')
                return

            # 方案2：尝试第三方音乐API（需要额外配置）
            self.try_third_party_api()

        except Exception as e:
            mes_box.showerror(title='技术方案失败', message=f'技术学习方案执行失败���{str(e)}\n建议使用正版音乐平台')

    def create_demo_audio(self):
        """生成演示音频文件"""
        try:
            # 检查是否有音频生成库
            import numpy as np
            from scipy.io.wavfile import write

            # 生成简单音调
            sample_rate = 44100
            duration = 5
            frequency = 440  # A4音调

            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * frequency * t)

            filename = f"{self.song_name}--{self.song_author}_demo.wav"
            save_path = os.path.join('./qqMusic', filename)
            write(save_path, sample_rate, (audio_data * 32767).astype(np.int16))

            return save_path
        except ImportError:
            mes_box.showwarning(title='缺少依赖', message='需要安装 numpy 和 scipy 库来生成演示音频\n运行: pip install numpy scipy')
            return None
        except Exception as e:
            print(f"生成音频失败: {e}")
            return None

    def try_third_party_api(self):
        """
        尝试第三方音乐API - 技术学习用
        注意：这些通常也有版权限制
        """
        # 这里可以尝试一些提供音频预览的API
        preview_apis = [
            "https://api.spotify.com/v1/search",  # Spotify预览API
            "https://api.deezer.com/search",      # Deezer API
            "https://api.jamendo.com/v3.0/tracks" # Jamendo免费音乐
        ]

        mes_box.showinfo(
            title='技术学习提示',
            message="""技术学习方向：
1. 学习使用合法的音乐API（如Spotify SDK）
2. 研究音频信号处理技术
3. 了解流媒体技术原理
4. 学习版权保��技术

推荐合法途径：
- Spotify Developer API
- Apple Music API  
- YouTube Music API
- SoundCloud API

注意：请始终遵守版权法律！"""
        )

    def progress_bar(self, file_size):
        """
        任务加载进度条
        :return:
        """
        layout = [[sg.Text('任务完成进度')],
                  [sg.ProgressBar(file_size, orientation='h', size=(40, 20), key='progressbar')],
                  [sg.Cancel()]]

        # window只需将自定义的布局加载出来即可 第一个参数是窗口标题。
        window = sg.Window('机器人执行进度', layout)
        # 根据key值获取到进度条
        _progress_bar = window['progressbar']
        for i in range(file_size):  # 循环
            event, values = window.read(timeout=10)
            if event == 'Cancel' or event is None:
                break
            _progress_bar.UpdateBar(i + 1)

    def ui_center(self):
        """
        UI界面窗口设置：居中
        """
        ws = self.ui_root.winfo_screenwidth()
        hs = self.ui_root.winfo_screenheight()
        x = int((ws / 2) - (self.ui_weight / 2))
        y = int((hs / 2) - (self.ui_height / 2))
        self.ui_root.geometry('{}x{}+{}+{}'.format(self.ui_weight, self.ui_height, x, y))

    def loop(self):
        """
        函数说明:loop等待用户事件
        """
        self.ui_root.resizable(False, False)  # 禁止修改窗口大小
        self.ui_center()  # 窗口居中
        self.set_ui()
        self.ui_root.mainloop()


if __name__ == '__main__':
    a = SetUI()
    a.loop()