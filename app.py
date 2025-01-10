import os
import subprocess
from dotenv import load_dotenv
import sys
import openai
from modes import MODES

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


def chat_with_mode(mode, sub_mode, conversation_history):
    # Define the system prompt with instructions to keep responses concise
    system_prompt = (
        f"You are a tool for {MODES[mode]['name']}. "
        f"Always maintain this voice: {MODES[mode]['style']} "
        f"Do not provide actions, solutions, or advice. "
        f"Respond empathetically and always end with a soft, open-ended question."
    )
    
    # Initialize the conversation with the system message
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add an initial assistant message based on the mode and sub-mode
    initial_messages = {
        1: {
            1: "I'm here to understand you better. What's on your mind?",
            2: "I'm here to provide comfort. How are you feeling right now?",
            3: "Let's find some positivity together. What's something you're proud of today?",
        },
        2: {
            1: "What emotions stood out to you today? Let's reflect together.",
            2: "Tell me about the events that made your day unique.",
            3: "What’s one thing you feel grateful for today?",
        },
        3: {
            1: "What personal goal is on your mind right now?",
            2: "What’s something you want to plan for work or studies?",
            3: "What’s a dream or aspiration you want to work toward?",
        },
    }
    assistant_initial_reply = initial_messages[mode][sub_mode]
    print(f"{MODES[mode]['name']} ({MODES[mode]['name']}): {assistant_initial_reply}")
    
    # Append the assistant's initial reply to the conversation history
    conversation_history.append({"role": "assistant", "content": assistant_initial_reply})

    while True:
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
            messages=[{"role": "system", "content": system_prompt}] + conversation_history
        )

        # Extract and display the assistant's reply
        assistant_reply = response["choices"][0]["message"]["content"]
        print(f"{MODES[mode]['name']} ({MODES[mode]['name']}): {assistant_reply}")

        # Append the assistant's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": assistant_reply})

def main():
    mode = int(input("What would you like to do?\n1: Emotional Support\n2: Journaling\n3: Planning\nSelect a mode (1, 2, or 3): "))
    if mode not in MODES:
        print("Invalid mode selected. Exiting.")
        return

    print(f"\nYou selected: {MODES[mode]['name']}")
    sub_modes = MODES[mode]['style']
    for sub_mode_key, sub_mode_description in sub_modes.items():
        print(f"{sub_mode_key}: {sub_mode_description.split(':')[0]}")

    sub_mode = int(input("Select a sub-mode (1, 2, or 3): "))
    if sub_mode not in sub_modes:
        print("Invalid sub-mode selected. Exiting.")
        return
    
    try:
        print(f"You've selected: {MODES[mode]['name']} - {sub_modes[sub_mode].split(':')[0]}")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        conversation_history = []  # Initialize conversation history as an empty list
        conversation_history = chat_with_mode(mode, sub_mode, conversation_history)
        while True:
            if conversation_history is None:
                break
    except ValueError:
        print("Please enter a valid mode and sub-mode number.")

if __name__ == "__main__":
    main()