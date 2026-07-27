"use client";

import { useEffect, useState, useRef } from "react";

interface Heading {
  level: number;
  text: string;
  slug: string;
}

interface TableOfContentsProps {
  headings: Heading[];
}

export default function TableOfContents({ headings }: TableOfContentsProps) {
  const [activeId, setActiveId] = useState<string>("");
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll the TOC so the active link is visible
  useEffect(() => {
    if (activeId && scrollContainerRef.current) {
      const activeLink = document.getElementById(`toc-link-${activeId}`);
      if (activeLink) {
        const container = scrollContainerRef.current;
        // Scroll the container so the active link sits ~60px from the top
        // which places it nicely below the "On this page" header
        const scrollTarget = activeLink.offsetTop - 60;
        container.scrollTo({
          top: scrollTarget,
          behavior: 'smooth'
        });
      }
    }
  }, [activeId]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: "-10% 0px -80% 0px" } // trigger when near the top
    );

    headings.forEach((heading) => {
      const element = document.getElementById(heading.slug);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [headings]);

  if (headings.length === 0) {
    return null;
  }

  return (
    <aside className="w-64 flex-shrink-0 hidden xl:flex flex-col border-l-2 border-[var(--offblack)] sticky top-32 h-[calc(100vh-10rem)]">
      <div ref={scrollContainerRef} className="flex-1 overflow-y-auto overscroll-contain pl-8 pr-4 pb-8 relative">
        <div className="font-mono text-sm tracking-widest uppercase mb-6 opacity-60 sticky top-0 bg-[var(--offwhite)] py-2 z-10">
          On this page
        </div>
        <nav className="flex flex-col gap-3">
          {headings.map((heading) => (
            <a
              id={`toc-link-${heading.slug}`}
              key={heading.slug}
              href={`#${heading.slug}`}
              className={`text-sm transition-all duration-200 border-l-2 pl-4 py-1
                ${activeId === heading.slug 
                  ? 'border-[var(--offblack)] font-bold text-[var(--offblack)]' 
                  : 'border-transparent text-[var(--offblack)] opacity-60 hover:opacity-100 hover:border-[var(--offblack)]'
                }`}
              style={{ 
                marginLeft: `${(heading.level - 2) * 1}rem`,
                fontSize: heading.level > 2 ? '0.8rem' : '0.875rem'
              }}
            >
              {heading.text}
            </a>
          ))}
        </nav>
      </div>
    </aside>
  );
}
