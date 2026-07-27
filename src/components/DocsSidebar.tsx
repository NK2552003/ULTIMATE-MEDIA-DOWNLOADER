"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import TransitionLink from "./TransitionLink";

interface DocsSidebarProps {
  docs: string[];
}

export default function DocsSidebar({ docs }: DocsSidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 hidden lg:flex flex-col border-r-2 border-[var(--offblack)] sticky top-32 h-[calc(100vh-10rem)]">
      <div className="flex-1 overflow-y-auto overscroll-contain pr-8 pb-8">
        <div className="font-black text-xl uppercase tracking-tighter mb-6">
          Documentation
        </div>
        <nav className="flex flex-col gap-2">
          {docs.map((slug) => {
            const href = `/docs/${slug}`;
            const isActive = pathname.replace(/\/$/, '') === href;
            
            return (
              <TransitionLink 
                key={slug} 
                href={href}
                className={`font-mono text-sm uppercase tracking-wider py-2 px-3 border-[2px] transition-all
                  ${isActive 
                    ? 'border-[var(--offblack)] bg-[var(--accent-color)] shadow-[4px_4px_0px_var(--offblack)] font-bold translate-x-[-2px] translate-y-[-2px]' 
                    : 'border-transparent hover:border-[var(--offblack)] hover:bg-[var(--offwhite)] hover:shadow-[4px_4px_0px_var(--offblack)] hover:translate-x-[-2px] hover:translate-y-[-2px]'
                  }`}
              >
                {slug}.md
              </TransitionLink>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
