"use client";

import { useEffect } from "react";
import { toast } from "sonner";
import { X } from "lucide-react";

export default function DevelopmentToast() {
  useEffect(() => {
    // Show toast after a short delay
    const timer = setTimeout(() => {
      toast.custom((t) => (
        <div className="mt-20 md:mt-24 border-[2px] border-[var(--offblack)] bg-[#ff0000]/10 text-[var(--offblack)] p-3 flex items-center justify-between gap-4 shadow-[4px_4px_0px_var(--offblack)] w-full max-w-sm pointer-events-auto backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <span className="animate-pulse text-lg">🚧</span>
            <div className="font-mono text-[10px] md:text-xs font-bold uppercase tracking-widest">
              Site under development
            </div>
          </div>
          <button 
            onClick={() => toast.dismiss(t)}
            className="p-1 hover:bg-black/10 transition-colors"
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>
      ), {
        position: 'top-right',
        duration: 8000,
        id: "dev-toast",
      });
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return null;
}
