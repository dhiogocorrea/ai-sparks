import os
import json

from core.video_handler import mp4_to_wav, cut_video
from core.transcription import transcribe
from core.agent import ViralCutAgent

def prepare_folders():
    if not os.path.exists('audio'):
        os.mkdir('audio')

    if not os.path.exists('transcripts'):
        os.mkdir('transcripts')

    if not os.path.exists('video_cuts'):
        os.mkdir('video_cuts')

def process(
        video_path: str,
        language: str = 'portuguese'
):
    prepare_folders()
    filename = os.path.basename(video_path)

    audio_path = f'audio/{filename}.wav'
    transcript_path = f'transcripts/{filename}.txt'
    json_path = f'video_cuts/{filename}.json'

    if os.path.exists(transcript_path) == False:
        mp4_to_wav(input_file=video_path, output_file=audio_path)
        transcription = transcribe(audio_path=audio_path, language=language)

        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcription)
    else:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcription = f.read()

    if os.path.exists(json_path) == False:
        agent = ViralCutAgent()
        cuts = agent.invoke(transcription=transcription)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cuts, f, ensure_ascii=False)
    else:
        with open(json_path, 'r', encoding='utf-8') as f:
            cuts = json.load(f)

    for i, cut in enumerate(cuts):
        cut_path = f'video_cuts/{filename}_{str(i)}.mp4'
        cut_video(
            input_file=video_path,
            output_file=cut_path,
            start_time=cut['start_time'],
            end_time=cut['end_time']
        )

if __name__ == '__main__':
    process('videos/FELCA - Flow #379.mp4')