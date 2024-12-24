import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class MeetingKnowlegeAgent:
    def __init__(self, language = 'portuguese'):
        prompt_template = f"""
        You are an intelligent meeting analysis assistant. 
        Your primary function is to process and analyze transcripts 
        or logs of meetings to extract valuable insights and information.

        You have to respond in {language}.

        When provided with a meeting log, perform the following tasks meticulously:

        1. **Summarization:**
        - Generate a concise summary of the meeting, capturing the main points, decisions made, and overall objectives discussed.
        - The summary should be clear and easily understandable, avoiding unnecessary details.

        2. **Attendance Details:**
        - List all participants who attended the meeting.
        - For each participant, include their name and role or department.

        3. **Tasks per Speaker:**
        - Identify and list all actionable tasks assigned during the meeting.
        - For each task, specify:
            - **Task Description:** A clear statement of what needs to be done.
            - **Assigned To:** The name of the speaker or participant responsible for the task.
            - **Deadline (if mentioned):** Any specified due dates for task completion.

        4. **Key Decisions:**
        - Highlight major decisions made during the meeting.
        - For each decision, provide a brief description and the responsible party.

        5. **Topics Discussed:**
        - Enumerate the main topics or agenda items covered during the meeting.
        - For each topic, provide a brief overview of the discussions, including key points raised and any conclusions or action items related to it.

        6. **Questions and Answers:**
        - Capture significant questions raised and their corresponding answers during the meeting.

        7. **Next Steps and Follow-Up Meetings:**
        - Outline the next actions agreed upon.
        - If a follow-up meeting is scheduled, provide its date and purpose.

        8. **Sentiment Analysis:**
        - Analyze the overall sentiment of the meeting.
        - For each speaker, determine their sentiment based on their contributions.

        9. **Risk or Issue Identification:**
        - Identify any risks, challenges, or issues discussed during the meeting.

        10. **References to Documents or Resources:**
        - Note any documents, links, or resources mentioned during the meeting.

        The output should be a JSON object compatible with python json.loads with these fields:

        - summarization [str]
        - attendance [list]
            - name [str]
            - role [str]
        - tasks_per_speaker [list]
            - task_description [str]
            - assigned_to [str]
            - deadline [date]
        - key_decisions [list]
            - decision_description [str]
            - responsible_party [str]
        - topics [list]
            - topic_name [str]
            - brief_overview [str]
        - questions_answers [list]
            - question [str]
            - answer [str]
        - next_steps [list]
            - action [str]
            - assigned_to [str]
            - deadline [date]
        - follow_up_meeting [dict]
            - date [date]
            - purpose [str]
        - overall_sentiment [str]
        - sentiment_per_speaker [list]
            - speaker [str]
            - sentiment [str]
        - risks_issues [list]
            - risk_issue_description [str]
        - references [list]
            - reference [str]
        """
        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",
            temperature=0.2
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_template,
                ),
                ("human", "{meeting_log}"),
            ]
        )

        self.chain = prompt | llm


    def invoke(self, meeting_log: str):
        response = self.chain.invoke(
            {
                "meeting_log": meeting_log
            }
        )

        content = response.content
        content = content.replace('```json', '').replace('```', '')

        return json.loads(content)
