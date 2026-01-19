import { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/JobRunner.css';

const JobRunner = ({ onRunComplete }) => {
  const { theme } = useTheme();
  const [jobCategory, setJobCategory] = useState('freelance');
  const [jobType, setJobType] = useState('software');
  const [jobField, setJobField] = useState('tech');
  const [keywords, setKeywords] = useState('');
  const [jobLimit, setJobLimit] = useState(30);
  const [aiModel, setAiModel] = useState('google/gemini-2.0-flash-exp:free');
  const [location, setLocation] = useState('');
  const [jobName, setJobName] = useState('');
  const [useEnvMethod, setUseEnvMethod] = useState(false);
  const [sendEmails, setSendEmails] = useState(true);
  const [generateMotivationalLetter, setGenerateMotivationalLetter] = useState(true);
  const [logOutput, setLogOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  // Define all available free models
  const freeModels = [
    { value: 'nousresearch/hermes-3-llama-3.1-405b:free', label: 'Hermes 3 Llama 3.1 405B (Free)' },
    { value: 'mistralai/devstral-2512:free', label: 'DevStral 2512 (Free)' },
    { value: 'nex-agi/deepseek-v3.1-nex-n1:free', label: 'DeepSeek V3.1 NEX N1 (Free)' },
    { value: 'amazon/nova-2-lite-v1:free', label: 'Amazon Nova 2 Lite V1 (Free)' },
    { value: 'arcee-ai/trinity-mini:free', label: 'Arcee Trinity Mini (Free)' },
    { value: 'tngtech/tng-r1t-chimera:free', label: 'TNG R1T Chimera (Free)' },
    { value: 'allenai/olmo-3-32b-think:free', label: 'OLMo 3 32B Think (Free)' },
    { value: 'kwaipilot/kat-coder-pro:free', label: 'KAT Coder Pro (Free)' },
    { value: 'nvidia/nemotron-nano-12b-v2-vl:free', label: 'Nemotron Nano 12B V2 VL (Free)' },
    { value: 'alibaba/tongyi-deepresearch-30b-a3b:free', label: 'Tongyi DeepResearch 30B A3B (Free)' },
    { value: 'nvidia/nemotron-nano-9b-v2:free', label: 'Nemotron Nano 9B V2 (Free)' },
    { value: 'openai/gpt-oss-120b:free', label: 'OpenAI GPT OSS 120B (Free)' },
    { value: 'openai/gpt-oss-20b:free', label: 'OpenAI GPT OSS 20B (Free)' },
    { value: 'z-ai/glm-4.5-air:free', label: 'GLM 4.5 Air (Free)' },
    { value: 'qwen/qwen3-coder:free', label: 'Qwen3 Coder (Free)' },
    { value: 'moonshotai/kimi-k2:free', label: 'Kimi K2 (Free)' },
    { value: 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free', label: 'Dolphin Mistral 24B Venice Edition (Free)' },
    { value: 'google/gemma-3n-e2b-it:free', label: 'Gemma 3N E2B IT (Free)' },
    { value: 'tngtech/deepseek-r1t2-chimera:free', label: 'DeepSeek R1T2 Chimera (Free)' },
    { value: 'google/gemma-3n-e4b-it:free', label: 'Gemma 3N E4B IT (Free)' },
    { value: 'qwen/qwen3-4b:free', label: 'Qwen3 4B (Free)' },
    { value: 'qwen/qwen3-235b-a22b:free', label: 'Qwen3 235B A22B (Free)' },
    { value: 'tngtech/deepseek-r1t-chimera:free', label: 'DeepSeek R1T Chimera (Free)' },
    { value: 'mistralai/mistral-small-3.1-24b-instruct:free', label: 'Mistral Small 3.1 24B Instruct (Free)' },
    { value: 'google/gemma-3-4b-it:free', label: 'Gemma 3 4B IT (Free)' },
    { value: 'google/gemma-3-12b-it:free', label: 'Gemma 3 12B IT (Free)' },
    { value: 'google/gemma-3-27b-it:free', label: 'Gemma 3 27B IT (Free)' },
    { value: 'google/gemini-2.0-flash-exp:free', label: 'Gemini 2.0 Flash EXP (Free)' },
    { value: 'meta-llama/llama-3.3-70b-instruct:free', label: 'Llama 3.3 70B Instruct (Free)' },
    { value: 'meta-llama/llama-3.2-3b-instruct:free', label: 'Llama 3.2 3B Instruct (Free)' },
    { value: 'mistralai/mistral-7b-instruct:free', label: 'Mistral 7B Instruct (Free)' }
  ];

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
          generateMotivationalLetter,
          aiModel,
          location,
          jobName
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
          generateMotivationalLetter,
          aiModel,
          location,
          jobName
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
      <h3 style={{ color: theme.colors.text, marginBottom: '20px' }}>Job Runner</h3>

      <div className="runner-form" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px' }}>
        <div className="form-group">
          <label htmlFor="jobCategory" style={{ color: theme.colors.text }}>Job Category:</label>
          <select
            id="jobCategory"
            value={jobCategory}
            onChange={(e) => setJobCategory(e.target.value)}
            disabled={isRunning || useEnvMethod}
            style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder }}
          >
            <option value="freelance">Freelance Jobs</option>
            <option value="normal">Normal Jobs</option>
          </select>
        </div>

        {jobCategory === 'freelance' ? (
          <>
            <div className="form-group">
              <label htmlFor="jobType" style={{ color: theme.colors.text }}>Job Type:</label>
              <select
                id="jobType"
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                disabled={isRunning || useEnvMethod}
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
          </>
        ) : (
          // For normal jobs, only show job name and location
          <>
            <div className="form-group">
              <label htmlFor="jobName" style={{ color: theme.colors.text }}>Job Name (required):</label>
              <input
                type="text"
                id="jobName"
                placeholder="e.g., React Developer, Data Scientist"
                value={jobName}
                onChange={(e) => setJobName(e.target.value)}
                disabled={isRunning}
                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder, padding: '8px' }}
                required
              />
            </div>
          </>
        )}

        {/* Location is shown for both job categories */}
        <div className="form-group">
          <label htmlFor="location" style={{ color: theme.colors.text }}>Location (optional):</label>
          <input
            type="text"
            id="location"
            placeholder="e.g., New York, Remote, London"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            disabled={isRunning}
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

        <div className="form-group">
          <label htmlFor="aiModel" style={{ color: theme.colors.text }}>AI Model:</label>
          <select
            id="aiModel"
            value={aiModel}
            onChange={(e) => setAiModel(e.target.value)}
            disabled={isRunning}
            style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text, borderColor: theme.colors.inputBorder }}
          >
            {freeModels.map((model) => (
              <option key={model.value} value={model.value}>
                {model.label}
              </option>
            ))}
          </select>
        </div>

        {/* Other checkboxes remain the same */}
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
            Send Emails (Uncheck for dry run)
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