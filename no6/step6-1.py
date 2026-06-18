from pydub import AudioSegment
from pydub.playback import play

# MP3ファイルを読み込む
audio = AudioSegment.from_file("sample.mp3")

# 音声情報を表示
print(f"長さ: {len(audio)}ミリ秒")
print(f"チャンネル数: {audio.channels}")
print(f"サンプリングレート: {audio.frame_rate}Hz")
print(f"ビット深度: {audio.sample_width * 8}bit")

# 再生
play(audio)