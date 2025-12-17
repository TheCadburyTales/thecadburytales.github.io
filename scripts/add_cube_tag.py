
import json
import argparse
import os

def add_cube_tag_to_cards(txt_file_path, json_file_path):
    """
    Reads card names from a .txt file and appends a cube tag to the notes field
    of matching cards in a JSON file.
    """
    print(f"Processing text file: {txt_file_path}")
    print(f"Processing JSON file: {json_file_path}")

    # Extract cube name from the text file path
    cube_name = os.path.splitext(os.path.basename(txt_file_path))[0]
    cube_tag = f"cube:{cube_name}"

    # Read card names from the .txt file and prepare a lookup
    cards_to_tag_lookup = {}
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                parts = stripped_line.split('\t')
                card_name = parts[0]
                set_code = parts[1] if len(parts) > 1 else None

                if card_name not in cards_to_tag_lookup:
                    cards_to_tag_lookup[card_name] = []
                cards_to_tag_lookup[card_name].append(set_code)
        print(f"Found {len(cards_to_tag_lookup)} unique card names (with optional sets) in {txt_file_path}")
    except FileNotFoundError:
        print(f"Error: Text file not found at {txt_file_path}")
        return
    except Exception as e:
        print(f"Error reading text file: {e}")
        return

    # Load the all-cards.json file
    try:
        with open(json_file_path, 'r', encoding='utf-8-sig') as f:
            all_data = json.load(f)
        if "cards" not in all_data or not isinstance(all_data["cards"], list):
            print(f"Error: JSON file {json_file_path} does not contain a 'cards' list at the top level.")
            return
        all_cards_list = all_data["cards"]
        print(f"Loaded {len(all_cards_list)} cards from {json_file_path}")
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    modified_count = 0
    modified_cards = []
    # Iterate through cards and add the tag
    for card_data in all_cards_list:
        card_name_json = card_data.get('card_name')
        set_code_json = card_data.get('set') # Assuming 'set_code' is the key in all-cards.json

        if card_name_json and card_name_json in cards_to_tag_lookup:
            sets_to_match = cards_to_tag_lookup[card_name_json]
            
            matched = False
            for target_set in sets_to_match:
                if target_set is None: # Match any card with this name
                    matched = True
                    break
                elif set_code_json and target_set.lower() == set_code_json.lower(): # Match specific set (case-insensitive)
                    matched = True
                    break

            if matched:
                if 'notes' not in card_data or card_data['notes'] is None:
                    card_data['notes'] = ""
                
                # Check if the tag already exists to avoid duplicates
                if cube_tag not in card_data['notes']:
                    if card_data['notes']: # If notes field is not empty, add a space before the new tag
                        card_data['notes'] += f" {cube_tag}"
                    else:
                        card_data['notes'] = cube_tag
                    modified_count += 1
                    # print(f"Added '{cube_tag}' to card: {card_data['card_name']}") # Uncomment for verbose logging
        modified_cards.append(card_data) # Add card back to the list
    
    # Update the all_data with the modified cards list
    all_data["cards"] = modified_cards

    print(f"Modified {modified_count} cards with tag '{cube_tag}'")

    # Save the updated JSON data
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated {json_file_path}")
    except Exception as e:
        print(f"Error writing updated JSON file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a cube tag to cards in all-cards.json based on a .txt file.")
    parser.add_argument("txt_file", help="Path to the .txt file containing card names (one per line).")
    parser.add_argument("--json_file", default="lists/all-cards.json",
                        help="Path to the all-cards.json file. Defaults to lists/all-cards.json.")
    
    args = parser.parse_args()

    # Resolve absolute paths
    txt_file_abs_path = os.path.abspath(args.txt_file)
    json_file_abs_path = os.path.abspath(args.json_file)

    add_cube_tag_to_cards(txt_file_abs_path, json_file_abs_path)
