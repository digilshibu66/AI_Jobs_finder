# 🚀 Quick Start Guide

## Get Started in 5 Minutes!

### Step 1: Clone & Navigate
```bash
cd "D:\My projects\freelance_mailer_package"
```

### Step 2: Configure Environment

1. **Copy the example environment file:**
```bash
copy .env.example .env
```

2. **Edit `.env` with your details:**

**Required Settings:**
```ini
# Get free API key from https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Your Gmail and App Password (https://myaccount.google.com/apppasswords)
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

# Absolute path to your resume
RESUME_PATH=D:\My projects\freelance_mailer_package\resume.pdf

# AI Model (free tier)
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free

# Start with dry run (no actual emails sent)
SEND_EMAILS=false
```

### Step 3: Place Your Resume

Put your `resume.pdf` in the project root folder:
```
D:\My projects\freelance_mailer_package\resume.pdf
```

### Step 4: Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 5: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python server.py
```
Backend starts at: http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Dashboard starts at: http://localhost:3000

### Step 6: Start Your First Job Search!

1. Open http://localhost:3000 in your browser
2. Click **"Start Job Search"**
3. Configure:
   - **Job Category:** Freelance or Normal
   - **Job Type:** software, developer, data science, etc.
   - **Job Limit:** Start with 5-10 for testing
   - **Send Emails:** Keep OFF for first run (dry run)
4. Click **"Start Search"**
5. Watch the live progress!

### Step 7: Review Results

- Check the **Activity** tab for detailed logs
- Review `backend/email_log.xlsx` for full history
- Check `motivational_letters/` folder for generated PDFs

---

## 🎯 First Run Checklist

- [ ] `.env` file configured with all required variables
- [ ] `resume.pdf` placed in project root
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Backend server running (port 5000)
- [ ] Frontend server running (port 3000)
- [ ] Dashboard accessible at http://localhost:3000
- [ ] Dry run completed successfully
- [ ] Review `email_log.xlsx` for results

---

## 🔧 Troubleshooting First Run

### Backend won't start
```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill the process if needed
taskkill /PID <process_id> /F

# Or change port in server.py
```

### Frontend won't start
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

### No jobs found
- Check your job type matches actual job listings
- Try broader search terms: "software" instead of "senior react developer"
- Increase `JOB_LIMIT` to 30-50

### Email validation failing
- Check `.env` has correct `SMTP_EMAIL` and `SMTP_PASSWORD`
- Verify App Password (not your Gmail password)
- Test with dry run first (`SEND_EMAILS=false`)

---

## 💡 Pro Tips for First Run

### 1. Start Small
```ini
JOB_LIMIT=5
SEND_EMAILS=false
```
Run a small dry run first to see how it works!

### 2. Check Logs
Open `backend/email_log.xlsx` to see:
- What jobs were found
- What emails were discovered
- Email validation scores
- Reasons for skipping jobs

### 3. Review Generated Emails
Dry run generates emails without sending. Check the console output to see the email content.

### 4. Customize Resume
Make sure your `resume.pdf` is:
- Up to date
- Well formatted
- Contains relevant keywords
- Not password protected

### 5. Test Email Validation
Run this quick test:
```bash
cd backend
python -c "from modules.email_validator import EmailValidator; v=EmailValidator(); print(v.validate_and_score('careers@google.com', 'Google', 'google.com'))"
```

---

## 🎨 Explore the Dashboard

### Dashboard Tab
- **Quick Stats**: Total jobs, success rate, failures
- **Quick Actions**: Start search, view logs, settings
- **Recent Activity**: Last 5 processed jobs

### Jobs Tab
- **Start New Search**: Configure and run job search
- **Live Progress**: Real-time console output
- **Stop/Pause**: Control running searches

### Activity Tab
- **Filter Logs**: By status, platform, date
- **Search**: Find specific companies/jobs
- **Export**: Download logs as Excel

### Settings Tab
- **AI Model**: Choose free AI model
- **Job Preferences**: Default search settings
- **Email Settings**: SMTP configuration

---

## 📚 Next Steps

Once your first dry run works:

1. **Review Email Quality**
   - Check which emails were found
   - Verify they're genuine company emails
   - Adjust `CRAWL_DEPTH` if needed

2. **Customize Email Content**
   - Edit prompts in `email_agent.py`
   - Adjust motivational letter templates

3. **Test Live Sending**
   - Set `SEND_EMAILS=true`
   - Start with 1-2 jobs to verify sending works
   - Monitor for bounces/errors

4. **Scale Up**
   - Increase `JOB_LIMIT` to 30-50
   - Run searches multiple times per day
   - Track success rate in Excel

5. **Optimize**
   - Fine-tune job search keywords
   - Adjust email validation settings
   - Customize email templates

---

## 🆘 Need Help?

1. **Check README.md**: Full documentation
2. **Check IMPROVEMENTS.md**: What's new in this version
3. **Check Logs**: `backend/email_log.xlsx` has details
4. **Console Output**: Look for error messages
5. **Test Components**: Try email validator separately

---

**Ready to find your dream job? Let's go! 🚀**
