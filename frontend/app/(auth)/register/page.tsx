import { SignUp } from "@clerk/nextjs";

export const dynamic = "force-dynamic";

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-[#0A0B0E] flex items-center justify-center p-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-black text-lg">SV</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Start your free trial</h1>
          <p className="text-white/40 text-sm mt-1">14 days free · No credit card required</p>
        </div>
        <SignUp
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
            },
          }}
          redirectUrl="/dashboard"
        />
      </div>
    </div>
  );
}
