import openai

def analyze_metrics(user_input):
    analysis_prompt = (
        "Analyze the following user input and assign values from 1 to 10 for 10 conversational metrics. "
        "The purpose of this analysis is to determine the user's conversational tone and intent, "
        "which will dynamically influence the voice of the AI for the rest of the conversation. "
        "Each metric represents a conversational polarity, and the values should be weighted based on the tone, intent, and context "
        "of the user's input. Assign values thoughtfully based on the input, using the scales provided below:\n\n"
        
        "1. Logic vs. Emotion: 1 means purely emotional, 10 means purely logical.\n"
        "2. Action vs. Thinking: 1 means action-oriented, 10 means reflective/thoughtful.\n"
        "3. Directness vs. Subtlety: 1 means very direct, 10 means very subtle.\n"
        "4. Optimism vs. Realism: 1 means highly optimistic, 10 means grounded realism.\n"
        "5. Depth vs. Simplicity: 1 means simple/surface-level, 10 means deep/detailed.\n"
        "6. Supportiveness vs. Independence: 1 means highly supportive/guiding, 10 means empowering independence.\n"
        "7. Warmth vs. Neutrality: 1 means very warm/friendly, 10 means neutral/professional.\n"
        "8. Structured vs. Open-ended: 1 means highly structured guidance, 10 means open-ended/free-flowing.\n"
        "9. Empathy vs. Pragmatism: 1 means empathetic/understanding, 10 means pragmatic/problem-solving.\n"
        "10. Adaptability vs. Consistency: 1 means very adaptable/dynamic, 10 means consistent/predictable.\n\n"

        "For example, if the user input suggests they are feeling emotional and overwhelmed, the response may "
        "be weighted towards Emotion (e.g., Logic vs. Emotion = 2), with other metrics adjusted accordingly.\n\n"

        "Return the result in the following JSON format:\n"
        "{\n"
        '  "Logic vs. Emotion": 2,\n'
        '  "Action vs. Thinking": 7,\n'
        '  "Directness vs. Subtlety": 5,\n'
        '  "Optimism vs. Realism": 6,\n'
        '  "Depth vs. Simplicity": 8,\n'
        '  "Supportiveness vs. Independence": 3,\n'
        '  "Warmth vs. Neutrality": 4,\n'
        '  "Structured vs. Open-ended": 6,\n'
        '  "Empathy vs. Pragmatism": 2,\n'
        '  "Adaptability vs. Consistency": 5\n'
        "}\n\n"

        "User Input: {user_input}\n\n"
        "Respond ONLY with the JSON result. Do not provide explanations or additional text."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": analysis_prompt}]
    )
    
    return eval(response["choices"][0]["message"]["content"])