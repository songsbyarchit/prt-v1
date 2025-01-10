import os
import subprocess
import sys
from dotenv import load_dotenv
import openai

# Automatically install missing dependencies
def install_dependencies():
    try:
        import openai  # Check if the openai library is installed
        import dotenv  # Check if dotenv is installed
    except ImportError:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Ensure dependencies are installed
install_dependencies()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define modes and corresponding voice styles
MODES = {
    1: {
        "name": "Emotional Support",
        "style": "Respond with empathy, compassion, and supportive language. Use a calm and soothing tone.",
    },
    2: {
        "name": "Journaling",
        "style": "Respond as a reflective listener, prompting with open-ended questions and encouragement for elaboration.",
    },
    3: {
        "name": "Planning",
        "style": "Respond with structured, goal-oriented language. Be methodical and proactive in offering solutions."
    }
}

def chat_with_mode(mode, conversation_history):
    system_prompt = f"You are a tool for {MODES[mode]['name']}. Always maintain this voice: {MODES[mode]['style']}"
    messages = [{"role": "system", "content": system_prompt}] + conversation_history
    
    # Collect user input
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the conversation.")
        return None  # Exit the conversation

    # Append user input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Call the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5-turbo
        messages=messages
    )

    # Extract and display the assistant's reply
    assistant_reply = response["choices"][0]["message"]["content"]
    print(f"{MODES[mode]['name']} ({MODES[mode]['name']}): {assistant_reply}")
    
    # Append assistant reply to the conversation history
    conversation_history.append({"role": "assistant", "content": assistant_reply})

    return conversation_history

def main():
    print("Welcome to the Personalized Reflection Tool!")
    print("Choose a mode:")
    print("1: Dealing with Negative or Overwhelming Emotions")
    print("2: Journaling and Documenting Your Day")
    print("3: Planning for the Future")
    
    try:
        mode = int(input("Select a mode (1, 2, or 3): "))
        if mode not in MODES:
            print("Invalid mode selected. Exiting.")
            return
        
        print(f"You've selected: {MODES[mode]['name']}")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        conversation_history = []
        while True:
            conversation_history = chat_with_mode(mode, conversation_history)
            if conversation_history is None:
                break
    except ValueError:
        print("Please enter a valid mode number.")

if __name__ == "__main__":
    main()