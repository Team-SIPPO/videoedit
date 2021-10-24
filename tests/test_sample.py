from videoedit.core import VideoCallback, generate_video_looper
import av
import av.datasets
import numpy as np
import time
import cv2
import matplotlib.pyplot as plt
import warnings
from PIL import Image, ImageDraw, ImageFont
import platform
from datetime import date


class Stimulus1(VideoCallback):
    def __init__(self) -> None:
        super().__init__(
            video_frames=60,
            input_audio_path=None,
            output_video_path="./videos/sample05_2.mp4"
        )
        self.thinking_man = None
    
    def init(self):
        self.thinking_man = cv2.imread('thinking.png') #org size = 689x965

    def video_callback(self, frame_num):
        last_cnt = 54
        i = frame_num
        image = np.zeros((self.img_height, self.img_width, 3)).astype("uint8")
        image = cv2.putText(image,
                    text=f'00:{60-i-1:02}' if i<last_cnt else str(60-i-1),
                    org=(100,200) if i<last_cnt else (700,750),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=2.0 if i<last_cnt else 25.0,
                    color=(255, 255, 255),
                    thickness=2,
                    lineType=cv2.LINE_4)
        
        # before last 5
        if i<last_cnt:
            # message
            text1 = 'Do it'
            image = cv2.putText(image,
                        text=text1,
                        org=(150,550),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=8.0 if i%2==0 else 10.0,
                        color=(255, 255, 255),
                        thickness=2,
                        lineType=cv2.LINE_4)
            text2 = 'or Not'
            image = cv2.putText(image,
                        text=text2,
                        org=(150,800),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=8.0 if i%2==0 else 10.0,
                        color=(255, 255, 255),
                        thickness=2,
                        lineType=cv2.LINE_4)
            # thinking
            tmp = self.thinking_man
            sc = 0.8
            tmp = cv2.resize(tmp, dsize=None, fx=sc, fy=sc)
            height, width = tmp.shape[:2] 
            x,y = 1200, 200
            image[y:height + y, x:width + x] = tmp
        return image
    def end(self):
        self.thinking_man = None

class Stimulus2(VideoCallback):
    def __init__(self) -> None:
        super().__init__(
            video_frames=25,
            input_audio_path="./mc2.mp3",
            output_video_path="./videos/sample05_3.mp4",
            video_fps=1,
            audio_fps=48000)
        self.fig = None
        self.ax = None
        
    def _set_figure(self):
        plt.figure()
        fig, ax = plt.subplots(figsize=(8, 4))
        self.fig = fig
        self.ax = ax

    def init(self):
        self._set_figure()
    
    def _plot_graph(self, i):
        # y_value = np.repeat(np.nan, 5)
        # y_value[0:i] = np.arange(0, 5)[0:i]
        rate = np.min([i / 17.0, 1.0])
        rate_arr = np.clip(np.arange(18), 0, 1)[:i+1]
        y_value = np.array([10, 30, 35, 60, 70, 79, 94])
        max_y_value = y_value[-1]
        # last_y_value = y_value[-2] + (y_value[-1] - y_value[-2]) * rate
        last_y_value = y_value[-1] * rate
        graph_y = list(y_value[:-1]) + [last_y_value]
        self.ax.plot(np.arange(7)[:-1], graph_y[:-1])
        if rate == 1:
            self.ax.plot(np.arange(7)[-2:], graph_y[-2:], color="red")
        self.ax.scatter(np.repeat(7, len(rate_arr)), max_y_value * rate_arr)
        self.ax.scatter(np.repeat(6, i), last_y_value, marker="o", s=100, color="red")
        self.ax.scatter(6, last_y_value, marker="*", s=500, color="red")
        self.ax.set_ylim(0, max_y_value * 1.05)
        self.ax.set_xlim(0, 7)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.fig.canvas.draw()
            c = np.array(self.fig.canvas.renderer.buffer_rgba())
            c = cv2.cvtColor(c, cv2.COLOR_RGBA2BGR)
            self.ax.clear()
            # plt.clf()
            # plt.close()
        c = cv2.cvtColor(c, cv2.COLOR_BGR2RGB)
        return c

    def video_callback(self, frame_num):
        img = self._plot_graph(frame_num)
        img = cv2.resize(img, dsize=(self.img_width, self.img_height))
        return img
    
class Stimulus3(VideoCallback):
    def __init__(self, next_goal_time=1000, current_time=35) -> None:
        super().__init__(
            video_frames=4,
            input_audio_path="./ショック4.mp3",
            output_video_path="./stimulus_end_later.mp4"
        )
        self.next_goal_time = next_goal_time
        self.current_time = current_time
    
    def video_callback(self, frame_num):
        goal = self.next_goal_time
        rest = goal - self.current_time
        image = np.zeros((self.img_height, self.img_width, 3)).astype("uint8")
        # message
        text_list = [f'通算{goal}分まで', f'残り{rest}分']
        
        # print(self.img_height)
        pos_list = [
            (self.img_width // 2, self.img_height * 0.3),
            (self.img_width // 2, self.img_height * 0.53)
        ]
        # print(pos_list)
        size_list = [20, 70]

        for i in range(len(text_list)):
            text = text_list[i]
            pos = pos_list[i]
            size = size_list[i]
            image = cv2_putText(img = image,
                        text=text,
                        org=pos,
                        fontScale=size,
                        color=(255, 255, 255),
                        pos="center"
                        )            
        return image

    def end(self):
        pass

class Stimulus4(VideoCallback):
    def __init__(self) -> None:
        super().__init__(
            video_frames=None,
            input_video_path="./original_pre_v1_文字なし.mp4",
            output_video_path="./videos/sample05_4.mp4",
            video_fps=25,
            audio_fps=44100
        )
    
    def video_callback(self, frame_num, image):
        return super().video_callback(frame_num, image)

class Stimulus5(VideoCallback):
    def __init__(
        self, 
        start_date=date.today().strftime("%Y年%m月%d日"),
        total_time=1280,
        num_days=65, 
        continues_days=12,
        name="B.B",
        graph_path="",
        target_time=65, 
        ) -> None:
        super().__init__(
        video_frames=None,
        input_video_path="./original_pre_v1_文字なし.mp4",
        output_video_path="./stimulus_end_later.mp4",
        video_fps=25,
        audio_fps=44100,
        )
        self.start_date=start_date
        self.total_time=total_time
        self.num_days=num_days
        self.continues_days=continues_days
        self.name=name
        self.graph_path=graph_path
        self.target_time=target_time
        self.base_image = None
    
    def scaling(self, frame_num, )

    def video_callback(self, frame_num, input_image):

        pos_list = [
            (self.img_width // 2, self.img_height * 0.3),
            (self.img_width // 2, self.img_height * 0.53)
        ]
        text_list = []
        size_list = []
        # 10 sec    : 今日の日付
        # 13-17 sec : 総取り組み時間 XXXX分（ズームイン）
        # 18 sec    : 取り組み日数 xx日（アピール）
        # 21-25 sec : 継続日数 xx日 (ピークインバウンド)
        # 30-34 sec : 名前 (ズームイン)
        # 38-42 sec : グラフ (ズームイン)
        # 43-45 sec : 今週の目標
        # 46 sec    : 後 xx 分
        if (frame_num >= 10 * self.video_fps) and (frame_num < 13 * self.video_fps):
            #image = np.zeros((self.img_height, self.img_width, 3)).astype("uint8")
            image = np.ones((self.img_height, self.img_width, 3)).astype("uint8") * 255
            text_list = ['',self.start_date]
            size_list = [0,40]
            for i in range(len(text_list)):
                text = text_list[i]
                pos = pos_list[i]
                size = size_list[i]
                image = cv2_putText(img = image,
                            text=text,
                            org=pos,
                            fontScale=size,
                            #color=(255, 255, 255),
                            color=(0, 0, 0),
                            pos="center"
                            )
            input_image = image

        #325-450
        elif (frame_num >= 13 * self.video_fps) and (frame_num < 18 * self.video_fps):
            image = np.ones((self.img_height, self.img_width, 3)).astype("uint8") * 255
            text_list = ['総取り組み時間',f'{self.total_time}分']
            calc_size = 40
            size_list = [calc_size,calc_size]            
            for i in range(len(text_list)):
                text = text_list[i]
                pos = pos_list[i]
                size = size_list[i]
                image = cv2_putText(img = image,
                            text=text,
                            org=pos,
                            fontScale=size,
                            #color=(255, 255, 255),
                            color=(0, 0, 0),
                            pos="center"
                            )
            scale = 2.0 / (2.0*frame_num/450)
            #
            image = cv2.resize(image, None, fx=scale, fy=scale)
            input_image = cv2.resize(input_image, dsize=(self.img_width,self.img_height))
            pos_y = abs(self.img_height // 2 - image.shape[0] // 2)
            pos_x = abs(self.img_width  // 2 - image.shape[1] // 2)
            pre_y = pos_y 
            pre_x = pos_x
            if scale <= 1.0:
                post_y = pos_y + image.shape[0]
                post_x = pos_x + image.shape[1]
                input_image[pre_y:post_y,pre_x:post_x,:] = image
            else:
                post_y = image.shape[0]-pos_y
                post_x = image.shape[1]-pos_x
                input_image = image[pre_y:post_y,pre_x:post_x,:]
            
        return input_image

    def end(self):
        pass

# generate_video_looper(Stimulus1())
#generate_video_looper(Stimulus2())
# generate_video_looper(Stimulus3())
generate_video_looper(Stimulus5())
