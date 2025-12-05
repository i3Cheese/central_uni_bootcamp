import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#5a5a5a]">
      {/* Header */}
      <header style={{ padding: "0 24px" }} className="flex items-center justify-between h-14">
        <span className="text-[#a0a0a0] text-xl tracking-wide">Mirumir</span>
        
        {/* Auth Buttons */}
        <div className="flex h-full gap-4">
          <Link
            href="/auth"
            className="h-full px-6 flex items-center text-[#a0a0a0] text-base hover:bg-[#4a4a4a] transition-colors"
          >
            Войти
          </Link>
          <Link
            href="/auth/register"
            className="h-full px-6 flex items-center text-[#a0a0a0] text-base hover:bg-[#4a4a4a] transition-colors"
          >
            Регистрация
          </Link>
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
