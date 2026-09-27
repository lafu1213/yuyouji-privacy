"""Synthesizes a gentle, royalty-free music-box track (plus a few sound cues) for the promo.
Usage: python3 music.py  ->  music.wav (32 s, 44.1 kHz stereo)
"""
import wave
import numpy as np

SR = 44100
DUR = 32.0
BPM = 100
BEAT = 60 / BPM
N = int(SR * DUR)
mix = np.zeros((N, 2))


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    mix[i : i + len(sig), 0] += sig * (1 - pan) / 2 * 2 ** 0.5
    mix[i : i + len(sig), 1] += sig * (1 + pan) / 2 * 2 ** 0.5


def bell(freq, length=1.6):
    t = np.arange(int(SR * length)) / SR
    env = np.exp(-t * 3.2) * np.minimum(1, t * 400)
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 6) \
        + 0.12 * np.sin(2 * np.pi * freq * 3.01 * t) * np.exp(-t * 9)
    return s * env


def pad(freq, length):
    t = np.arange(int(SR * length)) / SR
    env = np.minimum(1, t / 0.4) * np.minimum(1, (length - t) / 0.6)
    s = sum(np.sin(2 * np.pi * freq * m * t + d) / m for m, d in [(1, 0), (2, .3), (3, .7)])
    s += 0.5 * np.sin(2 * np.pi * freq * 1.003 * t)
    return s * np.clip(env, 0, 1)


def pluck(freq, length=0.5):
    t = np.arange(int(SR * length)) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 9) * np.minimum(1, t * 300)


# I - vi - IV - V in C major, one chord per bar (4 beats)
chords = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [59, 62, 67])]
pent = [72, 74, 76, 79, 81, 84]  # C major pentatonic
rng = np.random.default_rng(7)
bar = 4 * BEAT
nbars = int(DUR / bar) + 1

# melody phrase repeats every 4 bars with small variation, rests during the intro hook
phrase = [0, 2, 3, 2, 4, 3, 2, -1, 1, 2, 3, 5, 4, 3, 2, -1,
          3, 4, 5, 4, 3, 2, 1, -1, 2, 1, 0, 1, 2, -1, 0, -1]
for b in range(nbars):
    start = b * bar
    root, tri = chords[b % 4]
    fade_in = 0.55 if b == 0 else 1.0
    add(pad(midi(root), bar + 0.3), start, 0.0, 0.10 * fade_in)
    for k, n in enumerate(tri):
        add(pad(midi(n), bar + 0.3), start, (k - 1) * 0.4, 0.035 * fade_in)
    for beat in range(4):  # soft bass pluck on each beat
        add(pluck(midi(root + (12 if beat % 2 else 0))), start + beat * BEAT, 0, 0.14 * fade_in)
    if b >= 1:
        for e in range(8):  # eighth notes
            idx = phrase[(b % 4) * 8 + e]
            if idx < 0 or (e % 2 == 1 and rng.random() < 0.35):
                continue
            add(bell(midi(pent[idx])), start + e * BEAT / 2, rng.uniform(-.5, .5), 0.12)

# sound cues synced to promo.html
add(bell(midi(84), 2.5) + bell(midi(91), 2.5) * .6, 4.3, 0, 0.22)                    # logo stamp
for i, n in enumerate([79, 84, 88]):
    add(bell(midi(n), 1.0), 19.2 + i * 0.08, 0.3, 0.18)                               # correct answer
for i in range(3):
    add(bell(midi(76 + i * 3), 0.8), 26.5 + i * .3, (i - 1) * .5, 0.12)              # badges
add(bell(midi(84), 3.0) + bell(midi(88), 3.0) * .7 + bell(midi(91), 3.0) * .5, 29.4, 0, 0.24)  # end card

# fade out, normalize, write
t = np.arange(N) / SR
mix *= np.clip((DUR - t) / 2.0, 0, 1)[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.2) * 0.8
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote music.wav')
