"""
Tests for UseCaseHelper LLM component.

These tests verify that the LLM-powered use case classifier:
1. Returns valid category classifications
2. Classifies descriptions to appropriate categories
3. Produces consistent results for similar inputs
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv()

from use_case_helper import UseCaseHelper


# Valid categories that the classifier should return
VALID_CATEGORIES = [
    'conversational_knowledge',
    'productivity_information',
    'creative_content',
    'technical_developer',
    'advanced_automation',
    'visual_ai'
]


class TestUseCaseClassificationOutput:
    """Test that LLM output matches expected format and valid categories."""

    @pytest.fixture
    def helper(self):
        """Create a UseCaseHelper instance for testing."""
        return UseCaseHelper()

    def test_classification_returns_valid_category(self, helper):
        """Test that classification returns one of the valid categories."""
        description = "I need a chatbot to answer customer questions about our products"

        result = helper.use_case_classification(description)

        assert result is not None, "Classification should not return None"
        assert isinstance(result, str), "Classification should return a string"
        assert result in VALID_CATEGORIES, \
            f"Classification '{result}' should be one of {VALID_CATEGORIES}"

    def test_classification_output_is_clean(self, helper):
        """Test that classification output doesn't contain special tokens or extra text."""
        description = "Help me write blog posts and marketing content"

        result = helper.use_case_classification(description)

        # Should not contain special tokens
        unwanted_tokens = ['<|', '|>', '</', 'EOF', '```', '\n\n']
        for token in unwanted_tokens:
            assert token not in result, f"Result should not contain special token '{token}'"

        # Should be a single category (no extra explanation)
        assert len(result.split()) == 1, \
            f"Result should be a single category, got: '{result}'"

    def test_technical_description_classified_correctly(self, helper):
        """Test that technical/developer descriptions are classified appropriately."""
        descriptions = [
            "I need help debugging Python code and generating unit tests",
            "Looking for a tool to help with code reviews and refactoring",
            "Want an AI to help me write SQL queries and optimize database performance"
        ]

        for desc in descriptions:
            result = helper.use_case_classification(desc)

            # Should classify as technical_developer
            assert result == 'technical_developer', \
                f"Technical description '{desc}' should be classified as 'technical_developer', got '{result}'"

    def test_visual_ai_description_classified_correctly(self, helper):
        """Test that visual AI descriptions are classified appropriately."""
        descriptions = [
            "I want to generate product images for my e-commerce site",
            "Need to analyze images and extract text from photos",
            "Looking to edit and enhance photos automatically"
        ]

        for desc in descriptions:
            result = helper.use_case_classification(desc)

            # Should classify as visual_ai
            assert result == 'visual_ai', \
                f"Visual description '{desc}' should be classified as 'visual_ai', got '{result}'"


class TestUseCaseClassificationConsistency:
    """Test that similar inputs produce consistent classifications."""

    @pytest.fixture
    def helper(self):
        """Create a UseCaseHelper instance for testing."""
        return UseCaseHelper()

    def test_similar_descriptions_same_category(self, helper):
        """Test that semantically similar descriptions get the same classification."""
        # Two different ways of describing a chatbot use case
        desc1 = "Build a conversational AI assistant for customer support"
        desc2 = "Create a virtual agent that can answer user questions"

        result1 = helper.use_case_classification(desc1)
        result2 = helper.use_case_classification(desc2)

        assert result1 == result2, \
            f"Similar descriptions should get same classification. Got '{result1}' and '{result2}'"
        assert result1 == 'conversational_knowledge', \
            "Both should be classified as conversational_knowledge"

    def test_creative_vs_productivity_distinction(self, helper):
        """Test that the classifier can distinguish between creative and productivity tasks."""
        creative_desc = "Write creative fiction stories and poetry"
        productivity_desc = "Summarize long documents and extract key information"

        creative_result = helper.use_case_classification(creative_desc)
        productivity_result = helper.use_case_classification(productivity_desc)

        assert creative_result == 'creative_content', \
            f"Creative description should be 'creative_content', got '{creative_result}'"
        assert productivity_result == 'productivity_information', \
            f"Productivity description should be 'productivity_information', got '{productivity_result}'"
        assert creative_result != productivity_result, \
            "Creative and productivity tasks should be classified differently"

    def test_automation_description_classified_correctly(self, helper):
        """Test that complex automation descriptions are identified."""
        descriptions = [
            "Build a multi-step workflow that processes data from APIs and generates reports",
            "Create an agent that orchestrates multiple tasks and integrates with various services",
            "Develop an automated system that chains together multiple AI operations"
        ]

        for desc in descriptions:
            result = helper.use_case_classification(desc)

            assert result == 'advanced_automation', \
                f"Automation description should be 'advanced_automation', got '{result}' for: {desc}"


class TestUseCasePromptBuilding:
    """Test that the prompt is constructed correctly."""

    @pytest.fixture
    def helper(self):
        """Create a UseCaseHelper instance for testing."""
        return UseCaseHelper()

    def test_prompt_includes_user_description(self, helper):
        """Test that the prompt includes the user's description."""
        user_desc = "I need help with data analysis and visualization"

        prompt = helper._build_prompt(user_desc)

        assert user_desc in prompt, "Prompt should include the user's description"
        assert 'Description:' in prompt, "Prompt should have a Description label"

    def test_prompt_includes_all_categories(self, helper):
        """Test that the prompt lists all possible categories."""
        prompt = helper._build_prompt("test description")

        # All categories should be mentioned in the prompt
        for category in VALID_CATEGORIES:
            assert category in prompt, f"Prompt should include category '{category}'"

    def test_prompt_has_clear_instructions(self, helper):
        """Test that the prompt has clear classification instructions."""
        prompt = helper._build_prompt("test description")

        # Should have instructions to return only the category name
        instruction_keywords = ['return', 'only', 'category', 'one']
        matches = sum(1 for keyword in instruction_keywords if keyword.lower() in prompt.lower())

        assert matches >= 3, "Prompt should have clear instructions to return only the category"

    def test_classification_with_empty_description_handled(self, helper):
        """Test that empty or very short descriptions are handled."""
        result = helper.use_case_classification("")

        # Should still return a valid category or None
        assert result is None or result in VALID_CATEGORIES, \
            "Empty description should return None or valid category"

    def test_classification_with_ambiguous_description(self, helper):
        """Test that ambiguous descriptions still return a valid category."""
        ambiguous_desc = "I need an AI tool"  # Very vague

        result = helper.use_case_classification(ambiguous_desc)

        # Should still return something valid (even if it's a best guess)
        assert result is None or result in VALID_CATEGORIES, \
            f"Ambiguous description should return valid category, got '{result}'"


class TestUseCaseEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def helper(self):
        """Create a UseCaseHelper instance for testing."""
        return UseCaseHelper()

    def test_mixed_use_case_description(self, helper):
        """Test descriptions that could fit multiple categories."""
        # This could be both creative AND productivity
        mixed_desc = "Help me write professional emails with creative language"

        result = helper.use_case_classification(mixed_desc)

        # Should pick one valid category
        assert result in VALID_CATEGORIES, \
            f"Mixed description should still return valid category, got '{result}'"
        # Likely productivity or creative
        assert result in ['productivity_information', 'creative_content'], \
            f"Mixed email description should be productivity or creative, got '{result}'"

    def test_very_long_description(self, helper):
        """Test that very long descriptions are handled properly."""
        long_desc = " ".join([
            "I need an AI system that can help with customer service automation.",
            "It should be able to understand customer inquiries, provide helpful responses,",
            "escalate complex issues to human agents, and maintain conversation context.",
            "The system needs to handle multiple languages and integrate with our CRM."
        ])

        result = helper.use_case_classification(long_desc)

        assert result in VALID_CATEGORIES, \
            "Long description should still return valid category"
        assert result in ['conversational_knowledge', 'advanced_automation'], \
            f"Complex customer service system should be conversational or automation, got '{result}'"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v'])
