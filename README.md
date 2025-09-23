# 🤖 PickLLM

![PickLLM Hero Image](./images/cover.png)

## 📝 What is PickLLM?

PickLLM helps users find the right large language model (LLM) for their specific use case. Instead of drowning in technical benchmarks and scattered metrics, PickLLM provides actionable recommendations tailored to your needs.

### 🎯 Why PickLLM?

**The Problem:**

- 🤯 Too many LLMs with varying size, cost, latency, and licensing
- 📊 Technical evaluation metrics that are scattered and hard to interpret
- ⚖️ Users must switch between different leaderboards when facing trade-offs among cost, latency, and intelligence
- 🔍 Users need actionable recommendations, not raw benchmark scores

**Our Solution:**

- 📝 Simple questionnaire to understand your use case
- 🧠 Smart recommendation engine powered by LLM database
- 🏆 Top 3 LLM recommendations with clear reasoning
- ⚖️ Compare models side-by-side to make the best choice

## 🚀 How It Works

```text
Landing Page → Questionnaire → Backend Analysis → Results → Your Perfect LLM
```

1. **Welcome** - Start with our friendly landing page
2. **Questionnaire** - Answer questions about your use case (multiple choice + optional description)
3. **Analysis** - Our backend queries the LLM database with your requirements
4. **Recommendations** - Get top 3 LLM suggestions with detailed reasoning
5. **Compare & Choose** - Review options and select your perfect match

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Jinja2 Templates + Bootstrap 5
- **Styling:** Custom CSS + Bootstrap
- **Package Management:** uv
- **Deployment:** Vercel, AWS/GCP/Azure

## ⚡ Quick Start

### Prerequisites

- Python 3.8+
- uv (for dependency management)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/PickLLM.git
cd PickLLM

# Install dependencies with uv
uv add flask python-dotenv

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your configuration if needed
```

### Running the Application

```bash
# Start the Flask development server
uv run python app.py

# Open your browser to http://localhost:5555
```

## 🎯 Features

- 📋 **Smart Questionnaire** - Intuitive questions to understand your needs
- 🔍 **LLM Database** - Comprehensive database of models with metrics
- 🏆 **Top 3 Recommendations** - Curated suggestions with reasoning
- ⚖️ **Side-by-Side Comparison** - Compare models on key metrics
- 💡 **Actionable Insights** - Clear explanations, not just numbers
- 🚀 **Fast & Simple** - Get recommendations in minutes, not hours
- 🎯 **No Signup Required** - Jump straight to finding your perfect LLM

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🗺️ Roadmap

- [x] **Phase 1:** Core questionnaire and recommendation engine
- [ ] **Phase 2:** Advanced filtering and comparison features
- [ ] **Phase 3:** LLM database integration with real-time data
- [ ] **Phase 4:** API access for developers
- [ ] **Phase 5:** Mobile app and advanced analytics