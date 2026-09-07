import React from "react";
import { cn } from "../../lib/utils";

interface ShinyTextProps {
  text: string;
  className?: string;
  shimmerWidth?: number;
}

export const ShinyText: React.FC<ShinyTextProps> = ({
  text,
  className = "",
}) => {
  return (
    <span
      className={cn(
        "inline-block bg-gradient-to-r from-zinc-100 via-crimson-400 to-zinc-100 bg-[length:200%_auto] bg-clip-text text-transparent animate-shimmer",
        className
      )}
    >
      {text}
    </span>
  );
};
