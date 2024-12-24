from dataclasses import dataclass
from typing import List, Optional, Any
import pickle

@dataclass
class SpeakerOutput:
    speaker: Optional[str]
    start_time: float
    end_time: float
    text: Optional[str]

    def to_str(self):
        return (
            f"Speaker: {self.speaker}, "
            f"Start Time: {self.start_time}, "
            f"End Time: {self.end_time}, "
            f"Text: {self.text}"
        )

@dataclass
class Meeting:
    speakers_dialog: List[SpeakerOutput]
    audio_path: str
    video_path: str
    knowledge: Any

    def save(self, file_path: str):
        """Saves the Meeting object to a file using pickle."""
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(file_path: str) -> 'Meeting':
        """Loads a Meeting object from a file using pickle."""
        with open(file_path, 'rb') as file:
            return pickle.load(file)
