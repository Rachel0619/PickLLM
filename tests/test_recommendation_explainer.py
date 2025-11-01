"""
Tests for RecommendationExplainer LLM component.

These tests verify that the LLM-powered explanation generator:
1. Produces correctly formatted output with expected structure
2. Generates content that matches user requirements
3. Handles different input scenarios consistently
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv()

from recommendation_explainer import RecommendationExplainer


# Sample test data
SAMPLE_RECOMMENDATIONS = [
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


class TestRecommendationExplainerOutput:
    """Test that LLM output has the correct structure and format."""

    @pytest.fixture
    def explainer(self):
        """Create an explainer instance for testing."""
        return RecommendationExplainer()

    def test_explanation_is_non_empty_string(self, explainer):
        """Test that the LLM returns a non-empty string response."""
        explanation = explainer.generate_explanation(
            use_case='conversational_knowledge',
            recommendations=SAMPLE_RECOMMENDATIONS,
            model_type='no_preference'
        )

        assert isinstance(explanation, str), "Explanation should be a string"
        assert len(explanation) > 0, "Explanation should not be empty"
        assert len(explanation) > 100, "Explanation should be substantial (>100 chars)"

    def test_explanation_has_paragraph_structure(self, explainer):
        """Test that the explanation has multiple paragraphs as expected."""
        explanation = explainer.generate_explanation(
            use_case='technical_developer',
            recommendations=SAMPLE_RECOMMENDATIONS,
            model_type='proprietary_only_enterprise'
        )

        # Check that explanation has multiple paragraphs (separated by double newlines)
        paragraphs = [p.strip() for p in explanation.split('\n\n') if p.strip()]

        assert len(paragraphs) >= 2, f"Explanation should have at least 2 paragraphs, got {len(paragraphs)}"

        # Each paragraph should be substantial
        for i, para in enumerate(paragraphs):
            assert len(para) > 50, f"Paragraph {i+1} should be substantial (>50 chars), got {len(para)}"

    def test_explanation_mentions_model_names(self, explainer):
        """Test that the LLM output mentions the recommended model names."""
        explanation = explainer.generate_explanation(
            use_case='creative_content',
            recommendations=SAMPLE_RECOMMENDATIONS,
            model_type='no_preference'
        )

        # Check that at least 2 of the 3 model names are mentioned
        model_names = ['GPT-4', 'Claude', 'Gemini']
        mentions = sum(1 for name in model_names if name.lower() in explanation.lower())

        assert mentions >= 2, f"Explanation should mention at least 2 model names, found {mentions}"


class TestRecommendationExplainerConsistency:
    """Test that prompt variations produce consistent and appropriate results."""

    @pytest.fixture
    def explainer(self):
        """Create an explainer instance for testing."""
        return RecommendationExplainer()

    def test_visual_ai_context_included(self, explainer):
        """Test that visual AI type is reflected in the explanation."""
        explanation = explainer.generate_explanation(
            use_case='visual_ai',
            recommendations=SAMPLE_RECOMMENDATIONS,
            visual_ai_type='image_generation',
            model_type='no_preference'
        )

        # Check that visual/image-related terms appear in the explanation
        visual_keywords = ['visual', 'image', 'vision', 'picture', 'photo', 'generation']
        has_visual_context = any(keyword in explanation.lower() for keyword in visual_keywords)

        assert has_visual_context, "Explanation for visual AI should mention visual/image-related concepts"

    def test_open_source_preference_reflected(self, explainer):
        """Test that model type preference is reflected in explanation."""
        # Create open-source recommendations
        open_source_recs = [
            {
                'model': 'Llama-3-70B',
                'organization': 'Meta',
                'arena_score': 1200,
                'votes': 35000,
                'license': 'Apache 2.0',
                'knowledge_cutoff': '2024/03'
            },
            {
                'model': 'Mixtral-8x7B',
                'organization': 'Mistral',
                'arena_score': 1190,
                'votes': 30000,
                'license': 'Apache 2.0',
                'knowledge_cutoff': '2024/01'
            },
            {
                'model': 'Qwen-2-72B',
                'organization': 'Alibaba',
                'arena_score': 1180,
                'votes': 25000,
                'license': 'Apache 2.0',
                'knowledge_cutoff': '2024/02'
            }
        ]

        explanation = explainer.generate_explanation(
            use_case='technical_developer',
            recommendations=open_source_recs,
            model_type='open_only'
        )

        # Check for open-source related keywords
        open_keywords = ['open', 'source', 'community', 'accessible', 'weights', 'transparent']
        has_open_context = any(keyword in explanation.lower() for keyword in open_keywords)

        assert has_open_context, "Explanation should reflect open-source preference"

    def test_different_use_cases_produce_different_explanations(self, explainer):
        """Test that different use cases generate contextually different explanations."""
        explanation_conversational = explainer.generate_explanation(
            use_case='conversational_knowledge',
            recommendations=SAMPLE_RECOMMENDATIONS
        )

        explanation_technical = explainer.generate_explanation(
            use_case='technical_developer',
            recommendations=SAMPLE_RECOMMENDATIONS
        )

        # The explanations should be different (not identical)
        assert explanation_conversational != explanation_technical, \
            "Different use cases should produce different explanations"

        # Conversational might mention chat/conversation/assistant
        conversational_keywords = ['chat', 'conversation', 'assistant', 'dialogue', 'interact']
        has_conversational = any(kw in explanation_conversational.lower() for kw in conversational_keywords)

        # Technical might mention code/development/programming
        technical_keywords = ['code', 'develop', 'program', 'technical', 'engineer', 'software']
        has_technical = any(kw in explanation_technical.lower() for kw in technical_keywords)

        # At least one should match its context
        assert has_conversational or has_technical, \
            "Explanations should include use-case-specific terminology"


class TestRecommendationExplainerPromptProcessing:
    """Test that the prompt is built and processed correctly."""

    @pytest.fixture
    def explainer(self):
        """Create an explainer instance for testing."""
        return RecommendationExplainer()

    def test_prompt_includes_all_recommendations(self, explainer):
        """Test that the internal prompt includes all 3 recommendations."""
        prompt = explainer._build_prompt(
            use_case='productivity_information',
            recommendations=SAMPLE_RECOMMENDATIONS,
            model_type='no_preference'
        )

        # Check that all model names appear in the prompt
        for rec in SAMPLE_RECOMMENDATIONS:
            assert rec['model'] in prompt, f"Model {rec['model']} should be in prompt"
            assert rec['organization'] in prompt, f"Organization {rec['organization']} should be in prompt"

    def test_prompt_formats_use_case_correctly(self, explainer):
        """Test that use case is formatted properly in the prompt."""
        prompt = explainer._build_prompt(
            use_case='advanced_automation',
            recommendations=SAMPLE_RECOMMENDATIONS
        )

        # Use case should be formatted (underscores replaced with spaces, title case)
        assert 'Advanced Automation' in prompt, "Use case should be formatted in title case"

    def test_fallback_explanation_works(self, explainer):
        """Test that fallback explanation is provided when API fails."""
        fallback = explainer._get_fallback_explanation(
            use_case='conversational_knowledge',
            recommendations=SAMPLE_RECOMMENDATIONS
        )

        assert isinstance(fallback, str), "Fallback should be a string"
        assert len(fallback) > 100, "Fallback should be substantial"
        assert 'LMSYS' in fallback or 'Arena' in fallback, \
            "Fallback should mention the leaderboard source"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v'])
