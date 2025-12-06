"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RegisterResponse {
  userId: number;
  login: string;
  createdAt: string;
}

interface ErrorDetail {
  error: string;
  message: string;
  details?: {
    field?: string;
    reason?: string;
  };
}

export default function RegisterPage() {
  console.log("API_URL", API_URL);
  const router = useRouter();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.title = "Mirumir - Регистрация";
  }, []);

  // Проверяем авторизацию
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/boards");
    }
  }, [router]);

  const handleRegister = async () => {
    // Валидация
    if (!login || !password || !confirmPassword) {
      setError("Заполните все поля");
      return;
    }

    if (login.length < 3) {
      setError("Логин должен быть не менее 3 символов");
      return;
    }

    if (password.length < 8) {
      setError("Пароль должен быть не менее 8 символов");
      return;
    }

    if (password !== confirmPassword) {
      setError("Пароли не совпадают");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ login, password }),
      });

      if (!response.ok) {
        const errorData: { detail: ErrorDetail } = await response.json();
        throw new Error(errorData.detail?.message || "Ошибка регистрации");
      }

      const data: RegisterResponse = await response.json();

      // Перенаправляем на страницу входа после успешной регистрации
      router.push(`/auth?registered=${encodeURIComponent(data.login)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#5a5a5a]">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-gray-600 text-xl tracking-wide hover:text-gray-900 transition-colors">
            Mirumir
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-4 bg-white min-h-[calc(100vh-56px-16px)] flex flex-col items-center pt-32 pb-16">
        {/* Title */}
        <h1 className="text-4xl font-normal text-black text-center mb-24 tracking-wide max-w-xs leading-tight">
          MIRUMIR
        </h1>

        {/* Form */}
        <div className="w-full max-w-[280px] flex flex-col gap-5">
          {/* Error Message */}
          {error && (
            <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-2 text-sm text-center">
              {error}
            </div>
          )}

          {/* Login Input */}
          <input
            type="text"
            placeholder="Введите логин"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            disabled={isLoading}
            className="w-full h-11 bg-[#dcdcdc] text-[#666666] text-sm text-center placeholder:text-[#666666] outline-none disabled:opacity-50"
          />

          {/* Password Input */}
          <input
            type="password"
            placeholder="Введите пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            className="w-full h-11 bg-[#dcdcdc] text-[#666666] text-sm text-center placeholder:text-[#666666] outline-none disabled:opacity-50"
          />

          {/* Confirm Password Input */}
          <input
            type="password"
            placeholder="Подтвердите пароль"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={isLoading}
            onKeyDown={(e) => e.key === "Enter" && handleRegister()}
            className="w-full h-11 bg-[#dcdcdc] text-[#666666] text-sm text-center placeholder:text-[#666666] outline-none disabled:opacity-50"
          />

          {/* Register Button */}
          <button
            onClick={handleRegister}
            disabled={isLoading}
            className="w-full h-9 bg-[#dcdcdc] text-[#666666] text-sm hover:bg-[#c8c8c8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Загрузка..." : "Зарегистрироваться"}
          </button>

          {/* Back to Login Link */}
          <Link
            href="/auth"
            className="text-[#666666] text-sm text-center hover:underline"
          >
            Уже есть аккаунт? Войти
          </Link>
        </div>
      </main>
    </div>
  );
}

