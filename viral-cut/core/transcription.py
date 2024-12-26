import whisper

def transcribe(audio_path: str, model: str = 'base', language = 'portuguese') -> str:
    model = whisper.load_model(model)
    result = model.transcribe(audio_path, language=language)
    
    segments = []
    for seg in result["segments"]:
        txt = f"[{seg['start']}:{seg['end']}] {seg['text']}"
        segments.append(txt)
    
    return '\n'.join(segments)