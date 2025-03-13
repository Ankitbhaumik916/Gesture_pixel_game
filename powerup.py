import numpy as np
import wave

sample_rate = 44100
duration = 0.3  # seconds
frequency = 1200  # Hz

t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
wave_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

with wave.open("powerup.wav", "w") as f:
    f.setnchannels(1)  # Mono
    f.setsampwidth(2)  # 16-bit
    f.setframerate(sample_rate)
    f.writeframes(wave_data.tobytes())

print("powerup.wav created successfully!")
