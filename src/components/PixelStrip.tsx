"use client";

import { useMemo, useId } from "react";

interface PixelStripProps {
  direction?: "up" | "down";
  primaryColor?: string;
  secondaryColor?: string;
}

export default function PixelStrip({ 
  direction = "up",
  primaryColor = "var(--offblack)",
  secondaryColor = "var(--accent-color)"
}: PixelStripProps) {
  const columns = 24; // Width of repeating pattern
  const rows = 4;
  const squareSize = 24;
  const uniqueId = useId().replace(/:/g, "");
  const patternId = `pixel-pattern-${direction}-${uniqueId}`;

  const pattern = useMemo(() => {
    // Basic pseudo-random number generator for stable hydration
    const getSeededRandom = (seed: number) => {
      const x = Math.sin(seed) * 10000;
      return x - Math.floor(x);
    };

    const rects = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < columns; c++) {
        const seed = r * 200 + c * 13;
        
        // If direction is 'up', density is sparse at top (r=0) and dense at bottom
        // If direction is 'down', density is dense at top (r=0) and sparse at bottom
        const prob = direction === "up" 
          ? ((r + 1) / (rows + 1.2))
          : 1 - ((r + 1) / (rows + 1.2));
        
        if (getSeededRandom(seed) < prob) {
          // 30% chance of being the secondary color
          const isAccent = getSeededRandom(seed + 1000) > 0.7;
          rects.push(
            <rect 
              key={`${r}-${c}`}
              x={c * squareSize} 
              y={r * squareSize} 
              width={squareSize} 
              height={squareSize} 
              fill={isAccent ? secondaryColor : primaryColor} 
            />
          );
        }
      }
    }
    return rects;
  }, [direction]);

  const svgContent = (
    <div className="w-full flex" style={{ height: `${rows * squareSize}px` }}>
      <svg aria-hidden="true" width="100%" height="100%" className="block">
        <defs>
          <pattern 
            id={patternId} 
            x="0" 
            y="0" 
            width={columns * squareSize} 
            height={rows * squareSize} 
            patternUnits="userSpaceOnUse"
          >
            {pattern}
          </pattern>
        </defs>
        <rect x="0" y="0" width="100%" height="100%" fill={`url(#${patternId})`} />
      </svg>
    </div>
  );

  const solidBar = <div className="w-full h-8 md:h-12 relative -mt-[1px] -mb-[1px]" style={{ backgroundColor: primaryColor }}></div>;

  return (
    <div className="w-full relative z-20 flex flex-col">
      {direction === "up" ? (
        <>
          {svgContent}
          {solidBar}
        </>
      ) : (
        <>
          {solidBar}
          {svgContent}
        </>
      )}
    </div>
  );
}
