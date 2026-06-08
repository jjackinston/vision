"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff, X } from "lucide-react";
import { cn } from "@/lib/utils";

export function VoiceAssistant() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const startListening = useCallback(async () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      alert("Voice recognition not supported in this browser.");
      return;
    }
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = async (event: any) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      setIsListening(false);
      await processVoiceQuery(text);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  }, []);

  const processVoiceQuery = async (query: string) => {
    setIsProcessing(true);
    try {
      const res = await fetch("/api/voice-assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResponse(data.response);
      // Text-to-speech
      if ("speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(data.response);
        utterance.rate = 1.1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
      }
    } catch {
      setResponse("Sorry, I couldn't process that request.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={isListening ? undefined : startListening}
        className={cn(
          "w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200",
          isListening
            ? "bg-red-500/20 text-red-400 ring-2 ring-red-500/40"
            : "text-white/40 hover:text-white hover:bg-white/5"
        )}
      >
        {isListening ? (
          <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 0.8 }}>
            <MicOff className="w-4 h-4" />
          </motion.div>
        ) : (
          <Mic className="w-4 h-4" />
        )}
      </button>

      <AnimatePresence>
        {(transcript || response) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="absolute top-10 right-0 w-80 bg-[#1A1B22] border border-white/10 rounded-xl p-4 shadow-2xl z-50"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
                <span className="text-xs font-semibold text-white">Voice Assistant</span>
              </div>
              <button onClick={() => { setTranscript(""); setResponse(""); }} className="text-white/30 hover:text-white">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
            {transcript && (
              <div className="mb-2">
                <p className="text-[10px] text-white/30 mb-1">You said:</p>
                <p className="text-xs text-white/70 italic">"{transcript}"</p>
              </div>
            )}
            {isProcessing && (
              <div className="flex items-center gap-2 text-xs text-violet-400">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                  className="w-3 h-3 border-2 border-violet-500 border-t-transparent rounded-full"
                />
                Analyzing your business data...
              </div>
            )}
            {response && (
              <div>
                <p className="text-[10px] text-white/30 mb-1">AI CEO:</p>
                <p className="text-xs text-white leading-relaxed">{response}</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
