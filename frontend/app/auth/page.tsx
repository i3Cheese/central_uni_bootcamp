"use client";

import { useState, useEffect } from "react";
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

export default function AuthPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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
      setError(err instanceof Error ? err.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#5a5a5a]">
      {/* Header */}
      <header style={{ padding: "0 24px" }} className="flex items-center justify-between h-14">
        <Link href="/" className="text-[#a0a0a0] text-xl tracking-wide hover:text-white transition-colors">
          Mirumir
        </Link>
        <span className="text-[#a0a0a0] text-xl tracking-wide">Auth Main</span>
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
            className="w-full h-9 bg-[#dcdcdc] text-[#666666] text-sm hover:bg-[#c8c8c8] transition-colors flex items-center justify-center"
          >
            Регистрация
          </Link>
        </div>
      </main>
    </div>
  );
}

