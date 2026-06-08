export default function OfflinePage() {
  return (
    <div className="min-h-screen bg-[#0A0B0E] flex items-center justify-center p-6">
      <div className="text-center max-w-sm">
        <div className="w-16 h-16 rounded-2xl bg-violet-600/20 flex items-center justify-center mx-auto mb-6">
          <svg className="w-8 h-8 text-violet-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M3 3l18 18M10.584 10.587a2 2 0 002.828 2.828M9 9a3 3 0 014.243.757M6.343 6.343A8 8 0 0117.657 17.657M6.343 6.343A8 8 0 0117.657 6.343" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">You&apos;re offline</h1>
        <p className="text-gray-400 text-sm mb-8">
          SellerVision AI needs an internet connection to load your data.
          Check your connection and try again.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="bg-violet-600 hover:bg-violet-500 text-white font-medium px-6 py-2.5 rounded-lg transition-colors"
        >
          Try again
        </button>
        <p className="text-gray-600 text-xs mt-6">
          Pages you recently visited may still be available from cache.
        </p>
      </div>
    </div>
  );
}
