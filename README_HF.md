---
title: PickLLM
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 🤖 PickLLM

Find the Right Large Language Model, Fast.

Stop juggling between different leaderboards. Get personalized LLM recommendations based on your specific needs for model capability, cost and latency.

## ✨ Features

- 🎯 **Smart Questionnaire** - Answer a few questions about your needs
- 🤖 **AI-Powered Matching** - Get recommendations from LMSYS Chatbot Arena leaderboard
- 🏆 **Top 3 Recommendations** - See the best models for your use case with detailed explanations

## 👤 About

Built by Rachel Li
- [LinkedIn](https://www.linkedin.com/in/runtian-li/)
- [X (Twitter)](https://x.com/RachelLi56161)

## 📊 Data Source

This application uses data from the [LMSYS Chatbot Arena Leaderboard](https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard).

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Jinja2 Templates + Bootstrap 5
- **AI Explanations:** OpenRouter API (GLM-4.5-Air)
- **Deployment:** Docker on Hugging Face Spaces

## 🚀 How It Works

1. **Landing Page** - Start with our friendly interface
2. **Questionnaire** - Answer questions about your use case
3. **Analysis** - Our backend queries the LLM database with your requirements
4. **Recommendations** - Get top 3 LLM suggestions with AI-generated explanations
5. **Compare & Choose** - Review options and select your perfect match
