import json
import csv
import argparse
import random

MODELS = {
    "Gemini": "gemini-2.5-pro",
    "DeepSeek": "DeepSeek-R1-0528",
    "Flash": "gemini-2.5-flash",
    "Qwen": "Qwen3-235B-A22B-2507"
}

IDENTITIES = [
    {"label": "Red Panda", "color": "red"},
    {"label": "Blue Whale", "color": "#04AFF2"},
    {"label": "Green Elephant", "color": "#04F247"},
    {"label": "Golden Fish", "color": "goldenrod"}
]

SC1_PAGE = {
  "name": "sanity_check_page_1",
  "elements": [
    {
      "type": "radiogroup",
      "name": "sanity_check_1",
      "title": "Please select the correct statement",
      "description": "ORIGINAL: The sun appears to rise each morning from the eastern horizon before setting in the west",
      "isRequired": True,
      "choices": [
        { "value": "1", "text": "The moon rises in the east." },
        { "value": "2", "text": "The sun rises in the west." },
        { "value": "3", "text": "The sun rises in the east." },
        { "value": "4", "text": "The sun never rises." }
      ],
      "correctAnswer": "3"
    }
  ]
}

SC2_PAGE = {
  "name": "sanity_check_page_2",
  "elements": [
    {
      "type": "radiogroup",
      "name": "sanity_check_2",
      "title": "Please select the correct statement",
      "description": "ORIGINAL: Pure water begins to freeze at exactly zero degrees Celsius",
      "isRequired": True,
      "choices": [
        { "value": "1", "text": "Water freezes at 100°C." },
        { "value": "2", "text": "Water freezes at 0°C." },
        { "value": "3", "text": "Water boils at 0°C." },
        { "value": "4", "text": "Ice melts at 0°C." }
      ],
      "correctAnswer": "2"
    }
  ]
}

def create_task_page(task_id, category, original, responses):
    random.shuffle(IDENTITIES)
    
    model_to_identity = {
        model_key: IDENTITIES[i] for i, model_key in enumerate(responses.keys())
    }

    html_parts = []
    for model_key, response_text in responses.items():
        identity = model_to_identity[model_key]
        html_parts.append(f"<p><strong><span style='color:{identity['color']};'>{identity['label']}</span></strong><br/>{response_text}</p>")

    choices = []
    for model_key in responses.keys():
        identity = model_to_identity[model_key]
        choices.append({"value": MODELS[model_key], "text": identity['label']})
    
    random.shuffle(choices)

    return {
        "name": task_id,
        "elements": [
            {
                "type": "html",
                "name": f"{task_id}_context",
                "title": f"Task {task_id}",
                "html": f"<h3>{category}</h3><p><strong>Original</strong>: {original}</p><hr/>" + "<br/>".join(html_parts)
            },
            {
                "type": "ranking",
                "name": f"{task_id}_fluency",
                "title": "Fluency",
                "description": "Rank from most to least smooth and error-free.",
                "isRequired": True,
                "choices": choices
            },
            {
                "type": "ranking",
                "name": f"{task_id}_coherence",
                "title": "Coherence",
                "description": "Rank from most to least logical and easy to follow.",
                "isRequired": True,
                "choices": choices
            },
            {
                "type": "ranking",
                "name": f"{task_id}_conciseness",
                "title": "Conciseness",
                "description": "Rank from most to least clear and compact.",
                "isRequired": True,
                "choices": choices
            },
            {
                "type": "checkbox",
                "name": f"{task_id}_factual_accuracy",
                "title": "Factual accuracy",
                "description": "Select all texts that are factually correct given the Original.",
                "isRequired": True,
                "choices": choices,
                "showSelectAllItem": True,
                "selectAllText": "All"
            },
            {
                "type": "ranking",
                "name": f"{task_id}_sentiment",
                "title": "Sentiment match",
                "description": "Rank from most to least similar to the Original in style and sentiment.",
                "isRequired": True,
                "choices": choices
            },
            {
                "type": "ranking",
                "name": f"{task_id}_motivational",
                "title": "Motivational tone",
                "description": "Rank from most to least empathetic and encouraging.",
                "isRequired": True,
                "choices": choices
            },
            {
                "type": "ranking",
                "name": f"{task_id}_constructiveness",
                "title": "Constructiveness",
                "description": "Rank from most to least helpful and constructive.",
                "isRequired": True,
                "choices": choices
            },
            {
                "type": "ranking",
                "name": f"{task_id}_final",
                "title": "Final choice",
                "description": "Rank from most to least suitable as a final version.",
                "isRequired": True,
                "choices": choices
            }
        ]
    }

def main():
    parser = argparse.ArgumentParser(description='Generate survey tasks from a CSV file.')
    parser.add_argument('csv_input_path', help='Path to the input CSV file.')
    parser.add_argument('json_output_path', help='Path to the output JSON file.')
    parser.add_argument('--volunteer', help='Volunteer name to filter by.', default='Volunteer 1')
    args = parser.parse_args()

    pages = []
    try:
        with open(args.csv_input_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Volunteer'] == args.volunteer:
                    responses = {model_key: row[model_key] for model_key in MODELS.keys()}
                    pages.append(create_task_page(
                        row['Task ID'],
                        row['Category'],
                        row['Original'],
                        responses
                    ))
    except FileNotFoundError:
        print(f"Error: The file {args.csv_input_path} was not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Add sanity checks
    if len(pages) >= 4:
        pages.insert(2, SC1_PAGE)
        pages.insert(5, SC2_PAGE)

    output_json = {
        "pages": pages,
        "headerView": "advanced"
    }

    with open(args.json_output_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(output_json, jsonfile, indent=2)

    print(f"Successfully generated {args.json_output_path} from {args.csv_input_path} for {args.volunteer}.")

if __name__ == '__main__':
    main()