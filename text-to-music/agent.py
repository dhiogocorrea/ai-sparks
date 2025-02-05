import os
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class MelodyAgent:
    def __init__(self):
        load_dotenv()

        prompt_template_str = """
        Your job is to get the best track for a given description.

        The available tracks are:
        {tracks}

        The description is:
        {description}

        Your output must be a JSON-structured object, with the following fields:

        - title [str]: The title of the track.
        - artist [str]: The artist of the track.
        - album_name [str]: The album name of the track.
        - tags [list]: The tags of the track.
        - url [str]: The URL of the track.

        You must ONLY respond with the JSON-structured object, nothing else.
        """

        prompt = ChatPromptTemplate.from_template(prompt_template_str)

        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o",
            temperature=0.9
        )

        self.chain = prompt | llm


    def invoke(self, genre: str, description: str):
        if os.path.exists(f'track_data/{genre}.json'):
            tracks = json.load(open(f'track_data/{genre}.json', 'r', encoding='utf-8'))
        else:
            tracks = json.load(open(f'track_data/rock.json', 'r', encoding='utf-8'))

        response = self.chain.invoke({"tracks": self.convert_tracks_data_to_text(tracks), "description": description})

        content = response.content
        content = content.replace('```json', '').replace('```', '')

        return json.loads(content)

    def convert_tracks_data_to_text(self, tracks):
        track_texts = []

        for track in tracks:
            track_text = f'Title: {track["title"]}, Artist: {track["artist"]}, Album: {track["album_name"]}, Tags: {";".join(track["tags"])}, URL: {track["url"]}'
            track_texts.append(track_text)

        return '\n'.join(track_texts)
