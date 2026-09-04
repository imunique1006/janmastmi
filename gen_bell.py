#!/usr/bin/env python3
"""
Temple Bell & BGM Generator for Janmashtami Katha
Generates an authentic Indian temple brass bell WAV file using harmonic synthesis.
"""
import wave
import struct
import math
import os

SAMPLE_RATE = 44100

def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write samples (list of floats in -1.0..1.0) to a WAV file."""
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        max_amp = 32767
        packed = struct.pack(f'<{len(samples)}h', *[
            int(max(min(s, 1.0), -1.0) * max_amp) for s in samples
        ])
        wf.writeframes(packed)

def make_temple_bell(duration=3.5, sample_rate=SAMPLE_RATE):
    """
    Authentic Ghanta (temple bell) using additive synthesis.
    A real brass bell has inharmonic partials and complex decay.
    Partials tuned to: 1x, 2.76x, 5.4x, 8.93x, 13.34x (standard bell modes)
    """
    n = int(duration * sample_rate)
    samples = [0.0] * n
    
    # Fundamental frequency of an Indian temple bell (~D5 = 587 Hz)
    f0 = 587.33
    
    # Inharmonic partials (frequency multipliers, amplitudes, decay rates)
    partials = [
        # (freq_mult, amplitude, decay_tau_seconds)
        (1.000,  0.60,  3.2),   # Fundamental — longest sustain
        (2.756,  0.30,  1.8),   # 2nd partial (minor 7th above)
        (5.404,  0.15,  1.0),   # 3rd partial (higher shimmer)
        (8.933,  0.08,  0.5),   # 4th partial (bright ting)
        (13.34,  0.04,  0.3),   # 5th partial (ultra-bright attack)
        (1.500,  0.12,  2.0),   # Perfect fifth overtone
        (3.999,  0.06,  0.8),   # 2 octaves
    ]
    
    # Attack envelope (very fast percussive onset)
    attack_samples = int(0.003 * sample_rate)  # 3ms attack
    
    for i in range(n):
        t = i / sample_rate
        value = 0.0
        
        for freq_mult, amp, tau in partials:
            freq = f0 * freq_mult
            # Exponential decay for each partial
            decay = math.exp(-t / tau)
            value += amp * decay * math.sin(2.0 * math.pi * freq * t)
        
        # Apply short attack to avoid click
        if i < attack_samples:
            value *= (i / attack_samples)
        
        # Add subtle metallic noise burst on attack (first 10ms)
        if t < 0.010:
            import random
            noise_amp = 0.08 * math.exp(-t / 0.005)
            value += noise_amp * (random.random() * 2 - 1)
        
        samples[i] = value
    
    # Normalize
    peak = max(abs(s) for s in samples)
    if peak > 0:
        samples = [s / peak * 0.92 for s in samples]
    
    return samples

def make_double_bell(sample_rate=SAMPLE_RATE):
    """Two bells: a large temple bell + a smaller bell chime."""
    bell1 = make_temple_bell(duration=3.5, sample_rate=sample_rate)
    
    # Smaller bell at slightly higher frequency (A5 = 880Hz), shorter
    n2 = int(2.2 * sample_rate)
    bell2 = [0.0] * n2
    f0_2 = 880.0
    
    partials2 = [
        (1.000, 0.5, 2.0),
        (2.756, 0.25, 1.0),
        (5.404, 0.12, 0.5),
    ]
    attack2 = int(0.002 * sample_rate)
    
    for i in range(n2):
        t = i / sample_rate
        val = 0.0
        for fm, amp, tau in partials2:
            val += amp * math.exp(-t/tau) * math.sin(2*math.pi*f0_2*fm*t)
        if i < attack2:
            val *= i / attack2
        bell2[i] = val
    
    peak2 = max(abs(s) for s in bell2)
    if peak2 > 0:
        bell2 = [s / peak2 * 0.65 for s in bell2]
    
    # Offset bell2 by 120ms, mix with bell1
    offset = int(0.12 * sample_rate)
    total_len = max(len(bell1), offset + len(bell2))
    combined = [0.0] * total_len
    
    for i, s in enumerate(bell1):
        combined[i] += s
    for i, s in enumerate(bell2):
        idx = i + offset
        if idx < total_len:
            combined[idx] += s * 0.6
    
    # Final normalize
    peak = max(abs(s) for s in combined)
    if peak > 0:
        combined = [s / peak * 0.95 for s in combined]
    
    return combined

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(__file__), 'audio')
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating temple bell sound...")
    bell_samples = make_double_bell()
    bell_path = os.path.join(out_dir, 'temple_bell.wav')
    write_wav(bell_path, bell_samples)
    print(f"✓ Temple bell saved: {bell_path} ({len(bell_samples)/SAMPLE_RATE:.2f}s)")
    
    print("Done! Audio assets generated successfully.")
