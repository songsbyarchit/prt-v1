import json

# Define the category and subcategories for the new prompts
CATEGORY = "self_discovery"
SUBCATEGORIES = [
    "understanding_values_or_priorities",
    "exploring_identity",
    "life_purpose",
    "reflection_on_personal_growth",
    "addressing_limiting_beliefs"
]

# Define the number of prompts per subcategory
PROMPTS_PER_SUBCATEGORY = 20

# Load existing updated prompts
with open("updated_prompts.json", "r", encoding="utf-8") as file:
    updated_prompts = json.load(file)

# Load the new prompts
with open("prompts.json", "r", encoding="utf-8") as file:
    new_prompts = json.load(file)

# Add category and subcategory to the new prompts
for index, prompt in enumerate(new_prompts):
    subcategory_index = index // PROMPTS_PER_SUBCATEGORY  # Determine subcategory based on index
    prompt["category"] = CATEGORY
    prompt["subcategory"] = SUBCATEGORIES[subcategory_index]

# Append the new prompts to the updated prompts
updated_prompts.extend(new_prompts)

# Save the combined dataset back to updated_prompts.json
with open("updated_prompts.json", "w", encoding="utf-8") as file:
    json.dump(updated_prompts, file, indent=4, ensure_ascii=False)

print("New prompts appended successfully.")