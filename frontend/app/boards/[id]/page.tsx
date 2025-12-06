// app/board/[id]/page.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useParams } from 'next/navigation';
import ResizableSticker from '../../components/sticker';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface StickerData {
  id: string;
  text: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  color: string;
}

interface BoardData {
  boardId: number;
  title: string;
  description: string;
  ownerId: number;
  ownerName: string;
  backgroundColor: string;
  createdAt: string;
  updatedAt: string;
  stickers: {
    stickerId: number;
    boardId: number;
    x: number;
    y: number;
    width: number;
    height: number;
    color: string;
    text: string;
    layerLevel: number;
    createdBy: number;
    createdAt: string;
    updatedAt: string;
  }[];
  permission: string;
}

// SAMPLE API RESPONSE FOR DEVELOPMENT/TESTING
const SAMPLE_BOARD_RESPONSE: BoardData = {
  boardId: 1,
  title: 'My First Board',
  description: 'A sample board for testing',
  ownerId: 123,
  ownerName: 'John Doe',
  backgroundColor: '#F5F5F5',
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T14:25:00Z',
  stickers: [
    {
      stickerId: 1,
      boardId: 1,
      x: 100,
      y: 100,
      width: 256,
      height: 128,
      color: '#FFEB3B',
      text: 'Welcome to the sticker board! Double click to edit.',
      layerLevel: 1,
      createdBy: 123,
      createdAt: '2024-01-15T10:30:00Z',
      updatedAt: '2024-01-15T14:25:00Z'
    },
    {
      stickerId: 2,
      boardId: 1,
      x: 400,
      y: 150,
      width: 256,
      height: 128,
      color: '#2196F3',
      text: 'Drag the top bar to move stickers around',
      layerLevel: 2,
      createdBy: 123,
      createdAt: '2024-01-15T10:30:00Z',
      updatedAt: '2024-01-15T14:25:00Z'
    },
    {
      stickerId: 3,
      boardId: 1,
      x: 200,
      y: 300,
      width: 256,
      height: 128,
      color: '#4CAF50',
      text: 'Click + button to add more stickers',
      layerLevel: 3,
      createdBy: 123,
      createdAt: '2024-01-15T10:30:00Z',
      updatedAt: '2024-01-15T14:25:00Z'
    }
  ],
  permission: 'owner'
};

export default function BoardPage() {
  const params = useParams();
  const boardId = params.id;
  
  const [board, setBoard] = useState<BoardData | null>(null);
  const [stickers, setStickers] = useState<StickerData[]>([]);
  const [selectedColor, setSelectedColor] = useState('bg-yellow-200');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [useSampleData, setUseSampleData] = useState(false);
  
  const boardRef = useRef<HTMLDivElement>(null);

  const colors = [
    { name: 'Yellow', value: 'bg-yellow-200', border: 'border-yellow-300' },
    { name: 'Blue', value: 'bg-blue-200', border: 'border-blue-300' },
    { name: 'Green', value: 'bg-green-200', border: 'border-green-300' },
    { name: 'Pink', value: 'bg-pink-200', border: 'border-pink-300' },
    { name: 'Purple', value: 'bg-purple-200', border: 'border-purple-300' },
    { name: 'Red', value: 'bg-red-200', border: 'border-red-300' },
    { name: 'Cyan', value: 'bg-cyan-200', border: 'border-cyan-300' },
    { name: 'Orange', value: 'bg-orange-200', border: 'border-orange-300' },
  ];

  // Convert hex color to Tailwind class
  const hexToTailwind = (hexColor: string): string => {
    const colorMap: Record<string, string> = {
      '#FFEB3B': 'bg-yellow-200',
      '#2196F3': 'bg-blue-200',
      '#4CAF50': 'bg-green-200',
      '#E91E63': 'bg-pink-200',
      '#9C27B0': 'bg-purple-200',
      '#F44336': 'bg-red-200',
      '#00BCD4': 'bg-cyan-200',
      '#FF9800': 'bg-orange-200',
      '#FFFFFF': 'bg-white',
      '#000000': 'bg-gray-800',
      '#F5F5F5': 'bg-gray-50',
    };
    
    return colorMap[hexColor.toUpperCase()] || 'bg-yellow-200';
  };

  // Convert API stickers to component format
  const convertApiStickers = (apiStickers: any[]): StickerData[] => {
    return apiStickers.map(sticker => ({
      id: sticker.stickerId.toString(),
      text: sticker.text,
      position: { x: sticker.x, y: sticker.y },
      size: { width: sticker.width, height: sticker.height },
      color: hexToTailwind(sticker.color),
    }));
  };

  // Load sample data for development/testing
  const loadSampleData = () => {
    console.log('Loading sample data for development...');
    setBoard(SAMPLE_BOARD_RESPONSE);
    setStickers(convertApiStickers(SAMPLE_BOARD_RESPONSE.stickers));
    setUseSampleData(true);
    setIsLoading(false);
  };

  // Fetch board data from API
  const fetchBoardFromApi = async () => {
    if (!boardId) {
      setError('Board ID is missing');
      setIsLoading(false);
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Get token from localStorage or auth context
      const token = localStorage.getItem('token') || 'demo-token-for-development';
      
      console.log(`Fetching board ${boardId} from API...`);
      
      // Using a relative URL that will be handled by Next.js API routes
      // or your actual backend if CORS is configured
      const response = await fetch(`${API_URL}/api/v1/boards/${boardId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        if (response.status === 404 || response.status >= 500) {
          console.log('API not available, falling back to sample data');
          loadSampleData();
          return;
        }
        throw new Error(`API returned ${response.status}: ${response.statusText}`);
      }
      
      const boardData: BoardData = await response.json();
      setBoard(boardData);
      setStickers(convertApiStickers(boardData.stickers));
      setUseSampleData(false);
      
    } catch (err) {
      console.warn('API call failed, using sample data instead:', err);
      // Comment out the error state and use sample data instead
      // setError(err instanceof Error ? err.message : 'Failed to load board');
      loadSampleData();
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch board data
  useEffect(() => {
    fetchBoardFromApi();
  }, [boardId]);

  const handleAddSticker = () => {
    // Get random position within board bounds
    const boardRect = boardRef.current?.getBoundingClientRect();
    let x = 50;
    let y = 50;
    
    if (boardRect) {
      x = Math.random() * (boardRect.width - 200);
      y = Math.random() * (boardRect.height - 200);
    }

    const newSticker: StickerData = {
      id: `sticker-${Date.now()}`,
      text: 'Click to edit this text...',
      position: { x, y },
      size: { width: 256, height: 128 },
      color: selectedColor,
    };
    
    setStickers([...stickers, newSticker]);
    
    if (useSampleData) {
      console.log('Adding sticker locally (sample mode)');
    } else {
      // TODO: Send API request to create sticker
      console.log('TODO: Send API request to create sticker');
      // createStickerOnBackend(boardId, newSticker);
    }
  };

  const handleTextChange = (id: string, text: string) => {
    setStickers(stickers.map(sticker => 
      sticker.id === id ? { ...sticker, text } : sticker
    ));
    
    if (useSampleData) {
      console.log('Updating sticker text locally (sample mode)');
    } else {
      // TODO: Send API request to update sticker text
      console.log('TODO: Send API request to update sticker text');
      // updateStickerTextOnBackend(id, text);
    }
  };

  const handleDragStop = (id: string, position: { x: number; y: number }) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, position } : sticker
    ));
    
    if (useSampleData) {
      console.log('Updating sticker position locally (sample mode)');
    } else {
      // TODO: Send API request to update sticker position
      console.log('TODO: Send API request to update sticker position');
      // updateStickerPositionOnBackend(id, position);
    }
  };

  const handleResizeStop = (id: string, size: { width: number; height: number }) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, size } : sticker
    ));
    
    if (useSampleData) {
      console.log('Updating sticker size locally (sample mode)');
    } else {
      // TODO: Send API request to update sticker size
      console.log('TODO: Send API request to update sticker size');
      // updateStickerSizeOnBackend(id, size);
    }
  };

  const handleDeleteSticker = (id: string) => {
    setStickers(stickers.filter(sticker => sticker.id !== id));
    
    if (useSampleData) {
      console.log('Deleting sticker locally (sample mode)');
    } else {
      // TODO: Send API request to delete sticker
      console.log('TODO: Send API request to delete sticker');
      // deleteStickerOnBackend(id);
    }
  };

  const handleColorChange = (id: string, color: string) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, color } : sticker
    ));
    
    if (useSampleData) {
      console.log('Updating sticker color locally (sample mode)');
    } else {
      // TODO: Send API request to update sticker color
      console.log('TODO: Send API request to update sticker color');
      // updateStickerColorOnBackend(id, color);
    }
  };

  const handleRetryApi = () => {
    fetchBoardFromApi();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-600 flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <div>Loading board...</div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="relative w-full h-screen overflow-hidden"
      style={{ backgroundColor: board?.backgroundColor || '#FFFFFF' }}
    >
      {/* Development mode banner */}
      {useSampleData && (
        <div className="absolute top-20 left-0 right-0 z-40 bg-yellow-500/90 backdrop-blur-sm p-2 text-center text-sm text-white">
          <div className="max-w-7xl mx-auto">
            <span className="font-semibold">Development Mode:</span> Using sample data. 
            <button 
              onClick={handleRetryApi}
              className="ml-2 underline hover:no-underline"
            >
              Retry API connection
            </button>
          </div>
        </div>
      )}
      
      {/* Error message (commented out - replaced with sample data fallback) */}
      {/* {error && !useSampleData && (
        <div className="absolute top-20 left-0 right-0 z-40 bg-red-500/90 backdrop-blur-sm p-4 text-center text-white">
          <div className="max-w-7xl mx-auto">
            Error: {error}
            <button 
              onClick={loadSampleData}
              className="ml-4 bg-white text-red-500 px-3 py-1 rounded hover:bg-red-50"
            >
              Use Sample Data Instead
            </button>
          </div>
        </div>
      )} */}

      {/* Controls Panel */}
      <div className="absolute top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-800">
              Mirumir
            </h1>
            {board && (
              <div className="text-sm text-gray-600">
                / {board?.title || 'Board'}
                {useSampleData && <span className="ml-2 text-yellow-600">(Sample Data)</span>}
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-gray-600">New Sticker Color:</span>
            <div className="flex gap-1">
              {colors.map((color) => (
                <button
                  key={color.value}
                  onClick={() => setSelectedColor(color.value)}
                  className={`w-6 h-6 rounded-full ${color.value} border-2 ${
                    selectedColor === color.value ? color.border : 'border-transparent'
                  } transition-all hover:scale-110`}
                  title={color.name}
                />
              ))}
            </div>
            <button
              onClick={handleAddSticker}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
            >
              <span>+</span>
              <span>Add Sticker</span>
            </button>
            <div className="text-xs text-gray-500 ml-2">
              {stickers.length} sticker{stickers.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
      </div>

      {/* Board Container */}
      <div 
        ref={boardRef}
        className="relative w-full h-full pt-20"
      >
        {/* Grid Background Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(90deg,#e0e0e0_1px,transparent_1px),linear-gradient(#e0e0e0_1px,transparent_1px)] bg-[size:20px_20px] opacity-20"></div>
        
        {/* Stickers */}
        {stickers.map((sticker) => (
          <ResizableSticker
            key={sticker.id}
            id={sticker.id}
            initialText={sticker.text}
            initialPosition={sticker.position}
            initialSize={sticker.size}
            color={sticker.color}
            onTextChange={handleTextChange}
            onDragStop={handleDragStop}
            onResizeStop={handleResizeStop}
            onColorChange={handleColorChange}
            onDelete={handleDeleteSticker}
          />
        ))}
        
        {/* Empty state */}
        {stickers.length === 0 && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-2xl mb-2">📋</div>
              <div className="text-lg font-medium mb-1">No stickers yet</div>
              <div className="text-sm">Click "Add Sticker" to create your first sticker</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}