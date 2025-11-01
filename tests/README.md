# PickLLM LLM Testing Suite

This directory contains comprehensive tests for PickLLM's AI/LLM components to ensure they behave correctly and produce reliable outputs.

## Test Files

### 1. `test_recommendation_explainer.py`
Tests for the LLM-powered recommendation explanation generator.

**Test Categories:**
- **Output Structure**: Verifies explanations are non-empty, well-structured with paragraphs, and mention model names
- **Consistency**: Ensures visual AI context is included, preferences are reflected, and different use cases produce appropriate explanations
- **Prompt Processing**: Validates prompt construction includes all recommendations and formats use cases correctly

**Key Tests:**
- ✅ Explanation is a substantial non-empty string (>100 chars)
- ✅ Explanation has multiple paragraphs with good structure
- ✅ Recommended model names are mentioned in the output
- ✅ Visual AI terminology appears when appropriate
- ✅ Open-source preference is reflected in explanations
- ✅ Different use cases generate contextually different content

### 2. `test_use_case_helper.py`
Tests for the LLM-powered use case classification system.

**Test Categories:**
- **Output Format**: Ensures classifications return valid categories without special tokens
- **Classification Accuracy**: Verifies technical and visual descriptions are classified correctly
- **Consistency**: Tests that similar descriptions get consistent classifications
- **Edge Cases**: Handles empty, ambiguous, and mixed-category descriptions

**Key Tests:**
- ✅ Returns one of 6 valid categories
- ✅ Output is clean (no special tokens or extra text)
- ✅ Technical descriptions → `technical_developer`
- ✅ Visual AI descriptions → `visual_ai`
- ✅ Similar descriptions get same classification
- ✅ Creative vs productivity tasks are distinguished correctly

### 3. `test_rag.py`
Tests for the RAG (Retrieval-Augmented Generation) chatbot.

**Test Categories:**
- **Output Quality**: Validates responses are strings, concise, and relevant
- **Context Retrieval**: Ensures vector search finds relevant documentation chunks
- **Prompt Formatting**: Verifies prompts include query, context, and system instructions
- **Initialization**: Tests that the RAG system builds indexes correctly

**Key Tests:**
- ✅ Chat response is a non-empty string
- ✅ Responses are concise (per prompt instructions)
- ✅ Responses are relevant to the query
- ✅ Vector search retrieves appropriate context
- ✅ Different queries retrieve different relevant chunks
- ✅ Prompt includes query, context, and conciseness instructions
- ✅ Handles out-of-context questions gracefully
- ✅ Similar questions get related answers

## Running the Tests

### Prerequisites
```bash
# Install test dependencies (using uv)
uv pip install pytest python-frontmatter sentence-transformers tqdm numpy minsearch

# Or using pip
pip install pytest python-frontmatter sentence-transformers tqdm numpy minsearch

# Set up environment variables
# Create .env file with:
OPENROUTER_API_KEY=your_api_key_here
```

### Run All Tests
```bash
# From the project root
pytest tests/ -v

# Run with verbose output
pytest tests/ -v -s
```

### Run Specific Test Files
```bash
# Test recommendation explainer
pytest tests/test_recommendation_explainer.py -v

# Test use case classifier
pytest tests/test_use_case_helper.py -v

# Test RAG chatbot
pytest tests/test_rag.py -v
```

### Run Specific Test Classes
```bash
# Test only output structure tests
pytest tests/test_recommendation_explainer.py::TestRecommendationExplainerOutput -v

# Test only classification accuracy
pytest tests/test_use_case_helper.py::TestUseCaseClassificationOutput -v
```

## Test Structure

Each test file follows this pattern:

1. **Output/Format Tests**: Check if LLM output has the right structure (JSON, specific fields, string format, etc.)
2. **Content/Accuracy Tests**: Verify the output matches expected content and is contextually appropriate
3. **Consistency Tests**: Ensure prompt variations produce consistent and appropriate results
4. **Edge Cases**: Test error handling and unusual inputs

## Important Notes

- **API Costs**: These tests make real API calls to OpenRouter. Run them thoughtfully to manage costs.
- **API Key Required**: Set `OPENROUTER_API_KEY` in your `.env` file
- **Network Required**: Tests require internet connection for API calls and repository downloads (RAG tests)
- **Non-Deterministic**: LLM outputs may vary slightly between runs due to temperature settings
- **Assertion Philosophy**: Tests use lenient assertions that check for semantic correctness rather than exact matches

## What Makes a Good LLM Test?

Based on these examples, good LLM tests should:

1. **Check Structure Over Exact Content**: Verify format, fields, and patterns rather than exact text
2. **Test Semantic Understanding**: Look for keywords, concepts, and relevance rather than word-for-word matches
3. **Validate Consistency**: Similar inputs should produce similar (not identical) outputs
4. **Handle Variability**: Use ranges, thresholds, and keyword presence instead of exact values
5. **Test Error Handling**: Ensure graceful degradation with edge cases
6. **Be Context-Aware**: Verify outputs are appropriate for the input context

## Continuous Integration

To run these tests in CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run LLM Tests
  env:
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
  run: pytest tests/ -v
```

## Extending the Tests

To add new tests:

1. Follow the existing test structure (3 classes per file: Output, Consistency, Edge Cases)
2. Use descriptive test names that explain what's being tested
3. Add docstrings to explain the test's purpose
4. Group related tests in the same class
5. Use fixtures to avoid redundant initialization

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing LLM Applications Best Practices](https://www.anthropic.com/index/testing-llm-applications)
- [OpenRouter API Docs](https://openrouter.ai/docs)
