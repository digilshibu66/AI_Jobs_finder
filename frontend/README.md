# Jobs Mail Sender Dashboard

A modern React dashboard for the Jobs Mail Sender application that provides a visual interface for monitoring and controlling job applications.

## ✨ Key Features

- **Real-time Statistics**: Interactive charts showing success/failure rates.
- **AI Model Selection**: Choose from 30+ verified free OpenRouter models (Llama, Mistral, Qwen).
- **One-Click Job Search**: Configure and run job scraping directly.
- **Live Monitoring**: Watch real-time logs as the backend processes jobs.
- **Activity History**: Searchable table of all past applications.
- **Dark/Light Mode**: Fully responsive theme support.

## 🛠️ Tech Stack

- **React** (Vite)
- **Chart.js**
- **React Router**
- **CSS Modules**

## 📂 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx   # Home stats
│   │   ├── JobsPage.jsx    # Main job runner (New)
│   │   ├── SettingsPage.jsx# Configuration & Models (New)
│   │   ├── ActivityPage.jsx# Historical logs
│   │   └── Navbar.jsx      # Navigation
│   ├── context/            # React Context (Theme)
│   ├── styles/             # Application styles
│   └── App.jsx             # Routes
```

## 🚀 Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Access at: `http://localhost:3000` (or `3001` depending on port availability)

## 🧩 Components

### Jobs Page (`JobsPage.jsx`)

The command center.

- **Select AI Model**: Choose which LLM generates your emails.
- **Search Parameters**: Set Job Title, Location, and Limit.
- **Dry Run Mode**: Test without sending emails.
- **Live Terminal**: View backend processing logs in real-time.

### Activity Page (`ActivityPage.jsx`)

Your application history.

- View all sent emails.
- Filter by status (Success, Failed, Initializing).
- View error logs for rejected emails.

### Settings Page (`SettingsPage.jsx`)

Global configuration.

- Set default AI model preferences.
- View verified working models.

## 🔗 API Integration

Communicates with the Python Flask backend at `http://localhost:5000`:

- `GET /api/logs`
- `GET /api/stats`
- `POST /api/run-jobs-stream`
- `POST /api/settings`

## 🎨 Styling

Modern, clean UI with glassmorphism effects and responsive layout. Supports system preference for Dark Mode.
