from smolagents import CodeAgent, HfApiModel
from dotenv import load_dotenv
import pyttsx3  # Install using: pip install pyttsx3

load_dotenv()

agent = CodeAgent(tools=[], model=HfApiModel(), add_base_tools=True)

# Run the agent
response = agent.run("list all stats of KL Rahul?")

# Convert text response to speech
engine = pyttsx3.init()
engine.save_to_file(response, "transformers_recording.mp3")
engine.runAndWait()

print("MP3 file saved successfully!")
