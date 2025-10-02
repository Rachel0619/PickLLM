from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from recommendation_engine import RecommendationEngine

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

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

    # Render results page with recommendations
    return render_template('results.html',
                         recommendations=recommendations,
                         use_case=use_case,
                         visual_ai_type=visual_ai_type,
                         user_data=data)

@app.route('/results')
def results():
    """Display LLM recommendations (direct access fallback)"""
    return render_template('results.html', recommendations=[])

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PickLLM"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
