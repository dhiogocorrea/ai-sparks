import os
from typing import List

from core.video_to_audio import mp4_to_wav
from core.speaker_diarization import SpeakerDiarization
from core.agent import MeetingKnowlegeAgent

from models.speaker import SpeakerOutput, Meeting

import pandas as pd

def speaker_outputs_to_dataframe(speaker_outputs: List[SpeakerOutput]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "speaker": s.speaker,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "text": s.text
        }
        for s in speaker_outputs
    ])

def process_video(video_path: str) -> List[SpeakerOutput]:
    filename = os.path.basename(video_path)

    if not os.path.exists('audio'):
        os.mkdir('audio')

    audio_path = f'audio/{filename}.wav'

    print('Converting mp4 to wav...')
    mp4_to_wav(input_file=video_path, output_file=audio_path)
    print('Transcribing the audio to text...')
    transcriptions = SpeakerDiarization().transcribe(audio_path=audio_path)

    return audio_path, transcriptions


def run_agent(transcriptions: List[SpeakerOutput], language: str):
    transcriptions_str = '\n'.join([t.to_str() for t in transcriptions])
    agent = MeetingKnowlegeAgent(language=language)
    return agent.invoke(transcriptions_str)


def get_meeting(
        video_path: str,
        language: str = 'portuguese',
        regenerate_knowledge: bool = False
    ) -> Meeting:
    filename = os.path.basename(video_path)

    if os.path.exists(f'meetings/{filename}.pkl'):
        meeting = Meeting.load(f'meetings/{filename}.pkl')
        
        if regenerate_knowledge is True:
            response = run_agent(
                transcriptions=meeting.speakers_dialog,
                language=language
            )
            meeting.knowledge = response
            meeting.save(f'meetings/{filename}.pkl')

    else:
        audio_path, transcriptions = process_video(video_path=video_path)

        response = run_agent(
            transcriptions=transcriptions,
            language=language
        )

        if not os.path.exists('meetings'):
            os.mkdir('meetings')
        
        meeting = Meeting(
            speakers_dialog=transcriptions,
            audio_path=audio_path,
            video_path=video_path,
            knowledge=response
        )

        meeting.save(f'meetings/{filename}.pkl')

        return meeting


if __name__ == '__main__':
    get_meeting('videos/test.mp4', True)
