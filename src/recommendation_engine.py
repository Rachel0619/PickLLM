import os
import pandas as pd
from typing import Dict, List, Optional, Tuple

class RecommendationEngine:
    def __init__(self):
        """Initialize the recommendation engine with data directory path."""
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

        # Organization to logo filename mapping
        self.org_to_logo = {
            'OpenAI': 'openai.png',
            'Google': 'google.png',
            'Anthropic': 'anthropic.png',
            'Meta': 'meta.png',
            'Microsoft': 'microsoft.png',
            'Mistral': 'mistral.png',
            'Cohere': 'cohere.png',
            'xAI': 'xai.png',
            'DeepSeek': 'deepseek.png',
            'Alibaba': 'alibaba.png',
            'Z.ai': 'zai.png',
            'Moonshot': 'moonshot.png',
            'Tencent': 'tencent.png',
            'LG AI Research': 'lg.png',
            'Perplexity': 'perplexity.png',
            'AI21 Labs': 'ai21.png',
            'Reka': 'reka.png',
            'Inflection': 'inflection.png',
            'Stability AI': 'stability.png',
        }

        # Mapping from questionnaire choices to CSV files (with pricing data)
        self.use_case_mapping = {
            'conversational_knowledge': ['lmarena_text_with_pricing_or.csv'],
            'productivity_information': ['lmarena_text_with_pricing_or.csv'],
            'creative_content': ['lmarena_text_with_pricing_or.csv'],
            'technical_developer': ['lmarena_webdev_with_pricing_or.csv'],
            'advanced_automation': ['lmarena_text_with_pricing_or.csv'],
            'visual_ai': ['lmarena_vision_with_pricing_or.csv', 'lmarena_image_with_pricing.csv', 'lmarena_image-edit_with_pricing.csv']
        }

        # Visual AI sub-category mapping
        self.visual_ai_mapping = {
            'image_understanding': ['lmarena_vision_with_pricing_or.csv'],
            'image_generation': ['lmarena_image_with_pricing.csv'],
            'image_editing': ['lmarena_image-edit_with_pricing.csv']
        }

    def get_relevant_csv_files(self, use_case: str, visual_ai_type: Optional[str] = None) -> List[str]:
        """
        Map user's use case choice to relevant CSV files.

        Args:
            use_case: Primary use case selected by user
            visual_ai_type: Visual AI type if use_case is 'visual_ai'

        Returns:
            List of CSV filenames to use for recommendations
        """
        if use_case == 'visual_ai' and visual_ai_type:
            # If Visual AI is selected, use the specific visual AI mapping
            return self.visual_ai_mapping.get(visual_ai_type, [])
        else:
            # For all other use cases, use the primary mapping
            return self.use_case_mapping.get(use_case, [])

    def load_leaderboard_data(self, csv_files: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Load leaderboard data from specified CSV files.

        Args:
            csv_files: List of CSV filenames to load

        Returns:
            Dictionary mapping filename to DataFrame
        """
        data = {}

        for csv_file in csv_files:
            file_path = os.path.join(self.data_dir, csv_file)

            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    data[csv_file] = df
                    print(f"✅ Loaded {csv_file}: {len(df)} models")
                except Exception as e:
                    print(f"❌ Error loading {csv_file}: {e}")
            else:
                print(f"⚠️  File not found: {csv_file}")

        return data

    def get_top_recommendations(self, use_case: str, visual_ai_type: Optional[str] = None, model_type: Optional[str] = None, priority: Optional[str] = None, top_n: int = 3) -> List[Dict]:
        """
        Get top N model recommendations for a given use case.

        Args:
            use_case: Primary use case selected by user
            visual_ai_type: Visual AI type if use_case is 'visual_ai'
            model_type: Model type preference ('open_only', 'proprietary_only_enterprise', 'no_preference')
            priority: User priority ('lower_cost' or 'better_performance')
            top_n: Number of top recommendations to return (default: 3)

        Returns:
            List of dictionaries containing model information
        """
        # Get relevant CSV files
        csv_files = self.get_relevant_csv_files(use_case, visual_ai_type)

        if not csv_files:
            print(f"❌ No CSV files mapped for use case: {use_case}")
            return []

        # Load the data
        loaded_data = self.load_leaderboard_data(csv_files)

        if not loaded_data:
            print(f"❌ No data loaded for use case: {use_case}")
            return []

        # Get the first CSV file's data (primary ranking source)
        primary_csv = csv_files[0]
        df = loaded_data.get(primary_csv)

        if df is None or df.empty:
            print(f"❌ No data in primary CSV: {primary_csv}")
            return []

        # Apply model type filter based on user preference
        if model_type == 'open_only':
            # Filter to exclude proprietary models
            df = df[df['license'] != 'Proprietary']
            print(f"🔓 Filtered to open weights models: {len(df)} models")
        elif model_type == 'proprietary_only_enterprise':
            # Filter to include only proprietary models
            df = df[df['license'] == 'Proprietary']
            print(f"🔒 Filtered to proprietary models: {len(df)} models")
        # If 'no_preference', no filtering is applied

        if df.empty:
            print(f"❌ No models found after applying model_type filter: {model_type}")
            return []

        # Apply sorting based on user's priority
        if priority == 'lower_cost':
            # Sort by pricing (ascending) - lower cost first
            # Convert pricing to float, handling non-numeric values
            df['pricing_numeric'] = pd.to_numeric(df['pricing'], errors='coerce')
            df = df.sort_values('pricing_numeric', ascending=True)
            print(f"💰 Sorted by cost (lowest first)")
        else:
            # Default: Sort by rank (better performance first)
            # CSV is already sorted by rank, but ensure it
            df = df.sort_values('rank', ascending=True)
            print(f"🏆 Sorted by performance (rank)")

        # Get top N models
        top_models = df.head(top_n)

        # Convert to list of dictionaries with relevant fields
        recommendations = []
        for idx, row in top_models.iterrows():
            organization = row.get('organization', 'Unknown')
            # Get logo filename from mapping
            logo_filename = self.org_to_logo.get(organization, '')
            logo_url = f'/static/images/logos/{logo_filename}' if logo_filename else ''

            model_info = {
                'rank': int(row.get('rank', idx + 1)),
                'model': row.get('displayed_name', row.get('model', 'Unknown')),  # Use displayed_name if available
                'arena_score': row.get('arena_score', 'N/A'),
                'votes': row.get('votes', 'N/A'),
                'organization': organization,
                'license': row.get('license', 'Unknown'),
                'url': row.get('url', ''),
                'ci': row.get('95_pct_ci', 'N/A'),
                'logo_url': logo_url,
                'knowledge_cutoff': row.get('knowledge_cutoff', 'N/A'),
                'pricing': row.get('pricing', 'N/A')  # Add pricing information
            }
            recommendations.append(model_info)

        print(f"✅ Generated {len(recommendations)} recommendations")
        return recommendations

    def process_user_input(self, questionnaire_data: Dict) -> Tuple[List[str], Dict[str, pd.DataFrame]]:
        """
        Process user questionnaire input and return relevant data.

        Args:
            questionnaire_data: Dictionary containing user's questionnaire responses

        Returns:
            Tuple of (csv_files_used, loaded_dataframes)
        """
        # Extract primary use case
        use_case = questionnaire_data.get('use_case')
        visual_ai_type = questionnaire_data.get('visual_ai_type')

        print(f"🎯 User selected use case: {use_case}")
        if visual_ai_type:
            print(f"🖼️  Visual AI type: {visual_ai_type}")

        # Get relevant CSV files
        csv_files = self.get_relevant_csv_files(use_case, visual_ai_type)

        if not csv_files:
            print(f"❌ No CSV files mapped for use case: {use_case}")
            return [], {}

        print(f"📊 Mapped to CSV files: {csv_files}")

        # Load the data
        loaded_data = self.load_leaderboard_data(csv_files)

        return csv_files, loaded_data

    def test_mapping(self):
        """Test the mapping logic with sample inputs."""
        print("🧪 Testing Use Case Mapping:")
        print("=" * 50)

        test_cases = [
            {'use_case': 'conversational_knowledge'},
            {'use_case': 'productivity_information'},
            {'use_case': 'creative_content'},
            {'use_case': 'technical_developer'},
            {'use_case': 'advanced_automation'},
            {'use_case': 'visual_ai', 'visual_ai_type': 'image_understanding'},
            {'use_case': 'visual_ai', 'visual_ai_type': 'image_generation'},
            {'use_case': 'visual_ai', 'visual_ai_type': 'image_editing'},
        ]

        for test_case in test_cases:
            print(f"\nTest case: {test_case}")
            csv_files, data = self.process_user_input(test_case)
            print(f"Result: {len(data)} datasets loaded")
            print("-" * 30)


if __name__ == "__main__":
    # Initialize and test the recommendation engine
    engine = RecommendationEngine()
    engine.test_mapping()