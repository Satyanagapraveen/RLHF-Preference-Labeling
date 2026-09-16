import { useState, useEffect, useCallback } from 'react';
import { getNextPair, submitLabel } from './services/api';

function App() {
  const [annotatorId] = useState('user_1');
  const [pair, setPair] = useState(null);
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);
  const [sessionCount, setSessionCount] = useState(0);

  const loadPair = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getNextPair(annotatorId);
      if (!data) {
        setFinished(true);
      } else {
        setPair(data);
      }
    } catch (error) {
      console.error("Failed to fetch pair", error);
    } finally {
      setLoading(false);
    }
  }, [annotatorId]);

  useEffect(() => {
    loadPair();
  }, [loadPair]);

  const handleChoice = async (choice) => {
    if (!pair || loading) return;
    
    setLoading(true);
    try {
      await submitLabel(pair.id, annotatorId, choice);
      setSessionCount(prev => prev + 1);
      await loadPair();
    } catch (error) {
      console.error("Failed to submit label", error);
      setLoading(false); 
    }
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (finished || loading) return;
      
      const key = e.key.toLowerCase();
      if (key === 'a') handleChoice('A');
      if (key === 'b') handleChoice('B');
      if (key === 't') handleChoice('tie');
      if (key === 's') handleChoice('skip');
    };

    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [pair, loading, finished]);

  if (finished) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100">
        <h1 className="text-3xl font-bold text-green-600">All available pairs have been labeled. Thank you!</h1>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800">RLHF Annotation Interface</h1>
          <div className="text-gray-600 font-medium">Session Labels: {sessionCount}</div>
        </header>

        {loading ? (
          <div className="flex justify-center py-20 text-xl text-blue-500 animate-pulse">Loading next pair...</div>
        ) : pair && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-sm font-bold text-gray-500 uppercase mb-2">Prompt</h2>
              <p className="text-lg text-gray-800 whitespace-pre-wrap">{pair.prompt}</p>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex flex-col">
                <h2 className="text-sm font-bold text-blue-500 uppercase mb-4">Response A (Press 'A')</h2>
                <div className="flex-grow text-gray-700 whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded border overflow-y-auto max-h-96">
                  {pair.response_a}
                </div>
                <button 
                  onClick={() => handleChoice('A')}
                  className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded transition-colors"
                >
                  Choose A
                </button>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex flex-col">
                <h2 className="text-sm font-bold text-purple-500 uppercase mb-4">Response B (Press 'B')</h2>
                <div className="flex-grow text-gray-700 whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded border overflow-y-auto max-h-96">
                  {pair.response_b}
                </div>
                <button 
                  onClick={() => handleChoice('B')}
                  className="mt-4 w-full bg-purple-500 hover:bg-purple-600 text-white font-bold py-3 rounded transition-colors"
                >
                  Choose B
                </button>
              </div>
            </div>

            <div className="flex justify-center gap-4 mt-8">
              <button 
                onClick={() => handleChoice('tie')}
                className="px-8 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded shadow-sm transition-colors"
              >
                Tie (Press 'T')
              </button>
              <button 
                onClick={() => handleChoice('skip')}
                className="px-8 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded shadow-sm transition-colors"
              >
                Skip (Press 'S')
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;