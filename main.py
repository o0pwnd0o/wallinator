import tkinter as tk
from tkinter import filedialog, ttk

import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment, silence
from pydub.playback import play

parts = []
global_amp = 15  # Global voice amplifier gain in dB
fs = 44100  # Global sample rate for recording
sd.default.samplerate = fs
sd.default.channels = 2


class Part:
    def __init__(self, audio, start, stop):
        self.takes = []
        self.selected_take = 0
        self.takes.append(audio)
        self.start = start
        self.stop = stop
        self.duration = (stop - start) / 1000

    def add_take(self, audio):
        self.takes.append(audio)


# Load a mp3 beat
def load_beat():
    path = filedialog.askopenfilename()
    global beat
    beat = AudioSegment.from_mp3(path)


# Define the parts
def init_parts():
    record(beat.duration_seconds)
    print("recording...")
    play(beat)
    initial_recording = AudioSegment.from_wav("initialrecording.wav")
    nonsilent = silence.detect_nonsilent(initial_recording, min_silence_len=1000, silence_thresh=-40)
    global parts
    for start, stop in nonsilent:
        audio = initial_recording[start:stop] + global_amp
        parts.append(Part(audio, start, stop))
    comboExample = ttk.Combobox(root, values=[("Part" + str(i)) for i in range(len(parts))])

    print(dict(comboExample))
    comboExample.current(1)

    print(comboExample.current(), comboExample.get())


def record_take(part):
    record(part.duration)
    print("recording...")
    play(beat[part.start:part.stop])
    take = AudioSegment.from_wav("temp_recording.wav")
    part.takes.append(take)


# Mix and preview
def preview():
    mixer = beat
    for part in parts:
        mixer = mixer.overlay(part.takes[part.selected_take], position=part.start)
    play(mixer)


# Record for the given duration in seconds and save it to temp_recording.wav
def record(duration):
    recording = sd.rec(int(duration * fs))
    sf.write('temp_recording.wav', recording, fs)


# Tkinter setup
global root
root = tk.Tk()
root.geometry('200x100')
root.title("Wallinator")

labelTop = tk.Label(root, text="Choose part to edit")

load_btn = tk.Button(root, text="Load Beat", command=load_beat).pack()
preview_btn = tk.Button(root, text="Play Preview", command=preview).pack()
init_btn = tk.Button(root, text="Initialize Parts", command=init_parts).pack()
root.mainloop()
