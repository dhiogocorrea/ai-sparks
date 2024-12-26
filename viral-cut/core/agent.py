import os
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class ViralCutAgent:
    def __init__(self):
        load_dotenv()

        self.CHUNK_SIZE = 1500

        prompt_template_str = """
        You are a digital marketing and viral content expert.
        You received the following excerpt from a podcast.
        Identify moments that can be turned into viral social media clips.

        Output should be in {language}

        Criteria:
        - Funny, controversial, emotional, or inspiring segments
        - Catchy phrases, intriguing questions, revelations
        - Clips duration is at greater than 60 seconds and lower than 300 seconds
        - Do not create overlayed clips
        - Create AT LEAST (<DURATION OF VIDEO> / 300 seconds) clips. For example: for a 3600 seconds video, AT LEAST 12 clips.

        Your output must be a JSON-structured list, where each item contains:
        - explanation [str]: Why this segment is potentially viral
        - title [str]: An attention-grabbing title for the clip (good for posting on YouTube, for example).
            Try some click baits.
            Add UPPERCASE words to emphatize the important ones.
        - start_time [float]: Start time of the segment (in seconds)
        - end_time [float]: End time of the segment (in seconds)

        Podcast audio transcription:
        {transcription}

        Return ONLY the JSON list of identified segments, with no additional explanations or text.
        """
        prompt = ChatPromptTemplate.from_template(prompt_template_str)

        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o",
            temperature=0.9
        )

        self.chain = prompt | llm


    def invoke(self, transcription: str, language: str = 'portuguese'):
        response = self.chain.invoke({"language": language, "transcription": transcription})

        content = response.content
        content = content.replace('```json', '').replace('```', '')

        return json.loads(content)
