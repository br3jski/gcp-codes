import json
import re

def custom_transform(entity_data):
    # Correct handling of escaped double quotes within strings
    # This should be done after ensuring all property names are enclosed in double quotes
    # and replacing single quotes with double quotes to avoid unintended replacements.
    
    # Ensure all property names are enclosed in double quotes
    transformed_data = re.sub(r'([{,]\s*)(\w+)(\s*:\s*)', r'\1"\2"\3', entity_data)
    
    # Replace single quotes with double quotes, except within the tags field
    transformed_data = re.sub(r'(?<!\\)\'', '"', transformed_data)
    
    # Now, correct handling of escaped double quotes within strings
    transformed_data = re.sub(r'\\\\"', r'\\"', transformed_data)
    
    # Convert boolean and null values correctly
    transformed_data = transformed_data.replace('False', 'false').replace('True', 'true').replace('None', 'null')
    
    # Handle datetime conversion to ISO 8601 string format
    transformed_data = re.sub(
        r'DatetimeWithNanoseconds\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), tzinfo=datetime\.timezone\.utc\)',
        lambda m: f'"{int(m.group(1))}-{int(m.group(2)):02}-{int(m.group(3)):02}T{int(m.group(4)):02}:{int(m.group(5)):02}:{int(m.group(6)):02}.{int(m.group(7))}Z"',
        transformed_data
    )
    
    # Simplify double backslashes to single backslashes as an example of custom handling
    # This step is adjusted to occur after handling escaped double quotes to ensure
    # backslashes used in escape sequences are not unintentionally modified.
    transformed_data = transformed_data.replace('\\\\', '\\')

    return transformed_data

def process_object_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        pattern = r"<Entity\('ObjectInfo', (\d+)\) (\{.*?\})>"
        matches = re.finditer(pattern, file_content, re.DOTALL)

        for match in matches:
            object_id = match.group(1)
            entity_data = match.group(2)

            try:
                # Apply the custom transformation to make the data JSON-compatible
                json_compatible_data = custom_transform(entity_data)

                # Convert the transformed data into a JSON object
                data = json.loads(json_compatible_data)

                # Create a new dictionary with 'id' as the first entry
                ordered_data = {"id": object_id}
                # Update this dictionary with the rest of the data
                ordered_data.update(data)

                # Print the formatted JSON string
                print(json.dumps(ordered_data, indent=4))
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON for Object ID {object_id}: {e}")
                # Optionally, print the transformed data for inspection
                print(f"Transformed data (Object ID {object_id}): {json_compatible_data[:150]}...")

    except Exception as e:
        print(f"Error processing file: {e}")

# Replace 'path/to/your/ObjectInfo.json' with the actual file path
process_object_info('./ObjectInfo.json')
