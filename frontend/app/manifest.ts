import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "SellerVision AI",
    short_name: "SellerVision",
    description: "The AI CEO for your e-commerce business — product research, inventory, analytics, and automation in one platform.",
    start_url: "/dashboard",
    display: "standalone",
    background_color: "#0A0B0E",
    theme_color: "#7C3AED",
    orientation: "portrait-primary",
    categories: ["business", "productivity", "finance"],
    icons: [
      {
        src: "/icons/icon-192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/icon-192-maskable.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "maskable",
      },
      {
        src: "/icons/icon-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/icon-512-maskable.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
    screenshots: [
      {
        src: "/screenshots/dashboard-mobile.png",
        sizes: "390x844",
        type: "image/png",
        // @ts-ignore — form_factor is valid per spec but not yet in TS types
        form_factor: "narrow",
        label: "AI CEO Dashboard",
      },
    ],
    shortcuts: [
      {
        name: "Product Research",
        short_name: "Products",
        url: "/products",
        description: "Search and track products across all marketplaces",
        icons: [{ src: "/icons/shortcut-products.png", sizes: "96x96" }],
      },
      {
        name: "Analytics",
        url: "/analytics",
        description: "Revenue, profit and performance metrics",
        icons: [{ src: "/icons/shortcut-analytics.png", sizes: "96x96" }],
      },
    ],
  };
}
