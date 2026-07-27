"use client";

import { useEffect, useState } from "react";

export default function Fireflies() {
  const [fireflies, setFireflies] = useState<{ id: number; left: number; top: number; delay: number; duration: number; size: number }[]>([]);

  useEffect(() => {
    // Generate fireflies
    const count = 25;
    const newFireflies = Array.from({ length: count }).map((_, i) => ({
      id: i,
      left: Math.random() * 100, // percentage horizontally
      top: 20 + Math.random() * 80, // Start lower in the container
      delay: Math.random() * 5, // random delay
      duration: 4 + Math.random() * 4, // 4-8 seconds
      size: 2 + Math.random() * 3, // 2-5 px
    }));
    setFireflies(newFireflies);
  }, []);

  return (
    <div 
      className="absolute inset-0 pointer-events-none z-0 overflow-hidden" 
      style={{ 
        maskImage: 'linear-gradient(to top, black 30%, transparent 100%)', 
        WebkitMaskImage: 'linear-gradient(to top, black 30%, transparent 100%)' 
      }}
    >
      {fireflies.map((ff) => (
        <div
          key={ff.id}
          className="absolute rounded-full bg-[var(--offblack)] opacity-0 animate-firefly"
          style={{
            left: `${ff.left}%`,
            top: `${ff.top}%`,
            width: `${ff.size}px`,
            height: `${ff.size}px`,
            animationDelay: `${ff.delay}s`,
            animationDuration: `${ff.duration}s`,
          }}
        />
      ))}
    </div>
  );
}
