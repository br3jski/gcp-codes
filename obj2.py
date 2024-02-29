import json
import re

def parse_tags_field(tags_str):
    # This is a simplified placeholder logic. You'll need to adjust it based on the actual structure of your 'tags' field.
    try:
        # Correcting known issues with escape sequences for this example.
        corrected_str = tags_str.replace('\\"', '"').replace('\\\\', '\\')
        # Assuming the 'tags' content is a JSON-like list of dictionaries in string format.
        tags_data = json.loads(corrected_str)
        return tags_data
    except Exception as e:
        print(f"Error parsing tags field: {e}")
        return []

def custom_transform(entity_data):
    # Ensure all property names are enclosed in double quotes
    transformed_data = re.sub(r'([{,]\s*)(\w+)(\s*:\s*)', r'\1"\2"\3', entity_data)
    
    # Replace single quotes with double quotes, being careful with embedded structures
    transformed_data = re.sub(r'(?<!\\)\'', '"', transformed_data)
    
    # Convert boolean and null values correctly
    transformed_data = transformed_data.replace('False', 'false').replace('True', 'true').replace('None', 'null')
    
    # Handle datetime conversion to ISO 8601 string format
    transformed_data = re.sub(
        r'DatetimeWithNanoseconds\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), tzinfo=datetime.timezone.utc\)',
        lambda m: f'"{int(m.group(1))}-{int(m.group(2)):02d}-{int(m.group(3)):02d}T{int(m.group(4)):02d}:{int(m.group(5)):02d}:{int(m.group(6)):02d}.{int(m.group(7))}Z"',
        transformed_data
    )

    # Manually parse and transform the 'tags' field
    tags_pattern = r'"tags":\s*"(.*?)"'
    matches = re.findall(tags_pattern, transformed_data)
    for match in matches:
        parsed_tags = parse_tags_field(match)
        if parsed_tags is not None:
            # Replace the original 'tags' string with the correctly formatted JSON string
            transformed_data = transformed_data.replace(match, json.dumps(parsed_tags))

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
                json_compatible_data = custom_transform(entity_data)
                data = json.loads(json_compatible_data)
                ordered_data = {"id": object_id}
                ordered_data.update(data)
                print(json.dumps(ordered_data, indent=4))
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON for Object ID {object_id}: {e}")
                print(f"Transformed data (Object ID {object_id}): {json_compatible_data[:150]}...")

    except Exception as e:
        print(f"Error processing file: {e}")

# Replace 'path/to/your/ObjectInfo.json' with the actual file path
process_object_info('./ObjectInfo.json')
