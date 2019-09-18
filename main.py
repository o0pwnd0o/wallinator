from tkinter import *
from tkinter import filedialog, ttk

import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment, silence
from pydub.playback import play

global_amp = 15  # Global voice amplifier gain in dB
fs = 44100  # Global sample rate for recording
sd.default.samplerate = fs
sd.default.channels = 2

selected_part = 0
parts = []


class Part:
    def __init__(self, audio, start, stop):
        self.takes = []
        self.takes.append(audio)
        self.start = start
        self.stop = stop
        self.duration = (stop - start) / 1000
        self.selected_take = self.takes[0]

    def add_take(self, audio):
        self.takes.append(audio)

    def select_take(self, takenbr):
        self.selected_take = self.takes[takenbr]


# Load a mp3 beat
def load_beat():
    path = filedialog.askopenfilename()
    global beat
    beat = AudioSegment.from_mp3(path)
    beat.export("beat.wav", format="wav")
    global beat_sd
    beat_sd = sf.read("beat.wav", dtype='float32')


# Define the parts
def init_parts():
    data, fssd = sf.read("beat.wav", dtype='float32')
    print("recording...")
    recording = sd.playrec(data, fs, channels=2, blocking=True)
    sf.write('initialrecording.wav', recording, fs)
    initial_recording = AudioSegment.from_wav("initialrecording.wav")
    print("loaded")
    nonsilent = silence.detect_nonsilent(initial_recording, min_silence_len=1000, silence_thresh=-40)
    global parts
    parts = []
    titles = []
    for start, stop in nonsilent:
        audio = initial_recording[start:stop]
        parts.append(Part(audio, start, stop))
        titles.append(str(start) + " - " + str(stop))

    cb1["values"] = titles


def record_take():
    recording = sd.rec(int(selected_part.duration * fs), samplerate=fs, channels=2)
    print("recording...")
    play(beat[selected_part.start:selected_part.stop])
    sf.write('temp_recording.wav', recording, fs)
    take = AudioSegment.from_wav("temp_recording.wav")
    selected_part.takes.append(take)

    titles = []
    for i in range(len(selected_part.takes)):
        titles.append("Take " + str(i))
    cb2["values"] = titles
    cb2.current(selected_part.takes.index(selected_part.selected_take))


# Mix and preview
def preview():
    mixer = beat
    for part in parts:
        mixer = mixer.overlay(part.selected_take + global_amp, position=part.start - 300)
    play(mixer)



def select_part(event):
    global selected_part
    selected_part = parts[cb1.current()]
    titles = []
    for i in range(len(selected_part.takes)):
        titles.append("Take " + str(i))
    cb2["values"] = titles
    cb2.current(selected_part.takes.index(selected_part.selected_take))


def select_take(event):
    selected_part.select_take(cb2.current())


def play_take():
    play(selected_part.selected_take + global_amp)


# Tkinter setup
root = Tk()
root.title("Wallinator by pwnd")

# Create frames
playback_frame = Frame(root, relief=RAISED, borderwidth=1).pack()
edit_frame = Frame(root, relief=RAISED, borderwidth=1).pack()

# Playback controls
# Label(playback_frame, text="Choose part to edit")
Button(playback_frame, text="Load Beat", command=load_beat).pack(side=LEFT)
Button(playback_frame, text="Play Preview", command=preview).pack(side=LEFT)
Button(playback_frame, text="Initialize Parts", command=init_parts).pack(side=LEFT)

# Editing selection
global cb1
global cb2
Label(edit_frame, text="Select Part").pack()
cb1 = ttk.Combobox(edit_frame, width=10)
cb1.bind("<<ComboboxSelected>>", select_part)
cb1.pack()

Label(edit_frame, text="Select Take").pack()
cb2 = ttk.Combobox(edit_frame, width=10)
cb2.bind("<<ComboboxSelected>>", select_take)
cb2.pack()

Button(edit_frame, text="Play Take", command=play_take).pack(side=LEFT)
Button(edit_frame, text="New Take", command=record_take).pack(side=LEFT)

root.mainloop()
