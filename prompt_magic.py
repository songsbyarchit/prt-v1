import json
import openai
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env variables

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define categories and subcategories (only 3 to 20)
categories = {
    "decision_making": ["clarifying_options", "weighing_pros_and_cons", "fear_of_wrong_choice", "long_term_vs_short_term", "alignment_with_goals"],
    "relationships": ["conflict_resolution", "navigating_relationships", "family_dynamics", "social_anxiety", "setting_boundaries"],
    "career_work": ["work_stress", "career_transitions", "workplace_conflicts", "career_goals", "aligning_work_with_values"],
    "mental_health": ["coping_with_anxiety", "managing_intrusive_thoughts", "building_resilience", "reflecting_on_therapy", "self_esteem_issues"],
    "physical_wellbeing": ["managing_health", "healthy_habits", "body_image", "coping_with_illness", "fitness_goals"],
    "creativity_productivity": ["overcoming_blocks", "enhancing_focus", "unfinished_projects", "time_management", "balance_with_rest"],
    "gratitude_positivity": ["practicing_gratitude", "small_wins", "joy_in_life", "overcoming_negativity", "celebrating_achievements"],
    "coping_with_change": ["life_transitions", "adapting_to_uncertainty", "accepting_change", "letting_go", "embracing_opportunities"],
    "spirituality_reflection": ["exploring_spirituality", "finding_meaning", "mindfulness_reflection", "life_questions", "connecting_with_nature"],
    "financial_practical_challenges": ["budgeting_saving", "financial_stress", "spending_habits", "future_planning", "emotional_balance"],
    "goal_setting_ambitions": ["long_term_planning", "overcoming_procrastination", "visualizing_success", "setting_expectations", "progress_reflection"],
    "past_events": ["childhood_reflection", "processing_trauma", "positive_memories", "impact_of_past", "letting_go_of_mistakes"],
    "problem_solving": ["breaking_down_problems", "creative_solutions", "seeking_clarity", "reflecting_on_failures", "brainstorming_approaches"],
    "future_planning": ["envisioning_possibilities", "actionable_steps", "managing_fears", "major_event_preparation", "defining_success"],
    "interpersonal_growth": ["communication", "developing_empathy", "reflecting_on_mistakes", "building_trust", "understanding_perspectives"],
    "conflict_resolution": ["personal_conflicts", "workplace_disputes", "reflecting_on_arguments", "mutual_solutions", "unresolved_tension"],
    "celebrations_joy": ["milestones", "gratitude_for_achievements", "positive_relationships", "small_joys", "moments_of_pride"],
    "habits_behavior": ["breaking_bad_habits", "positive_routines", "daily_choices", "understanding_triggers", "accountability"]
}

# Path to the updated prompts file
output_file = "updated_prompts.json"

# Function to call the OpenAI API and generate prompts
def generate_prompts(category, subcategory):
    try:
        prompt = (
            f"Generate exactly 20 detailed examples of what a user might initially say when asked, "
            f"'What brings you here?' for the journaling category '{category}' and subcategory '{subcategory}'. "
            f"The examples should be conversational, specific, and reflect realistic concerns, feelings, or goals. "
            f"The output **must** be in strict JSON format as an array of dictionaries. "
            f"Each dictionary **must** contain three keys: 'prompt', 'category', and 'subcategory'. "
            f"'prompt' should contain a string of 1-2 sentences representing what a user might say. "
            f"The 'category' key **must** be '{category}', and the 'subcategory' key **must** be '{subcategory}'. "
            f"Ensure there is no extra text, only the valid JSON output in this format: "
            f'[{{"prompt": "Example of user statement", "category": "{category}", "subcategory": "{subcategory}"}}].'
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000  # Adjust as needed
        )
        return json.loads(response.choices[0].message['content'].strip())
    except Exception as e:
        print(f"Error generating prompts for {category}/{subcategory}: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response}")
        return []

# Load existing prompts
try:
    with open(output_file, "r") as file:
        all_prompts = json.load(file)
except FileNotFoundError:
    all_prompts = []

# Generate and append prompts for categories 3 to 20
for category, subcategories in categories.items():
    for subcategory in subcategories:
        print(f"Generating prompts for {category} -> {subcategory}...")
        prompts = generate_prompts(category, subcategory)
        # Add category and subcategory fields to each prompt
        for prompt in prompts:
            prompt["category"] = category
            prompt["subcategory"] = subcategory
        all_prompts.extend(prompts)
        # Save after each subcategory to avoid data loss
        with open(output_file, "w") as file:
            json.dump(all_prompts, file, indent=4)
        sleep(1)  # To avoid hitting rate limits
        print(f"Completed: {category}/{subcategory}")

print("Prompts generation completed!")