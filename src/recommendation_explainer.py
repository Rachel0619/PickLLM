import os
from openai import OpenAI
from typing import Dict, List, Optional


class RecommendationExplainer:
    """Generate natural language explanations for LLM recommendations using AI."""

    def __init__(self):
        """Initialize the explainer with OpenRouter API client."""
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = "z-ai/glm-4.5-air:free"

    def generate_explanation(
        self,
        use_case: str,
        recommendations: List[Dict],
        visual_ai_type: Optional[str] = None,
        model_type: Optional[str] = None
    ) -> str:
        """
        Generate a natural language explanation for why these models were recommended.

        Args:
            use_case: User's primary use case
            recommendations: List of top 3 recommended models with their details
            visual_ai_type: Visual AI type if applicable
            model_type: Model type preference (open/proprietary/no preference)

        Returns:
            Natural language explanation (2-3 paragraphs)
        """
        # Build the prompt
        prompt = self._build_prompt(use_case, recommendations, visual_ai_type, model_type)

        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://pickllm.com",
                    "X-Title": "PickLLM",
                },
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant helping users understand LLM recommendations. Provide clear, concise explanations in 2-3 paragraphs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            explanation = completion.choices[0].message.content
            return explanation

        except Exception as e:
            print(f"Error generating explanation: {e}")
            # Fallback to static explanation
            return self._get_fallback_explanation(use_case, recommendations)

    def _build_prompt(
        self,
        use_case: str,
        recommendations: List[Dict],
        visual_ai_type: Optional[str] = None,
        model_type: Optional[str] = None
    ) -> str:
        """Build the prompt for the LLM to generate explanation."""

        # Format use case
        use_case_formatted = use_case.replace('_', ' ').title()

        # Format recommendations
        rec_text = []
        for i, rec in enumerate(recommendations, 1):
            rec_text.append(
                f"{i}. {rec['model']} by {rec['organization']}\n"
                f"   - Arena Score: {rec['arena_score']}\n"
                f"   - Votes: {rec['votes']}\n"
                f"   - License: {rec['license']}\n"
                f"   - Knowledge Cutoff: {rec.get('knowledge_cutoff', 'N/A')}"
            )

        recommendations_text = "\n".join(rec_text)

        # Build the full prompt
        prompt = f"""A user is looking for LLM recommendations based on the following requirements:

**Use Case**: {use_case_formatted}
"""

        if visual_ai_type:
            prompt += f"**Visual AI Type**: {visual_ai_type.replace('_', ' ').title()}\n"

        if model_type:
            model_pref = {
                'open_only': 'Open-source models only',
                'proprietary_only_enterprise': 'Proprietary/Enterprise models only',
                'no_preference': 'No preference on model type'
            }.get(model_type, 'No preference')
            prompt += f"**Model Preference**: {model_pref}\n"

        prompt += f"""
Based on their requirements, we recommended these top 3 models from the LMSYS Chatbot Arena leaderboard:

{recommendations_text}

Please write a 3-paragraph explanation following this structure:

**Paragraph 1**: Summarize the user's needs in natural language. For example: "You are looking for an open-weight model for conversational use cases, with low cost and medium latency." Make it conversational and personalized based on their use case and model preference.

**Paragraph 2**: Briefly introduce the three recommended models by name and organization. DO NOT mention their Arena scores or vote counts (this info is already shown in the result cards).

**Paragraph 3**: For each of the 3 models, write 2-3 sentences describing what makes it unique and its key advantages for the user's use case. Format this as a bulleted list where each bullet starts with the model name in bold (e.g., "**Gemini-2.5-Pro**: ..."). Focus on practical benefits, capabilities, and differentiators.

Keep it concise, informative, and user-friendly. Avoid repeating data already visible in the cards."""

        return prompt

    def _get_fallback_explanation(self, use_case: str, recommendations: List[Dict]) -> str:
        """Provide a static fallback explanation if API fails."""
        use_case_formatted = use_case.replace('_', ' ').title()

        return f"""Based on your requirement for {use_case_formatted}, we've selected the top-performing models from the LMSYS Chatbot Arena leaderboard. These models have been rigorously tested through thousands of community evaluations, ensuring they meet high standards for real-world performance.

The recommended models represent the best options currently available, ranked by their Arena Score which reflects head-to-head comparisons in blind tests. Each model has received substantial community validation through voting, providing confidence in their capabilities for your specific use case.

These rankings are continuously updated based on the latest leaderboard data, ensuring you get recommendations based on current performance metrics and community feedback."""


if __name__ == "__main__":
    # Test the explainer
    from dotenv import load_dotenv
    load_dotenv()

    explainer = RecommendationExplainer()

    # Test with sample data
    test_recommendations = [
        {
            'model': 'GPT-4',
            'organization': 'OpenAI',
            'arena_score': 1250,
            'votes': 50000,
            'license': 'Proprietary',
            'knowledge_cutoff': '2023/09'
        },
        {
            'model': 'Claude-3-Opus',
            'organization': 'Anthropic',
            'arena_score': 1240,
            'votes': 45000,
            'license': 'Proprietary',
            'knowledge_cutoff': '2023/08'
        },
        {
            'model': 'Gemini-Pro',
            'organization': 'Google',
            'arena_score': 1230,
            'votes': 40000,
            'license': 'Proprietary',
            'knowledge_cutoff': '2023/11'
        }
    ]

    explanation = explainer.generate_explanation(
        use_case='conversational_knowledge',
        recommendations=test_recommendations,
        model_type='no_preference'
    )

    print("Generated Explanation:")
    print("=" * 80)
    print(explanation)
