import os
from openai import OpenAI
from typing import Dict, List, Optional

class UseCaseHelper:

    def __init__(self):
        """Initialize the helper with OpenRouter API client."""
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        # Using DeepSeek R1 Distill which is reliable, free, and good at instruction following
        self.model = "deepseek/deepseek-chat-v3.1:free"     

    def _build_prompt(
        self,
        user_description: str
    ) -> str:
        """Build the prompt for classifying user's use case description."""

        prompt = f"""Classify this use case into exactly one category.

Description: "{user_description}"

Categories:
- conversational_knowledge: Chatbots, Q&A, virtual assistants, customer support, knowledge retrieval
- productivity_information: Document processing, summarization, email drafting, data organization
- creative_content: Writing, marketing copy, social media content, story generation
- technical_developer: Code generation, debugging, technical docs, programming help
- advanced_automation: Multi-step workflows, agent orchestration, API integration
- visual_ai: Image understanding/generation/editing, visual content creation

Return ONLY the category name, nothing else."""

        return prompt

    def use_case_classification(
        self,
        use_case_description: str
    ) -> str:
        """
        Classify user's input into one of the 6 use cases.

        Args:
            use_case_description: User's primary use case written in descriptive natural language

        Returns:
            classification (one of: conversational_knowledge, productivity_information,
            creative_content, technical_developer, advanced_automation, visual_ai)
        """
        # Build the prompt
        prompt = self._build_prompt(use_case_description)

        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://pickllm.com",
                    "X-Title": "PickLLM",
                },
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )

            classification = completion.choices[0].message.content
            if classification:
                # Clean up the response: strip whitespace and remove special tokens
                classification = classification.strip()
                # Remove common special tokens that some models add
                special_tokens = ['<|begin_of_sentence|>', '<｜begin▁of▁sentence｜>', '<|end_of_text|>', '<|im_end|>', '<|im_start|>']
                for token in special_tokens:
                    classification = classification.replace(token, '')
                # Strip again after removing tokens
                classification = classification.strip()
            return classification

        except Exception as e:
            print(f"Error classifying use case: {e}")
            return None

if __name__ == "__main__":
    # Test the classifier
    from dotenv import load_dotenv
    load_dotenv()

    classifier = UseCaseHelper()

    # Test with a sample description
    test_description = "I need to analyze product images from our e-commerce site, generate detailed descriptions of items, and categorize them automatically based on visual features like color, style, and composition."

    print(f"Testing with description: {test_description}\n")
    response = classifier.use_case_classification(test_description)
    print(f"Classification result: {response}")