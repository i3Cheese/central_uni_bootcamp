// app/board/[id]/page.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import ResizableSticker from '../../components/sticker';
import { HEADER_PADDING_X } from '../../constants/borders';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

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
  const router = useRouter();
  const boardId = params.id;

  const [board, setBoard] = useState<BoardData | null>(null);
  const [stickers, setStickers] = useState<StickerData[]>([]);
  const [selectedColor, setSelectedColor] = useState('bg-yellow-200');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [useSampleData, setUseSampleData] = useState(false);
  const [userLogin, setUserLogin] = useState<string | null>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  const boardRef = useRef<HTMLDivElement>(null);

  const canEdit = board?.permission === "edit" || board?.permission === "owner";

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

  // Convert Tailwind class to hex color
  const tailwindToHex = (tailwindClass: string): string => {
    const colorMap: Record<string, string> = {
      'bg-yellow-200': '#FFEB3B',
      'bg-blue-200': '#2196F3',
      'bg-green-200': '#4CAF50',
      'bg-pink-200': '#E91E63',
      'bg-purple-200': '#9C27B0',
      'bg-red-200': '#F44336',
      'bg-cyan-200': '#00BCD4',
      'bg-orange-200': '#FF9800',
      'bg-white': '#FFFFFF',
      'bg-gray-800': '#000000',
      'bg-gray-50': '#F5F5F5',
    };

    return colorMap[tailwindClass] || '#FFEB3B';
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

      const token = localStorage.getItem('token');
      if (!token) {
        setError('Not authenticated');
        setIsLoading(false);
        return;
      }

      const response = await fetch(`${API_URL}/api/v1/boards/${boardId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        // Добавляем mode для лучшей обработки CORS ошибок
        mode: 'cors',
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        setError('Session expired. Please login again.');
        setIsLoading(false);
        return;
      }

      if (response.status === 403) {
        setError('You do not have access to this board');
        setIsLoading(false);
        return;
      }

      if (response.status === 404) {
        setError('Board not found');
        setIsLoading(false);
        return;
      }

      if (!response.ok) {
        throw new Error(`API returned ${response.status}: ${response.statusText}`);
      }

      const boardData: BoardData = await response.json();
      setBoard(boardData);
      setStickers(convertApiStickers(boardData.stickers));
      setUseSampleData(false);

    } catch (err) {
      console.error('API call failed:', err);
      if (err instanceof TypeError && err.message === 'Failed to fetch') {
        setError(
          `Cannot connect to backend at ${API_URL}. ` +
          `Make sure the backend is running. ` +
          `Check: 1) Backend is running (docker-compose up or uvicorn), ` +
          `2) CORS is configured for this origin, ` +
          `3) API_URL is correct in .env`
        );
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load board');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Load user login from localStorage
  useEffect(() => {
    const login = localStorage.getItem('userLogin');
    setUserLogin(login);
  }, []);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('userLogin');
    router.push('/auth');
  };

  // Update page title
  useEffect(() => {
    if (board) {
      document.title = board.title ? `Mirumir - ${board.title}` : "Mirumir - Доска";
    } else {
      document.title = "Mirumir - Загрузка доски...";
    }
  }, [board]);

  // Fetch board data
  useEffect(() => {
    fetchBoardFromApi();
  }, [boardId]);

  const handleAddSticker = async () => {
    if (!board || !boardId || !canEdit) return;

    // Get random position within board bounds
    const boardRect = boardRef.current?.getBoundingClientRect();
    let x = 50;
    let y = 50;

    if (boardRect) {
      x = Math.random() * (boardRect.width - 200);
      y = Math.random() * (boardRect.height - 200);
    }

    const hexColor = tailwindToHex(selectedColor);

    if (useSampleData) {
      const newSticker: StickerData = {
        id: `sticker-${Date.now()}`,
        text: 'Click to edit this text...',
        position: { x, y },
        size: { width: 256, height: 128 },
        color: selectedColor,
      };
      setStickers([...stickers, newSticker]);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${API_URL}/api/v1/boards/${boardId}/stickers`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          x,
          y,
          width: 256,
          height: 128,
          color: hexColor,
          text: 'Click to edit this text...',
          layerLevel: 0,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create sticker');
      }

      const newSticker = await response.json();
      const convertedSticker: StickerData = {
        id: newSticker.stickerId.toString(),
        text: newSticker.text || '',
        position: { x: newSticker.x, y: newSticker.y },
        size: { width: newSticker.width || 256, height: newSticker.height || 128 },
        color: hexToTailwind(newSticker.color),
      };

      setStickers([...stickers, convertedSticker]);
    } catch (err) {
      console.error('Failed to create sticker:', err);
      setError(err instanceof Error ? err.message : 'Failed to create sticker');
    }
  };

  const handleTextChange = async (id: string, text: string) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, text } : sticker
    ));

    if (useSampleData) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const sticker = stickers.find(s => s.id === id);
      if (!sticker) return;

      await fetch(`${API_URL}/api/v1/boards/${boardId}/stickers/${id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
        }),
      });
    } catch (err) {
      console.error('Failed to update sticker text:', err);
    }
  };

  const handleDragStop = async (id: string, position: { x: number; y: number }) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, position } : sticker
    ));

    if (useSampleData) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      await fetch(`${API_URL}/api/v1/boards/${boardId}/stickers/${id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          x: position.x,
          y: position.y,
        }),
      });
    } catch (err) {
      console.error('Failed to update sticker position:', err);
    }
  };

  const handleResizeStop = async (id: string, size: { width: number; height: number }) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, size } : sticker
    ));

    if (useSampleData) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      await fetch(`${API_URL}/api/v1/boards/${boardId}/stickers/${id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          width: size.width,
          height: size.height,
        }),
      });
    } catch (err) {
      console.error('Failed to update sticker size:', err);
    }
  };

  const handleDeleteSticker = async (id: string) => {
    if (!confirm('Delete this sticker?')) return;

    setStickers(stickers.filter(sticker => sticker.id !== id));

    if (useSampleData) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${API_URL}/api/v1/boards/${boardId}/stickers/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok && response.status !== 204) {
        throw new Error('Failed to delete sticker');
      }
    } catch (err) {
      console.error('Failed to delete sticker:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete sticker');
      // Reload board to sync state
      fetchBoardFromApi();
    }
  };

  const handleColorChange = async (id: string, color: string) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, color } : sticker
    ));

    if (useSampleData) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const hexColor = tailwindToHex(color);

      await fetch(`${API_URL}/api/v1/boards/${boardId}/stickers/${id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          color: hexColor,
        }),
      });
    } catch (err) {
      console.error('Failed to update sticker color:', err);
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

      {/* Error message */}
      {error && (
        <div className="absolute top-20 left-0 right-0 z-40 bg-red-500/90 backdrop-blur-sm p-4 text-center text-white">
          <div className="max-w-7xl mx-auto">
            <div className="font-semibold mb-2">Error: {error}</div>
            <button
              onClick={handleRetryApi}
              className="bg-white text-red-500 px-4 py-2 rounded hover:bg-red-50 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Controls Panel */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-indigo-200/40 p-4 flex items-center">
        <div className="flex flex-wrap items-center justify-between gap-4 w-full" style={{ paddingLeft: `${HEADER_PADDING_X}px`, paddingRight: `${HEADER_PADDING_X}px` }}>
          <div className="flex items-center gap-4">
            <Link href="/boards" className="text-black text-2xl font-normal tracking-wide hover:text-indigo-600 transition-colors leading-none">
              MIRUMIR
            </Link>
            {board && (
              <div className="text-sm text-slate-700">
                / {board?.title || 'Board'}
                {useSampleData && <span className="ml-2 text-yellow-600">(Sample Data)</span>}
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex flex-wrap items-center gap-2">
              {canEdit && (
                <>
                  <span className="text-sm text-slate-700">New Sticker Color:</span>
                  <div className="flex gap-1">
                    {colors.map((color) => (
                      <button
                        key={color.value}
                        onClick={() => setSelectedColor(color.value)}
                        className={`w-6 h-6 rounded-full ${color.value} border-2 ${selectedColor === color.value ? color.border : 'border-transparent'
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
                </>
              )}
              <div className="text-xs text-slate-500 ml-2">
                {stickers.length} sticker{stickers.length !== 1 ? 's' : ''}
              </div>
            </div>
            {userLogin && (
              <div ref={userMenuRef} className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="text-slate-700 text-base hover:text-indigo-600 transition-colors flex items-center gap-2 font-medium"
                >
                  {userLogin}
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 12 12"
                    fill="currentColor"
                    className={`transition-transform ${showUserMenu ? "rotate-180" : ""}`}
                  >
                    <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="2" fill="none" />
                  </svg>
                </button>

                {showUserMenu && (
                  <div
                    style={{ padding: "4px" }}
                    className="absolute right-0 top-full mt-1 bg-white border border-indigo-200/40 rounded-lg shadow-lg z-20"
                  >
                    <button
                      onClick={handleLogout}
                      style={{ padding: "8px 16px" }}
                      className="text-sm text-red-500 hover:bg-red-50 rounded transition-colors"
                    >
                      Выйти
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

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
            onTextChange={canEdit ? handleTextChange : undefined}
            onDragStop={canEdit ? handleDragStop : undefined}
            onResizeStop={canEdit ? handleResizeStop : undefined}
            onColorChange={canEdit ? handleColorChange : undefined}
            onDelete={canEdit ? handleDeleteSticker : undefined}
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
