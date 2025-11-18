"""
OpenAI Whisper speech recognition engine.
"""

import asyncio
import io
import numpy as np
from pathlib import Path
from typing import Optional, Callable
from loguru import logger
import torch
import whisper


class WhisperEngine:
    """Whisper-based speech recognition engine."""
    
    def __init__(self, config):
        """Initialize Whisper engine.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Model settings
        self.model_name = config.get("whisper.model", "base")
        self.device = config.get("whisper.device", "cpu")
        self.language = config.get("whisper.language", "en")
        self.fp16 = config.get("whisper.fp16", False)
        
        # Check CUDA availability
        if self.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"
            self.fp16 = False
        
        # Load model
        logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")
        self.model = whisper.load_model(
            self.model_name,
            device=self.device,
            download_root=str(Path("models"))
        )
        logger.success(f"Whisper model loaded: {self.model_name}")
        
        # Callbacks
        self.on_transcription_ready: Optional[Callable] = None
        
        # Cache
        self.last_transcription = ""
    
    def transcribe(self, audio_data: bytes) -> dict:
        """Transcribe audio data.
        
        Args:
            audio_data: Audio data in WAV format
            
        Returns:
            Transcription result dictionary
        """
        try:
            # Load audio from bytes
            audio = self._load_audio_from_bytes(audio_data)
            
            # Transcribe
            result = self.model.transcribe(
                audio,
                language=self.language,
                fp16=self.fp16,
                beam_size=self.config.get("whisper.beam_size", 5),
                best_of=self.config.get("whisper.best_of", 5),
                temperature=self.config.get("whisper.temperature", 0.0)
            )
            
            transcription = result["text"].strip()
            self.last_transcription = transcription
            
            logger.info(f"Transcription: '{transcription}'")
            
            return {
                "text": transcription,
                "language": result.get("language", self.language),
                "confidence": self._calculate_confidence(result)
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def transcribe_async(self, audio_data: bytes) -> str:
        """Asynchronously transcribe audio.
        
        Args:
            audio_data: Audio data in WAV format
            
        Returns:
            Transcription text
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.transcribe, audio_data)
        
        text = result["text"]
        confidence = result["confidence"]
        
        if self.on_transcription_ready:
            await self.on_transcription_ready(text, confidence)
        
        return text
    
    def _load_audio_from_bytes(self, audio_bytes: bytes) -> np.ndarray:
        """Load audio from WAV bytes.
        
        Args:
            audio_bytes: WAV file bytes
            
        Returns:
            Audio array
        """
        import wave
        
        # Open WAV from bytes
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wav:
            sample_rate = wav.getframerate()
            frames = wav.readframes(wav.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Resample if needed
        if sample_rate != 16000:
            import scipy.signal as signal
            audio = signal.resample(audio, int(len(audio) * 16000 / sample_rate))
        
        return audio
    
    def _calculate_confidence(self, result: dict) -> float:
        """Calculate transcription confidence.
        
        Args:
            result: Whisper result dictionary
            
        Returns:
            Confidence score (0-1)
        """
        # Use no_speech_prob as confidence indicator
        no_speech_prob = result.get("no_speech_prob", 0.5)
        confidence = 1.0 - no_speech_prob
        
        return max(0.0, min(1.0, confidence))
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up Whisper engine")
        if hasattr(self, 'model'):
            del self.model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
