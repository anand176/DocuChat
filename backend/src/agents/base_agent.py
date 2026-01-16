import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, role_name, system_instruction):
        self.role_name = role_name
        self.system_instruction = system_instruction
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )
        self.chat = self.model.start_chat(history=[])

    def ask(self, prompt, stream=False):
        """Send a message to the agent and get a response."""
        if stream:
            return self.chat.send_message(prompt, stream=True)
        else:
            response = self.chat.send_message(prompt)
            return response.text
