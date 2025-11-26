# Voice Transfer

Voice cloning microservice based on [Seed-VC](https://github.com/Plachtaa/seed-vc).

## What It Does

Transfers voice characteristics from one speaker to another while preserving the original speech content. Uses a diffusion-based generative model with speech disentanglement to separate content (what is said) from timbre (who says it), enabling high-quality voice conversion without parallel training data.

## Quick Start

```bash
# Install dependencies
pip install -r requirements_api.txt

# Run server
python manage.py runserver 0.0.0.0:8001
```

## API Usage

```bash
curl -X POST http://localhost:8001/api/clone/ \
  -F "source_audio=@source.wav" \
  -F "target_audio=@target.wav" \
  --output output.wav
```

See `API_README.md` for detailed documentation.

**Requirements:** Python 3.10, CUDA GPU (recommended)
