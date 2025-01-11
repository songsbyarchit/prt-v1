import os
import subprocess
from dotenv import load_dotenv
import sys
import openai
from metrics_analyzer import analyze_metrics
from modes import MODES
from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import time

app = Flask(__name__, template_folder="static/templates")

# Automatically install missing dependencies
def install_dependencies():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All dependencies from requirements.txt are installed.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while installing dependencies:", e)

# Ensure dependencies are installed
install_dependencies()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("VOICE_ID")

conversation_history = []

def generate_dynamic_prompt(metrics, user_input):
    return (
        "You are a **reflection assistant**. Your only role is to **ask guiding questions** that help the user reflect on their thoughts, "
        "feelings, and situation. **You are NOT allowed to give advice, solutions, or guidance of any kind.**\n\n"
        "Your first sentence MUST always be a **reflective question** that directly relates to the user's situation, encouraging them to dig deeper into their feelings or thoughts. "
        "Do not start with any advice or solutions — only ask open-ended questions to help the user explore their emotions and thoughts. "
        "You are NOT a general advisor or problem solver, just a guide for reflection.\n\n"
        "Your second sentence, if necessary, should be a **follow-up question** to dig deeper or guide them further, but still NO solutions or advice.\n\n"
        "Your responses MUST be **brief** and **contain no more than 30 words**. If your response exceeds 30 words, it will be cut off. "
        "Your responses MUST remain purely **questions**, and should avoid anything that resembles advice or instructions.\n\n"
        "The conversation begins with the user saying:\n'{user_input}'\n\n"
        "Here are some metrics for your response:\n" +
        "\n".join(
            [
                f"{metric}: {value}% {metric.split(' vs. ')[0].lower()}, {100 - value}% {metric.split(' vs. ')[1].lower()}."
                for metric, value in metrics.items()
            ]
        ) +
        "\n\n**Guidance on how to reflect based on the metrics** (but still ONLY ask questions, no advice):\n"
        "1. **Logic vs. Emotion**: If the metric is high in **logic**, your question can focus on logical exploration. "
        "If it is high in **emotion**, ask how the user is feeling.\n"
        "2. **Action vs. Thinking**: If the metric is high in **action**, your question might help the user think about steps but **no solutions**. "
        "If it is high in **thinking**, ask the user to reflect more deeply.\n"
        "3. **Directness vs. Subtlety**: If the metric is high in **directness**, ask clear, concise questions. "
        "If it is high in **subtlety**, use softer and more nuanced questions.\n"
        "4. **Optimism vs. Realism**: If the metric is high in **optimism**, encourage the user to think about possibilities. "
        "If it is high in **realism**, keep the questions grounded.\n"
        "5. **Depth vs. Simplicity**: If the metric is high in **depth**, ask deep, probing questions. "
        "If it is high in **simplicity**, ask straightforward, simpler questions.\n"
        "6. **Supportiveness vs. Independence**: If the metric is high in **supportiveness**, ask questions that help the user feel heard. "
        "If it is high in **independence**, ask questions that empower the user to come up with their own answers.\n"
        "7. **Warmth vs. Neutrality**: If the metric is high in **warmth**, your questions should be friendly and compassionate. "
        "If it is high in **neutrality**, your questions should be more detached and professional.\n"
        "8. **Structured vs. Open-ended**: If the metric is high in **structure**, ask focused questions that guide the user to think within a framework. "
        "If it is high in **open-endedness**, let the user explore their thoughts freely.\n"
        "9. **Empathy vs. Pragmatism**: If the metric is high in **empathy**, your questions should center on understanding feelings. "
        "If it is high in **pragmatism**, ask reflective questions without offering solutions.\n"
        "10. **Adaptability vs. Consistency**: If the metric is high in **adaptability**, adjust your questions to follow the user's flow. "
        "If it is high in **consistency**, keep your questions steady and focused.\n\n"
        "The goal is to help the user **reflect** and **explore** their thoughts and feelings, NOT to advise them. "
        "Your role is to only ask questions — **never** offer any advice, solutions, or guidance of any kind. "
        "Ensure every response is a **question** that prompts reflection without offering any form of solution."
    )

def calculate_input_tokens(messages):
    # Calculate the number of tokens used by the input
    return sum(len(message['content'].split()) for message in messages)

@app.route("/process-transcript", methods=["POST"])
def process_transcript():
    try:
        data = request.get_json()
        transcript = data.get("transcript", "")
        
        if not transcript:
            return jsonify({"error": "No transcript provided"}), 400

        metrics = analyze_metrics(transcript)
        system_prompt = generate_dynamic_prompt(metrics, transcript)

        # Map metrics to voice parameters
        stability, clarity, pitch, speed, depth = map_metrics_to_voice_params(metrics)

        # Append user input to conversation history
        # Maintain global conversation history to keep track of the entire conversation
        conversation_history.append({"role": "user", "content": transcript})

        # Log conversation history to check what's being sent to OpenAI
        print(f"Sending request to OpenAI with the following conversation history:\n{conversation_history}")

        # Calculate input tokens
        input_tokens = calculate_input_tokens(conversation_history)

        # Define max total tokens to limit the total number of tokens (4096 for GPT-3.5)
        max_total_tokens = 4096  # GPT-3.5 token limit

        # Calculate input tokens
        input_tokens = calculate_input_tokens(conversation_history)

        # Calculate remaining tokens for output
        remaining_tokens_for_output = max_total_tokens - input_tokens

        # Set max tokens for output (you can adjust this as per your needs)
        max_output_tokens = min(remaining_tokens_for_output, 100)  # For example, 100 tokens output

        # Make API call with the calculated max tokens for output
        response_openai = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,  # Send the conversation history to maintain context
            max_tokens=max_output_tokens
        )

        print(f"Received response from OpenAI: {response_openai['choices'][0]['message']['content']}")

        assistant_reply = response_openai["choices"][0]["message"]["content"]  # Get the assistant's reply

        # Log the assistant's reply being sent to ElevenLabs for voice generation
        print(f"Sending request to ElevenLabs with the following assistant reply:\n{assistant_reply}")

        # Call ElevenLabs API to generate the audio
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": elevenlabs_api_key, "Content-Type": "application/json"},
            json={
                "text": assistant_reply,  # Send the assistant's response
                "model_id": "eleven_monolingual_v1"
            }
        )

        # Log the response from ElevenLabs to check for issues
        if response.status_code == 200:
            print(f"ElevenLabs response received successfully, content length: {len(response.content)}")
            voice_response = response.content
        else:
            print(f"Failed to generate audio with ElevenLabs. Status code: {response.status_code}, Error: {response.text}")
            return jsonify({"error": "Failed to generate audio"}), 500

        if response.status_code == 200:
            voice_response = response.content
        else:
            print("Failed to generate audio. Error:", response.text)
            return jsonify({"error": "Failed to generate audio"}), 500

        # Save the audio response with a unique filename (including a timestamp)
        timestamp = int(time.time())
        audio_filename = f"response_{timestamp}.mp3"
        print(f"Returning audio file: {audio_filename}")

        with open(audio_filename, "wb") as audio_file:
            audio_file.write(voice_response)

        # Return the path of the new audio file in the response
        return jsonify({
            "metrics": metrics,
            "response_prompt": system_prompt,
            "audio_generated": True,
            "audio_file": audio_filename  # This will just return the audio filename (e.g., response_1736608762.mp3)
        })
            
    except Exception as e:
        # Print the error to the console for debugging
        print("Error in process_transcript:", str(e))
        # Return the error message to the client
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def chat_with_dynamic_prompt(system_prompt, conversation_history):
    max_total_tokens = 4096  # GPT-3.5 token limit
    # Initialize the conversation with the system message
    messages = [{"role": "system", "content": system_prompt}]

    # Generate the initial assistant message based on the system prompt and metrics
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages + conversation_history
    )

    assistant_initial_reply = response["choices"][0]["message"]["content"]
    print(f"\nAssistant: {assistant_initial_reply}\n")
    conversation_history.append({"role": "assistant", "content": assistant_initial_reply})

    while True:
        # Collect user input
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the conversation.")
            return

        # Append user input to the conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Calculate input tokens
        input_tokens = calculate_input_tokens(conversation_history)

        # Calculate remaining tokens for output
        remaining_tokens_for_output = max_total_tokens - input_tokens
        max_output_tokens = min(remaining_tokens_for_output, 100)  # Adjust as per your needs

        # Make API call with max tokens for output
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages + conversation_history,
            max_tokens=max_output_tokens,
            stop=["."]
        )

        # Make API call with max tokens for output
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            max_tokens=max_output_tokens,
            stop=["."]
        )

        # Extract and display the assistant's reply
        assistant_reply = response["choices"][0]["message"]["content"]
        
        print(f"\nAssistant: {assistant_reply}\n")

        # Append the assistant's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": assistant_reply})

def main():
    # Ask the user for their input
    user_input = input("Hey, what brings you here?\nYou: ")

    # Analyze the user's response using the analyze_metrics function
    metrics = analyze_metrics(user_input)

    print(f"Metrics generated from your response: {metrics}\n")

    # Generate a dynamic system prompt based on the analyzed metrics
    system_prompt = generate_dynamic_prompt(metrics, user_input)

    print("Type 'exit' or 'quit' to end the conversation.")

    # Initialize the conversation history with the first user input
    conversation_history = [{"role": "user", "content": user_input}]

    # Start the conversation using the chat_with_dynamic_prompt function
    chat_with_dynamic_prompt(system_prompt, conversation_history)

@app.route("/")
def index():
    return render_template("index.html")

conversation_history = []  # Ensure this is defined globally

@app.route('/<filename>')
def serve_audio(filename):
    return send_from_directory('.', filename)  # Serve from current directory

def map_metrics_to_voice_params(metrics):
    stability = metrics.get("Adaptability vs. Consistency", 5) / 10
    clarity = metrics.get("Warmth vs. Neutrality", 5) / 10
    pitch = (metrics.get("Optimism vs. Realism", 5) - 5) * 0.1 + 1  # Adjust pitch around 1.0
    speed = (metrics.get("Action vs. Thinking", 5) - 5) * 0.05 + 1  # Adjust speed around 1.0
    depth = metrics.get("Depth vs. Simplicity", 5) / 10  # A placeholder for potential future voice API parameters
    return stability, clarity, pitch, speed, depth

if __name__ == "__main__":
    app.run(debug=True)