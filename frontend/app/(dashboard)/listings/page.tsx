"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Sparkles, Globe, Plus, Check, RefreshCw, ExternalLink, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const MARKETPLACES = ["amazon", "walmart", "shopify", "ebay", "tiktok", "etsy"];

const MARKETPLACE_COLORS: Record<string, string> = {
  amazon: "bg-amber-500/20 text-amber-400 border-amber-500/20",
  walmart: "bg-blue-500/20 text-blue-400 border-blue-500/20",
  shopify: "bg-violet-500/20 text-violet-400 border-violet-500/20",
  ebay: "bg-red-500/20 text-red-400 border-red-500/20",
  tiktok: "bg-pink-500/20 text-pink-400 border-pink-500/20",
  etsy: "bg-orange-500/20 text-orange-400 border-orange-500/20",
};

export default function ListingsPage() {
  const [tab, setTab] = useState<"builder" | "manager" | "optimizer">("builder");
  const [selectedMarketplaces, setSelectedMarketplaces] = useState<string[]>(["amazon"]);
  const [generatedListings, setGeneratedListings] = useState<Record<string, any>>({});
  const [activeMarketplace, setActiveMarketplace] = useState("amazon");

  const [productData, setProductData] = useState({
    title: "",
    category: "",
    features: "",
    target_audience: "",
    price: "",
    brand: "",
  });
  const [keywords, setKeywords] = useState("");

  const generateMutation = useMutation({
    mutationFn: () => api.generateMultiPlatformListings(productData, selectedMarketplaces),
    onSuccess: (data) => {
      setGeneratedListings(data);
      toast.success(`Listings generated for ${selectedMarketplaces.length} platform${selectedMarketplaces.length !== 1 ? "s" : ""}`);
    },
    onError: () => toast.error("Listing generation failed — try again"),
  });

  const toggleMarketplace = (mp: string) =>
    setSelectedMarketplaces((prev) =>
      prev.includes(mp) ? prev.filter((x) => x !== mp) : [...prev, mp]
    );

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold text-white">AI Listing Builder</h1>
            <Badge className="bg-blue-500/20 text-blue-400 border-0 text-xs">Modules 9 + 15</Badge>
          </div>
          <p className="text-sm text-white/40">
            Generate SEO-optimized listings for all platforms simultaneously
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white/5 rounded-lg p-1 w-fit">
        {[
          { id: "builder", label: "AI Builder" },
          { id: "manager", label: "Listing Manager" },
          { id: "optimizer", label: "SEO Optimizer" },
        ].map((t) => (
          <button key={t.id} onClick={() => setTab(t.id as any)}
            className={cn("px-4 py-1.5 rounded-md text-xs font-medium transition-all",
              tab === t.id ? "bg-blue-600 text-white" : "text-white/40 hover:text-white")}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === "builder" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input panel */}
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Product Information</p>

            <div className="space-y-3 mb-5">
              {[
                { key: "title", label: "Product Name / Idea", placeholder: "Bamboo travel coffee mug with strainer" },
                { key: "brand", label: "Brand Name", placeholder: "EcoHome" },
                { key: "category", label: "Category", placeholder: "Kitchen & Dining" },
                { key: "target_audience", label: "Target Audience", placeholder: "Coffee lovers, eco-conscious travelers" },
                { key: "price", label: "Price Point", placeholder: "29.99" },
              ].map(({ key, label, placeholder }) => (
                <div key={key}>
                  <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">{label}</label>
                  <input
                    value={(productData as any)[key]}
                    onChange={(e) => setProductData((p) => ({ ...p, [key]: e.target.value }))}
                    placeholder={placeholder}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/20 outline-none focus:border-blue-500/50"
                  />
                </div>
              ))}
              <div>
                <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">Key Features</label>
                <textarea
                  value={productData.features}
                  onChange={(e) => setProductData((p) => ({ ...p, features: e.target.value }))}
                  placeholder="• Leak-proof bamboo lid&#10;• 16oz capacity&#10;• Built-in stainless steel strainer&#10;• Dishwasher safe"
                  rows={4}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/20 outline-none focus:border-blue-500/50 resize-none"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">
                  Target Keywords (optional)
                </label>
                <input
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="travel mug, bamboo coffee mug, eco travel mug..."
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/20 outline-none focus:border-blue-500/50"
                />
              </div>
            </div>

            {/* Platform selector */}
            <div className="mb-5">
              <p className="text-[10px] font-semibold uppercase text-white/30 mb-2">
                Generate For
              </p>
              <div className="flex flex-wrap gap-2">
                {MARKETPLACES.map((mp) => (
                  <button
                    key={mp}
                    onClick={() => toggleMarketplace(mp)}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium capitalize transition-all",
                      selectedMarketplaces.includes(mp)
                        ? MARKETPLACE_COLORS[mp]
                        : "bg-white/3 border-white/8 text-white/40 hover:text-white"
                    )}
                  >
                    {selectedMarketplaces.includes(mp) && <Check className="w-3 h-3" />}
                    {mp}
                  </button>
                ))}
              </div>
            </div>

            <Button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending || !productData.title || selectedMarketplaces.length === 0}
              className="w-full bg-blue-600 hover:bg-blue-500 h-10"
            >
              {generateMutation.isPending ? (
                <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Generating {selectedMarketplaces.length} listings...</>
              ) : (
                <><Sparkles className="w-4 h-4 mr-2" />Generate AI Listings</>
              )}
            </Button>
          </div>

          {/* Results panel */}
          <div>
            {Object.keys(generatedListings).length > 0 ? (
              <div>
                {/* Marketplace tabs */}
                <div className="flex gap-1 mb-4 bg-white/5 rounded-lg p-1 overflow-x-auto">
                  {Object.keys(generatedListings).map((mp) => (
                    <button
                      key={mp}
                      onClick={() => setActiveMarketplace(mp)}
                      className={cn(
                        "px-3 py-1.5 rounded-md text-xs font-medium capitalize whitespace-nowrap transition-all",
                        activeMarketplace === mp ? "bg-white/15 text-white" : "text-white/40 hover:text-white"
                      )}
                    >
                      {mp}
                    </button>
                  ))}
                </div>

                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeMarketplace}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    className="bg-[#111218] border border-white/5 rounded-xl p-5 space-y-4"
                  >
                    {(() => {
                      const listing = generatedListings[activeMarketplace];
                      if (!listing || listing instanceof Error) return <p className="text-red-400 text-sm">Generation failed</p>;

                      return (
                        <>
                          {/* SEO Score */}
                          {listing.seo_score && (
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-white/40">SEO Score</span>
                              <span className={cn("text-sm font-bold",
                                listing.seo_score >= 80 ? "text-emerald-400" :
                                listing.seo_score >= 60 ? "text-amber-400" : "text-red-400")}>
                                {listing.seo_score}/100
                              </span>
                            </div>
                          )}

                          {/* Title */}
                          {listing.title && (
                            <div>
                              <div className="flex items-center justify-between mb-1.5">
                                <p className="text-[10px] font-semibold uppercase text-white/30">Title</p>
                                <button onClick={() => copyToClipboard(listing.title)} className="text-white/20 hover:text-white/60">
                                  <Copy className="w-3 h-3" />
                                </button>
                              </div>
                              <p className="text-sm text-white leading-snug bg-white/3 rounded-lg p-3">{listing.title}</p>
                            </div>
                          )}

                          {/* Bullet Points */}
                          {(listing.bullet_points || listing.key_features)?.length > 0 && (
                            <div>
                              <p className="text-[10px] font-semibold uppercase text-white/30 mb-1.5">
                                {listing.bullet_points ? "Bullet Points" : "Key Features"}
                              </p>
                              <ul className="space-y-2">
                                {(listing.bullet_points || listing.key_features).map((bp: string, i: number) => (
                                  <li key={i} className="text-xs text-white/70 bg-white/3 rounded-lg p-2.5 flex gap-2">
                                    <span className="text-blue-400 flex-shrink-0">•</span>
                                    {bp}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Description */}
                          {(listing.description || listing.long_description) && (
                            <div>
                              <div className="flex items-center justify-between mb-1.5">
                                <p className="text-[10px] font-semibold uppercase text-white/30">Description</p>
                                <button onClick={() => copyToClipboard(listing.description || listing.long_description)} className="text-white/20 hover:text-white/60">
                                  <Copy className="w-3 h-3" />
                                </button>
                              </div>
                              <p className="text-xs text-white/60 leading-relaxed bg-white/3 rounded-lg p-3 max-h-40 overflow-y-auto">
                                {listing.description || listing.long_description}
                              </p>
                            </div>
                          )}

                          {/* Tags / Keywords */}
                          {(listing.tags || listing.backend_keywords) && (
                            <div>
                              <p className="text-[10px] font-semibold uppercase text-white/30 mb-1.5">
                                {listing.tags ? "Tags" : "Backend Keywords"}
                              </p>
                              <div className="flex flex-wrap gap-1.5">
                                {(listing.tags || listing.backend_keywords?.split(",") || []).slice(0, 13).map((tag: string, i: number) => (
                                  <span key={i} className="text-[10px] bg-white/5 text-white/50 px-2 py-0.5 rounded-full">{tag.trim()}</span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* TikTok-specific */}
                          {listing.hashtags && (
                            <div>
                              <p className="text-[10px] font-semibold uppercase text-white/30 mb-1.5">Hashtags</p>
                              <div className="flex flex-wrap gap-1.5">
                                {listing.hashtags.map((h: string, i: number) => (
                                  <span key={i} className="text-[10px] bg-pink-500/10 text-pink-400 px-2 py-0.5 rounded-full">{h}</span>
                                ))}
                              </div>
                            </div>
                          )}

                          <div className="flex gap-2 pt-2">
                            <Button size="sm" className="flex-1 bg-blue-600 hover:bg-blue-500 h-7 text-xs">
                              Publish to {activeMarketplace}
                            </Button>
                            <Button size="sm" variant="outline" className="h-7 text-xs border-white/10 bg-white/5 text-white/50">
                              <Copy className="w-3 h-3 mr-1" /> Copy All
                            </Button>
                          </div>
                        </>
                      );
                    })()}
                  </motion.div>
                </AnimatePresence>
              </div>
            ) : (
              <div className="bg-[#111218] border border-white/5 border-dashed rounded-xl p-12 flex flex-col items-center justify-center text-center">
                <Sparkles className="w-10 h-10 text-white/10 mb-4" />
                <p className="text-white/30 text-sm mb-1">AI-generated listings appear here</p>
                <p className="text-white/15 text-xs">Fill in product details and select platforms to get started</p>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "manager" && <ListingManagerTable />}
    </div>
  );
}

function ListingManagerTable() {
  const { data: listings, isLoading } = useQuery({
    queryKey: ["listings-list"],
    queryFn: () => api.getListings(),
    staleTime: 1000 * 60 * 2,
  });

  const rows: any[] = Array.isArray(listings) ? listings : [];

  if (isLoading) {
    return <div className="bg-[#111218] border border-white/5 rounded-xl p-8 text-center text-white/30 text-sm">Loading listings…</div>;
  }

  return (
    <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
      <div className="grid grid-cols-5 px-4 py-2.5 border-b border-white/5 text-[10px] font-semibold uppercase text-white/25">
        <span className="col-span-2">Product</span>
        <span>Platform</span>
        <span>SEO Score</span>
        <span>Actions</span>
      </div>
      {rows.map((item: any, i: number) => {
        const seoScore = Math.round(item.seo_score ?? 0);
        const publishedAt = item.published_at
          ? new Date(item.published_at).toLocaleDateString()
          : "Never";
        return (
          <div key={i} className="grid grid-cols-5 px-4 py-3 border-b border-white/3 hover:bg-white/3 items-center">
            <div className="col-span-2">
              <p className="text-sm text-white font-medium truncate max-w-xs">{item.title}</p>
              <p className="text-[10px] text-white/30">Published: {publishedAt}</p>
            </div>
            <Badge className={cn("border w-fit capitalize text-[10px]", MARKETPLACE_COLORS[item.marketplace] ?? "bg-white/5 text-white/40 border-white/10")}>
              {item.marketplace}
            </Badge>
            <div className="flex items-center gap-2">
              <div className="w-16 bg-white/5 rounded-full h-1.5">
                <div className={cn("h-1.5 rounded-full", seoScore >= 75 ? "bg-emerald-500" : seoScore >= 55 ? "bg-amber-500" : "bg-red-500")}
                  style={{ width: `${seoScore}%` }} />
              </div>
              <span className="text-xs text-white/50">{seoScore}</span>
            </div>
            <div className="flex gap-1.5">
              <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px] text-white/40 hover:text-white">Edit</Button>
              <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px] text-white/40 hover:text-white">Sync</Button>
            </div>
          </div>
        );
      })}
      {rows.length === 0 && (
        <div className="px-4 py-8 text-center text-white/30 text-sm">No listings yet — generate one above</div>
      )}
    </div>
  );
}
