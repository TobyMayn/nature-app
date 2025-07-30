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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-96 max-h-[80vh] overflow-hidden">
        <div className="p-4 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Analysis Results</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-xl"
            >
              ×
            </button>
          </div>
        </div>
        
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {isLoading ? (
            <div className="text-center py-4">
              <p className="text-gray-500">Loading results...</p>
            </div>
          ) : (
            <div className="space-y-3">
              {results.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-4">No results available</p>
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
          )}
        </div>
        
        <div className="p-4 border-t bg-gray-50">
          <button
            onClick={fetchResults}
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>
    </div>
  );
}