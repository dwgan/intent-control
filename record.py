import pyaudio
import wave

framerate = 16000
NUM_SAMPLES = 2000
channels = 1
sampwidth = 2
TIME = 10


def save_wave_file(filename, data):
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()


def record(f, time=5):
    p = pyaudio.PyAudio()

    # # 打印所有设备信息，找到麦克风的设备索引
    # for i in range(p.get_device_count()):
    #     print(i, p.get_device_info_by_index(i).get('name'))
    #
    # # 在 record 函数中指定正确的设备索引
    # stream = p.open(
    #     format=pyaudio.paInt16,
    #     channels=1,
    #     rate=16000,
    #     input=True,
    #     frames_per_buffer=1024,
    #     input_device_index=3  # 修改为你的麦克风设备索引
    # )
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=framerate,
        input=True,
        frames_per_buffer=NUM_SAMPLES,
    )
    my_buf = []
    count = 0
    print(f"录音中({time}s)")
    while count < TIME * time:
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        count += 1
        print(".", end="", flush=True)

    save_wave_file(f, my_buf)
    stream.close()
