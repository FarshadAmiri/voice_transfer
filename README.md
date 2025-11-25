# Voice Transfer

A simple voice cloning project based on [Seed-VC](https://github.com/Plachtaa/seed-vc).

## Overview

This project provides an easy-to-use interface for voice-to-voice conversion using the Seed-VC model.

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Use the `easy_voice_clone.py` module for simple voice cloning:

```python
from easy_voice_clone import clone_voice

clone_voice(
    source_audio="path/to/source.wav",
    target_audio="path/to/target.wav",
    output_path="path/to/output.wav"
)
```

## Requirements

- Python 3.10
- PyTorch with CUDA support
- See `requirements.txt` for full list of dependencies

## Credits

This project is based on [Seed-VC](https://github.com/Plachtaa/seed-vc) by Plachtaa.
