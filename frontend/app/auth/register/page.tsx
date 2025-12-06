"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { BORDER_LEFT, BORDER_RIGHT, BORDER_BOTTOM, BORDER_TOP, ENABLE_TOP_BORDER } from "../../constants/borders";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
      {/* Main Content */}
      <div style={{ 
        paddingLeft: `${BORDER_LEFT}px`, 
        paddingRight: `${BORDER_RIGHT}px`, 
        paddingBottom: `${BORDER_BOTTOM}px`, 
        paddingTop: ENABLE_TOP_BORDER ? `${BORDER_TOP}px` : "0px"
      }}>
        <main 
          className={ENABLE_TOP_BORDER ? "bg-white rounded-2xl flex flex-col items-center pt-32 pb-16" : "bg-white rounded-b-2xl flex flex-col items-center pt-32 pb-16"}
          style={{ height: ENABLE_TOP_BORDER ? `calc(100vh - ${BORDER_TOP}px - ${BORDER_BOTTOM}px)` : `calc(100vh - ${BORDER_BOTTOM}px)` }}
        >
        {/* Title */}
        <Link href="/">
          <h1 className="text-4xl font-normal text-black text-center mb-24 tracking-wide max-w-xs leading-tight hover:text-indigo-600 transition-colors cursor-pointer">
            MIRUMIR
          </h1>
        </Link>

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
            className="w-full h-11 bg-[#dcdcdc] text-[#666666] text-sm text-center placeholder:text-[#666666] outline-none disabled:opacity-50 rounded-lg"
          />

          {/* Password Input */}
          <input
            type="password"
            placeholder="Введите пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            className="w-full h-11 bg-[#dcdcdc] text-[#666666] text-sm text-center placeholder:text-[#666666] outline-none disabled:opacity-50 rounded-lg"
          />

          {/* Confirm Password Input */}
          <input
            type="password"
            placeholder="Подтвердите пароль"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={isLoading}
            onKeyDown={(e) => e.key === "Enter" && handleRegister()}
            className="w-full h-11 bg-[#dcdcdc] text-[#666666] text-sm text-center placeholder:text-[#666666] outline-none disabled:opacity-50 rounded-lg"
          />

          {/* Register Button */}
          <button
            onClick={handleRegister}
            disabled={isLoading}
            className="w-full h-9 bg-[#dcdcdc] text-[#666666] text-sm hover:bg-[#c8c8c8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed rounded-lg"
          >
            {isLoading ? "Загрузка..." : "Зарегистрироваться"}
          </button>

          {/* Back to Login Link */}
          <div className="text-[#666666] text-sm text-center">
            Уже есть аккаунт?{" "}
            <Link
              href="/auth"
              className="text-[#444444] hover:text-[#333333] hover:underline transition-colors"
            >
              Войти
            </Link>
          </div>
        </div>
        </main>
      </div>
    </div>
  );
}

