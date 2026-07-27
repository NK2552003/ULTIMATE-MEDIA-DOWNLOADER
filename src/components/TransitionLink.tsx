"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ReactNode } from "react";

export default function TransitionLink({ 
  href, 
  children, 
  className,
  style,
  onClick
}: { 
  href: string; 
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}) {
  const router = useRouter();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    if (onClick) onClick();
    
    // Create strips dynamically
    const container = document.createElement("div");
    container.className = "transition-link-strips fixed inset-0 z-[9998] pointer-events-none";
    container.style.display = "grid";
    container.style.gridTemplateRows = "repeat(5, 1fr)";
    
    for (let i = 0; i < 5; i++) {
      const strip = document.createElement("div");
      strip.style.width = "100%";
      strip.style.marginBottom = "-1px";
      strip.style.transformOrigin = "left";
      strip.style.transform = "scaleX(0)";
      strip.style.backgroundColor = "var(--offblack)";
      strip.style.transition = "transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)";
      
      // Stagger the animation slightly
      setTimeout(() => {
        strip.style.transform = "scaleX(1)";
      }, i * 80);
      
      container.appendChild(strip);
    }
    
    document.body.appendChild(container);
    
    // Wait for the IN animation to finish before navigating
    // 500ms duration + (4 * 80ms delay) = 820ms max
    setTimeout(() => {
      router.push(href);
      
      const animateOut = () => {
        if (!document.body.contains(container)) return;
        
        // Animate the strips OUT
        Array.from(container.children).forEach((strip: any, index) => {
          strip.style.transformOrigin = "right";
          
          setTimeout(() => {
            strip.style.transform = "scaleX(0)";
          }, index * 80);
        });
        
        // Clean up the DOM node after OUT animation finishes
        setTimeout(() => {
          if (document.body.contains(container)) {
            document.body.removeChild(container);
          }
        }, 850);
      };

      // If it's a hash link on the same page, animate out immediately
      const isSamePage = href === window.location.pathname || href.startsWith(window.location.pathname + '#') || (href.startsWith('#') && !href.startsWith('#/'));
      
      if (isSamePage) {
        setTimeout(animateOut, 50);
      } else {
        // Wait for the route to actually change before revealing the new page
        window.addEventListener('routeChangeComplete', animateOut, { once: true });
        
        // Fallback safety timeout just in case the route change fails or gets cancelled
        setTimeout(() => {
          window.removeEventListener('routeChangeComplete', animateOut);
          animateOut();
        }, 8000);
      }
    }, 850);
  };

  return (
    <a href={href} onClick={handleClick} className={className} style={style}>
      {children}
    </a>
  );
}
