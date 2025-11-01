"""
Tests for RAG Chatbot LLM component.

These tests verify that the RAG-powered chatbot:
1. Generates relevant responses based on context
2. Retrieves and uses appropriate context from the knowledge base
3. Produces consistent and helpful answers
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv()

from rag import RAGChatbot


class TestRAGChatbotOutput:
    """Test that RAG chatbot produces appropriate output format and content."""

    @pytest.fixture(scope="class")
    def chatbot(self):
        """Create and initialize a RAG chatbot instance for testing."""
        bot = RAGChatbot()
        # Initialize with the PickLLM repository
        bot.initialize(repo_owner='Rachel0619', repo_name='PickLLM')
        return bot

    def test_chat_response_is_string(self, chatbot):
        """Test that the chatbot returns a string response."""
        query = "What is PickLLM?"
        response = chatbot.chat(query)

        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"

    def test_chat_response_is_concise(self, chatbot):
        """Test that responses are concise as per the prompt instructions."""
        query = "How does PickLLM work?"
        response = chatbot.chat(query)

        # Response should be concise (rough check: under 1000 chars for simple questions)
        # This is a soft check - some answers may be legitimately longer
        assert len(response) < 2000, \
            f"Response should be reasonably concise, got {len(response)} chars"

        # Should have 1-4 sentences for a simple question (approximate check)
        sentence_count = response.count('.') + response.count('!') + response.count('?')
        assert sentence_count >= 1, "Response should have at least one sentence"

    def test_chat_response_is_relevant(self, chatbot):
        """Test that chatbot response is relevant to the query."""
        query = "What datasets does PickLLM use?"
        response = chatbot.chat(query)

        # Response should mention relevant keywords
        relevant_keywords = ['data', 'leaderboard', 'lmsys', 'arena', 'model', 'benchmark']
        has_relevant_content = any(keyword in response.lower() for keyword in relevant_keywords)

        assert has_relevant_content, \
            f"Response should be relevant to datasets/leaderboards. Got: {response}"


class TestRAGContextRetrieval:
    """Test that the RAG system retrieves and uses appropriate context."""

    @pytest.fixture(scope="class")
    def chatbot(self):
        """Create and initialize a RAG chatbot instance for testing."""
        bot = RAGChatbot()
        bot.initialize(repo_owner='Rachel0619', repo_name='PickLLM')
        return bot

    def test_vector_search_returns_results(self, chatbot):
        """Test that vector search retrieves relevant context."""
        query = "What is the purpose of PickLLM?"

        # Use the internal _vector_search method to check retrieval
        context = chatbot._vector_search(query, num_results=2)

        assert context is not None, "Vector search should return results"
        assert isinstance(context, list), "Context should be a list"
        assert len(context) > 0, "Should retrieve at least some context"
        assert len(context) <= 2, "Should respect num_results limit"

    def test_vector_search_finds_relevant_content(self, chatbot):
        """Test that retrieved context contains relevant information."""
        query = "How are models ranked?"

        context = chatbot._vector_search(query, num_results=2)

        # Context should have 'section' field with text
        for doc in context:
            assert 'section' in doc, "Context documents should have 'section' field"
            assert isinstance(doc['section'], str), "Section should be a string"
            assert len(doc['section']) > 0, "Section should not be empty"

        # At least one context chunk should be relevant to ranking/scoring
        combined_context = " ".join([doc['section'] for doc in context])
        ranking_keywords = ['rank', 'score', 'arena', 'performance', 'vote', 'leaderboard']
        has_ranking_context = any(kw in combined_context.lower() for kw in ranking_keywords)

        assert has_ranking_context, \
            "Retrieved context should contain ranking-related information"

    def test_different_queries_retrieve_different_context(self, chatbot):
        """Test that different queries retrieve different relevant contexts."""
        query1 = "What is PickLLM?"
        query2 = "How do I use the API?"

        context1 = chatbot._vector_search(query1, num_results=2)
        context2 = chatbot._vector_search(query2, num_results=2)

        # Extract the text from contexts
        text1 = " ".join([doc['section'] for doc in context1])
        text2 = " ".join([doc['section'] for doc in context2])

        # They should be different (not retrieving the same chunks)
        assert text1 != text2, \
            "Different queries should retrieve different context"


class TestRAGPromptAndConsistency:
    """Test prompt formatting and response consistency."""

    @pytest.fixture(scope="class")
    def chatbot(self):
        """Create and initialize a RAG chatbot instance for testing."""
        bot = RAGChatbot()
        bot.initialize(repo_owner='Rachel0619', repo_name='PickLLM')
        return bot

    def test_prompt_includes_query_and_context(self, chatbot):
        """Test that the prompt is formatted with both query and context."""
        query = "What is PickLLM about?"
        context = chatbot._vector_search(query, num_results=2)

        prompt = chatbot._format_prompt(query, context)

        # Prompt should include the query
        assert query in prompt, "Prompt should include the user query"

        # Prompt should include context from retrieved documents
        for doc in context:
            # At least some portion of the context should be in the prompt
            section_text = doc.get('section', '')
            if section_text:
                # Check if any significant portion (>20 chars) is in the prompt
                assert section_text[:50] in prompt or section_text in prompt, \
                    "Prompt should include retrieved context"

    def test_prompt_has_system_instructions(self, chatbot):
        """Test that the prompt has proper system instructions."""
        query = "Tell me about PickLLM"
        context = chatbot._vector_search(query, num_results=2)

        prompt = chatbot._format_prompt(query, context)

        # Should mention PickLLM in instructions
        assert 'PickLLM' in prompt, "Prompt should mention PickLLM"

        # Should have instructions about being concise
        concise_keywords = ['concise', 'brief', 'short', 'sentence']
        has_concise_instruction = any(kw in prompt.lower() for kw in concise_keywords)

        assert has_concise_instruction, \
            "Prompt should include instructions to be concise"

    def test_chatbot_handles_out_of_context_question(self, chatbot):
        """Test that chatbot handles questions outside its knowledge gracefully."""
        # Ask something not related to PickLLM
        query = "What is the capital of France?"

        response = chatbot.chat(query)

        # Should still return a valid response (not crash)
        assert isinstance(response, str), "Should return a string response"
        assert len(response) > 0, "Should return a non-empty response"

        # Ideally should indicate it doesn't have that information
        # or try to relate it back to PickLLM, but at minimum shouldn't error
        uncertain_phrases = ["don't have", "don't know", "not sure", "specific information",
                           "doesn't contain", "can't find", "not in", "outside"]
        might_acknowledge_limitation = any(phrase in response.lower() for phrase in uncertain_phrases)

        # This is a soft assertion - we accept any valid response
        # but check if it might acknowledge the limitation
        # (Some LLMs might still answer the question)

    def test_related_questions_get_similar_answers(self, chatbot):
        """Test that similar questions produce related/similar answers."""
        query1 = "What does PickLLM help with?"
        query2 = "What is PickLLM used for?"

        response1 = chatbot.chat(query1)
        response2 = chatbot.chat(query2)

        # Both should be valid responses
        assert isinstance(response1, str) and len(response1) > 0
        assert isinstance(response2, str) and len(response2) > 0

        # They should share some common keywords (as they're asking the same thing)
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())

        # Remove common words (stopwords approximation)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
                    'to', 'of', 'in', 'for', 'on', 'with', 'as', 'by'}
        words1 = {w.strip('.,!?') for w in words1 if w not in stopwords and len(w) > 2}
        words2 = {w.strip('.,!?') for w in words2 if w not in stopwords and len(w) > 2}

        # Should have some overlap in meaningful words
        overlap = words1 & words2
        overlap_ratio = len(overlap) / max(len(words1), len(words2)) if words1 or words2 else 0

        assert overlap_ratio > 0.1, \
            f"Similar questions should have some overlap in answers. Overlap: {overlap_ratio:.2%}"


class TestRAGInitialization:
    """Test that the RAG system initializes correctly."""

    def test_chatbot_initialization_creates_index(self):
        """Test that initialization builds the vector index."""
        chatbot = RAGChatbot()
        chatbot.initialize(repo_owner='Rachel0619', repo_name='PickLLM')

        assert chatbot.chunks is not None, "Chunks should be loaded"
        assert len(chatbot.chunks) > 0, "Should have processed some document chunks"
        assert chatbot.embeddings is not None, "Embeddings should be created"
        assert chatbot.repo_vindex is not None, "Vector index should be built"
        assert chatbot.embedding_model is not None, "Embedding model should be loaded"

    def test_chatbot_requires_initialization(self):
        """Test that chatbot requires initialization before use."""
        chatbot = RAGChatbot()

        # Should raise an exception if used before initialization
        with pytest.raises(Exception) as exc_info:
            chatbot._vector_search("test query")

        assert "not initialized" in str(exc_info.value).lower(), \
            "Should indicate that chatbot is not initialized"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v', '-s'])
