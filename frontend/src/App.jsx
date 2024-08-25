import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import useDebounce from './hooks/useDebounce'; // Assuming you saved the hook in useDebounce.js

function App() {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [prNumber, setPrNumber] = useState('');
  const [repoSuggestions, setRepoSuggestions] = useState([]);
  const [prSuggestions, setPrSuggestions] = useState([]);

  const debouncedRepoUrl = useDebounce(repoUrl, 300);
  const debouncedPrNumber = useDebounce(prNumber, 300);

  const searchRepos = useCallback(async (query) => {
    if (query.length < 3) return;
    try {
      const response = await axios.get(`http://localhost:8000/search-repos?q=${query}`);
      setRepoSuggestions(response.data);
    } catch (error) {
      console.error('Error fetching repo suggestions:', error);
    }
  }, []);

  const fetchPRs = useCallback(async (repo) => {
    try {
      const response = await axios.get(`http://localhost:8000/list-prs?repo=${repo}`);
      setPrSuggestions(response.data);
    } catch (error) {
      console.error('Error fetching PR suggestions:', error);
    }
  }, []);

  useEffect(() => {
    if (debouncedRepoUrl) {
      searchRepos(debouncedRepoUrl);
    } else {
      setRepoSuggestions([]);
    }
  }, [debouncedRepoUrl, searchRepos]);

  useEffect(() => {
    const [owner, repo] = debouncedRepoUrl.split('/');
    if (owner && repo) {
      fetchPRs(`${owner}/${repo}`);
    } else {
      setPrSuggestions([]);
    }
  }, [debouncedRepoUrl, fetchPRs]);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setResponse('');
    try {
      const result = await axios.post('http://localhost:8000/generate', { 
        repo_url: repoUrl, 
        pr_number: parseInt(prNumber) 
      });
      setResponse(result.data.response);
    } catch (error) {
      console.error('Error generating response:', error);
      setError(error.response?.data?.detail || 'An error occurred while generating the response.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div>
              <h1 className="text-2xl font-semibold text-center">README Generator</h1>
            </div>
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <div className="relative">
                  <input 
                    id="repo-url" 
                    name="repo-url" 
                    type="text" 
                    className="peer placeholder-transparent h-10 w-full border-b-2 border-gray-300 text-gray-900 focus:outline-none focus:border-rose-600" 
                    placeholder="Repository URL" 
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    list="repo-suggestions"
                  />
                  <label htmlFor="repo-url" className="absolute left-0 -top-3.5 text-gray-600 text-sm peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-440 peer-placeholder-shown:top-2 transition-all peer-focus:-top-3.5 peer-focus:text-gray-600 peer-focus:text-sm">Repository URL</label>
                  <datalist id="repo-suggestions">
                    {repoSuggestions.map((suggestion, index) => (
                      <option key={index} value={suggestion} />
                    ))}
                  </datalist>
                </div>
                <div className="relative">
                  <input 
                    id="pr-number" 
                    name="pr-number" 
                    type="text" 
                    className="peer placeholder-transparent h-10 w-full border-b-2 border-gray-300 text-gray-900 focus:outline-none focus:border-rose-600" 
                    placeholder="PR Number" 
                    value={prNumber}
                    onChange={(e) => setPrNumber(e.target.value)}
                    list="pr-suggestions"
                  />
                  <label htmlFor="pr-number" className="absolute left-0 -top-3.5 text-gray-600 text-sm peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-440 peer-placeholder-shown:top-2 transition-all peer-focus:-top-3.5 peer-focus:text-gray-600 peer-focus:text-sm">PR Number</label>
                  <datalist id="pr-suggestions">
                    {prSuggestions.map((suggestion, index) => (
                      <option key={index} value={suggestion} />
                    ))}
                  </datalist>
                </div>
                <div className="relative">
                  <button 
                    onClick={handleGenerate}
                    disabled={!repoUrl || !prNumber || loading}
                    className="bg-blue-500 text-white rounded-md px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-opacity-50 disabled:opacity-50"
                  >
                    {loading ? 'Generating...' : 'Generate Updated README'}
                  </button>
                </div>
              </div>
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                  <strong className="font-bold">Error!</strong>
                  <span className="block sm:inline"> {error}</span>
                </div>
              )}
              {response && (
                <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                  <h2 className="text-xl font-semibold">Generated README:</h2>
                  <pre className="bg-gray-100 p-4 rounded-md overflow-auto">
                    {response}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
