import os
import subprocess
from dotenv import load_dotenv
import sys
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
    # Define the system prompt with instructions to keep responses concise
    system_prompt = (
        f"You are a tool for {MODES[mode]['name']}. "
        f"Always maintain this voice: {MODES[mode]['style']} "
        f"Do not provide actions, solutions, or advice. "
        f"Respond empathetically and always end with a soft, open-ended question."
    )
    
    # Initialize the conversation with the system message
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add an initial assistant message based on the mode
    initial_message = {
        1: "Hello, I'm here to provide emotional support. What's on your mind?",
        2: "Hi! Let's document your day. What's something memorable today?",
        3: "Hey! Let's plan for your future. What's your main goal?",
    }
    assistant_initial_reply = initial_message[mode]
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