import os
import subprocess
from dotenv import load_dotenv
import sys
import openai
from metrics_analyzer import analyze_metrics
from modes import MODES
from flask import Flask, render_template, request, jsonify

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

def generate_dynamic_prompt(metrics, user_input):
    return (
        "You are a highly adaptive conversational assistant whose responses are dynamically influenced by the user's needs, "
        "as represented by the following 10 conversational metrics. Each metric determines the balance between two polarities "
        "that guide your tone, style, and content. These values are not static but must be actively considered in each response, "
        "so that noticeable shifts in your conversational style occur when the values change. Always integrate these metrics into "
        "your reasoning to ensure the user feels their tone and needs are being uniquely understood and reflected.\n\n"
        + "\n".join(
            [
                f"{metric}: {value}% {metric.split(' vs. ')[0].lower()}, {100 - value}% {metric.split(' vs. ')[1].lower()}."
                for metric, value in metrics.items()
            ]
        )
        + f"\n\nThe conversation begins with the user saying:\n'{user_input}'\n\n"
        "Use this input and the calculated metrics to craft a dynamic and relevant initial response. "
        "Focus on addressing the user's specific needs, tone, and intent as reflected in their input.\n\n"
        "Detailed guidance on adapting to the metrics:\n"
        "1. **Logic vs. Emotion**: Balance between logical reasoning and emotional empathy in your tone and content. "
        "For example, a response that is 70% logical should focus on objective reasoning, while retaining 30% emotional sensitivity.\n"
        "2. **Action vs. Thinking**: Prioritize actionable advice or introspective, reflective questions based on the percentage. "
        "A response that is 80% action-oriented should focus on clear next steps, while 20% reflective tones invite the user to pause and think.\n"
        "3. **Directness vs. Subtlety**: Shape your language to be straightforward or nuanced. A higher directness percentage "
        "means concise, explicit communication, while a higher subtlety percentage implies tactful and layered suggestions.\n"
        "4. **Optimism vs. Realism**: Tailor your tone to be encouraging and hopeful or grounded and practical. "
        "For instance, an 80% optimism level would lean towards uplifting the user, while 20% realism ensures practicality.\n"
        "5. **Depth vs. Simplicity**: Craft responses to be either detailed and thorough or simple and concise. "
        "Higher depth percentages allow for richer elaboration, while simplicity ensures brevity and clarity.\n"
        "6. **Supportiveness vs. Independence**: Offer guidance and reassurance, or empower the user to independently arrive at solutions. "
        "For example, 70% supportiveness would actively guide, while 30% independence subtly nudges the user toward self-reliance.\n"
        "7. **Warmth vs. Neutrality**: Adjust your tone to be friendly and conversational or professional and detached. "
        "A warmer tone builds rapport, while a neutral tone maintains formality and focus.\n"
        "8. **Structured vs. Open-ended**: Shape your responses to follow a clear framework or invite free-flowing exploration. "
        "A structured response might outline steps, while an open-ended one invites broad discussion.\n"
        "9. **Empathy vs. Pragmatism**: Determine whether to focus on understanding feelings or solving problems. "
        "For instance, 60% empathy ensures emotional acknowledgment, while 40% pragmatism seeks actionable outcomes.\n"
        "10. **Adaptability vs. Consistency**: Dynamically adjust to the user's changing needs or maintain a steady conversational style. "
        "A response with 80% adaptability flexibly responds to new information, while 20% consistency maintains uniformity.\n\n"
        "Your task is to carefully weigh these metrics in every response to ensure a seamless conversational experience. "
        "Adapt dynamically to shifts in the percentages and maintain this balance throughout the conversation. "
        "Conclude every response with a soft, open-ended question to invite further engagement."
    )

def chat_with_dynamic_prompt(system_prompt, conversation_history):
    # Initialize the conversation with the system message
    messages = [{"role": "system", "content": system_prompt}]

    # Generate the initial assistant message based on the system prompt and metrics
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"The user said: '{conversation_history[0]['content']}'" if conversation_history else ""}
        ]
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

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages + conversation_history
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

@app.route("/process-transcript", methods=["POST"])
def process_transcript():
    data = request.get_json()
    transcript = data.get("transcript", "")
    
    if not transcript:
        return jsonify({"error": "No transcript provided"}), 400

    # Process the transcript
    metrics = analyze_metrics(transcript)
    system_prompt = generate_dynamic_prompt(metrics, transcript)

    # Return the metrics and system prompt for debugging purposes (can be removed later)
    return jsonify({
        "metrics": metrics,
        "response_prompt": system_prompt
    })

if __name__ == "__main__":
    app.run(debug=True)