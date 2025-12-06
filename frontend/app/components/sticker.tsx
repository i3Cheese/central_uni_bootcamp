// components/ResizableSticker.tsx
"use client";

import { useState, useRef, useEffect, useCallback } from "react";

interface StickerProps {
  id: string;
  initialText: string;
  initialPosition?: { x: number; y: number };
  initialSize?: { width: number; height: number };
  color?: string;
  onTextChange?: (id: string, text: string) => void;
  onDragStop?: (id: string, position: { x: number; y: number }) => void;
  onResizeStop?: (id: string, size: { width: number; height: number }) => void;
  onDelete?: (id: string) => void;
  onColorChange?: (id: string, color: string) => void;
}

export default function ResizableSticker({
  id,
  initialText,
  initialPosition = { x: 100, y: 100 },
  initialSize = { width: 256, height: 128 },
  color = "bg-yellow-200",
  onTextChange,
  onDragStop,
  onResizeStop,
  onDelete,
  onColorChange, // New prop
}: StickerProps) {
  const [text, setText] = useState(initialText);
  const [isEditing, setIsEditing] = useState(false);
  const [position, setPosition] = useState(initialPosition);
  const [size, setSize] = useState(initialSize);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [currentColor, setCurrentColor] = useState(color);
  const [showColorPicker, setShowColorPicker] = useState(false);

  const stickerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const animationFrameRef = useRef<number>(0);
  const colorPickerRef = useRef<HTMLDivElement>(null);

  // Color presets
  const colorOptions = [
    { name: "Yellow", value: "bg-yellow-200", border: "border-yellow-300" },
    { name: "Blue", value: "bg-blue-200", border: "border-blue-300" },
    { name: "Green", value: "bg-green-200", border: "border-green-300" },
    { name: "Pink", value: "bg-pink-200", border: "border-pink-300" },
    { name: "Purple", value: "bg-purple-200", border: "border-purple-300" },
    { name: "Red", value: "bg-red-200", border: "border-red-300" },
    { name: "Cyan", value: "bg-cyan-200", border: "border-cyan-300" },
    { name: "Orange", value: "bg-orange-200", border: "border-orange-300" },
  ];

  // Handle color change
  const handleColorChange = (colorValue: string) => {
    setCurrentColor(colorValue);
    setShowColorPicker(false);
    onColorChange?.(id, colorValue);
  };

  // Close color picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        colorPickerRef.current &&
        !colorPickerRef.current.contains(event.target as Node)
      ) {
        setShowColorPicker(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // ===== DRAGGING FUNCTIONS =====
  const handleDragStart = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.preventDefault();
      e.stopPropagation();

      if (!onDragStop || isEditing || isResizing || showColorPicker) return;

      setIsDragging(true);

      // Store the initial mouse position and sticker position
      const startClientX =
        "touches" in e ? e.touches[0].clientX : (e as React.MouseEvent).clientX;
      const startClientY =
        "touches" in e ? e.touches[0].clientY : (e as React.MouseEvent).clientY;
      const startPosition = { ...position };

      // Add global event listeners
      const handleMove = (moveEvent: MouseEvent | TouchEvent) => {
        if (!animationFrameRef.current) {
          animationFrameRef.current = requestAnimationFrame(() => {
            const clientX =
              "touches" in moveEvent
                ? (moveEvent as TouchEvent).touches[0].clientX
                : (moveEvent as MouseEvent).clientX;
            const clientY =
              "touches" in moveEvent
                ? (moveEvent as TouchEvent).touches[0].clientY
                : (moveEvent as MouseEvent).clientY;

            // Calculate how far the mouse has moved from the start
            const deltaX = clientX - startClientX;
            const deltaY = clientY - startClientY;

            // Apply the same movement to the sticker position
            const newX = startPosition.x + deltaX;
            const newY = startPosition.y + deltaY;

            setPosition({ x: newX, y: newY });

            animationFrameRef.current = 0;
          });
        }
      };

      const handleEnd = (endEvent: MouseEvent | TouchEvent) => {
        setIsDragging(false);

        // Get final position
        const clientX =
          "changedTouches" in endEvent
            ? (endEvent as TouchEvent).changedTouches[0].clientX
            : (endEvent as MouseEvent).clientX;
        const clientY =
          "changedTouches" in endEvent
            ? (endEvent as TouchEvent).changedTouches[0].clientY
            : (endEvent as MouseEvent).clientY;

        // Calculate final position based on movement
        const deltaX = clientX - startClientX;
        const deltaY = clientY - startClientY;

        const finalPosition = {
          x: startPosition.x + deltaX,
          y: startPosition.y + deltaY,
        };

        setPosition(finalPosition);
        onDragStop?.(id, finalPosition);

        // Cleanup
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = 0;

        if ("touches" in e) {
          document.removeEventListener("touchmove", handleMove);
          document.removeEventListener("touchend", handleEnd);
        } else {
          document.removeEventListener("mousemove", handleMove);
          document.removeEventListener("mouseup", handleEnd);
        }

        document.body.style.userSelect = "";
        document.body.style.cursor = "";
      };

      if ("touches" in e) {
        document.addEventListener("touchmove", handleMove, { passive: false });
        document.addEventListener("touchend", handleEnd);
      } else {
        document.addEventListener("mousemove", handleMove);
        document.addEventListener("mouseup", handleEnd);
      }

      document.body.style.userSelect = "none";
      document.body.style.cursor = "grabbing";
    },
    [id, isEditing, isResizing, onDragStop, position, showColorPicker],
  );

  const canDrag = !!onDragStop;

  // ===== RESIZING FUNCTIONS =====
  const handleResizeStart = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.preventDefault();
      e.stopPropagation();

      if (!onResizeStop || isEditing || isDragging || showColorPicker) return;

      setIsResizing(true);

      // Store initial size
      const startSize = { ...size };
      const startClientX = "touches" in e ? e.touches[0].clientX : e.clientX;
      const startClientY = "touches" in e ? e.touches[0].clientY : e.clientY;

      // Add global event listeners
      const handleMove = (moveEvent: MouseEvent | TouchEvent) => {
        if (!animationFrameRef.current) {
          animationFrameRef.current = requestAnimationFrame(() => {
            const clientX =
              "touches" in moveEvent
                ? (moveEvent as TouchEvent).touches[0].clientX
                : (moveEvent as MouseEvent).clientX;
            const clientY =
              "touches" in moveEvent
                ? (moveEvent as TouchEvent).touches[0].clientY
                : (moveEvent as MouseEvent).clientY;

            // Calculate delta from start
            const deltaX = clientX - startClientX;
            const deltaY = clientY - startClientY;

            // Calculate new size (minimum 150px x 100px)
            const newWidth = Math.max(150, startSize.width + deltaX);
            const newHeight = Math.max(100, startSize.height + deltaY);

            setSize({ width: newWidth, height: newHeight });

            animationFrameRef.current = 0;
          });
        }
      };

      const handleEnd = (endEvent: MouseEvent | TouchEvent) => {
        setIsResizing(false);

        // Get final position
        const clientX =
          "changedTouches" in endEvent
            ? (endEvent as TouchEvent).changedTouches[0].clientX
            : (endEvent as MouseEvent).clientX;
        const clientY =
          "changedTouches" in endEvent
            ? (endEvent as TouchEvent).changedTouches[0].clientY
            : (endEvent as MouseEvent).clientY;

        // Calculate final size
        const deltaX = clientX - startClientX;
        const deltaY = clientY - startClientY;

        const finalWidth = Math.max(150, startSize.width + deltaX);
        const finalHeight = Math.max(100, startSize.height + deltaY);

        const finalSize = { width: finalWidth, height: finalHeight };
        setSize(finalSize);
        onResizeStop?.(id, finalSize);

        // Cleanup
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = 0;

        if ("touches" in e) {
          document.removeEventListener("touchmove", handleMove);
          document.removeEventListener("touchend", handleEnd);
        } else {
          document.removeEventListener("mousemove", handleMove);
          document.removeEventListener("mouseup", handleEnd);
        }

        document.body.style.userSelect = "";
        document.body.style.cursor = "";
      };

      if ("touches" in e) {
        document.addEventListener("touchmove", handleMove, { passive: false });
        document.addEventListener("touchend", handleEnd);
      } else {
        document.addEventListener("mousemove", handleMove);
        document.addEventListener("mouseup", handleEnd);
      }

      document.body.style.userSelect = "none";
      document.body.style.cursor = "nwse-resize";
    },
    [id, isEditing, isDragging, size, onResizeStop, showColorPicker],
  );

  const canResize = !!onResizeStop;
  const canEditText = !!onTextChange;
  const canChangeColor = !!onColorChange;

  // Clean up on unmount
  useEffect(() => {
    return () => {
      cancelAnimationFrame(animationFrameRef.current);
    };
  }, []);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      const scrollHeight = textareaRef.current.scrollHeight;
      const minHeight = size.height - 100; // Account for padding and controls
      textareaRef.current.style.height = `${Math.max(scrollHeight, minHeight)}px`;
    }
  }, [text, size.height]);

  // Calculate number of rows based on height
  const calculateRows = () => {
    const minRowHeight = 24;
    return Math.max(3, Math.floor(size.height / minRowHeight) - 1);
  };

  // Handle text changes
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);
    onTextChange?.(id, newText);
  };

  // Prevent text selection while dragging/resizing
  useEffect(() => {
    const handleSelectStart = (e: Event) => {
      if (isDragging || isResizing) {
        e.preventDefault();
      }
    };

    document.addEventListener("selectstart", handleSelectStart);
    return () => {
      document.removeEventListener("selectstart", handleSelectStart);
    };
  }, [isDragging, isResizing]);

  return (
    <div
      ref={stickerRef}
      className={`absolute z-10 ${isDragging ? "cursor-grabbing" : canDrag ? "cursor-move" : "cursor-default"} select-none`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: `${size.width}px`,
        minHeight: `${size.height}px`,
      }}
    >
      <div
        className={`${currentColor}  shadow-lg/20 p-4 border-2 border-white/50 transition-all duration-150 h-full ${
          isDragging
            ? "scale-[1.02] shadow-2xl border-blue-300/50 opacity-90"
            : isResizing
              ? "scale-[1.01] border-green-300/50 shadow-xl"
              : "hover:shadow-xl hover:scale-[1.005]"
        }`}
      >
        {/* Drag Handle - Top Bar */}
        <div
          className={`pb-3 mb-3 border-b ${canDrag ? "border-gray-300/50 cursor-move active:cursor-grabbing group/drag" : "border-gray-200/30 cursor-default opacity-60"}`}
          onMouseDown={canDrag ? handleDragStart : undefined}
          onTouchStart={canDrag ? handleDragStart : undefined}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className={`w-8 h-1.5 rounded-full transition-colors ${canDrag ? "bg-gray-400/70 group-hover/drag:bg-blue-500/70" : "bg-gray-300/40"}`}
              ></div>
              <div
                className={`w-1 h-1 rounded-full ${canDrag ? "bg-gray-400/50 group-hover/drag:bg-blue-500/50" : "bg-gray-300/30"}`}
              ></div>
              <div
                className={`w-1 h-1 rounded-full ${canDrag ? "bg-gray-400/50 group-hover/drag:bg-blue-500/50" : "bg-gray-300/30"}`}
              ></div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="relative h-full">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleTextChange}
            onFocus={() => canEditText && setIsEditing(true)}
            onBlur={() => setIsEditing(false)}
            readOnly={!canEditText}
            className={`w-full bg-transparent border-none outline-none resize-none placeholder:text-gray-500/70 transition-all ${
              isEditing
                ? "bg-white/30 rounded-lg p-2 ring-2 ring-blue-400/50"
                : ""
            } ${isDragging || isResizing ? "pointer-events-none opacity-80" : canEditText ? "cursor-text" : "cursor-default"}`}
            rows={calculateRows()}
            placeholder={canEditText ? "Click to edit text..." : ""}
            style={{
              minHeight: `${Math.max(50, size.height - 100)}px`,
            }}
          />

          {/* Resize Handle - Bottom Right Corner */}
          {canResize && (
            <div
              className="absolute bottom-0 right-0 w-8 h-8 cursor-nwse-resize group/resize"
              onMouseDown={handleResizeStart}
              onTouchStart={handleResizeStart}
            >
              {/* Corner visual - always visible */}
              <div className="absolute bottom-1 right-1 w-5 h-5 border-r-2 border-b-2 border-gray-400/60 group-hover/resize:border-blue-500 group-active/resize:border-green-500 transition-all duration-200"></div>

              {/* Hover highlight effect */}
              <div className="absolute bottom-0 right-0 w-8 h-8 rounded-tl-lg bg-gradient-to-tl from-transparent via-transparent to-transparent group-hover/resize:from-blue-100/30 group-hover/resize:via-blue-100/20 group-hover/resize:to-blue-100/10 group-active/resize:from-green-100/40 group-active/resize:via-green-100/20 group-active/resize:to-green-100/10 transition-all duration-200"></div>

              {/* Animated resize indicator */}
              <div className="absolute bottom-2 right-2 flex flex-col items-end justify-end opacity-0 group-hover/resize:opacity-100 group-active/resize:opacity-100 transition-opacity duration-200">
                <div className="flex gap-0.5 mb-0.5">
                  <div
                    className={`w-1.5 h-1.5 rounded-full ${isResizing ? "bg-green-500 animate-pulse" : "bg-blue-500"}`}
                  ></div>
                  <div
                    className={`w-1.5 h-1.5 rounded-full ${isResizing ? "bg-green-500 animate-pulse" : "bg-blue-500"}`}
                  ></div>
                </div>
                <div className="flex gap-0.5">
                  <div
                    className={`w-1.5 h-1.5 rounded-full ${isResizing ? "bg-green-500 animate-pulse" : "bg-blue-500"}`}
                  ></div>
                </div>
              </div>

              {/* Size indicator during resize */}
              {isResizing && (
                <div className="absolute -top-8 -right-8 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-90 whitespace-nowrap">
                  {Math.round(size.width)} × {Math.round(size.height)}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex justify-between items-center mt-3 pt-2 border-t border-gray-300/50">
          <div className="flex gap-1 relative">
            {/* Color Picker Button */}
            {canChangeColor && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowColorPicker(!showColorPicker);
                }}
                className="text-xs  text-gray-700 px-2 py-1 rounded hover: transition-colors flex items-center gap-1"
                title="Change color"
              >
                <span>Change Color</span>
              </button>
            )}

            {/* Color Picker Popup */}
            {canChangeColor && showColorPicker && (
              <div
                ref={colorPickerRef}
                className="absolute bottom-full right-0 mb-2 bg-white rounded-lg shadow-xl border border-gray-200 p-3 z-50 w-64"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Quick Color Wheel */}
                <div>
                  <div className="text-xs text-gray-500 mb-2">Colors</div>
                  <div className="flex flex-wrap gap-1">
                    {colorOptions.slice(0, 8).map((colorOption) => (
                      <button
                        key={colorOption.value}
                        onClick={() => handleColorChange(colorOption.value)}
                        className={`flex-1 min-w-[calc(25%-4px)] h-8 rounded-md ${colorOption.value} border ${
                          currentColor === colorOption.value
                            ? "border-gray-800 ring-2 ring-offset-1 ring-gray-400"
                            : "border-gray-200 hover:border-gray-400"
                        } transition-all`}
                        title={colorOption.name}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          {/* Delete Button */}
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(id);
              }}
              className="text-m  text-red-700 px-2 py-1 rounded hover:bg-red-500/20 transition-colors"
              title="Delete sticker"
            >
              🗑️
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
