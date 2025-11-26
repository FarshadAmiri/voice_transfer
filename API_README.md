# Voice Transfer Django Microservice

A Django REST API microservice for voice cloning based on [Seed-VC](https://github.com/Plachtaa/seed-vc).

## Overview

This microservice provides a REST API endpoint for voice-to-voice conversion using the Seed-VC model. It's designed to run independently with Python 3.10 and can be called from other applications (like Django 3.12 apps) via HTTP requests.

## Setup

### 1. Environment Setup

Use the existing virtual environment:
```bash
D:\Projects\venv_voice\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements_api.txt
```

### 3. Run the Server

```bash
python manage.py runserver 0.0.0.0:8001
```

The API will be available at `http://localhost:8001`

## API Endpoints

### Health Check
```
GET http://localhost:8001/api/health/
```

**Response:**
```json
{
    "status": "healthy",
    "service": "voice-clone-api",
    "version": "1.0.0"
}
```

### Voice Clone
```
POST http://localhost:8001/api/clone/
```

**Request (multipart/form-data):**
- `source_audio`: Audio file (the content/speech to transfer)
- `target_audio`: Audio file (the voice style to clone)
- `diffusion_steps`: Integer (optional, default: 100)
- `f0_condition`: Boolean (optional, default: true)
- `auto_f0_adjust`: Boolean (optional, default: true)
- `inference_cfg_rate`: Float (optional, default: 0.7)

**Response:**
- Returns the cloned audio file as `audio/wav`

## Usage from Another Django App (Python 3.12)

### Using Python Requests

```python
import requests

def call_voice_clone_service(source_audio_path, target_audio_path, output_path):
    """
    Call the voice cloning microservice from another app.
    """
    url = "http://localhost:8001/api/clone/"
    
    with open(source_audio_path, 'rb') as source_file, \
         open(target_audio_path, 'rb') as target_file:
        
        files = {
            'source_audio': source_file,
            'target_audio': target_file,
        }
        
        data = {
            'diffusion_steps': 100,
            'f0_condition': 'true',
            'auto_f0_adjust': 'true',
            'inference_cfg_rate': 0.7
        }
        
        response = requests.post(url, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as output_file:
                output_file.write(response.content)
            return True
        else:
            print(f"Error: {response.json()}")
            return False

# Example usage in Django view
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def clone_voice_view(request):
    source_file = request.FILES.get('source_audio')
    target_file = request.FILES.get('target_audio')
    
    # Save temporary files
    source_path = f'/tmp/source_{source_file.name}'
    target_path = f'/tmp/target_{target_file.name}'
    output_path = f'/tmp/cloned_{source_file.name}'
    
    with open(source_path, 'wb') as f:
        f.write(source_file.read())
    with open(target_path, 'wb') as f:
        f.write(target_file.read())
    
    # Call microservice
    success = call_voice_clone_service(source_path, target_path, output_path)
    
    if success:
        return JsonResponse({'status': 'success', 'output': output_path})
    else:
        return JsonResponse({'status': 'error'}, status=500)
```

### Using cURL for Testing

```bash
curl -X POST http://localhost:8001/api/clone/ \
  -F "source_audio=@path/to/source.wav" \
  -F "target_audio=@path/to/target.wav" \
  -F "diffusion_steps=100" \
  -F "f0_condition=true" \
  -F "auto_f0_adjust=true" \
  -F "inference_cfg_rate=0.7" \
  --output cloned_output.wav
```

## Production Considerations

1. **Security**: Add authentication (e.g., API keys, JWT tokens)
2. **ALLOWED_HOSTS**: Update `settings.py` with specific domains
3. **SECRET_KEY**: Use environment variable for production
4. **HTTPS**: Deploy behind a reverse proxy (nginx) with SSL
5. **File Cleanup**: Implement proper temporary file cleanup
6. **Rate Limiting**: Add rate limiting to prevent abuse
7. **Async Processing**: Consider using Celery for long-running tasks
8. **Monitoring**: Add logging and monitoring tools

## Requirements

- Python 3.10
- Virtual environment at: `D:\Projects\venv_voice\Scripts`
- CUDA-capable GPU (recommended for faster processing)

## Credits

Based on [Seed-VC](https://github.com/Plachtaa/seed-vc) by Plachtaa.
