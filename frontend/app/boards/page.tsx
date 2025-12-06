"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BoardSummary {
  boardId: number;
  title: string;
  description?: string;
  ownerId: number;
  ownerName?: string;
  permission: "owner" | "view" | "edit";
  stickerCount?: number;
  updatedAt: string;
}

interface BoardsResponse {
  boards: BoardSummary[];
}

export default function BoardsPage() {
  const router = useRouter();
  const [ownBoards, setOwnBoards] = useState<BoardSummary[]>([]);
  const [sharedBoards, setSharedBoards] = useState<BoardSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);
  const [userLogin, setUserLogin] = useState<string | null>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newBoardTitle, setNewBoardTitle] = useState("");
  const [newBoardDescription, setNewBoardDescription] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [infoBoardId, setInfoBoardId] = useState<number | null>(null);
  const [deleteBoardId, setDeleteBoardId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [shareBoardId, setShareBoardId] = useState<number | null>(null);
  const [shareUserId, setShareUserId] = useState("");
  const [sharePermission, setSharePermission] = useState<"view" | "edit">("view");
  const [isSharing, setIsSharing] = useState(false);
  const [shareError, setShareError] = useState<string | null>(null);
  const [shareSuccess, setShareSuccess] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Получить доску для шаринга
  const getShareBoard = (): BoardSummary | null => {
    if (!shareBoardId) return null;
    return ownBoards.find(b => b.boardId === shareBoardId) ||
      sharedBoards.find(b => b.boardId === shareBoardId) || null;
  };

  // Получить доску по ID для отображения информации
  const getInfoBoard = (): BoardSummary | null => {
    if (!infoBoardId) return null;
    return ownBoards.find(b => b.boardId === infoBoardId) ||
      sharedBoards.find(b => b.boardId === infoBoardId) || null;
  };

  // Получить доску для удаления
  const getDeleteBoard = (): BoardSummary | null => {
    if (!deleteBoardId) return null;
    return ownBoards.find(b => b.boardId === deleteBoardId) ||
      sharedBoards.find(b => b.boardId === deleteBoardId) || null;
  };

  // Получаем логин пользователя
  useEffect(() => {
    const login = localStorage.getItem("userLogin");
    setUserLogin(login);
  }, []);

  // Выход из аккаунта
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    localStorage.removeItem("userLogin");
    router.push("/");
  };

  // Закрытие меню при клике вне его
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenuId(null);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Загрузка досок
  useEffect(() => {
    const fetchBoards = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        router.push("/auth");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Загружаем собственные доски
        const ownResponse = await fetch(`${API_URL}/api/v1/boards?filter=own`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (ownResponse.status === 401) {
          localStorage.removeItem("token");
          router.push("/auth");
          return;
        }

        const ownContentType = ownResponse.headers.get("content-type");
        if (!ownContentType || !ownContentType.includes("application/json")) {
          const text = await ownResponse.text();
          throw new Error(`Ошибка сервера: получен не-JSON ответ. Проверьте, что backend запущен на ${API_URL || "http://localhost:8000"}`);
        }

        if (!ownResponse.ok) {
          const errorData = await ownResponse.json().catch(() => ({ detail: { message: "Ошибка загрузки досок" } }));
          throw new Error(errorData.detail?.message || "Ошибка загрузки досок");
        }

        const ownData: BoardsResponse = await ownResponse.json();
        setOwnBoards(ownData.boards || []);

        // Загружаем расшаренные доски
        const sharedResponse = await fetch(`${API_URL}/api/v1/boards?filter=shared`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (sharedResponse.ok) {
          const sharedContentType = sharedResponse.headers.get("content-type");
          if (sharedContentType && sharedContentType.includes("application/json")) {
            const sharedData: BoardsResponse = await sharedResponse.json();
            setSharedBoards(sharedData.boards || []);
          }
        }
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Произошла ошибка при загрузке досок. Проверьте подключение к серверу.");
        }
        console.error("Boards loading error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBoards();
  }, [router]);

  const confirmDeleteBoard = async () => {
    if (!deleteBoardId) return;

    const token = localStorage.getItem("token");
    if (!token) return;

    setIsDeleting(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/boards/${deleteBoardId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      if (response.ok || response.status === 204) {
        setOwnBoards(ownBoards.filter((b) => b.boardId !== deleteBoardId));
        setSharedBoards(sharedBoards.filter((b) => b.boardId !== deleteBoardId));
        setDeleteBoardId(null);
      }
    } catch (err) {
      console.error("Ошибка удаления доски:", err);
    } finally {
      setIsDeleting(false);
    }
  };

  const toggleMenu = (boardId: number) => {
    setOpenMenuId(openMenuId === boardId ? null : boardId);
  };

  // Создание новой доски
  const handleCreateBoard = async () => {
    if (!newBoardTitle.trim()) {
      setCreateError("Введите название доски");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) return;

    setIsCreating(true);
    setCreateError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/boards`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: newBoardTitle.trim(),
          description: newBoardDescription.trim() || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error("Ошибка создания доски");
      }

      const newBoard = await response.json();

      // Добавляем новую доску в список
      setOwnBoards([...ownBoards, { ...newBoard, permission: "owner" }]);

      // Закрываем модалку и очищаем поля
      setShowCreateModal(false);
      setNewBoardTitle("");
      setNewBoardDescription("");
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Произошла ошибка");
    } finally {
      setIsCreating(false);
    }
  };

  // Закрытие модалки создания
  const closeCreateModal = () => {
    setShowCreateModal(false);
    setNewBoardTitle("");
    setNewBoardDescription("");
    setCreateError(null);
  };

  // Шаринг доски
  const handleShareBoard = async () => {
    if (!shareUserId.trim()) {
      setShareError("Введите логин пользователя");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token || !shareBoardId) return;

    setIsSharing(true);
    setShareError(null);
    setShareSuccess(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/boards/${shareBoardId}/share`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userLogin: shareUserId.trim(),
          permission: sharePermission,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || "Ошибка предоставления доступа");
      }

      setShareSuccess(`Доступ успешно предоставлен пользователю ${shareUserId.trim()}`);
      setShareUserId("");
      setSharePermission("view");
    } catch (err) {
      setShareError(err instanceof Error ? err.message : "Произошла ошибка");
    } finally {
      setIsSharing(false);
    }
  };

  // Закрытие модалки шаринга
  const closeShareModal = () => {
    setShareBoardId(null);
    setShareUserId("");
    setSharePermission("view");
    setShareError(null);
    setShareSuccess(null);
  };

  const BoardCard = ({ board, showMenu = true }: { board: BoardSummary; showMenu?: boolean }) => (
    <div className="relative w-[200px] h-[200px] border-2 border-gray-800 rounded-2xl flex flex-col">
      {/* Область доски */}
      <Link
        href={`/boards/${board.boardId}`}
        className="flex-1 rounded-t-2xl hover:bg-gray-50 transition-colors"
      />

      {/* Нижняя панель с названием и меню */}
      <div className="relative flex items-center justify-center px-3 py-2 border-t border-gray-300">
        <span className="text-sm text-gray-700 truncate text-center">
          {board.title}
        </span>

        {showMenu && (
          <button
            onClick={(e) => {
              e.preventDefault();
              toggleMenu(board.boardId);
            }}
            className="absolute right-3 text-gray-600 hover:text-gray-900 p-1"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <circle cx="8" cy="3" r="1.5" />
              <circle cx="8" cy="8" r="1.5" />
              <circle cx="8" cy="13" r="1.5" />
            </svg>
          </button>
        )}
      </div>

      {/* Выпадающее меню */}
      {openMenuId === board.boardId && (
        <div
          ref={menuRef}
          className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 py-1 min-w-[140px]"
        >
          <button
            onClick={() => {
              setInfoBoardId(board.boardId);
              setOpenMenuId(null);
            }}
            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Information
          </button>
          {board.permission === "owner" && (
            <button
              onClick={() => {
                setShareBoardId(board.boardId);
                setOpenMenuId(null);
              }}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              Share board
            </button>
          )}
          {board.permission === "owner" && (
            <button
              onClick={() => {
                setDeleteBoardId(board.boardId);
                setOpenMenuId(null);
              }}
              className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-100"
            >
              Delete board
            </button>
          )}
        </div>
      )}
    </div>
  );

  const AddBoardCard = () => (
    <button
      onClick={() => setShowCreateModal(true)}
      className="w-[200px] h-[200px] border-2 border-gray-300 border-dashed rounded-2xl flex items-center justify-center hover:border-gray-400 hover:bg-gray-50 transition-colors"
    >
      <svg
        width="48"
        height="48"
        viewBox="0 0 48 48"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        className="text-gray-400"
      >
        <line x1="24" y1="8" x2="24" y2="40" />
        <line x1="8" y1="24" x2="40" y2="24" />
      </svg>
    </button>
  );

  // Компонент хедера
  const Header = () => (
    <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200 p-4">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        <Link href="/" className="text-gray-600 text-xl tracking-wide hover:text-gray-900 transition-colors">
          Mirumir
        </Link>
        {userLogin && (
          <div ref={userMenuRef} className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="text-gray-600 text-base hover:text-gray-900 transition-colors flex items-center gap-2"
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
                className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20"
              >
                <button
                  onClick={handleLogout}
                  style={{ padding: "8px 16px" }}
                  className="text-sm text-red-500 hover:bg-gray-100 rounded"
                >
                  Выйти
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#5a5a5a]">
        <Header />
        <main className="mx-4 bg-white min-h-[calc(100vh-56px-16px)] flex items-center justify-center">
          <span className="text-gray-500 text-lg">Загрузка...</span>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#5a5a5a]">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="mx-4 bg-white min-h-[calc(100vh-56px-16px)]" style={{ paddingTop: "48px", paddingLeft: "48px" }}>
        {error && (
          <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-2 mb-8 rounded">
            {error}
          </div>
        )}

        {/* Your boards */}
        <section style={{ marginBottom: "48px" }}>
          <h2 className="text-4xl font-light text-black mb-8">Your boards</h2>
          <div className="flex flex-wrap gap-6">
            {ownBoards.map((board) => (
              <BoardCard key={board.boardId} board={board} />
            ))}
            <AddBoardCard />
          </div>
        </section>

        {/* Shared boards */}
        {sharedBoards.length > 0 && (
          <section>
            <h2 className="text-4xl font-light text-black mb-8">Shared boards</h2>
            <div className="flex flex-wrap gap-6">
              {sharedBoards.map((board) => (
                <BoardCard key={board.boardId} board={board} />
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Модалка создания доски */}
      {showCreateModal && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={closeCreateModal}
        >
          <div
            style={{ padding: "40px" }}
            className="bg-white rounded-2xl w-full max-w-lg shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Заголовок */}
            <h2 style={{ marginBottom: "32px" }} className="text-3xl font-light text-black">
              Создать доску
            </h2>

            {createError && (
              <div style={{ marginBottom: "24px" }} className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded text-sm">
                {createError}
              </div>
            )}

            {/* Форма */}
            <div style={{ marginBottom: "32px" }}>
              {/* Название */}
              <div style={{ marginBottom: "24px" }}>
                <label style={{ marginBottom: "12px", display: "block" }} className="text-base text-gray-600">
                  Название <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newBoardTitle}
                  onChange={(e) => setNewBoardTitle(e.target.value)}
                  placeholder="Введите название доски"
                  maxLength={200}
                  disabled={isCreating}
                  style={{ height: "56px", padding: "0 20px" }}
                  className="w-full bg-[#f5f5f5] text-gray-700 text-base rounded-xl outline-none focus:ring-2 focus:ring-gray-300 disabled:opacity-50"
                />
              </div>

              {/* Описание */}
              <div>
                <label style={{ marginBottom: "12px", display: "block" }} className="text-base text-gray-600">
                  Описание
                </label>
                <textarea
                  value={newBoardDescription}
                  onChange={(e) => setNewBoardDescription(e.target.value)}
                  placeholder="Введите описание (необязательно)"
                  maxLength={1000}
                  disabled={isCreating}
                  rows={4}
                  style={{ padding: "16px 20px" }}
                  className="w-full bg-[#f5f5f5] text-gray-700 text-base rounded-xl outline-none focus:ring-2 focus:ring-gray-300 disabled:opacity-50 resize-none"
                />
              </div>
            </div>

            {/* Кнопки */}
            <div style={{ display: "flex", gap: "16px" }}>
              <button
                onClick={closeCreateModal}
                disabled={isCreating}
                style={{ height: "56px" }}
                className="flex-1 border border-gray-300 text-gray-600 text-base rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateBoard}
                disabled={isCreating}
                style={{ height: "56px" }}
                className="flex-1 bg-[#5a5a5a] text-white text-base rounded-xl hover:bg-[#4a4a4a] transition-colors disabled:opacity-50"
              >
                {isCreating ? "Создание..." : "Создать"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модалка информации о доске */}
      {infoBoardId && getInfoBoard() && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setInfoBoardId(null)}
        >
          <div
            style={{ padding: "40px" }}
            className="bg-white rounded-2xl w-full max-w-lg shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginBottom: "32px" }} className="text-3xl font-light text-black">
              Информация о доске
            </h2>

            <div style={{ marginBottom: "32px" }} className="space-y-4">
              <div className="flex justify-between py-3 border-b border-gray-200">
                <span className="text-gray-500">ID</span>
                <span className="text-gray-800 font-medium">{getInfoBoard()?.boardId}</span>
              </div>

              <div className="flex justify-between py-3 border-b border-gray-200">
                <span className="text-gray-500">Название</span>
                <span className="text-gray-800 font-medium">{getInfoBoard()?.title}</span>
              </div>

              {getInfoBoard()?.description && (
                <div className="py-3 border-b border-gray-200">
                  <span className="text-gray-500 block mb-2">Описание</span>
                  <span className="text-gray-800">{getInfoBoard()?.description}</span>
                </div>
              )}

              <div className="flex justify-between py-3 border-b border-gray-200">
                <span className="text-gray-500">Владелец</span>
                <span className="text-gray-800 font-medium">
                  {getInfoBoard()?.ownerName || `ID: ${getInfoBoard()?.ownerId}`}
                </span>
              </div>

              <div className="flex justify-between py-3 border-b border-gray-200">
                <span className="text-gray-500">Ваши права</span>
                <span className="text-gray-800 font-medium">
                  {getInfoBoard()?.permission === "owner" && "Владелец"}
                  {getInfoBoard()?.permission === "edit" && "Редактирование"}
                  {getInfoBoard()?.permission === "view" && "Просмотр"}
                </span>
              </div>

              {getInfoBoard()?.stickerCount !== undefined && (
                <div className="flex justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-500">Стикеров</span>
                  <span className="text-gray-800 font-medium">{getInfoBoard()?.stickerCount}</span>
                </div>
              )}

              <div className="flex justify-between py-3 border-b border-gray-200">
                <span className="text-gray-500">Обновлено</span>
                <span className="text-gray-800 font-medium">
                  {new Date(getInfoBoard()?.updatedAt || "").toLocaleString("ru-RU")}
                </span>
              </div>
            </div>

            <button
              onClick={() => setInfoBoardId(null)}
              style={{ height: "56px" }}
              className="w-full border border-gray-300 text-gray-600 text-base rounded-xl hover:bg-gray-50 transition-colors"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}

      {/* Модалка подтверждения удаления */}
      {deleteBoardId && getDeleteBoard() && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => !isDeleting && setDeleteBoardId(null)}
        >
          <div
            style={{ padding: "40px" }}
            className="bg-white rounded-2xl w-full max-w-md shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginBottom: "16px" }} className="text-2xl font-light text-black">
              Удалить доску?
            </h2>

            <p style={{ marginBottom: "32px" }} className="text-gray-600">
              Вы уверены, что хотите удалить доску{" "}
              <span className="font-medium text-gray-800">"{getDeleteBoard()?.title}"</span>?
              Это действие нельзя отменить.
            </p>

            <div style={{ display: "flex", gap: "16px" }}>
              <button
                onClick={() => setDeleteBoardId(null)}
                disabled={isDeleting}
                style={{ height: "56px" }}
                className="flex-1 border border-gray-300 text-gray-600 text-base rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Отмена
              </button>
              <button
                onClick={confirmDeleteBoard}
                disabled={isDeleting}
                style={{ height: "56px" }}
                className="flex-1 bg-red-500 text-white text-base rounded-xl hover:bg-red-600 transition-colors disabled:opacity-50"
              >
                {isDeleting ? "Удаление..." : "Удалить"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модалка шаринга доски */}
      {shareBoardId && getShareBoard() && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => !isSharing && closeShareModal()}
        >
          <div
            style={{ padding: "40px" }}
            className="bg-white rounded-2xl w-full max-w-lg shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginBottom: "16px" }} className="text-3xl font-light text-black">
              Поделиться доской
            </h2>

            <p style={{ marginBottom: "32px" }} className="text-gray-600">
              Доска: <span className="font-medium text-gray-800">"{getShareBoard()?.title}"</span>
            </p>

            {shareError && (
              <div style={{ marginBottom: "24px" }} className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded text-sm">
                {shareError}
              </div>
            )}

            {shareSuccess && (
              <div style={{ marginBottom: "24px" }} className="bg-green-100 border border-green-300 text-green-700 px-4 py-3 rounded text-sm">
                {shareSuccess}
              </div>
            )}

            <div style={{ marginBottom: "32px" }}>
              {/* Логин пользователя */}
              <div style={{ marginBottom: "24px" }}>
                <label style={{ marginBottom: "12px", display: "block" }} className="text-base text-gray-600">
                  Логин пользователя <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={shareUserId}
                  onChange={(e) => setShareUserId(e.target.value)}
                  placeholder="Введите логин пользователя (например, user@example.com)"
                  disabled={isSharing}
                  style={{ height: "56px", padding: "0 20px" }}
                  className="w-full bg-[#f5f5f5] text-gray-700 text-base rounded-xl outline-none focus:ring-2 focus:ring-gray-300 disabled:opacity-50"
                />
              </div>

              {/* Уровень доступа */}
              <div>
                <label style={{ marginBottom: "12px", display: "block" }} className="text-base text-gray-600">
                  Уровень доступа
                </label>
                <div style={{ display: "flex", gap: "12px" }}>
                  <button
                    onClick={() => setSharePermission("view")}
                    disabled={isSharing}
                    style={{ height: "56px" }}
                    className={`flex-1 rounded-xl text-base transition-colors disabled:opacity-50 ${sharePermission === "view"
                      ? "bg-[#5a5a5a] text-white"
                      : "bg-[#f5f5f5] text-gray-700 hover:bg-gray-200"
                      }`}
                  >
                    Просмотр
                  </button>
                  <button
                    onClick={() => setSharePermission("edit")}
                    disabled={isSharing}
                    style={{ height: "56px" }}
                    className={`flex-1 rounded-xl text-base transition-colors disabled:opacity-50 ${sharePermission === "edit"
                      ? "bg-[#5a5a5a] text-white"
                      : "bg-[#f5f5f5] text-gray-700 hover:bg-gray-200"
                      }`}
                  >
                    Редактирование
                  </button>
                </div>
              </div>
            </div>

            <div style={{ display: "flex", gap: "16px" }}>
              <button
                onClick={closeShareModal}
                disabled={isSharing}
                style={{ height: "56px" }}
                className="flex-1 border border-gray-300 text-gray-600 text-base rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Закрыть
              </button>
              <button
                onClick={handleShareBoard}
                disabled={isSharing}
                style={{ height: "56px" }}
                className="flex-1 bg-[#5a5a5a] text-white text-base rounded-xl hover:bg-[#4a4a4a] transition-colors disabled:opacity-50"
              >
                {isSharing ? "Отправка..." : "Поделиться"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

