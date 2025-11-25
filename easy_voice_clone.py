"""
Easy Voice Cloning Interface

This module provides a simple interface for voice-to-voice cloning using Seed-VC.
Just import this file and call the clone_voice() function!

Example:
    from easy_voice_clone import clone_voice
    
    clone_voice(
        source_audio="path/to/source.wav",
        target_audio="path/to/target.wav",
        output_path="path/to/output.wav"
    )
"""

import os
import torch
import numpy as np
import soundfile as sf
from seed_vc_wrapper import SeedVCWrapper


class EasyVoiceClone:
    """Easy-to-use wrapper for Seed-VC voice cloning."""
    
    def __init__(self, device=None):
        """
        Initialize the voice cloning model.
        
        Args:
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
        """
        print("🎤 Initializing Seed-VC voice cloning models...")
        print("   This may take a few minutes on first run (downloading models)...")
        
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                print(f"   ✓ Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                self.device = torch.device("cpu")
                print("   ⚠ Using CPU (this will be slower)")
        else:
            self.device = torch.device(device)
            print(f"   ✓ Using device: {device}")
        
        self.model = SeedVCWrapper(device=self.device)
        print("   ✓ Models loaded successfully!")
    
    def clone_voice(
        self,
        source_audio,
        target_audio,
        output_path,
        # Voice conversion parameters
        diffusion_steps=25,
        length_adjust=1.0,
        inference_cfg_rate=0.7,
        # F0 (pitch) parameters for singing voice
        f0_condition=False,
        auto_f0_adjust=True,
        pitch_shift=0,
        # Output parameters
        sample_rate=None
    ):
        """
        Clone voice from source audio to match target voice.
        
        Args:
            source_audio (str): Path to source audio file (the speech/singing to convert)
            target_audio (str): Path to target audio file (the voice to clone)
            output_path (str): Path where output audio will be saved
            
            diffusion_steps (int): Number of diffusion steps. Default: 25
                - Higher = better quality but slower (10-100 recommended)
                - Use 10 for fast results, 50-100 for best quality
            
            length_adjust (float): Speed adjustment. Default: 1.0
                - <1.0 speeds up the speech
                - >1.0 slows down the speech
            
            inference_cfg_rate (float): Classifier-free guidance rate. Default: 0.7
                - Has subtle influence on output quality
            
            f0_condition (bool): Use F0 (pitch) conditioning. Default: False
                - MUST be True for singing voice conversion
                - Set to False for regular speech
            
            auto_f0_adjust (bool): Automatically adjust F0 to match target. Default: True
                - Only works when f0_condition=True
            
            pitch_shift (int): Pitch shift in semitones. Default: 0
                - Positive values = higher pitch
                - Negative values = lower pitch
                - Only works when f0_condition=True
            
            sample_rate (int): Output sample rate. Default: None (auto-detect)
                - 22050 Hz for regular speech
                - 44100 Hz for singing voice (when f0_condition=True)
        
        Returns:
            str: Path to the output audio file
        
        Example:
            # Simple speech conversion
            clone_voice("my_speech.wav", "target_voice.wav", "output.wav")
            
            # Singing voice conversion with pitch adjustment
            clone_voice(
                "my_singing.wav",
                "target_singer.wav",
                "output.wav",
                f0_condition=True,
                pitch_shift=-2,  # Lower by 2 semitones
                diffusion_steps=50
            )
        """
        # Validate input files
        if not os.path.exists(source_audio):
            raise FileNotFoundError(f"Source audio not found: {source_audio}")
        if not os.path.exists(target_audio):
            raise FileNotFoundError(f"Target audio not found: {target_audio}")
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n🎵 Converting voice...")
        print(f"   Source: {os.path.basename(source_audio)}")
        print(f"   Target: {os.path.basename(target_audio)}")
        print(f"   Output: {output_path}")
        print(f"   Settings: steps={diffusion_steps}, f0={f0_condition}, pitch_shift={pitch_shift}")
        
        # Determine sample rate
        if sample_rate is None:
            sample_rate = 44100 if f0_condition else 22050
        
        # Run voice conversion using streaming but collect all chunks
        # (The function is a generator even with stream_output=False due to yield statements)
        result_gen = self.model.convert_voice(
            source=source_audio,
            target=target_audio,
            diffusion_steps=diffusion_steps,
            length_adjust=length_adjust,
            inference_cfg_rate=inference_cfg_rate,
            f0_condition=f0_condition,
            auto_f0_adjust=auto_f0_adjust,
            pitch_shift=pitch_shift,
            stream_output=True  # Use streaming to get the final audio
        )
        
        # Consume the generator and get the final audio
        result = None
        for mp3_bytes, full_audio in result_gen:
            if full_audio is not None:
                # full_audio is a tuple (sample_rate, audio_array)
                if isinstance(full_audio, tuple) and len(full_audio) == 2:
                    _, result = full_audio
                else:
                    result = full_audio
        
        # Convert result to numpy array if needed
        if result is None:
            raise TypeError("No audio was generated from convert_voice")
        
        if isinstance(result, torch.Tensor):
            result = result.cpu().numpy()
        elif not isinstance(result, np.ndarray):
            raise TypeError(f"Unexpected audio type: {type(result)}")
        
        # Ensure result is proper numpy array with correct shape
        if len(result.shape) > 1:
            # If multi-dimensional, flatten to mono
            result = result.flatten()
        
        # Normalize to prevent clipping
        max_val = np.abs(result).max()
        if max_val > 1.0:
            result = result / max_val * 0.95
        elif max_val < 0.1:  # Boost quiet audio
            result = result / max_val * 0.5
        
        # Convert to float32 for compatibility
        result = result.astype(np.float32)
        
        # Save output audio
        try:
            sf.write(output_path, result, sample_rate, subtype='PCM_16')
            print(f"   ✓ Voice cloning complete!")
            print(f"   ✓ Saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"   ✗ Error saving file: {e}")
            print(f"   Debug info: shape={result.shape}, dtype={result.dtype}, sr={sample_rate}")
            raise


# Global instance (lazy loading)
_global_cloner = None


def clone_voice(
    source_audio,
    target_audio,
    output_path,
    diffusion_steps=25,
    length_adjust=1.0,
    inference_cfg_rate=0.7,
    f0_condition=False,
    auto_f0_adjust=True,
    pitch_shift=0,
    sample_rate=None,
    device=None
):
    """
    Simple function to clone voice. Automatically initializes the model on first call.
    
    This is the easiest way to use voice cloning - just call this function!
    
    Args:
        source_audio (str): Path to source audio file (the speech/singing to convert)
        target_audio (str): Path to target audio file (the voice to clone)
        output_path (str): Path where output audio will be saved
        diffusion_steps (int): Quality vs speed (10=fast, 50-100=best quality)
        length_adjust (float): Speed adjustment (<1.0=faster, >1.0=slower)
        inference_cfg_rate (float): Classifier-free guidance rate
        f0_condition (bool): Use F0 conditioning (MUST be True for singing)
        auto_f0_adjust (bool): Auto-adjust pitch to match target
        pitch_shift (int): Pitch shift in semitones
        sample_rate (int): Output sample rate (None=auto)
        device (str): Device to use ('cuda', 'cpu', or None=auto)
    
    Returns:
        str: Path to the output audio file
    
    Example:
        # Speech conversion
        clone_voice("my_speech.wav", "celebrity_voice.wav", "output.wav")
        
        # Singing voice with pitch adjustment
        clone_voice(
            "my_singing.wav", 
            "singer_voice.wav", 
            "output.wav",
            f0_condition=True,
            pitch_shift=-3,
            diffusion_steps=50
        )
    """
    global _global_cloner
    
    # Initialize model on first call
    if _global_cloner is None:
        _global_cloner = EasyVoiceClone(device=device)
    
    return _global_cloner.clone_voice(
        source_audio=source_audio,
        target_audio=target_audio,
        output_path=output_path,
        diffusion_steps=diffusion_steps,
        length_adjust=length_adjust,
        inference_cfg_rate=inference_cfg_rate,
        f0_condition=f0_condition,
        auto_f0_adjust=auto_f0_adjust,
        pitch_shift=pitch_shift,
        sample_rate=sample_rate
    )


if __name__ == "__main__":
    # Example usage when run directly
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python easy_voice_clone.py <source_audio> <target_audio> <output_path> [--f0] [--pitch_shift N]")
        print("\nExample:")
        print("  python easy_voice_clone.py my_voice.wav celebrity.wav output.wav")
        print("  python easy_voice_clone.py singing.wav singer.wav output.wav --f0 --pitch_shift -2")
        sys.exit(1)
    
    # Parse command line arguments
    source = sys.argv[1]
    target = sys.argv[2]
    output = sys.argv[3]
    
    # Optional flags
    use_f0 = "--f0" in sys.argv
    pitch = 0
    if "--pitch_shift" in sys.argv:
        idx = sys.argv.index("--pitch_shift")
        if idx + 1 < len(sys.argv):
            pitch = int(sys.argv[idx + 1])
    
    # Run voice cloning
    clone_voice(
        source_audio=source,
        target_audio=target,
        output_path=output,
        f0_condition=use_f0,
        pitch_shift=pitch,
        diffusion_steps=25
    )
