"use client";

import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { Maximize, Minimize, Image as ImageIcon, Code, ZoomIn, ZoomOut, LocateFixed } from "lucide-react";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

export default function Mermaid({ chart }: { chart: string }) {
  const [svgContent, setSvgContent] = useState<string>("");
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const id = useRef(`mermaid-${Math.random().toString(36).substring(2, 9)}`);
  const svgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      themeVariables: {
        fontFamily: "PP Neue Montreal",
        primaryColor: "#f4f1ee",
        primaryTextColor: "#3a3a38",
        primaryBorderColor: "#3a3a38",
        lineColor: "#3a3a38",
        secondaryColor: "#cccccc",
        tertiaryColor: "#f4f1ee",
        background: "#f4f1ee",
      }
    });

    let isMounted = true;

    const renderChart = async () => {
      try {
        const cleanChart = chart.replace(/\r/g, '').trim();
        const uniqueId = `mermaid-${Math.random().toString(36).substring(2, 11)}-${Date.now()}`;
        
        const { svg } = await mermaid.render(uniqueId, cleanChart);
        
        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (e: any) {
        console.error("Mermaid rendering failed:", e);
        if (isMounted) {
          const errorMessage = e?.message || String(e);
          setSvgContent(`<div class="p-4 overflow-x-auto text-sm text-red-600 bg-red-100/10 font-mono whitespace-pre-wrap">Error rendering chart:<br/>${errorMessage}</div>`);
        }
      }
    };

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isFullscreen) setIsFullscreen(false);
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isFullscreen]);

  const downloadSvg = () => {
    if (!svgContent) return;
    const blob = new Blob([svgContent], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${id.current}.svg`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadPng = () => {
    if (!svgContent || !svgRef.current) return;
    
    const svgElement = svgRef.current.querySelector('svg');
    if (!svgElement) return;

    const width = svgElement.viewBox.baseVal?.width || svgElement.getBoundingClientRect().width;
    const height = svgElement.viewBox.baseVal?.height || svgElement.getBoundingClientRect().height;

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const blob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      const scale = 2;
      canvas.width = width * scale;
      canvas.height = height * scale;
      
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.fillStyle = "#f4f1ee"; 
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.scale(scale, scale);
        ctx.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob((pngBlob) => {
          if (pngBlob) {
            const pngUrl = URL.createObjectURL(pngBlob);
            const link = document.createElement("a");
            link.href = pngUrl;
            link.download = `${id.current}.png`;
            link.click();
            URL.revokeObjectURL(pngUrl);
          }
        }, "image/png");
      }
      URL.revokeObjectURL(url);
    };
    img.src = url;
  };

  if (!svgContent) {
    return <div className="flex justify-center my-8 p-4 md:p-8 border-[2px] border-[var(--offblack)] bg-[var(--offwhite)]">Loading diagram...</div>;
  }

  if (isFullscreen) {
    return (
      <TransformWrapper initialScale={1} minScale={0.2} maxScale={8} centerOnInit>
        {({ zoomIn, zoomOut, centerView }) => (
          <div className="fixed inset-0 z-[99999] bg-[var(--offwhite)] p-8 md:p-16 flex flex-col items-center justify-center overflow-hidden">
            {/* Fullscreen Toolbar */}
            <div className="absolute top-4 right-4 flex gap-2 z-10 bg-[var(--offwhite)] p-1 border-[2px] border-[var(--offblack)] shadow-[4px_4px_0px_var(--offblack)]">
              <button title="Zoom In" onClick={() => zoomIn()} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
                <ZoomIn size={20} />
              </button>
              <button title="Zoom Out" onClick={() => zoomOut()} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
                <ZoomOut size={20} />
              </button>
              <button title="Reset View" onClick={() => centerView()} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
                <LocateFixed size={20} />
              </button>
              <div className="w-[2px] bg-[var(--offblack)] mx-1" />
              <button title="Download as SVG" onClick={downloadSvg} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
                <Code size={20} />
              </button>
              <button title="Download as PNG" onClick={downloadPng} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
                <ImageIcon size={20} />
              </button>
              <button title="Exit Fullscreen" onClick={() => setIsFullscreen(false)} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
                <Minimize size={20} />
              </button>
            </div>

            <TransformComponent wrapperStyle={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", cursor: "grab" }} contentStyle={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div 
                ref={svgRef}
                className="w-full h-full flex items-center justify-center [&_svg]:max-w-[90vw] [&_svg]:max-h-[80vh] [&_svg]:w-auto [&_svg]:h-auto"
                dangerouslySetInnerHTML={{ __html: svgContent }}
              />
            </TransformComponent>
          </div>
        )}
      </TransformWrapper>
    );
  }

  return (
    <div className="relative group flex justify-center my-8 p-4 md:p-8 border-[2px] border-[var(--offblack)] shadow-[4px_4px_0px_var(--offblack)] bg-[var(--offwhite)] overflow-hidden">
      {/* Default Toolbar */}
      <div className="absolute top-4 right-4 flex gap-2 transition-opacity duration-300 opacity-0 group-hover:opacity-100 z-10 bg-[var(--offwhite)] p-1 border-[2px] border-[var(--offblack)] shadow-[4px_4px_0px_var(--offblack)]">
        <button title="Download as SVG" onClick={downloadSvg} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
          <Code size={20} />
        </button>
        <button title="Download as PNG" onClick={downloadPng} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
          <ImageIcon size={20} />
        </button>
        <button title="Fullscreen" onClick={() => setIsFullscreen(true)} className="p-2 hover:bg-[var(--accent-color)] transition-colors border-2 border-transparent hover:border-[var(--offblack)] text-[var(--offblack)]">
          <Maximize size={20} />
        </button>
      </div>

      {/* SVG Content */}
      <div 
        ref={svgRef}
        className="w-full flex justify-center overflow-x-auto"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
}
