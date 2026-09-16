import { useState, useEffect } from 'react';
import { getAnalytics } from './services/api';

function Analytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getAnalytics();
        setStats(data);
      } catch (err) {
        setError("Failed to load analytics data.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div className="py-20 text-center text-xl text-blue-500 animate-pulse">Loading Analytics...</div>;
  }

  if (error) {
    return <div className="py-20 text-center text-xl text-red-500">{error}</div>;
  }

  if (!stats) return null;

  return (
    <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Performance Analytics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-100">
          <div className="text-sm font-bold text-blue-500 uppercase">Total Labels Submitted</div>
          <div className="text-4xl font-black text-blue-700 mt-2">{stats.total_labels}</div>
        </div>
        
        <div className="bg-green-50 p-6 rounded-lg border border-green-100">
          <div className="text-sm font-bold text-green-500 uppercase">Inter-Rater Agreement</div>
          <div className="text-4xl font-black text-green-700 mt-2">
            {(stats.agreement_rate * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-700 mb-4">Choice Distribution</h3>
        <div className="grid grid-cols-4 gap-4">
          {Object.entries(stats.label_distribution).map(([choice, count]) => (
            <div key={choice} className="bg-gray-50 p-4 rounded border border-gray-200 text-center">
              <div className="text-sm font-bold text-gray-500 uppercase">{choice === 'tie' ? 'Tie' : choice === 'skip' ? 'Skip' : `Choice ${choice}`}</div>
              <div className="text-2xl font-bold text-gray-800 mt-1">{count}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Analytics;