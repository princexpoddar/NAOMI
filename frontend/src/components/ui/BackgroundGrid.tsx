import React, { useEffect, useState } from "react";

export const BackgroundGrid: React.FC = () => {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden bg-pitch-black">
      {/* 1. Subtle Dot Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-[0.18]"
        style={{
          backgroundImage: `radial-gradient(rgba(255, 255, 255, 0.25) 1px, transparent 1px)`,
          backgroundSize: "24px 24px",
        }}
      />

      {/* 2. Ambient Crimson Radial Spotlights */}
      <div
        className="absolute w-[800px] h-[800px] rounded-full blur-[140px] opacity-25 transition-all duration-300 ease-out pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(225, 29, 72, 0.45) 0%, rgba(153, 27, 27, 0.15) 50%, transparent 70%)",
          left: `${mousePos.x - 400}px`,
          top: `${mousePos.y - 400}px`,
        }}
      />

      {/* 3. Static Crimson Atmosphere in top-left & bottom-right */}
      <div className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-crimson-900/15 blur-[150px] pointer-events-none" />
      <div className="absolute top-1/2 -right-40 w-[600px] h-[600px] rounded-full bg-ruby-dark/15 blur-[160px] pointer-events-none" />

      {/* 4. Vignette Shadow around edges */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_30%,#000000_90%)]" />
    </div>
  );
};
