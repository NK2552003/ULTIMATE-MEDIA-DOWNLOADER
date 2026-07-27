"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

export default function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isPresent, setIsPresent] = useState(false);

  useEffect(() => {
    // Immediately remove the old transition strips injected by TransitionLink
    // to prevent flashing of the old page content!
    const oldStrips = document.querySelectorAll('.transition-link-strips');
    oldStrips.forEach(el => el.remove());
    
    // Force scroll to top on every new page navigation
    window.scrollTo(0, 0);
    
    setIsPresent(true);
  }, [pathname]);

  const strips = Array.from({ length: 5 });

  return (
    <>
      <div className="pointer-events-none fixed inset-0 z-[9999] grid" style={{ gridTemplateRows: `repeat(5, 1fr)` }}>
        {strips.map((_, index) => (
          <motion.div
            key={index}
            className="bg-[var(--offblack)] w-full"
            style={{ marginBottom: '-1px' }}
            initial={{ scaleX: 1, originX: 1 }}
            animate={{ scaleX: 0, originX: 1 }}
            transition={{
              duration: 0.5,
              ease: "circOut",
              delay: index * 0.08,
            }}
          />
        ))}
      </div>
      {children}
    </>
  );
}
