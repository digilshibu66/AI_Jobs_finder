import { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/JobRunner.css';

const JobRunner = ({ onRunComplete }) => {
  const { theme } = useTheme();
  const [isRunning, setIsRunning] = useState(false);
  const [jobType, setJobType] = useState('software');
  const [jobCategory, setJobCategory] = useState('freelance');
  const [jobLimit, setJobLimit] = useState(30);
  const [sendEmails, setSendEmails] = useState(false);
  const [keywords, setKeywords] = useState('');
  const [jobField, setJobField] = useState('tech');
  const [generateMotivationalLetter, setGenerateMotivationalLetter] = useState(true); // New state for motivational letter
  const [useEnvMethod, setUseEnvMethod] = useState(false); // New state for method selection
  const [logOutput, setLogOutput] = useState('');

  const runJobs = async () => {
    setIsRunning(true);
    setLogOutput('Starting job processing...\n');
    
    try {
      if (useEnvMethod) {
        // Use the new method that modifies .env file
        const requestData = {
          jobType,
          jobCategory,
          jobLimit,
          generateMotivationalLetter
        };
        
        const response = await fetch('/api/run-jobs-modified', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Display output from the job runner
          setLogOutput(prev => prev + result.stdout);
          
          // If there were errors, display them
          if (result.stderr) {
            setLogOutput(prev => prev + '\nSTDERR:\n' + result.stderr);
          }
          
          // Notify parent component to refresh data
          if (onRunComplete) {
            onRunComplete();
          }
        } else {
          setLogOutput(prev => prev + `Error: ${result.error}\n`);
        }
      } else {
        // Use the original method with command-line parameters
        const requestData = {
          jobCategory,
          jobType,
          jobLimit,
          sendEmails,
          keywords: keywords || undefined,
          jobField: jobField || undefined,
          generateMotivationalLetter
        };
        
        // Call backend API to run jobs
        const response = await fetch('/api/run-jobs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Display output from the job runner
          setLogOutput(prev => prev + result.stdout);
          
          // If there were errors, display them
          if (result.stderr) {
            setLogOutput(prev => prev + '\nSTDERR:\n' + result.stderr);
          }
          
          // Notify parent component to refresh data
          if (onRunComplete) {
            onRunComplete();
          }
        } else {
          setLogOutput(prev => prev + `Error: ${result.error}\n`);
        }
      }
      
      setIsRunning(false);
    } catch (error) {
      setLogOutput(prev => prev + `Network Error: ${error.message}\n`);
      setIsRunning(false);
    }
  };

  return (
    <div className="job-runner" style={{ backgroundColor: theme.colors.surface, padding: '20px', borderRadius: '8px', boxShadow: theme.colors.cardShadow }}>
      <h3 style={{ color: theme.colors.text }}>Job Runner</h3>
      <div className="runner-controls">
        <div className="form-group">
          <label htmlFor="jobCategory" style={{ color: theme.colors.text }}>Job Category:</label>
          <select 
            id="jobCategory" 
            value={jobCategory} 
            onChange={(e) => setJobCategory(e.target.value)}
            disabled={isRunning}
            style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder }}
          >
            <option value="freelance">Freelance</option>
            <option value="normal">Normal (Full-time)</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="jobType" style={{ color: theme.colors.text }}>Job Type:</label>
          <select 
            id="jobType" 
            value={jobType} 
            onChange={(e) => setJobType(e.target.value)}
            disabled={isRunning}
            style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder }}
          >
            <option value="software">Software Development</option>
            <option value="web">Web Development</option>
            <option value="mobile">Mobile Development</option>
            <option value="data">Data Science</option>
            <option value="healthcare">Healthcare</option>
            <option value="finance">Finance & Banking</option>
            <option value="education">Education</option>
            <option value="legal">Legal</option>
            <option value="marketing">Marketing & Sales</option>
            <option value="manufacturing">Manufacturing & Engineering</option>
            <option value="hospitality">Hospitality & Tourism</option>
            <option value="nonprofit">Nonprofit & NGO</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="jobField" style={{ color: theme.colors.text }}>Job Field:</label>
          <select 
            id="jobField" 
            value={jobField} 
            onChange={(e) => setJobField(e.target.value)}
            disabled={isRunning || useEnvMethod}
            style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder }}
          >
            <option value="tech">Technology/IT</option>
            <option value="marketing">Marketing</option>
            <option value="design">Design/UX</option>
            <option value="business">Business</option>
            <option value="healthcare">Healthcare</option>
            <option value="finance">Finance</option>
            <option value="education">Education</option>
            <option value="legal">Legal</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="hospitality">Hospitality</option>
            <option value="nonprofit">Nonprofit</option>
            <option value="pharma">Pharmaceutical</option>
            <option value="agriculture">Agriculture</option>
            <option value="construction">Construction</option>
            <option value="retail">Retail & E-commerce</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="keywords" style={{ color: theme.colors.text }}>Keywords (comma-separated):</label>
          <input 
            type="text" 
            id="keywords" 
            placeholder="e.g., React, Python, Machine Learning" 
            value={keywords} 
            onChange={(e) => setKeywords(e.target.value)}
            disabled={isRunning || useEnvMethod}
            style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder, padding: '8px' }}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="jobLimit" style={{ color: theme.colors.text }}>Job Limit (1-100):</label>
          <input 
            type="number" 
            id="jobLimit" 
            min="1" 
            max="100" 
            value={jobLimit} 
            onChange={(e) => setJobLimit(Math.min(100, Math.max(1, parseInt(e.target.value) || 1)))}
            disabled={isRunning}
            style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder, padding: '8px', width: '100px' }}
          />
        </div>
        
        <div className="form-group checkbox-group">
          <label style={{ color: theme.colors.text }}>
            <input 
              type="checkbox" 
              checked={useEnvMethod} 
              onChange={(e) => setUseEnvMethod(e.target.checked)}
              disabled={isRunning}
            />
            Use .env Method (Modify .env file directly)
          </label>
        </div>
        
        <div className="form-group checkbox-group">
          <label style={{ color: theme.colors.text }}>
            <input 
              type="checkbox" 
              checked={sendEmails} 
              onChange={(e) => setSendEmails(e.target.checked)}
              disabled={isRunning || useEnvMethod}
            />
            Send Emails (Uncheck for Dry Run)
          </label>
        </div>
        
        <div className="form-group checkbox-group">
          <label style={{ color: theme.colors.text }}>
            <input 
              type="checkbox" 
              checked={generateMotivationalLetter} 
              onChange={(e) => setGenerateMotivationalLetter(e.target.checked)}
              disabled={isRunning}
            />
            Generate Motivational Letters
          </label>
        </div>
        
        <button 
          className={`run-button ${isRunning ? 'running' : ''}`} 
          onClick={runJobs}
          disabled={isRunning}
          style={{
            backgroundColor: isRunning ? theme.colors.warning : theme.colors.secondary,
            color: theme.colors.headerText,
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: isRunning ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            transition: 'background-color 0.3s'
          }}
        >
          {isRunning ? 'Running...' : 'Run Jobs'}
        </button>
      </div>
      
      <div className="runner-output" style={{ marginTop: '20px' }}>
        <h4 style={{ color: theme.colors.text }}>Output Log</h4>
        <pre className="log-output" style={{
          backgroundColor: theme.colors.background,
          color: theme.colors.text,
          padding: '12px',
          borderRadius: '4px',
          overflowX: 'auto',
          border: `1px solid ${theme.colors.border}`,
          maxHeight: '400px',
          overflowY: 'auto'
        }}>{logOutput}</pre>
      </div>
    </div>
  );
};

export default JobRunner;