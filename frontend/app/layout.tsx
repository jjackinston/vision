import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { Toaster } from "sonner";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SellerVision AI — The Bloomberg Terminal for E-Commerce",
  description: "AI-powered multi-platform e-commerce intelligence. Predict trends, optimize listings, automate operations, and grow your business with AI.",
  keywords: ["amazon seller", "ecommerce intelligence", "AI seller tools", "product research"],
  openGraph: {
    title: "SellerVision AI",
    description: "The AI CEO for your e-commerce business",
    type: "website",
  },
};

const clerkPubKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryProvider>
      {children}
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          style: { background: "#1A1B22", border: "1px solid rgba(255,255,255,0.1)", color: "#fff" },
        }}
      />
    </QueryProvider>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0A0B0E] text-white antialiased`}>
        {clerkPubKey ? (
          <ClerkProvider>
            <Providers>{children}</Providers>
          </ClerkProvider>
        ) : (
          <Providers>{children}</Providers>
        )}
      </body>
    </html>
  );
}
