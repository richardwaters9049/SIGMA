import os
import pygame
import random
import math
import numpy

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.muted = False
        self.setup_sounds()
    
    def setup_sounds(self):
        """Initialize all game sounds with default fallbacks"""
        # UI Sounds
        self.load_sound('select', self._create_beep(440, 50))  # Higher pitch for selection
        self.load_sound('confirm', self._create_beep(660, 100))  # Confirmation sound
        self.load_sound('back', self._create_beep(220, 50))  # Lower pitch for back/cancel
        
        # Mission-specific sounds
        self.load_sound('hack_start', self._create_glitch(3))
        self.load_sound('download', self._create_download_sound())
        self.load_sound('decrypt', self._create_decrypt_sound())
    
    def load_sound(self, name, default_sound):
        """Load a sound file or use the provided default"""
        try:
            # Try to load from file if available
            sound_path = os.path.join('assets', 'sounds', f'{name}.wav')
            if os.path.exists(sound_path):
                self.sounds[name] = pygame.mixer.Sound(sound_path)
            else:
                self.sounds[name] = default_sound
        except Exception as e:
            print(f"[!] Error loading sound {name}: {e}")
            self.sounds[name] = default_sound
    
    def play(self, name, volume=0.5):
        """Play a sound by name"""
        try:
            if self.muted or name not in self.sounds or self.sounds[name] is None:
                return
                
            sound = self.sounds[name]
            if sound is not None:
                sound.set_volume(volume)
                sound.play()
        except Exception as e:
            print(f"[!] Error playing sound '{name}': {e}")
    
    def toggle_mute(self):
        """Toggle sound on/off"""
        self.muted = not self.muted
        return self.muted
    
    # Sound generation functions
    def _create_beep(self, frequency=440, duration=100):
        """Generate a simple beep sound"""
        sample_rate = 44100
        n_samples = int(sample_rate * duration / 1000.0)
        
        # Create a numpy array for the sound
        t = numpy.linspace(0, duration / 1000.0, n_samples, False)
        tone = numpy.sin(2 * numpy.pi * frequency * t) * 0.5
        
        # Convert to 16-bit data
        audio = numpy.array([(tone * 32767).astype(numpy.int16)]).T
        
        # Convert to stereo
        stereo = numpy.column_stack((audio, audio))
        
        # Create sound from numpy array
        return pygame.sndarray.make_sound(stereo.astype(numpy.int16))
    
    def _create_glitch(self, duration=1000):
        """Create a glitchy sound effect using numpy for better performance"""
        try:
            sample_rate = 44100
            n_samples = int(sample_rate * duration / 1000)
            
            # Create an array of zeros
            samples = numpy.zeros(n_samples, dtype=numpy.int16)
            
            # Add random glitches
            glitch_indices = numpy.random.randint(0, n_samples, size=n_samples//10)  # 10% glitch density
            samples[glitch_indices] = numpy.random.randint(-32767, 32767, size=len(glitch_indices), dtype=numpy.int16)
            
            # Convert to stereo
            stereo = numpy.column_stack((samples, samples))
            
            # Create the sound
            sound = pygame.sndarray.make_sound(stereo.astype(numpy.int16))
            sound.set_volume(0.3)
            return sound
        except Exception as e:
            print(f"[!] Error creating glitch sound: {e}")
            # Return a simple beep as fallback
            return self._create_beep(440, 100)
    
    def _create_download_sound(self):
        """Create a download progress sound using numpy for better performance"""
        sample_rate = 44100
        duration = 2000  # 2 seconds
        n_samples = int(sample_rate * duration / 1000)
        
        # Create time array
        t = numpy.linspace(0, duration / 1000.0, n_samples, False)
        
        # Create rising frequency (200Hz to 1000Hz)
        freq = 200 + (t / (duration / 1000.0)) * 800
        
        # Generate the base tone
        tone = numpy.sin(2 * numpy.pi * freq * t) * 0.3
        
        # Add some noise (10% of samples get random noise)
        noise_mask = numpy.random.random(n_samples) < 0.1
        noise = numpy.random.uniform(-0.1, 0.1, n_samples) * noise_mask
        tone = numpy.clip(tone + noise, -1.0, 1.0)
        
        # Convert to 16-bit data and stereo
        audio = (tone * 32767).astype(numpy.int16)
        stereo = numpy.column_stack((audio, audio))
        
        # Create and return the sound
        return pygame.sndarray.make_sound(stereo.astype(numpy.int16)).set_volume(0.3)
    
    def _create_decrypt_sound(self):
        """Create a decryption sound effect using numpy for better performance"""
        sample_rate = 44100
        duration = 1000  # 1 second
        n_samples = int(sample_rate * duration / 1000)
        
        # Create time array
        t = numpy.linspace(0, duration / 1000.0, n_samples, False)
        
        # Create a sweeping frequency (100Hz to 1100Hz and back)
        progress = numpy.linspace(0, 1, n_samples)
        freq = 100 + numpy.sin(progress * numpy.pi) * 1000
        
        # Generate the base tone
        tone = numpy.sin(2 * numpy.pi * freq * t) * 0.4
        
        # Add some digital noise (5% of samples get random values)
        noise_mask = numpy.random.random(n_samples) < 0.05
        noise = numpy.random.uniform(-1.0, 1.0, n_samples) * noise_mask
        tone = numpy.where(noise_mask, noise, tone)
        
        # Convert to 16-bit data and stereo
        audio = (tone * 32767).astype(numpy.int16)
        stereo = numpy.column_stack((audio, audio))
        
        # Create and return the sound
        return pygame.sndarray.make_sound(stereo.astype(numpy.int16)).set_volume(0.3)
