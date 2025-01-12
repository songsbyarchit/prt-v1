import json
import openai
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to calculate cosine similarity
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Function to get the embedding of a text
def get_embedding(text):
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def add_user_prompt(user_prompt):
    # Check if the user_prompt already exists in the dataset to prevent duplicates
    if any(entry["prompt"] == user_prompt for entry in prompts_data):
        print(f"The prompt '{user_prompt}' already exists in the dataset. It will not be added again.")
        return

    user_embedding = get_embedding(user_prompt)
    if not user_embedding:
        print("Failed to compute embedding for user input.")
        return

    # Calculate similarity
    best_match = None
    highest_similarity = 0
    for entry in prompts_data:
        similarity = cosine_similarity(user_embedding, entry["embedding"])
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = entry

    # Check threshold and add if valid
    if highest_similarity >= 0.9:
        new_entry = {
            "prompt": user_prompt,
            "category": best_match["category"],
            "subcategory": best_match["subcategory"],
            "embedding": user_embedding
        }
        prompts_data.append(new_entry)
        with open("updated_prompts_with_embeddings.json", "w") as file:
            json.dump(prompts_data, file, indent=4)
        print(f"Added new prompt to {best_match['category']} -> {best_match['subcategory']}.")
    else:
        print("No similar match found above the 0.9 threshold. Prompt not added.")

# Load precomputed embeddings from file
with open("updated_prompts_with_embeddings.json", "r") as file:
    prompts_data = json.load(file)

def semantic_search(user_input, top_n=5):
    user_embedding = get_embedding(user_input)
    if not user_embedding:
        print("Failed to compute embedding for user input.")
        return []  # Ensure an empty list is returned when embedding fails

    # Calculate similarity scores
    results = []
    for entry in prompts_data:
        similarity = cosine_similarity(user_embedding, entry["embedding"])
        results.append((entry["prompt"], similarity, entry["category"], entry["subcategory"]))

    # Sort results by similarity in descending order
    results = sorted(results, key=lambda x: x[1], reverse=True)

    # Display results
    for i, (prompt, score, category, subcategory) in enumerate(results[:top_n], 1):
        print(f"{i}. Prompt: {prompt}")
        print(f"   Similarity Score: {score:.4f}")
        print(f"   Category: {category}")
        print(f"   Subcategory: {subcategory}\n")

    return results[:top_n]  # Always return the results

# Interactive console for semantic search
if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt (or 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Exiting program.")
            break
        else:
            print(f"Searching for prompts similar to: '{user_input}'\n")
            search_results = semantic_search(user_input)
            
            # After displaying results, check if user input should be added
            if search_results and search_results[0][1] >= 0.9:
                add_user_prompt(user_input)