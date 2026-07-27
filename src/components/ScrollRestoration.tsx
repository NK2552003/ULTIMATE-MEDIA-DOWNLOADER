"use client";

import { useEffect } from 'react';

export default function ScrollRestoration() {
  useEffect(() => {
    // Attempt to restore scroll position on mount
    const savedPosition = sessionStorage.getItem(`scrollPos:${window.location.pathname}`);
    if (savedPosition) {
      window.scrollTo(0, parseInt(savedPosition, 10));
    }

    const handleScroll = () => {
      sessionStorage.setItem(`scrollPos:${window.location.pathname}`, window.scrollY.toString());
    };

    // Save position periodically on scroll
    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return null;
}
