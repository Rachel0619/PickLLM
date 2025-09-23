from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

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
    """Process questionnaire responses and redirect to results"""
    data = request.get_json() if request.is_json else request.form.to_dict()

    # TODO: Process questionnaire data and generate recommendations
    # For now, just pass the data to results page
    return redirect(url_for('results', **data))

@app.route('/results')
def results():
    """Display LLM recommendations"""
    # TODO: Implement recommendation logic
    # For now, show placeholder results
    return render_template('results.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PickLLM"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)