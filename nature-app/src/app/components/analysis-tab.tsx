"use client";
import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api-client';

interface AnalysisResult {
  results_id: number;
  user_id: number;
  location_id: number;
  analysis_date: string;
  analysis_type: string;
  request_params: {
    analysis_type: string;
    start_date: string;
    end_date: string;
    bbox: number[];
    requested_at: string;
  };
  status: string;
  requested_at: string;
  completed_at: string | null;
  error_message: string | null;
  result: Record<string, unknown> | null;
}

interface AnalysisTabProps {
  isVisible: boolean;
  onClose: () => void;
  polygonBbox: number[] | null;
}

export default function AnalysisTab({ isVisible, onClose, polygonBbox }: AnalysisTabProps) {
  const [analysisType, setAnalysisType] = useState<'ortho' | 'satellite'>('ortho');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isVisible) {
      fetchResults();
    }
  }, [isVisible]);

  const fetchResults = async () => {
    try {
      const data = await apiClient.get('/results') as AnalysisResult[];
      setResults(data.slice(0, 10)); // Show max 10 most recent results
    } catch (error) {
      console.error('Error fetching results:', error);
    }
  };

  const handleAnalyze = async () => {
    if (!startDate || !endDate) {
      alert('Please select both start and end dates');
      return;
    }

    if (!polygonBbox) {
      alert('Please draw a polygon first');
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.post('/results/analyse', {
        analysisType,
        startDate,
        endDate,
        bbox: polygonBbox,
      });

      // Refresh results after analysis is submitted
      fetchResults();
    } catch (error) {
      console.error('Error submitting analysis:', error);
      alert('Error submitting analysis request');
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
          <h2 className="text-xl font-semibold">Analysis</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ×
          </button>
        </div>

        {/* Analysis Type Section */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-3">Analysis Type</h3>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="analysisType"
                value="ortho"
                checked={analysisType === 'ortho'}
                onChange={(e) => setAnalysisType(e.target.value as 'ortho' | 'satellite')}
                className="mr-2"
              />
              Ortho Analysis
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="analysisType"
                value="satellite"
                checked={analysisType === 'satellite'}
                onChange={(e) => setAnalysisType(e.target.value as 'ortho' | 'satellite')}
                className="mr-2"
              />
              Satellite Analysis
            </label>
          </div>
        </div>

        {/* Period Section */}
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-3">Analysis Period</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed mb-6"
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>

        {/* Results Section */}
        <div>
          <h3 className="text-lg font-medium mb-3">Recent Results</h3>
          <div className="space-y-3">
            {results.length === 0 ? (
              <p className="text-gray-500 text-sm">No results available</p>
            ) : (
              results.map((result) => (
                <div
                  key={result.results_id}
                  className="border border-gray-200 rounded-lg p-3"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{result.analysis_date}</p>
                      <p className="text-sm text-gray-600 capitalize">
                        {result.analysis_type} Analysis
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
                        onClick={() => handleApplyLayer(result.results_id.toString())}
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
        </div>
      </div>
    </div>
  );
}