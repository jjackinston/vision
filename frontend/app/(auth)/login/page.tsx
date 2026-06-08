import { SignIn } from "@clerk/nextjs";

export const dynamic = "force-dynamic";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-[#0A0B0E] flex">
      {/* Left — branding */}
      <div className="hidden lg:flex w-1/2 flex-col justify-between p-12 bg-gradient-to-br from-violet-950/50 to-[#0A0B0E] border-r border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">SV</span>
          </div>
          <span className="text-white font-bold text-lg">SellerVision AI</span>
        </div>
        <div>
          <h1 className="text-4xl font-black text-white leading-tight mb-6">
            The Bloomberg Terminal<br />for E-Commerce
          </h1>
          <div className="space-y-4">
            {[
              "AI CEO tells you exactly what to do daily",
              "Predict product success before launch",
              "Autonomous agents work 24/7 for you",
              "One platform for all 6 marketplaces",
            ].map((point) => (
              <div key={point} className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 bg-violet-400 rounded-full" />
                </div>
                <span className="text-white/60 text-sm">{point}</span>
              </div>
            ))}
          </div>
        </div>
        <p className="text-white/20 text-xs">
          Trusted by 3,500+ e-commerce sellers worldwide
        </p>
      </div>

      {/* Right — sign in */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <SignIn
            appearance={{
              variables: {
                colorPrimary: "#8B5CF6",
                colorBackground: "#13141A",
                colorInputBackground: "rgba(255,255,255,0.05)",
                colorText: "#ffffff",
                colorTextSecondary: "rgba(255,255,255,0.5)",
                borderRadius: "0.75rem",
              },
              elements: {
                card: "shadow-none border border-white/10",
                headerTitle: "text-white",
              },
            }}
            redirectUrl="/dashboard"
          />
        </div>
      </div>
    </div>
  );
}
