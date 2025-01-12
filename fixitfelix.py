import json

# Function to replace '\u2019' with apostrophe in the JSON file
def replace_unicode_in_json(input_file, output_file):
    try:
        # Open the JSON file and load its data
        with open(input_file, 'r') as file:
            data = json.load(file)

        # Iterate through each entry in the JSON data and replace '\u2019' with apostrophe
        for entry in data:
            if 'prompt' in entry:
                entry['prompt'] = entry['prompt'].replace('\u2019', "'")

        # Write the updated data to a new file
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"Updated JSON saved to {output_file}")

    except Exception as e:
        print(f"Error processing the file: {e}")

# Define the input and output file paths
input_file = "updated_prompts_with_embeddings.json"  # Input file path
output_file = "updated_prompts_with_apostrophes.json"  # Output file path

# Run the function
replace_unicode_in_json(input_file, output_file)