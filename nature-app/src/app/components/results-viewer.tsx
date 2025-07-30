"use client";
import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api-client';

interface AnalysisResult {
  id: string;
  date: string;
  analysisType: 'ortho' | 'satellite';
  status: 'pending' | 'error' | 'complete';
}

interface ResultsViewerProps {
  isVisible: boolean;
  onClose: () => void;
}

export default function ResultsViewer({ isVisible, onClose }: ResultsViewerProps) {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isVisible) {
      fetchResults();
    }
  }, [isVisible]);

  const fetchResults = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.get('/results');
      setResults(data.slice(0, 10)); // Show max 10 most recent results
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyLayer = (resultId: string) => {
    // TODO: Implement layer application logic
    console.log('Applying layer for result:', resultId);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed left-0 top-0 w-96 h-full bg-white shadow-lg border-r border-gray-200 z-50 overflow-y-auto">
      <div className="p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Analysis Results</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ×
          </button>
        </div>

        <div>
          <h3 className="text-lg font-medium mb-3">Recent Results</h3>
          <div className="space-y-3">
            {isLoading ? (
              <p className="text-gray-500 text-sm">Loading results...</p>
            ) : results.length === 0 ? (
              <p className="text-gray-500 text-sm">No results available</p>
            ) : (
              results.map((result) => (
                <div
                  key={result.id}
                  className="border border-gray-200 rounded-lg p-3"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{result.date}</p>
                      <p className="text-sm text-gray-600 capitalize">
                        {result.analysisType} Analysis
                      </p>
                      <span
                        className={`inline-block px-2 py-1 text-xs rounded-full mt-1 ${
                          result.status === 'complete'
                            ? 'bg-green-100 text-green-800'
                            : result.status === 'error'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {result.status}
                      </span>
                    </div>
                    {result.status === 'complete' && (
                      <button
                        onClick={() => handleApplyLayer(result.id)}
                        className="text-sm bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded"
                      >
                        Apply Layer
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
          
          <button
            onClick={fetchResults}
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed mt-4"
          >
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>
    </div>
  );
}