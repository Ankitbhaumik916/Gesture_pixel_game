import numpy as np
import wave

# Parameters for the sound
sample_rate = 44100
duration = 0.2  # seconds
frequency = 800  # Hz

# Generate a sine wave
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
wave_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

# Save as WAV file
with wave.open("jump.wav", "w") as f:
    f.setnchannels(1)  # Mono
    f.setsampwidth(2)  # 16-bit
    f.setframerate(sample_rate)
    f.writeframes(wave_data.tobytes())

print("jump.wav created successfully!")
