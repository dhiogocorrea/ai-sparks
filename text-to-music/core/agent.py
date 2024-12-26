import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class MusicalAgent:
    def __init__(self):
        load_dotenv()
        
        # Base MusicXML structure with placeholders
        self.base_musicxml = """
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
        <score-partwise version="3.1">
          <part-list>
            <score-part id="P1">
              <part-name>Electric Guitar (Rhythm)</part-name>
            </score-part>
            <score-part id="P2">
              <part-name>Electric Guitar (Lead)</part-name>
            </score-part>
            <score-part id="P3">
              <part-name>Bass Guitar</part-name>
            </score-part>
            <score-part id="P4">
              <part-name>Drum Set</part-name>
            </score-part>
            <score-part id="P5">
              <part-name>Keyboards</part-name>
            </score-part>
            <score-part id="P6">
              <part-name>Vocals</part-name>
            </score-part>
          </part-list>
          
          <!-- Insert generated parts here -->
          {parts}
          
        </score-partwise>
        """
        
        # Template for generating each section
        self.section_prompt_template = """
        You are a music composition assistant specializing in generating structured MusicXML files for musical pieces.
        Your task is to create a MusicXML snippet for the {section_name} section of a musical composition based on the following description.

        IMPORTANT REQUIREMENTS:
        1) The XML (MusicXML) **must** follow the specified structure exactly—no additional keys or extraneous text.
        2) Ensure that the {section_name} section is complete with all necessary opening and closing tags.
        3) Incorporate the required instrumentation, dynamics, articulations, and variations as per the overall composition guidelines.

        ### Context about the song or mood:
        {description}
        """

        self.corrector_tempplate = """
        You will receive a MusicXML string with potential formatting errors. Your job is to correct it and return it.

        **IMPORTANT**: Return ONLY the XML, without code tags or texts.

        ### XML:
        {xml}
        """
        
        prompt = ChatPromptTemplate.from_template(self.section_prompt_template)
        prompt_xml = ChatPromptTemplate.from_template(self.corrector_tempplate)

        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            temperature=0.2
        )

        self.chain = prompt | llm
        self.chain_corrector = prompt_xml | llm
    
    def generate_section(self, section_name: str, description: str) -> str:
        """
        Generates MusicXML for a specific section.
        """        
        response = self.chain.invoke({'section_name': section_name, 'description': description})        
        return response.content
    
    def invoke(self, music_description: str) -> str:
        """
        Generates the complete MusicXML by assembling all sections.
        """
        sections = ["Intro", "Verse", "Chorus", "Bridge", "Solo", "Outro"]
        generated_parts = []
        
        for section in sections:
            print(f"Generating section: {section}")
            section_xml = self.generate_section(section, music_description)
            generated_parts.append(section_xml)
        
        # Assemble all parts into the base MusicXML
        all_parts_xml = "\n".join(generated_parts)
        complete_musicxml = self.base_musicxml.format(parts=all_parts_xml)
        
        response = self.chain_corrector.invoke({ 'xml': complete_musicxml })
        content = response.content.replace('```xml', '').replace('```', '')

        return content
