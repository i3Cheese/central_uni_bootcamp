// components/StickerBoard.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import CustomDraggableSticker from '../components/sticker';

interface StickerData {
  id: string;
  text: string;
  position: { x: number; y: number };
  color: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function StickerBoard() {
  const [stickers, setStickers] = useState<StickerData[]>([
    { 
      id: '1', 
      text: 'Welcome to the sticker board! Double click to edit.', 
      position: { x: 100, y: 100 }, 
      color: 'bg-yellow-200',
      size: 'md'
    },
    { 
      id: '2', 
      text: 'Drag the top bar to move stickers around', 
      position: { x: 400, y: 150 }, 
      color: 'bg-blue-200',
      size: 'md'
    },
    { 
      id: '3', 
      text: 'Click + button to add more stickers', 
      position: { x: 200, y: 300 }, 
      color: 'bg-green-200',
      size: 'md'
    },
  ]);

  const [selectedColor, setSelectedColor] = useState('bg-yellow-200');
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

  const sizes = [
    { name: 'Small', width: 'w-48', height: 'min-h-24' },
    { name: 'Medium', width: 'w-64', height: 'min-h-32' },
    { name: 'Large', width: 'w-80', height: 'min-h-40' },
  ];

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
      color: selectedColor,
      size: 'md'
    };
    
    setStickers([...stickers, newSticker]);
  };

  const handleTextChange = (id: string, text: string) => {
    setStickers(stickers.map(sticker => 
      sticker.id === id ? { ...sticker, text } : sticker
    ));
  };

  const handleDragStop = (id: string, position: { x: number; y: number }) => {
    setStickers(stickers.map(sticker =>
      sticker.id === id ? { ...sticker, position } : sticker
    ));
  };

  const handleDeleteSticker = (id: string) => {
    setStickers(stickers.filter(sticker => sticker.id !== id));
  };

  

  const handleColorChange = (id: string, color: string) => {
  setStickers(stickers.map(sticker =>
    sticker.id === id ? { ...sticker, color } : sticker
  ));
  };

  

  

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-gray-50 to-gray-100 overflow-hidden">
      {/* Controls Panel */}
      <div className="absolute top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-800">Mirumir</h1>
            <div className="flex items-center gap-2">
              
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-gray-600">New Sticker Color:</span>
              <div className="flex gap-1">
                {colors.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => setSelectedColor(color.value)}
                    className={`w-6 h-6 rounded-full ${color.value} border-2 ${selectedColor === color.value ? color.border : 'border-transparent'} transition-all hover:scale-110`}
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
            
            <button
              //onClick={}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              disabled={stickers.length === 0}
            >
              Users
            </button>

            

            
          </div>
        </div>
      </div>

      {/* Board Container */}
      <div 
        ref={boardRef}
        className="relative w-full h-full pt-20" // pt-20 to account for controls height
      >
        {/* Grid Background Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(90deg,#f0f0f0_1px,transparent_1px),linear-gradient(#f0f0f0_1px,transparent_1px)] bg-[size:20px_20px] opacity-50"></div>
        
        {/* Stickers */}
        {stickers.map((sticker) => (
          <CustomDraggableSticker
            key={sticker.id}
            id={sticker.id}
            initialText={sticker.text}
            initialPosition={sticker.position}
            color={sticker.color}
            onTextChange={handleTextChange}
            onDragStop={handleDragStop}
            onColorChange={handleColorChange}
            onDelete={handleDeleteSticker}
          />
        ))}

        
      </div>

      {/* Stats Footer 
      <div className="absolute bottom-0 left-0 right-0 bg-white/80 backdrop-blur-sm border-t border-gray-200 p-2">
        <div className="max-w-7xl mx-auto text-center text-sm text-gray-600">
          <span className="font-medium">{stickers.length}</span> stickers • 
          <span className="ml-4">Drag the top bar of any sticker to move it</span> • 
          <span className="ml-4">Double-click text to edit</span>
        </div>
      </div>*/}
    </div>
  );
}