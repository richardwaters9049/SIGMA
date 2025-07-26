import os
import pygame
import random
import math
import numpy
from enum import Enum
from typing import Optional, Dict, List


class SoundType(Enum):
    MUSIC = "music"
    SFX = "sfx"
    AMBIENT = "ambient"


class SoundTrack:
    def __init__(
        self,
        name: str,
        sound: Optional[pygame.mixer.Sound] = None,
        sound_type: SoundType = SoundType.SFX,
        volume: float = 1.0,
        loop: bool = False,
    ):
        self.name = name
        self.sound = sound
        self.type = sound_type
        self.volume = volume
        self.loop = loop
        self.channel: Optional[pygame.mixer.Channel] = None


class SoundManager:
    def __init__(self):
        # Initialize mixer with more channels
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        pygame.mixer.set_num_channels(16)  # More channels for simultaneous sounds

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, SoundTrack] = {}
        self.ambient_tracks: Dict[str, SoundTrack] = {}
        self.current_music: Optional[SoundTrack] = None
        self.current_ambient: Optional[SoundTrack] = None
        self.muted = False
        self.music_volume = 0.6
        self.sfx_volume = 0.7
        self.ambient_volume = 0.4

        # Create a separate channel for music and ambient
        self.music_channel = pygame.mixer.Channel(0)
        self.ambient_channel = pygame.mixer.Channel(1)

        # Pre-load all sounds and music
        self.setup_sounds()
        self.setup_music()
        self.setup_ambient()

    def setup_sounds(self):
        """Initialize all game sound effects with default fallbacks"""
        # UI Sounds
        self.load_sound(
            "select", self._create_beep(440, 50)
        )  # Higher pitch for selection
        self.load_sound("confirm", self._create_beep(660, 100))  # Confirmation sound
        self.load_sound(
            "back", self._create_beep(220, 50)
        )  # Lower pitch for back/cancel
        self.load_sound("error", self._create_error_sound())
        self.load_sound("typing", self._create_typing_sound())
        self.load_sound("glitch", self._create_glitch(500))

        # Mission-specific sounds
        self.load_sound("hack_start", self._create_glitch(3000))
        self.load_sound("download", self._create_download_sound())
        self.load_sound("decrypt", self._create_decrypt_sound())
        self.load_sound("success", self._create_success_sound())
        self.load_sound("failure", self._create_failure_sound())

        # Ambient sounds - removed static sound as per user request
        self.load_sound(
            "keyboard", self._create_keyboard_sound(5000)
        )  # 5 seconds of typing

    def setup_music(self):
        """Set up music tracks"""
        # Create music tracks with procedurally generated music
        self.music_tracks = {
            "menu": SoundTrack(
                "menu", self._create_menu_music(), SoundType.MUSIC, 0.6, True
            ),
            "hacking": SoundTrack(
                "hacking", self._create_hacking_music(), SoundType.MUSIC, 0.5, True
            ),
            "tense": SoundTrack(
                "tense", self._create_tense_music(), SoundType.MUSIC, 0.5, True
            ),
            "success": SoundTrack(
                "success", self._create_success_music(), SoundType.MUSIC, 0.5, False
            ),
        }

    def setup_ambient(self):
        """Set up ambient sound tracks"""
        # No ambient sounds
        self.ambient_tracks = {}

    def load_sound(
        self, name: str, default_sound: Optional[pygame.mixer.Sound] = None
    ) -> Optional[pygame.mixer.Sound]:
        """Load a sound file or use the provided default"""
        try:
            # Try to load from file if available
            sound_path = os.path.join("assets", "sounds", f"{name}.wav")
            if os.path.exists(sound_path):
                sound = pygame.mixer.Sound(sound_path)
                self.sounds[name] = sound
                return sound
        except Exception as e:
            print(f"[!] Error loading sound {name}: {e}")

        # Use default sound if provided and no file was loaded
        if default_sound is not None:
            self.sounds[name] = default_sound
            return default_sound

        return None

    def play(
        self, name: str, volume: float = None, loop: bool = False
    ) -> Optional[pygame.mixer.Channel]:
        """Play a sound effect by name"""
        if self.muted or name not in self.sounds or self.sounds[name] is None:
            return None

        try:
            sound = self.sounds[name]
            if sound is None:
                return None

            # Use provided volume or default SFX volume
            sound.set_volume(volume if volume is not None else self.sfx_volume)

            # Find an available channel
            channel = pygame.mixer.find_channel(force=False)
            if channel is None:
                channel = pygame.mixer.Channel(2)  # Use a higher channel for one-shots

            if loop:
                channel.play(sound, loops=-1)  # -1 means loop indefinitely
            else:
                channel.play(sound)

            return channel
        except Exception as e:
            print(f"[!] Error playing sound '{name}': {e}")

    def toggle_mute(self) -> bool:
        """Toggle sound on/off"""
        self.muted = not self.muted

        # Update all volumes based on mute state
        if self.muted:
            # Mute all channels
            for i in range(pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(i).set_volume(0)
        else:
            # Restore volumes
            self.set_volumes(self.music_volume, self.sfx_volume, self.ambient_volume)

        return self.muted

    def set_volumes(
        self, music_volume: float, sfx_volume: float, ambient_volume: float
    ) -> None:
        """Set volume levels for different sound types"""
        self.music_volume = max(0.0, min(1.0, music_volume))
        self.sfx_volume = max(0.0, min(1.0, sfx_volume))
        self.ambient_volume = max(0.0, min(1.0, ambient_volume))

        # Update currently playing sounds
        if self.current_music:
            self.music_channel.set_volume(self.music_volume * self.current_music.volume)

        if self.current_ambient:
            self.ambient_channel.set_volume(
                self.ambient_volume * self.current_ambient.volume
            )

        # Update SFX channels (this will affect future SFX plays)
        for i in range(2, pygame.mixer.get_num_channels()):
            channel = pygame.mixer.Channel(i)
            if channel.get_busy():
                # Get current volume scale if we can
                current_volume = getattr(channel, "_last_volume", 1.0)
                channel.set_volume(self.sfx_volume * current_volume)

    def play_music(self, track_name: str, fade_in: int = 1000) -> bool:
        """Play a music track by name with optional fade-in"""
        if self.muted or track_name not in self.music_tracks:
            return False

        try:
            track = self.music_tracks[track_name]
            if track.sound is None:
                return False

            # Stop current music if playing
            if self.current_music:
                self.stop_music()

            # Set volume and play with fade in
            track.sound.set_volume(0)  # Start at 0 for fade in
            self.music_channel.play(track.sound, loops=-1 if track.loop else 0)
            self.music_channel.set_volume(self.music_volume * track.volume)

            # Fade in if specified
            if fade_in > 0:
                self.music_channel.set_volume(0)
                self.music_channel.fadeout(0)  # Stop any pending fades
                self.music_channel.play(track.sound, loops=-1 if track.loop else 0)
                self.music_channel.fade(self.music_volume * track.volume, fade_in)

            self.current_music = track
            return True

        except Exception as e:
            print(f"[!] Error playing music '{track_name}': {e}")
            return False

    def play_ambient(self, ambient_name: str, fade_in: int = 1000) -> bool:
        """Play an ambient sound by name with optional fade-in"""
        if self.muted or ambient_name not in self.ambient_tracks:
            return False

        try:
            track = self.ambient_tracks[ambient_name]
            if track.sound is None:
                return False

            # Don't restart if already playing
            if self.current_ambient == track:
                return True

            # Stop current ambient if playing
            if self.current_ambient:
                self.stop_ambient()

            # Set volume and play with fade in
            track.sound.set_volume(0)  # Start at 0 for fade in
            self.ambient_channel.play(track.sound, loops=-1 if track.loop else 0)
            self.ambient_channel.set_volume(self.ambient_volume * track.volume)

            # Fade in if specified
            if fade_in > 0:
                self.ambient_channel.set_volume(0)
                self.ambient_channel.fadeout(0)  # Stop any pending fades
                self.ambient_channel.play(track.sound, loops=-1 if track.loop else 0)
                self.ambient_channel.fade(self.ambient_volume * track.volume, fade_in)

            self.current_ambient = track
            return True

        except Exception as e:
            print(f"[!] Error playing ambient '{ambient_name}': {e}")
            return False

    def stop_music(self, fade_out: int = 1000) -> None:
        """Stop the currently playing music with optional fadeout"""
        if self.current_music:
            if fade_out > 0:
                self.music_channel.fadeout(fade_out)
            else:
                self.music_channel.stop()
            self.current_music = None

    def stop_ambient(self, fade_out: int = 1000) -> None:
        """Stop the currently playing ambient sound with optional fadeout"""
        if self.current_ambient:
            if fade_out > 0:
                self.ambient_channel.fadeout(fade_out)
            else:
                self.ambient_channel.stop()
            self.current_ambient = None

    def pause_all(self) -> None:
        """Pause all audio playback"""
        pygame.mixer.pause()

    def unpause_all(self) -> None:
        """Resume all audio playback"""
        pygame.mixer.unpause()

    # ==============================================
    # Procedural Sound Generation Methods
    # ==============================================

    def _create_menu_music(self) -> pygame.mixer.Sound:
        """Create ambient menu music with a cyberpunk feel"""
        sample_rate = 44100
        duration = 30  # seconds
        n_samples = int(sample_rate * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Create multiple layers of sound
        bass = 0.2 * numpy.sin(2 * numpy.pi * 110 * t)  # A2
        pad = 0.15 * numpy.sin(2 * numpy.pi * 220 * t)  # A3
        arp = 0.1 * numpy.sin(
            2 * numpy.pi * 440 * t * (1 + 0.1 * numpy.sin(0.5 * t))
        )  # A4 with vibrato

        # Add some percussion
        kick = numpy.zeros_like(t)
        kick_times = numpy.arange(0, duration, 0.5)  # Kick every 0.5 seconds
        for time in kick_times:
            start = int(time * sample_rate)
            end = min(start + 1000, len(kick))  # 1ms kick
            if start < len(kick):
                kick[start:end] += numpy.linspace(1, 0, end - start) * 0.3

        # Combine all layers
        audio = 0.7 * (bass + pad + arp) + 0.5 * kick

        # Normalize and convert to stereo
        audio = numpy.clip(audio, -0.99, 0.99)
        stereo = numpy.column_stack((audio, audio))
        return pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))

    def _create_hacking_music(self) -> pygame.mixer.Sound:
        """Create intense hacking music"""
        sample_rate = 44100
        duration = 60  # seconds
        n_samples = int(sample_rate * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Create a pulsing bassline
        bass_freq = 110 * (1 + 0.1 * numpy.sin(0.5 * t))  # Slight detune
        bass = 0.25 * numpy.sin(2 * numpy.pi * bass_freq * t)

        # Add arpeggios
        arp_notes = [220, 277, 330, 440]  # A3, C#4, E4, A4
        arp = numpy.zeros_like(t)
        for i in range(len(t)):
            note_idx = int(t[i] * 4) % len(arp_notes)
            arp[i] = 0.15 * numpy.sin(2 * numpy.pi * arp_notes[note_idx] * t[i])

        # Add glitch effects
        glitch = numpy.random.uniform(-0.1, 0.1, len(t))
        glitch_mask = numpy.random.random(len(t)) > 0.99  # 1% chance of glitch
        glitch = glitch * glitch_mask

        # Combine and normalize
        audio = 0.8 * (bass + arp) + 0.3 * glitch
        audio = numpy.clip(audio, -0.99, 0.99)
        stereo = numpy.column_stack((audio, audio))

        sound = pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))
        sound.set_volume(0.6)
        return sound

    def _create_tense_music(self) -> pygame.mixer.Sound:
        """Create tense, suspenseful music"""
        sample_rate = 44100
        duration = 45  # seconds
        n_samples = int(sample_rate * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Create a drone
        drone = 0.1 * numpy.sin(2 * numpy.pi * 73.42 * t)  # D#2
        drone += 0.08 * numpy.sin(2 * numpy.pi * 110 * t)  # A2

        # Add random plucks
        pluck_env = numpy.exp(-5 * (t % 1.0))  # Exponential decay for plucks
        pluck = 0.15 * pluck_env * numpy.sin(2 * numpy.pi * 440 * t)

        # Add noise for tension
        noise = 0.05 * numpy.random.uniform(-1, 1, len(t))

        # Combine and normalize
        audio = 0.7 * (drone + pluck + noise)
        audio = numpy.clip(audio, -0.99, 0.99)
        stereo = numpy.column_stack((audio, audio))

        sound = pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))
        sound.set_volume(0.5)
        return sound

    def _create_success_music(self) -> pygame.mixer.Sound:
        """Create a short success fanfare"""
        sample_rate = 44100
        duration = 5  # seconds
        n_samples = int(sample_rate * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Create a rising arpeggio
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        audio = numpy.zeros_like(t)

        for i, note in enumerate(notes):
            start = int(i * 0.2 * sample_rate)
            end = int((i + 1) * 0.2 * sample_rate)
            if end > len(audio):
                break
            env = numpy.linspace(1, 0, end - start) ** 2  # Decaying envelope
            audio[start:end] += (
                0.3 * env * numpy.sin(2 * numpy.pi * note * t[start:end])
            )

        # Add some sparkle
        sparkle = numpy.random.uniform(-0.1, 0.1, len(t))
        sparkle_mask = numpy.random.random(len(t)) > 0.95  # 5% chance of sparkle
        audio += 0.5 * sparkle * sparkle_mask

        # Apply a fade out
        fade_out = numpy.linspace(1, 0, int(0.5 * sample_rate))  # 0.5s fade out
        if len(fade_out) < len(audio):
            audio[-len(fade_out) :] *= fade_out

        audio = numpy.clip(audio, -0.99, 0.99)
        stereo = numpy.column_stack((audio, audio))

        sound = pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))
        sound.set_volume(0.7)
        return sound

    def _create_server_room_ambient(self, duration_ms: int) -> pygame.mixer.Sound:
        """Create server room ambient sound"""
        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000)
        t = numpy.linspace(0, duration_ms / 1000, n_samples, False)

        # Add some low-frequency hum for server room ambience
        hum = 0.02 * numpy.sin(2 * numpy.pi * 60 * t)  # 60Hz hum

        # Add some random server fan sounds
        fan_env = 0.5 * (1 + numpy.sin(2 * numpy.pi * 0.05 * t))  # Slow pulsing
        fan = fan_env * 0.01 * numpy.sin(2 * numpy.pi * 120 * t)  # Clean 120Hz fan sound

        # Add occasional disk activity
        disk = numpy.zeros(n_samples)
        disk_times = numpy.random.poisson(5, size=100) * 0.1  # Random disk activity
        for time in numpy.cumsum(disk_times):
            if time * sample_rate < n_samples:
                start = int(time * sample_rate)
                end = min(start + 100, n_samples)
                # Subtle, clean disk activity
                disk[start:end] = 0.02 * numpy.sin(2 * numpy.pi * 800 * numpy.linspace(0, 0.1, end - start))

        # Combine all layers with reduced overall volume
        audio = 0.5 * (hum + fan + disk)
        audio = numpy.clip(audio, -0.99, 0.99)

        # Convert to stereo with slight variation between channels
        left = audio * 0.9 + 0.1 * numpy.random.uniform(-1, 1, n_samples)
        right = audio * 0.9 + 0.1 * numpy.random.uniform(-1, 1, n_samples)
        stereo = numpy.column_stack((left, right))

        return pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))

    def _create_keyboard_sound(self, duration_ms: int = 5000) -> pygame.mixer.Sound:
        """Create a keyboard typing sound effect"""
        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000)

        # Create an array to hold the audio data
        audio = numpy.zeros(n_samples)

        # Create key press events with varying speeds and patterns
        key_interval = int(
            sample_rate * random.uniform(0.05, 0.15)
        )  # 50-150ms between key presses

        for i in range(0, n_samples - 1000, key_interval):
            if random.random() > 0.3:  # 70% chance of a key press
                # Randomize the timing slightly
                pos = min(
                    i + random.randint(-key_interval // 3, key_interval // 3),
                    n_samples - 1000,
                )

                # Random key press length (3-10ms)
                press_len = random.randint(130, 400)

                # Random frequency for this key (higher frequencies for higher keys)
                freq = random.uniform(100, 1000)

                # Create a short tone for the key press
                t = numpy.linspace(0, press_len / 1000, press_len, False)
                tone = 0.2 * numpy.sin(2 * numpy.pi * freq * t)

                # Apply an envelope (quick attack, quick release)
                attack = int(press_len * 0.2)
                release = int(press_len * 0.3)
                sustain = press_len - attack - release

                envelope = numpy.ones(press_len)
                if attack > 0:
                    envelope[:attack] = numpy.linspace(0, 1, attack)
                if release > 0:
                    envelope[-release:] = numpy.linspace(1, 0, release)

                # Add some randomness to the volume
                volume = random.uniform(0.1, 0.3)

                # Add the key press to the audio
                end = min(pos + press_len, n_samples)
                audio[pos:end] += (tone * envelope * volume)[: end - pos]

        # Add some subtle background noise
        noise = numpy.random.uniform(-0.02, 0.02, n_samples)
        audio = audio * 0.8 + noise * 0.2

        # Normalize and convert to stereo
        audio = numpy.clip(audio, -0.99, 0.99)
        stereo = numpy.column_stack((audio, audio * 0.9))  # Slight stereo variation

        return pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))

    def _create_typing_sound(self, duration_ms: int = 5000) -> pygame.mixer.Sound:
        """Create a typing sound effect (alias for backward compatibility)"""
        return self._create_keyboard_sound(duration_ms)

    def _create_static_sound(self, duration_ms: int) -> pygame.mixer.Sound:
        """Create a static noise sound"""
        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000)

        # Create noise with some filtering
        noise = numpy.random.uniform(-1, 1, n_samples)

        # Apply a filter to make it more like radio static
        for i in range(2, n_samples):
            noise[i] = 0.5 * noise[i] + 0.3 * noise[i - 1] + 0.2 * noise[i - 2]

        # Add some variation in volume
        env = 0.5 * (
            1 + numpy.sin(2 * numpy.pi * 0.5 * numpy.linspace(0, 1, n_samples))
        )
        noise *= env

        noise = numpy.clip(noise, -0.99, 0.99)
        stereo = numpy.column_stack((noise, noise * 0.95))  # Slight stereo variation

        return pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))

    # ==============================================
    # Basic Sound Effects
    # ==============================================

    def _create_success_sound(self) -> pygame.mixer.Sound:
        """Create a success confirmation sound"""
        sample_rate = 44100
        duration = 0.6  # seconds
        n_samples = int(sample_rate * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Create a rising major chord (C-E-G)
        c_note = 0.2 * numpy.sin(2 * numpy.pi * 523.25 * t)  # C5
        e_note = 0.15 * numpy.sin(2 * numpy.pi * 659.25 * t)  # E5
        g_note = 0.15 * numpy.sin(2 * numpy.pi * 783.99 * t)  # G5

        # Create amplitude envelope (quick attack, medium release)
        attack = int(0.05 * sample_rate)  # 50ms attack
        release = int(0.3 * sample_rate)  # 300ms release

        envelope = numpy.ones(n_samples)
        if attack > 0:
            envelope[:attack] = numpy.linspace(0, 1, attack)
        if release > 0:
            envelope[-release:] = numpy.linspace(1, 0, release)

        # Combine notes and apply envelope
        audio = (c_note + e_note + g_note) * envelope
        audio = numpy.clip(audio, -0.99, 0.99)

        # Convert to stereo with slight variation
        stereo = numpy.column_stack((audio, audio * 0.95))

        sound = pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))
        sound.set_volume(0.6)
        return sound

    def _create_failure_sound(self) -> pygame.mixer.Sound:
        """Create a failure sound effect"""
        sample_rate = 44100
        duration = 0.8  # seconds
        n_samples = int(sample_rate * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Create a dissonant minor second interval (C and C#)
        c_note = 0.2 * numpy.sin(2 * numpy.pi * 261.63 * t)  # C4
        cs_note = 0.2 * numpy.sin(2 * numpy.pi * 277.18 * t)  # C#4

        # Create a wobbly low frequency for tension
        wobble = 0.1 * numpy.sin(2 * numpy.pi * 2 * t)  # 2Hz wobble

        # Create amplitude envelope (quick attack, medium release)
        attack = int(0.05 * sample_rate)  # 50ms attack
        decay = int(0.1 * sample_rate)  # 100ms decay to sustain
        release = int(0.3 * sample_rate)  # 300ms release

        envelope = numpy.ones(n_samples)
        if attack > 0:
            envelope[:attack] = numpy.linspace(0, 1, attack)
        if decay > 0 and attack + decay < n_samples:
            envelope[attack : attack + decay] = numpy.linspace(1, 0.7, decay)
        if release > 0:
            envelope[-release:] = numpy.linspace(envelope[-release - 1], 0, release)

        # Add some noise for a harsh quality
        noise = 0.15 * numpy.random.uniform(-1, 1, n_samples)
        noise *= numpy.linspace(1, 0.2, n_samples)  # Fade out noise

        # Combine all elements
        audio = (c_note + cs_note + wobble + noise) * envelope
        audio = numpy.clip(audio, -0.99, 0.99)

        # Convert to stereo with slight variation
        stereo = numpy.column_stack((audio, audio * 0.9))

        sound = pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))
        sound.set_volume(0.65)
        return sound

    def _create_error_sound(self) -> pygame.mixer.Sound:
        """Create an error beep sound"""
        sample_rate = 44100
        duration = 0.3  # seconds
        n_samples = int(sample_rate * duration)
        t = numpy.linspace(0, duration, n_samples, False)

        # Create a harsh beep with a falling pitch
        start_freq = 880  # A5
        end_freq = 220  # A3
        freq = numpy.linspace(start_freq, end_freq, n_samples)

        # Create amplitude envelope (quick attack, slow release)
        attack = int(0.05 * sample_rate)  # 50ms attack
        release = int(0.15 * sample_rate)  # 150ms release

        envelope = numpy.ones(n_samples)
        if attack > 0:
            envelope[:attack] = numpy.linspace(0, 1, attack)
        if release > 0:
            envelope[-release:] = numpy.linspace(1, 0, release)

        # Generate the sound wave
        audio = 0.4 * numpy.sin(2 * numpy.pi * freq * t) * envelope
        audio = numpy.clip(audio, -0.99, 0.99)

        # Convert to stereo
        stereo = numpy.column_stack((audio, audio * 0.9))  # Slight stereo variation

        sound = pygame.sndarray.make_sound((stereo * 32767).astype(numpy.int16))
        sound.set_volume(0.7)
        return sound

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
            glitch_indices = numpy.random.randint(
                0, n_samples, size=n_samples // 10
            )  # 10% glitch density
            samples[glitch_indices] = numpy.random.randint(
                -32767, 32767, size=len(glitch_indices), dtype=numpy.int16
            )

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
