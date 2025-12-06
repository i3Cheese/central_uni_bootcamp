"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  BORDER_LEFT,
  BORDER_RIGHT,
  BORDER_BOTTOM,
  BORDER_TOP,
  ENABLE_TOP_BORDER,
} from "./constants/borders";

export default function Home() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    document.title = "Mirumir - Главная";
  }, []);

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
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex items-center justify-center">
        <span className="text-slate-300 text-lg">Загрузка...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
      {/* Main Content */}
      <div
        style={{
          paddingLeft: `${BORDER_LEFT}px`,
          paddingRight: `${BORDER_RIGHT}px`,
          paddingBottom: `${BORDER_BOTTOM}px`,
          paddingTop: ENABLE_TOP_BORDER ? `${BORDER_TOP}px` : "0px",
        }}
      >
        <main
          className={
            ENABLE_TOP_BORDER
              ? "bg-white rounded-2xl flex flex-col items-center justify-center"
              : "bg-white rounded-b-2xl flex flex-col items-center justify-center"
          }
          style={{
            height: ENABLE_TOP_BORDER
              ? `calc(100vh - ${BORDER_TOP}px - ${BORDER_BOTTOM}px)`
              : `calc(100vh - ${BORDER_BOTTOM}px)`,
          }}
        >
          {/* Title */}
          <Link href="/">
            <h1 className="text-5xl font-normal text-black text-center mb-8 tracking-wide hover:text-indigo-600 transition-colors cursor-pointer">
              MIRUMIR
            </h1>
          </Link>

          {/* Subtitle */}
          <p className="text-lg text-[#666666] text-center mb-12 max-w-md">
            Сервис коллаборативных досок для совместной работы
          </p>

          {/* CTA Button */}
          <Link
            href="/auth/register"
            style={{ padding: "20px 60px" }}
            className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white text-lg hover:from-slate-800 hover:via-indigo-900 hover:to-slate-800 transition-all rounded-full shadow-lg"
          >
            Начать пользоваться
          </Link>
        </main>
      </div>
    </div>
  );
}
