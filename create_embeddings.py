import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to calculate embedding using OpenAI's API
def calculate_embedding(prompt_text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=prompt_text
    )
    # Extract the embedding from the response
    return response['data'][0]['embedding']

# Function to process and update the JSON file with embeddings
def process_json_file(input_file, output_file):
    try:
        # Open the original JSON file and load its data
        with open(input_file, 'r') as file:
            data = json.load(file)
        
        # Iterate over each prompt in the JSON and calculate its embedding
        for index, prompt_entry in enumerate(data):
            prompt_text = prompt_entry.get("prompt", "")
            if prompt_text:
                # Calculate the embedding for the prompt
                embedding = calculate_embedding(prompt_text)
                prompt_entry['embedding'] = embedding  # Add the embedding to the prompt entry
                print(f"Processed {index + 1}/{len(data)}: {prompt_text[:50]}...")  # Output progress
        
        # Write the updated data with embeddings to the new JSON file
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Updated JSON with embeddings has been saved to {output_file}")
    
    except Exception as e:
        print(f"Error processing the file: {e}")

# Main function to define input/output paths and call the processing function
if __name__ == "__main__":
    input_file = "updated_prompts.json"  # Path to the input JSON file
    output_file = "updated_prompts_with_embeddings.json"  # Path to the output JSON file

    process_json_file(input_file, output_file)