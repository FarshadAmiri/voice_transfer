"""
Voice Clone API Views
"""
import os
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
from django.conf import settings
from easy_voice_clone import clone_voice
import logging

logger = logging.getLogger(__name__)


class VoiceCloneView(APIView):
    """
    API endpoint for voice cloning.
    
    POST /api/clone/
    
    Accepts two audio files and returns the cloned voice audio.
    """
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        """
        Clone voice from source to target audio.
        
        Request body (multipart/form-data):
        - source_audio: audio file (the voice content to transfer)
        - target_audio: audio file (the voice style to clone)
        - diffusion_steps: int (optional, default: 100)
        - f0_condition: bool (optional, default: True)
        - auto_f0_adjust: bool (optional, default: True)
        - inference_cfg_rate: float (optional, default: 0.7)
        
        Returns:
        - cloned audio file
        """
        
        # Validate input files
        source_audio = request.FILES.get('source_audio')
        target_audio = request.FILES.get('target_audio')
        
        if not source_audio or not target_audio:
            return Response(
                {'error': 'Both source_audio and target_audio files are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional parameters
        diffusion_steps = int(request.data.get('diffusion_steps', 100))
        f0_condition = request.data.get('f0_condition', 'true').lower() == 'true'
        auto_f0_adjust = request.data.get('auto_f0_adjust', 'true').lower() == 'true'
        inference_cfg_rate = float(request.data.get('inference_cfg_rate', 0.7))
        
        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        try:
            # Save uploaded files
            source_path = os.path.join(temp_dir, f'source_{source_audio.name}')
            target_path = os.path.join(temp_dir, f'target_{target_audio.name}')
            output_path = os.path.join(temp_dir, 'cloned_output.wav')
            
            with open(source_path, 'wb+') as f:
                for chunk in source_audio.chunks():
                    f.write(chunk)
            
            with open(target_path, 'wb+') as f:
                for chunk in target_audio.chunks():
                    f.write(chunk)
            
            logger.info(f"Starting voice cloning: source={source_audio.name}, target={target_audio.name}")
            
            # Perform voice cloning
            clone_voice(
                source_audio=source_path,
                target_audio=target_path,
                output_path=output_path,
                diffusion_steps=diffusion_steps,
                f0_condition=f0_condition,
                auto_f0_adjust=auto_f0_adjust,
                inference_cfg_rate=inference_cfg_rate
            )
            
            # Return the cloned audio file
            if os.path.exists(output_path):
                response = FileResponse(
                    open(output_path, 'rb'),
                    content_type='audio/wav',
                    as_attachment=True,
                    filename='cloned_voice.wav'
                )
                logger.info("Voice cloning completed successfully")
                return response
            else:
                logger.error("Output file was not generated")
                return Response(
                    {'error': 'Failed to generate cloned audio'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Voice cloning error: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Voice cloning failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Cleanup temporary files
            try:
                if os.path.exists(source_path):
                    os.remove(source_path)
                if os.path.exists(target_path):
                    os.remove(target_path)
                # Keep output_path for response, but it will be cleaned up after sending
            except Exception as e:
                logger.warning(f"Cleanup error: {str(e)}")


class HealthCheckView(APIView):
    """
    Health check endpoint.
    
    GET /api/health/
    """
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'voice-clone-api',
            'version': '1.0.0'
        })
