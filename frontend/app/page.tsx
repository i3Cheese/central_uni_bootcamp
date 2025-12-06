"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function Home() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/boards");
    } else {
      setIsChecking(false);
    }
  }, [router]);

  if (isChecking) {
    return (
      <div className="min-h-screen bg-[#5a5a5a] flex items-center justify-center">
        <span className="text-[#a0a0a0] text-lg">Загрузка...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#5a5a5a]">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="text-gray-600 text-xl tracking-wide hover:text-gray-900 transition-colors">
            Mirumir
          </Link>

          {/* Auth Buttons */}
          <div className="flex gap-4">
            <Link
              href="/auth"
              className="text-gray-600 text-base hover:text-gray-900 transition-colors"
            >
              Войти
            </Link>
            <Link
              href="/auth/register"
              className="text-gray-600 text-base hover:text-gray-900 transition-colors"
            >
              Регистрация
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-4 bg-white min-h-[calc(100vh-56px-16px)] flex flex-col items-center justify-center">
        {/* Title */}
        <h1 className="text-5xl font-normal text-black text-center mb-8 tracking-wide">
          MIRUMIR
        </h1>

        {/* Subtitle */}
        <p className="text-lg text-[#666666] text-center mb-12 max-w-md">
          Сервис коллаборативных досок для совместной работы
        </p>

        {/* CTA Button */}
        <Link
          href="/auth/register"
          style={{ padding: "20px 60px" }}
          className="bg-[#5a5a5a] text-white text-lg hover:bg-[#4a4a4a] transition-colors rounded-full"
        >
          Начать пользоваться
        </Link>
      </main>
    </div>
  );
}
