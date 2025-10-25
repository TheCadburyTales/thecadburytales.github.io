import json
import sys
import os
import subprocess
import shutil

def validate_card_names(input_file):
    """
    Reads a list of card names from a text file, checks for their existence in
    'lists/all-cards.json', and prints out the names of the cards that were not found.
    If all cards are found, it creates a new JSON file with the card data,
    runs the print_draft_file.py script on it, and then deletes the temporary files.
    """
    try:
        with open(input_file, 'r') as f:
            card_names_to_check = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
        return

    script_dir = os.path.dirname(sys.argv[0])
    all_cards_path = os.path.join(script_dir, '..', 'lists', 'all-cards.json')
    print_draft_file_path = os.path.join(script_dir, 'print_draft_file.py')

    try:
        with open(all_cards_path, 'r', encoding='utf-8-sig') as f:
            all_cards_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{all_cards_path}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from '{all_cards_path}'.")
        print(f"  {e.msg} at line {e.lineno} column {e.colno}")
        return

    all_cards_map = {card['card_name']: card for card in all_cards_data['cards']}
    
    not_found_cards = [name for name in card_names_to_check if name not in all_cards_map]

    if not_found_cards:
        print("Cards not found in 'lists/all-cards.json':")
        for card_name in not_found_cards:
            print(card_name)
    else:
        print("All cards found in 'lists/all-cards.json'.")
        
        basename = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = os.path.join(script_dir, '..', 'sets', f"{basename}-files")
        output_path = os.path.join(output_dir, f"{basename}.json")
        
        os.makedirs(output_dir, exist_ok=True)
        
        found_cards = [all_cards_map[name] for name in card_names_to_check]
        
        output_data = {
            "name": basename,
            "formats": "",
            "trimmed": "y",
            "draft_structure": "cube",
            "image_type": "png",
            "cards": found_cards
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=4)
            
        print(f"Successfully created temporary JSON file at '{output_path}'")

        try:
            subprocess.run(['python3', print_draft_file_path, basename], check=True, cwd=os.path.join(script_dir, '..'))
            print(f"Successfully ran print_draft_file.py for '{basename}'")

            draft_file_source = os.path.join(output_dir, f"{basename}-draft.txt")
            input_dir = os.path.dirname(input_file)
            draft_file_dest = os.path.join(input_dir, f"{basename}-draft.txt")

            if os.path.exists(draft_file_source):
                shutil.move(draft_file_source, draft_file_dest)
                print(f"Successfully created draft file: {draft_file_dest}")
            else:
                print(f"Error: Draft file could not be created.")

        except subprocess.CalledProcessError as e:
            print(f"Error running print_draft_file.py: {e}")
        finally:
            shutil.rmtree(output_dir)
            print(f"Cleaned up temporary directory '{output_dir}'")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_card_names.py <input_file.txt>")
    else:
        validate_card_names(sys.argv[1])
