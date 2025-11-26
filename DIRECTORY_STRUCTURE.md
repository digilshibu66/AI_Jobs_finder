# Directory Structure

```
freelance_mailer_package/
├── config/
│   ├── .env.example          # Configuration file template
│   └── requirements.txt      # Python dependencies
├── docs/
│   └── README.md             # Project documentation
├── scripts/
│   ├── run_jobs.py           # Script to run job searches
│   ├── run_jobs.bat          # Windows batch script
│   └── run_jobs.sh           # Unix/Linux/Mac shell script
├── src/
│   ├── main.py               # Main entry point
│   └── modules/
│       ├── email_agent.py    # AI-powered email generation
│       ├── excel_logger.py   # Email activity logging
│       ├── resume_embedder.py# Resume text extraction
│       ├── scraper.py        # Job scraping functionality
│       └── smtp_sender.py    # Email sending functionality
└── run.py                    # Root entry point
```

## Directory Descriptions

### config/
Contains configuration files and dependencies:
- `.env.example` - Template for environment variables
- `requirements.txt` - Python package dependencies

### docs/
Documentation files:
- `README.md` - Main project documentation

### scripts/
Helper scripts for running the application:
- `run_jobs.py` - Python script to run job searches
- `run_jobs.bat` - Windows batch script
- `run_jobs.sh` - Unix/Linux/Mac shell script

### src/
Source code for the application:
- `main.py` - Main entry point
- `modules/` - Core functionality modules

### src/modules/
Individual modules that handle specific functionality:
- `email_agent.py` - Generates personalized emails using AI
- `excel_logger.py` - Logs email activities to Excel
- `resume_embedder.py` - Extracts text from resume PDFs
- `scraper.py` - Scrapes job listings from multiple sources
- `smtp_sender.py` - Sends emails via SMTP

### Root Level
- `run.py` - Simplified entry point to run the application