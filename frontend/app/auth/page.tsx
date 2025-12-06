"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface LoginResponse {
  userId: number;
  login: string;
  token: string;
  expiresAt: string;
}

interface ErrorDetail {
  error: string;
  message: string;
  details?: {
    field?: string;
    reason?: string;
  };
}

function AuthContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    document.title = "Mirumir - Вход";
  }, []);

  // Проверяем авторизацию и редирект после регистрации
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/boards");
      return;
    }

    const registered = searchParams.get("registered");
    if (registered) {
      setSuccess(`Пользователь ${registered} успешно зарегистрирован! Теперь войдите в систему.`);
      setLogin(registered);
    }
  }, [searchParams, router]);

  const handleLogin = async () => {
    if (!login || !password) {
      setError("Заполните все поля");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ login, password }),
      });

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        throw new Error(`Ошибка сервера: получен не-JSON ответ. Проверьте, что backend запущен на ${API_URL || "http://localhost:8000"}`);
      }

      if (!response.ok) {
        const errorData: { detail: ErrorDetail } = await response.json();
        throw new Error(errorData.detail?.message || "Ошибка авторизации");
      }

      const data: LoginResponse = await response.json();

      // Сохраняем токен в localStorage
      localStorage.setItem("token", data.token);
      localStorage.setItem("userId", String(data.userId));
      localStorage.setItem("userLogin", data.login);

      // Перенаправляем на страницу досок
      router.push("/boards");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError("Произошла ошибка при авторизации. Проверьте подключение к серверу.");
      }
      console.error("Login error:", err);
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

          {/* Success Message */}
          {success && (
            <div className="bg-green-100 border border-green-300 text-green-700 px-4 py-2 text-sm text-center">
              {success}
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
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            className="w-full h-11 bg-[#dcdcdc] text-[#666666] text-sm text-center placeholder:text-[#666666] outline-none disabled:opacity-50"
          />

          {/* Login Button */}
          <button
            onClick={handleLogin}
            disabled={isLoading}
            className="w-full h-9 bg-[#dcdcdc] text-[#666666] text-sm hover:bg-[#c8c8c8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Загрузка..." : "Войти"}
          </button>

          {/* Register Link */}
          <Link
            href="/auth/register"
            className="mt-5 text-[#666666] text-sm text-center hover:underline"
          >
            Еще нет аккаунта? Зарегистрироваться
          </Link>
        </div>
      </main>
    </div>
  );
}

export default function AuthPage() {
  return (
    <Suspense fallback={<div>Загрузка...</div>}>
      <AuthContent />
    </Suspense>
  );
}
