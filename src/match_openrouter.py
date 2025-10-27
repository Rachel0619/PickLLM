"""
Add pricing data to lmarena_*.csv:
- For Proprietary models: Match with OpenRouter and get real pricing
- For Open-source models: Set pricing to $0
"""

import requests
import csv
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


def fetch_openrouter_models() -> List[Dict]:
    """Fetch all models from OpenRouter API."""
    url = "https://openrouter.ai/api/v1/models"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['data']


def normalize_model_name(name: str) -> str:
    """Normalize model name for matching."""
    normalized = name.lower()
    # Remove organization prefix if present
    if '/' in normalized:
        normalized = normalized.split('/')[-1]
    # Remove :free suffix
    normalized = normalized.replace(':free', '')
    # Remove common separators for better matching
    normalized = normalized.replace('-', '').replace('_', '').replace(' ', '')
    return normalized


def find_best_match(
    model_name: str,
    organization: str,
    openrouter_models: List[Dict]
) -> Tuple[Optional[Dict], float]:
    """
    Find the best matching OpenRouter model.

    Args:
        model_name: Model name from lmarena CSV (e.g., 'GPT-4o-latest')
        organization: Organization name (e.g., 'OpenAI')
        openrouter_models: List of all OpenRouter models

    Returns:
        Tuple of (best matching model dict or None, similarity score)
    """
    normalized_name = normalize_model_name(model_name)
    normalized_org = normalize_model_name(organization)

    best_match = None
    best_score = 0.0

    for or_model in openrouter_models:
        or_id = or_model['id']
        or_name = or_model['name']

        # Normalize OpenRouter identifiers
        normalized_or_id = normalize_model_name(or_id)
        normalized_or_name = normalize_model_name(or_name)

        # Check if organization matches
        org_in_id = normalized_org in normalized_or_id

        # Calculate similarity scores
        score_name_id = SequenceMatcher(None, normalized_name, normalized_or_id).ratio()
        score_name_name = SequenceMatcher(None, normalized_name, normalized_or_name).ratio()

        # Boost score if organization matches
        max_score = max(score_name_id, score_name_name)
        if org_in_id:
            max_score = min(1.0, max_score * 1.2)  # 20% boost for org match

        if max_score > best_score:
            best_score = max_score
            best_match = or_model

    return (best_match, best_score)


def add_openrouter_ids(
    input_csv_path: str,
    output_csv_path: str
):
    """
    Add OpenRouter ID and match score columns to lmarena CSV files.

    Output columns added:
    - openrouter_id (suggested match for proprietary, empty for open-source)
    - match_score (confidence of the match, 0.0-1.0)
    """
    print(f"\n📄 Processing: {os.path.basename(input_csv_path)}")

    print("Fetching OpenRouter models...")
    openrouter_models = fetch_openrouter_models()
    print(f"✓ Fetched {len(openrouter_models)} models from OpenRouter")

    # Read input CSV
    with open(input_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) + ['openrouter_id', 'match_score']
        rows = list(reader)
    print(f"✓ Found {len(rows)} models in file")

    # Process each model
    results = []
    matched_count = 0

    for row in rows:
        model_name = row['model']
        license_type = row['license']
        organization = row['organization']

        result = row.copy()

        # Check if proprietary
        is_proprietary = license_type.lower() == 'proprietary'

        if is_proprietary:
            # Match with OpenRouter
            or_model, score = find_best_match(model_name, organization, openrouter_models)

            if or_model and score >= 0.6:
                result['openrouter_id'] = or_model['id']
                result['match_score'] = f"{score:.2f}"
                matched_count += 1
            else:
                result['openrouter_id'] = ''
                result['match_score'] = '0.00'
        else:
            # Open-source: Leave empty
            result['openrouter_id'] = ''
            result['match_score'] = ''

        results.append(result)

    # Write output CSV
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✓ Matched {matched_count} proprietary models")
    print(f"✓ Output saved to: {os.path.basename(output_csv_path)}\n")


if __name__ == '__main__':
    import os
    import glob

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data')

    pattern = os.path.join(data_dir, 'lmarena_*.csv')
    all_files = glob.glob(pattern)

    # Filter out files that already have openrouter_ids or pricing
    input_files = [
        f for f in all_files
        if not ('_with_openrouter_ids' in f or '_with_pricing' in f or '_openrouter' in f)
    ]

    if not input_files:
        print("❌ No lmarena CSV files found to process!")
        exit(1)

    print("="*100)
    print("OpenRouter ID Matcher - Batch Processing")
    print("="*100)
    print(f"\nFound {len(input_files)} files to process:")
    for f in input_files:
        print(f"  - {os.path.basename(f)}")

    # Process each file
    for input_path in input_files:
        # Generate output filename
        base_name = os.path.basename(input_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_filename = f"{name_without_ext}_with_openrouter_ids.csv"
        output_path = os.path.join(data_dir, output_filename)

        try:
            add_openrouter_ids(input_path, output_path)
        except Exception as e:
            print(f"❌ Error processing {base_name}: {e}")
            import traceback
            traceback.print_exc()
            print("\nContinuing with next file...\n")

    print("="*100)
    print("✅ All files processed!")
    print("="*100)
