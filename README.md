# VentureAI - AI-Powered Startup Validation Platform

A comprehensive startup validation platform that uses AI to analyze business ideas using proven frameworks like Lean Canvas, TAM-SAM-SOM, and Y Combinator criteria.

## 🚀 Features

- **AI-Powered Analysis**: Uses OpenRouter API with Claude 3.5 Sonnet for comprehensive startup analysis
- **Proven Frameworks**: Implements Lean Canvas, TAM-SAM-SOM, and YC criteria assessment
- **Founder-Market Fit**: Analyzes founder background alignment with market opportunity
- **Interactive UI**: Modern, responsive design with TailwindCSS and Alpine.js
- **Real-time Processing**: Live progress tracking during AI analysis
- **Downloadable Reports**: Export validation reports for offline reference


## 📊 API Endpoints

### Core Endpoints

- `GET /` - API status and information
- `GET /health` - Health check endpoint
- `POST /validate` - Submit startup idea for validation
- `GET /report/{report_id}` - Retrieve validation report
- `GET /reports` - List all reports (admin)


## 📞 Support

For support and questions:
- Contact: shubhanshgupta18@gmail.com

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release
- AI-powered startup validation
- TAM-SAM-SOM analysis
- YC criteria assessment
- Founder-market fit analysis
- Modern responsive UI
---

**Built with ❤️ for entrepreneurs and startup founders**

<!-- To setup project follow the following Steps-->

<!-- create a virtual environment venv using the following commands -->
pip install virtualenv
python3 -m venv <myenvname>

<!-- to activate the virtual environment run the following command -->
.\<myenvname>\Scripts\activate

<!-- After virtual environment is active install all the dependencies from requirements.txt -->
pip install -r requirements.txt

<!-- command to start application -->
uvicorn app.main:app --reload

<!-- command to execute migration -->
alembic -c alembic.ini revision --autogenerate -m "YOUR MESSAGE"
alembic -c alembic.ini upgrade head

<!-- command to drop all tables using alembic for fresh data -->
alembic downgrade base

<!-- command to update requirements.txt with required versions of packages -->
pip freeze > requirements.txt