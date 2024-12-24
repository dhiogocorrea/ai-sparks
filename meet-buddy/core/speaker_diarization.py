import os
from typing import List
from dotenv import load_dotenv

from pyannote.audio import Pipeline
import whisper

from models.speaker import SpeakerOutput

load_dotenv()

class SpeakerDiarization:
    def __init__(self):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.getenv("HF_ACCESS_KEY")
        )
        self.whisper_model = whisper.load_model("small", device='cpu')

    def transcribe(self, audio_path: str) -> List[SpeakerOutput]:
        """
        1. Rodar Pyannote para diarização
        2. Rodar Whisper (uma vez no áudio completo)
        3. Distribuir cada trecho de texto do Whisper para o turno de fala
           que tiver a maior intersecção de tempo (evitando repetições)
        """

        # 1) Speaker Diarization
        diarization_result = self.pipeline(audio_path)

        # 2) Whisper Transcription (uma vez no arquivo inteiro)
        transcription = self.whisper_model.transcribe(
            audio_path, language="pt", fp16=False
        )
        whisper_segments = transcription["segments"]

        # ----------------------------------------
        # Criar objetos SpeakerOutput para cada turno
        # ----------------------------------------
        speaker_outputs = []
        for turn, _, speaker_label in diarization_result.itertracks(yield_label=True):
            speaker_outputs.append(
                SpeakerOutput(
                    speaker=speaker_label,
                    start_time=turn.start,
                    end_time=turn.end,
                    text=""
                )
            )

        # ----------------------------------------
        # 3) Para cada segmento do Whisper,
        #    encontrar o turno que mais se sobrepõe
        # ----------------------------------------
        for ws in whisper_segments:
            w_start, w_end = ws["start"], ws["end"]
            w_text = ws["text"]

            best_overlap = 0.0
            best_index = None

            # Verificar o grau de sobreposição com cada turno
            for i, spk_out in enumerate(speaker_outputs):
                spk_start = spk_out.start_time
                spk_end = spk_out.end_time

                overlap_start = max(spk_start, w_start)
                overlap_end = min(spk_end, w_end)
                overlap = overlap_end - overlap_start

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_index = i

            # Se houve alguma sobreposição, anexa o texto àquele turno
            if best_index is not None and best_overlap > 0:
                speaker_outputs[best_index].text += " " + w_text

        # Limpar espaços e ordenar por tempo de início
        for spk_out in speaker_outputs:
            spk_out.text = spk_out.text.strip()

        speaker_outputs.sort(key=lambda x: x.start_time)

        return speaker_outputs
