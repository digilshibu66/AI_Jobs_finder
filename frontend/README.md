# Jobs Mail Sender Dashboard

A modern React dashboard for the Jobs Mail Sender application that provides a visual interface for monitoring and controlling job applications.

## Features

- **Real-time Statistics**: Visual charts and metrics for job application success rates
- **Activity Logs**: Detailed table view of all job applications with status tracking
- **One-Click Execution**: Run job searches directly from the dashboard with configurable parameters
- **Live Output**: Real-time log output during job processing
- **Data Refresh**: Manual refresh capability for up-to-date statistics

## Tech Stack

- **React** - Frontend framework
- **Vite** - Build tool and development server
- **Chart.js** - Data visualization
- **React Chartjs 2** - React wrapper for Chart.js
- **CSS Modules** - Styling

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── Dashboard.jsx   # Main dashboard component
│   │   ├── JobStats.jsx    # Statistics visualization
│   │   ├── JobRunner.jsx   # Job execution controls
│   │   └── JobLogs.jsx     # Activity log display
│   ├── styles/             # CSS stylesheets
│   ├── App.jsx             # Main application component
│   └── main.jsx            # Application entry point
├── index.html              # HTML template
├── vite.config.js          # Vite configuration
└── package.json            # Project dependencies
```

## Getting Started

### Prerequisites

- Node.js 16+ (Recommended: Node.js 18+)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development

Start the development server:
```bash
npm run dev
```

The dashboard will be available at http://localhost:3001

### Building for Production

Create a production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Components

### Dashboard (`Dashboard.jsx`)

The main dashboard component that orchestrates all other components and manages data flow.

### Job Statistics (`JobStats.jsx`)

Displays application statistics using bar charts and summary cards:
- Total jobs processed
- Success rate
- Failure rate
- Skipped jobs
- Dry run jobs

### Job Runner (`JobRunner.jsx`)

Provides a form interface for configuring and running job searches:
- Job category selection (freelance/normal)
- Job type selection (software/web/mobile/data)
- Job limit configuration
- Send emails toggle
- Real-time log output

### Job Logs (`JobLogs.jsx`)

Displays a table of all job applications with status indicators:
- Timestamp
- Job title and company
- Recipient email
- Status (success/failed/skipped/dry-run)
- Error messages

## API Integration

The dashboard communicates with the backend server through the following endpoints:

- `GET /api/logs` - Retrieve application logs
- `GET /api/stats` - Retrieve application statistics
- `POST /api/run-jobs` - Execute job processing
- `GET /api/health` - Health check

## Styling

All components are styled with custom CSS files located in the `src/styles/` directory. The styling follows a clean, modern design with responsive layouts.

## Development Guidelines

1. All components should be functional components using React hooks
2. CSS files should be colocated with components in the `src/styles/` directory
3. API calls should be handled in the Dashboard component and passed down as props
4. State management should use React's built-in useState and useEffect hooks
5. Components should be reusable and modular