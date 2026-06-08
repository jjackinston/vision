import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { Toaster } from "sonner";
import { ServiceWorkerRegistrar } from "@/components/ServiceWorkerRegistrar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], display: "swap" });

// ── Viewport (replaces <meta name="viewport"> in Next.js 14) ──────────
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  minimumScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: [
    { media: "(prefers-color-scheme: dark)",  color: "#0A0B0E" },
    { media: "(prefers-color-scheme: light)", color: "#7C3AED" },
  ],
  viewportFit: "cover",  // honour iPhone notch / safe areas
};

// ── Page metadata ─────────────────────────────────────────────────────
export const metadata: Metadata = {
  title: {
    default: "SellerVision AI — The Bloomberg Terminal for E-Commerce",
    template: "%s | SellerVision AI",
  },
  description: "AI-powered multi-platform e-commerce intelligence. Predict trends, optimize listings, automate operations, and grow your business with AI.",
  keywords: ["amazon seller", "ecommerce intelligence", "AI seller tools", "product research", "inventory management"],
  applicationName: "SellerVision AI",
  authors: [{ name: "SellerVision AI" }],

  // PWA
  manifest: "/manifest.webmanifest",
  appleWebApp: {
    capable: true,
    title: "SellerVision AI",
    statusBarStyle: "black-translucent",
  },
  formatDetection: { telephone: false, date: false, email: false, address: false },

  // Open Graph
  openGraph: {
    title: "SellerVision AI",
    description: "The AI CEO for your e-commerce business",
    type: "website",
    siteName: "SellerVision AI",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "SellerVision AI" }],
  },

  // Icons
  icons: {
    icon: [
      { url: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [{ url: "/icons/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
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
      <ServiceWorkerRegistrar />
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
