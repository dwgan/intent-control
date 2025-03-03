import pyaudio
import wave
import webrtcvad
import numpy as np
import time


def auto_record(output_filename="output.wav", min_record_time=2, silence_timeout=1):
    """
    自动录音并保存为 wav 文件。

    参数：
    - output_filename (str): 保存的文件名（默认 "output.wav"）
    - min_record_time (int): 最小录音时长（秒，默认 2 秒）
    - silence_timeout (int): 静音持续时长（秒，默认 1 秒）
    """
    # 配置参数
    FORMAT = pyaudio.paInt16  # 音频格式
    CHANNELS = 1  # 单声道
    RATE = 16000  # 采样率
    CHUNK = 320  # 每次读取的音频块大小，确保符合 WebRTC VAD 要求
    VAD_MODE = 1  # WebRTC VAD 的灵敏度（0-3，3最灵敏）

    # 初始化 PyAudio 和 VAD
    p = pyaudio.PyAudio()
    vad = webrtcvad.Vad(VAD_MODE)

    # 开始录音
    def start_recording():
        # 打开音频流
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
        frames = []
        print("正在录音... 说话吧！")

        # 需要确保每帧符合 VAD 要求，320 个样本，即 20ms 的音频数据
        frame_duration_ms = 20  # 每帧持续时间，单位是毫秒
        samples_per_frame = int(RATE * frame_duration_ms / 1000)

        # 记录开始时间
        start_time = time.time()
        last_speech_time = start_time  # 上次检测到语音的时间
        silence_duration = 0  # 静音时长

        try:
            while True:
                data = stream.read(CHUNK)
                frames.append(data)

                # 将数据转换为 16-bit PCM 格式的 numpy 数组
                audio_data = np.frombuffer(data, dtype=np.int16)

                # 每次检查的音频数据大小必须满足 WebRTC VAD 的要求
                if len(audio_data) >= samples_per_frame:
                    is_speech = vad.is_speech(audio_data.tobytes(), RATE)

                    # 如果检测到语音，更新上次语音的时间
                    if is_speech:
                        last_speech_time = time.time()
                        silence_duration = 0  # 重置静音时长

                    # 如果没有检测到语音（静音），更新静音持续时间
                    if not is_speech:
                        silence_duration = time.time() - last_speech_time

                    # 判断是否符合停止录音条件
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= min_record_time and silence_duration >= silence_timeout:
                        print(f"检测到静音超过{silence_timeout}秒，录音结束。")
                        break
        except KeyboardInterrupt:
            print("录音被手动停止。")
        finally:
            # 结束录音
            stream.stop_stream()
            stream.close()

        return frames

    # 保存录音为 WAV 文件
    def save_audio(frames, filename=output_filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        print(f"录音已保存为 {filename}")

    # 执行录音和保存
    frames = start_recording()  # 开始录音
    save_audio(frames)  # 保存录音
    p.terminate()  # 关闭 PyAudio

