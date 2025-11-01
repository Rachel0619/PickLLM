# PickLLM User Feedback Outputs

This directory stores user feedback on LLM recommendations to help improve the quality and relevance of PickLLM's recommendations.

## Directory Structure

```
outputs/
├── thumbs_up/       # Positive feedback - helpful recommendations
├── thumbs_down/     # Negative feedback - unhelpful recommendations
└── README.md        # This file
```

## Feedback Data Format

Each feedback file is a JSON document with the following structure:

```json
{
  "type": "up" | "down",
  "comment": "Optional user comment (required for thumbs down)",
  "timestamp": "ISO 8601 timestamp",
  "data": {
    "use_case": "User's selected use case",
    "visual_ai_type": "Visual AI subcategory (if applicable)",
    "recommendations": [
      {
        "rank": 1,
        "model": "Model name",
        "arena_score": 1234,
        "votes": 12345,
        "organization": "Organization name",
        "license": "License type",
        "url": "Model URL",
        "ci": "Confidence interval",
        "logo_url": "Logo path",
        "knowledge_cutoff": "Date",
        "pricing": "Pricing info"
      }
    ],
    "explanation": "AI-generated explanation text",
    "user_data": {
      "use_case": "Selected use case",
      "visual_ai_type": "Visual AI type",
      "model_type": "Model preference",
      "priority": "User priority (cost vs performance)"
    }
  }
}
```

## Example Feedback Files

### Thumbs Up (Positive Feedback)

**Example 1**: [feedback_20250101_143022.json](thumbs_up/feedback_20250101_143022.json)
- **Use Case**: Technical/Developer Tools
- **Why Positive**: User found recommendations relevant for code generation and debugging
- **Models Recommended**: GPT-4o, Claude-3.5-Sonnet, Gemini-2.0-Flash-Thinking
- **Key Insight**: Users appreciate detailed technical explanations and balanced cost/performance recommendations

**Example 2**: [feedback_20250101_160512.json](thumbs_up/feedback_20250101_160512.json)
- **Use Case**: Visual AI - Image Generation
- **Why Positive**: User satisfied with variety of options (proprietary + open-source)
- **Models Recommended**: DALL-E 3, Midjourney v6, Stable Diffusion XL
- **Key Insight**: Users value having both high-end and cost-effective options explained clearly

### Thumbs Down (Negative Feedback)

**Example 1**: [feedback_20250101_091534.json](thumbs_down/feedback_20250101_091534.json)
- **Use Case**: Conversational & Knowledge Agents
- **Issue**: User wanted open-source models but got all proprietary recommendations
- **Comment**: "The recommendations are all expensive proprietary models. I specifically wanted open-source options for my startup, but the results don't reflect that preference."
- **Key Insight**: Need to better respect model_type preference filtering

**Example 2**: [feedback_20250101_134745.json](thumbs_down/feedback_20250101_134745.json)
- **Use Case**: Creative & Content Generation
- **Issue**: AI explanation was too generic and lacked specific examples
- **Comment**: "The AI explanation is too generic and doesn't really explain WHY these specific models are good for creative writing. It just lists features without concrete examples of how they help with storytelling or creative content."
- **Key Insight**: Explanations need more concrete, use-case-specific examples rather than generic feature lists

## Analysis & Insights

### Common Positive Feedback Themes
1. ✅ Clear explanations with specific use-case relevance
2. ✅ Good balance of cost and performance options
3. ✅ Accurate reflection of user preferences (open-source vs proprietary)
4. ✅ Detailed pricing information included

### Common Negative Feedback Themes
1. ❌ User preferences (model type, cost priority) not properly reflected
2. ❌ Generic explanations that don't provide use-case-specific insights
3. ❌ Lack of concrete examples in AI-generated explanations
4. ❌ Missing information about why specific models excel for the chosen use case

## How Feedback is Used

### Immediate Actions
- Review negative feedback weekly to identify patterns
- Test recommendation engine with problematic inputs
- Refine AI explanation prompts based on user comments

### Long-term Improvements
- Adjust ranking algorithm weights based on user satisfaction
- Improve AI explanation prompt engineering for more specific, relevant content
- Add more filtering options based on common user requests
- Build automated testing using feedback examples

## Privacy & Data Handling

- **No Personal Information**: Feedback does not include user emails, names, or identifying information
- **Anonymous**: All feedback is anonymous and used solely for product improvement
- **Local Storage**: Feedback is stored locally in this repository (not sent to external services)
- **Opt-in**: Users must click thumbs up/down to provide feedback

## Adding New Feedback

Feedback is automatically saved when users click the thumbs up/down buttons on the results page. Files are named with timestamps:

```
feedback_YYYYMMDD_HHMMSS.json
```

## Gitignore Recommendation

Consider adding to `.gitignore` if you don't want to commit user feedback:

```
outputs/thumbs_up/*.json
outputs/thumbs_down/*.json
!outputs/thumbs_up/feedback_*.json  # Keep example files
!outputs/thumbs_down/feedback_*.json
```

## Contributing

When analyzing feedback:
1. Look for recurring patterns in negative feedback
2. Identify what makes positive recommendations successful
3. Test edge cases mentioned in comments
4. Update recommendation engine or prompts accordingly
5. Document changes and re-test with similar inputs
