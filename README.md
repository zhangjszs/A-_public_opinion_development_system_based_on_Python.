# Weibo Public Opinion Analysis System

Based on Python, this system analyzes Weibo public opinion and provides visualization.

## Project Structure

```
root/
├── src/                    # Source Code
│   ├── app.py              # Application Entry (Flask App)
│   ├── config/             # Configuration Settings
│   ├── model/              # Sentiment Analysis Models & Training
│   ├── spider/             # Weibo Crawler
│   ├── utils/              # Utility Functions
│   ├── views/              # Web Route Controllers
│   ├── services/           # Business Logic
│   ├── static/             # Static Assets (JS, CSS, Images)
│   └── templates/          # HTML Templates
├── config/                 # (Optional) External configs
├── docs/                   # Documentation
├── scripts/                # Operations Scripts
│   ├── check_env.py        # Environment Check Script
│   └── deploy.py           # Deployment Helper
├── tests/                  # Test Suites
├── run.py                  # Main Entry Point
├── requirements.txt        # Python Dependencies
└── .env                    # Environment Variables (Secrets)
```

## Quick Start

1.  **Clone the repository**
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    -   Copy `.env.example` to `.env` (if available) or create a `.env` file.
    -   Set `WEIBO_COOKIE` and `user-agent` in `.env` if needed for the crawler.
4.  **Run the Application**:
    ```bash
    python run.py
    ```
    Access at `http://127.0.0.1:5000`

## Deployment

### Prerequisites
-   Python 3.8+
-   MySQL (Optional, depending on configuration)

### Steps
1.  Run environment check:
    ```bash
    python scripts/check_env.py
    ```
2.  Deploy (install deps, check db, etc):
    ```bash
    python scripts/deploy.py
    ```
3.  Start with Gunicorn (Production):
    ```bash
    gunicorn -w 4 -b 0.0.0.0:5000 run:app
    ```

## Scripts

-   `scripts/check_env.py`: Checks if required Python version and packages are installed.
-   `scripts/deploy.py`: Automates simple deployment tasks.

## Documentation
See `docs/` for detailed design documents.
