"use client";

import { useEffect } from "react";
import { toast } from "sonner";
import { ArrowUpRight } from "lucide-react";
import TransitionLink from "@/components/TransitionLink";

export default function ResponsibleUseToast() {
  useEffect(() => {
    const showToast = () => {
      toast.custom((t) => (
        <div className="w-[800px] max-w-[90vw] border-[2px] md:border-[3px] border-[var(--offblack)] bg-[var(--offwhite)] text-[var(--offblack)] p-4 md:p-6 flex flex-col md:flex-row items-start md:items-center gap-4 md:gap-6 shadow-[4px_4px_0px_var(--offblack)] md:shadow-[8px_8px_0px_var(--offblack)] relative overflow-hidden group">
          
          {/* Icon */}
          <div className="w-10 h-10 shrink-0 bg-[var(--accent-color)] border-[2px] border-[var(--offblack)] flex items-center justify-center text-[var(--offblack)] font-black text-xl shadow-[2px_2px_0px_var(--offblack)]">
            !
          </div>

          {/* Content */}
          <div className="flex-1 z-10">
            <h4 className="font-mono text-[10px] md:text-xs uppercase tracking-[0.15em] text-[var(--offblack)] opacity-60 font-bold mb-1 md:mb-2">
              Responsible Use
            </h4>
            <p className="text-base md:text-lg lg:text-xl font-bold mb-1 md:mb-2 leading-tight uppercase tracking-tight">Your library, your responsibility.</p>
            <p className="text-xs md:text-sm opacity-80 leading-snug md:leading-relaxed font-mono max-w-2xl">
              UMD is for content you own or have permission to save. Respect copyright, creator rights, platform terms, and the laws that apply to you. Never use it to bypass access controls or download protected content.
            </p>
          </div>

          {/* Action */}
          <div className="shrink-0 flex flex-col items-start md:items-end justify-between h-full gap-4 z-10 w-full md:w-auto mt-2 md:mt-0">
            <TransitionLink href="/security" onClick={() => toast.dismiss(t)} className="text-[10px] md:text-xs font-mono font-bold hover:bg-[var(--accent-color)] px-2 py-1 border-[2px] border-transparent hover:border-[var(--offblack)] transition-all flex items-center gap-1 group/link">
              Security policy <ArrowUpRight size={14} className="group-hover/link:translate-x-1 group-hover/link:-translate-y-1 transition-transform" />
            </TransitionLink>
            <button 
              onClick={() => toast.dismiss(t)} 
              className="bg-[var(--accent-color)] text-[var(--offblack)] font-mono font-bold px-4 py-2 border-[2px] border-[var(--offblack)] shadow-[4px_4px_0px_var(--offblack)] hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_var(--offblack)] active:translate-y-[4px] active:translate-x-[4px] active:shadow-none transition-all uppercase text-[10px] md:text-xs tracking-wider"
            >
              I understand
            </button>
          </div>
        </div>
      ), {
        duration: 5000,
        id: "responsible-use-toast", // Prevent duplicates stacking
      });
    };

    const interval = setInterval(showToast, 10000);
    return () => clearInterval(interval);
  }, []);

  return null;
}
