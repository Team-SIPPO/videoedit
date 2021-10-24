import av
import av.datasets
import numpy as np
import time
import cv2
from abc import ABCMeta, abstractmethod


class VideoCallback(metaclass=ABCMeta):
    def __init__(self, 
        video_frames=30,
        img_width=1920//4,
        img_height=1080//4,
        input_audio_path=None,
        input_video_path=None,
        output_video_path="./videos/sample05_2.mp4",
        video_fps=1,
        audio_fps=44100
    ) -> None:
        self.img_width = img_width
        self.img_height = img_height
        self.input_audio_path = input_audio_path
        self.input_video_path = input_video_path
        self.output_video_path = output_video_path
        self.video_fps = video_fps
        self.audio_fps = audio_fps
        self.video_frames = video_frames
    
    def video_callback(self, frame_num, image):
        if image is None:
            raise NotImplementedError()
        else:
            return image
    
    def sound_callback(self, frame_num, sound_arr):
        return sound_arr
    
    def init(self):
        pass

    def end(self):
        pass


def audio_packet_processing(packet, callback: VideoCallback, out_stream_audio, output, audio_frame_num):
    # We need to skip the "flushing" packets that `demux` generates.
    if packet.dts is None:
        return audio_frame_num

    if packet.stream.type != 'audio':
        return audio_frame_num

    for i, audio_frame in enumerate(packet.decode()):
        audio_frame_num += 1
        # to numpy
        arr = audio_frame.to_ndarray()
        if arr is None:
            continue

        # to audio frame
        arr = callback.sound_callback(audio_frame, arr)
        new_audio_frame = av.AudioFrame.from_ndarray(arr, format="fltp")
        new_audio_frame.rate = callback.audio_fps
        # encode frame to packet
        for new_packet in out_stream_audio.encode(new_audio_frame):
            output.mux(new_packet)
    return audio_frame_num

def video_packet_processing(packet, callback: VideoCallback, out_stream_video, output, video_frame):
    if packet.dts is None:
        return video_frame

    if packet.stream.type != 'video': 
        return video_frame
    for frame in packet.decode():
        video_frame += 1
        image = frame.to_image()
        image = np.array(image)
        image = callback.video_callback(video_frame, image)
        new_frame = av.VideoFrame.from_ndarray(image, format='rgb24')
        for new_packet in out_stream_video.encode(new_frame):
            output.mux(new_packet)
    return video_frame

def specify_video_feature(video_path):
    input_ = av.open(video_path)
    result = {
        "video": {
            "fps": int(input_.streams.video[0].rate),
            "width": int(input_.streams.video[0].width),
            "height": int(input_.streams.video[0].height),
            "frames": int(input_.streams.video[0].frames)
        }
    }
    if len(input_.streams.audio) > 0:
        result.update({
            "audio": {
                "rate": input_.streams.audio[0].rate
            }
        })
    input_.close()
    return result

def specify_audio_feature(audio_path):
    input_ = av.open(audio_path)
    result = {}
    if len(input_.streams.audio) > 0:
        result.update({
            "audio": {
                "rate": input_.stream.audio[0].rate
            }
        })
    input_.close()
    return result
    

def generate_video_looper(callback: VideoCallback):
    callback.init()
    video_frame = 0
    audio_frame = 0
    st = time.time()
    if callback.input_audio_path is not None and callback.input_video_path is not None:
        raise ValueError("one of video audio must be None")
    elif callback.input_video_path is not None:
        input_ = av.open(callback.input_video_path)
        in_stream = input_.streams.get(audio=0, video=0) 
    elif callback.input_audio_path is not None:
        input_ = av.open(callback.input_audio_path)
        in_stream = input_.streams.get(audio=0) 
    output = av.open(callback.output_video_path, 'w')

    # Make an output stream using the input as a template. This copies the stream
    # setup from one to the other.
    out_stream_video = output.add_stream("h264", rate=callback.video_fps, width=callback.img_width, height=callback.img_height)
    if callback.input_audio_path is not None or callback.video_callback is not None:
        out_stream_audio = output.add_stream("aac", rate=callback.audio_fps, layout="stereo")

    if callback.input_video_path is None:
        for frame_num in range(callback.video_frames):
            image = callback.video_callback(frame_num, image=None)
            # to frame
            new_frame = av.VideoFrame.from_ndarray(image, format='rgb24')
            # encode frame to packet
            for new_packet in out_stream_video.encode(new_frame):
                # mux packet
                output.mux(new_packet)
    else:
        for i, packet in enumerate(input_.demux(in_stream)):
            # import pdb; pdb.set_trace()
            if packet.stream.type == 'video': 
                if callback.video_frames is not None:
                    if video_frame > callback.video_frames:
                        continue
                video_frame = video_packet_processing(packet, callback, out_stream_video, output,video_frame)
            elif packet.stream.type == 'audio':
                audio_frame = audio_packet_processing(packet, callback, out_stream_audio, output, audio_frame)

    # Flush stream
    for packet in out_stream_video.encode():
        output.mux(packet)

    if callback.input_audio_path is not None or callback.video_callback is not None:
        for i, packet in enumerate(input_.demux(in_stream)):
            audio_packet_processing(packet, callback, out_stream_audio, output, audio_frame)

    if callback.input_audio_path is not None or callback.video_callback is not None:
        # Flush stream
        for packet in out_stream_audio.encode():
            output.mux(packet)

        input_.close()
    output.close()
    en = time.time()
    callback.end()
    print("time", en - st)