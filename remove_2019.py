import json

# Path to your JSON file
file_path = "updated_prompts_copy.json"
output_path = "fixed_file.json"

def fix_unicode_escapes(input_file, output_file):
    try:
        # Load the JSON file
        with open(input_file, "r") as file:
            data = json.load(file)

        # Replace all occurrences of \u2019 with an apostrophe in the prompts
        for entry in data:
            entry["prompt"] = entry["prompt"].replace("\u2019", "'")

        # Save the updated JSON to a new file
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)

        print(f"File fixed and saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function
fix_unicode_escapes(file_path, output_path)