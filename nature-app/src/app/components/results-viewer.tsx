"use client";
import { useEffect, useState } from 'react';
import { useAPI } from '../hooks/use-api';

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

interface AnalysisPolygon {
  type: string;
  coordinates: number[][][];
  area: number;
}

interface AnalysisResult {
  mask: number[][];
  polygons: AnalysisPolygon[];
  mask_shape: number[];
}

interface ResultsViewerProps {
  isVisible: boolean;
  onClose: () => void;
  onApplyResult: (result: AnalysisResult) => void;
}

export default function ResultsViewer({ isVisible, onClose, onApplyResult }: ResultsViewerProps) {
  const { apiClient } = useAPI();
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const resultsPerPage = 10;

  useEffect(() => {
    if (isVisible) {
      setCurrentPage(0);
      setHasMore(true);
      fetchResults(0, false);
    }
  }, [isVisible]);

  const fetchResults = async (page: number = 0, append: boolean = false) => {
    setIsLoading(true);
    try {
      const offset = page * resultsPerPage;
      const data = await apiClient.get(`/results?offset=${offset}&limit=${resultsPerPage}`) as AnalysisResult[];
      
      if (append && page > 0) {
        setResults(prev => [...prev, ...data]);
      } else {
        setResults(data);
        setCurrentPage(0);
      }
      
      // Check if there are more results
      setHasMore(data.length === resultsPerPage);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyLayer = async (resultId: string) => {
    try {
      // Fetch the specific result details
      const resultData = await apiClient.get(`/results/${resultId}`) as any;
      
      if (resultData.result && resultData.result.polygons) {
        // Apply the polygons to the map
        onApplyResult(resultData.result as AnalysisResult);
        console.log(`Applied layer for result ${resultId} with ${resultData.result.polygons.length} polygons`);
      } else {
        console.warn(`No polygon data found for result ${resultId}`);
      }
    } catch (error) {
      console.error('Error applying layer:', error);
    }
  };

  const handleLoadMore = () => {
    const nextPage = currentPage + 1;
    setCurrentPage(nextPage);
    fetchResults(nextPage, true);
  };

  const handleRefresh = () => {
    setCurrentPage(0);
    setHasMore(true);
    fetchResults(0, false);
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
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-medium">Recent Results</h3>
            <span className="text-sm text-gray-500">
              {results.length} result{results.length !== 1 ? 's' : ''} loaded
            </span>
          </div>
          <div className="space-y-3">
            {isLoading ? (
              <p className="text-gray-500 text-sm">Loading results...</p>
            ) : results.length === 0 ? (
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
          
          <div className="mt-4 space-y-2">
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading && currentPage === 0 ? 'Refreshing...' : 'Refresh'}
            </button>
            
            {hasMore && (
              <button
                onClick={handleLoadMore}
                disabled={isLoading}
                className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading && currentPage > 0 ? 'Loading More...' : 'Load More'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}