from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from recommendation_engine import RecommendationEngine
from recommendation_explainer import RecommendationExplainer
from use_case_helper import UseCaseHelper

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize recommendation engine and explainer
recommendation_engine = RecommendationEngine()
recommendation_explainer = RecommendationExplainer()
use_case_helper = UseCaseHelper()

# Initialize RAG chatbot (lazy initialization on first request)
rag_chatbot = None
chatbot_initialized = False
chatbot_error = None

def get_chatbot():
    """Get or initialize the RAG chatbot"""
    global rag_chatbot, chatbot_initialized, chatbot_error

    if chatbot_initialized:
        return rag_chatbot

    try:
        print("🤖 Initializing RAG chatbot...")
        from rag import RAGChatbot
        rag_chatbot = RAGChatbot()
        rag_chatbot.initialize()
        chatbot_initialized = True
        print("✅ RAG chatbot initialized successfully")
        return rag_chatbot
    except Exception as e:
        chatbot_error = str(e)
        chatbot_initialized = True  # Mark as initialized to avoid retrying
        print(f"❌ Failed to initialize chatbot: {e}")
        return None

# Custom Jinja filter for simple markdown rendering
import re
@app.template_filter('simple_markdown')
def simple_markdown(text):
    """Convert simple markdown to HTML (bold and bullets only)."""
    if not text:
        return text
    # Convert **text** to <strong>text</strong>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Convert bullet points (- or *) to HTML list items
    lines = text.split('\n')
    in_list = False
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result.append('<ul class="mb-3">')
                in_list = True
            result.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            if stripped:  # Only add non-empty lines
                result.append(f'<p>{line}</p>')
    if in_list:
        result.append('</ul>')
    return ''.join(result)

@app.route('/')
def landing():
    """Landing page with PickLLM introduction and CTA"""
    return render_template('landing.html')

@app.route('/questionnaire')
def questionnaire():
    """Questionnaire page for user requirements"""
    return render_template('questionnaire.html')

@app.route('/submit-questionnaire', methods=['POST'])
def submit_questionnaire():
    """Process questionnaire responses and generate recommendations"""
    data = request.get_json() if request.is_json else request.form.to_dict()

    # Get top 3 recommendations based on user's use case
    use_case = data.get('use_case')
    visual_ai_type = data.get('visual_ai_type')
    model_type = data.get('model_type')

    recommendations = recommendation_engine.get_top_recommendations(
        use_case=use_case,
        visual_ai_type=visual_ai_type,
        model_type=model_type,
        top_n=3
    )

    # Generate AI explanation for the recommendations
    try:
        explanation = recommendation_explainer.generate_explanation(
            use_case=use_case,
            recommendations=recommendations,
            visual_ai_type=visual_ai_type,
            model_type=model_type
        )
        print(f"✅ Generated explanation: {len(explanation) if explanation else 0} characters")
    except Exception as e:
        print(f"❌ Error generating explanation: {e}")
        explanation = ""

    # Render results page with recommendations
    return render_template('results.html',
                         recommendations=recommendations,
                         use_case=use_case,
                         visual_ai_type=visual_ai_type,
                         explanation=explanation,
                         user_data=data)

@app.route('/results')
def results():
    """Display LLM recommendations (direct access fallback)"""
    return render_template('results.html', recommendations=[])

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PickLLM"})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot endpoint for answering user questions"""
    try:
        data = request.get_json()
        query = data.get('message', '').strip()

        if not query:
            return jsonify({"error": "Message is required"}), 400

        # Get chatbot and generate response
        chatbot = get_chatbot()

        if chatbot is None:
            return jsonify({
                "response": "Sorry, the chatbot is currently unavailable. Please try again later or contact support.",
                "status": "success"
            })

        response = chatbot.chat(query)

        return jsonify({
            "response": response,
            "status": "success"
        })
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "response": "Sorry, I encountered an error processing your question. Please try again.",
            "status": "success"
        })

@app.route('/api/suggest-use-case', methods=['POST'])
def suggest_use_case():
    """Endpoint to suggest use case category based on user description"""
    try:
        data = request.get_json()
        description = data.get('description', '').strip()

        if not description:
            return jsonify({"error": "Description is required"}), 400

        # Get use case suggestion from AI
        suggested_category = use_case_helper.use_case_classification(description)

        if not suggested_category:
            return jsonify({
                "error": "Failed to classify use case. Please try again.",
                "status": "error"
            }), 500

        # Map category to display label
        category_labels = {
            'conversational_knowledge': 'Conversational & Knowledge Agents',
            'productivity_information': 'Productivity & Information Handling',
            'creative_content': 'Creative & Content Generation',
            'technical_developer': 'Technical & Developer Tools',
            'advanced_automation': 'Advanced Automation',
            'visual_ai': 'Visual AI'
        }

        return jsonify({
            "category": suggested_category,
            "label": category_labels.get(suggested_category, suggested_category),
            "status": "success"
        })

    except Exception as e:
        print(f"❌ Error in suggest-use-case endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "An error occurred while processing your request.",
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
