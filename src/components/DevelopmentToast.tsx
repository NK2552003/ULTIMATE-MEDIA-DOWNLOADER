"use client";

import { useEffect } from "react";
import { toast } from "sonner";
import { Hammer } from "lucide-react";

export default function DevelopmentToast() {
  useEffect(() => {
    // Show toast after a short delay
    const timer = setTimeout(() => {
      toast.custom((t) => (
        <div className="w-[800px] max-w-[90vw] border-[2px] md:border-[3px] border-[var(--offblack)] bg-[var(--offwhite)] text-[var(--offblack)] p-4 md:p-6 flex flex-col md:flex-row items-start md:items-center gap-4 md:gap-6 shadow-[4px_4px_0px_var(--offblack)] md:shadow-[8px_8px_0px_var(--offblack)] relative overflow-hidden group">
          
          {/* Icon */}
          <div className="w-10 h-10 shrink-0 bg-[var(--cyan)] border-[2px] border-[var(--offblack)] flex items-center justify-center text-[var(--offblack)] font-black text-xl shadow-[2px_2px_0px_var(--offblack)]">
            <Hammer size={20} />
          </div>

          {/* Content */}
          <div className="flex-1 z-10">
            <h4 className="font-mono text-[10px] md:text-xs uppercase tracking-[0.15em] text-[var(--offblack)] opacity-80 font-bold mb-1 md:mb-2">
              Work In Progress
            </h4>
            <p className="text-base md:text-lg lg:text-xl font-bold mb-1 md:mb-2 leading-tight uppercase tracking-tight">Site under development.</p>
            <p className="text-xs md:text-sm opacity-80 leading-snug md:leading-relaxed font-mono max-w-2xl">
              This website is currently being built. Some features, pages, or designs may be incomplete, broken, or subject to change. Please bear with us while we construct the ultimate media downloader experience.
            </p>
          </div>

          {/* Action */}
          <div className="shrink-0 flex flex-col items-start md:items-end justify-center h-full gap-4 z-10 w-full md:w-auto mt-2 md:mt-0">
            <button 
              onClick={() => toast.dismiss(t)} 
              className="bg-[var(--cyan)] text-[var(--offblack)] font-mono font-bold px-4 py-2 border-[2px] border-[var(--offblack)] shadow-[4px_4px_0px_var(--offblack)] hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_var(--offblack)] active:translate-y-[4px] active:translate-x-[4px] active:shadow-none transition-all uppercase text-[10px] md:text-xs tracking-wider"
            >
              Got it
            </button>
          </div>
        </div>
      ), {
        duration: 8000,
        id: "dev-toast", // Prevent duplicates stacking
      });
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return null;
}
