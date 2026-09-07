import React from "react";
import { cn } from "../../lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  highlight?: boolean;
}

export const SpotlightCard: React.FC<CardProps> = ({
  children,
  className,
  highlight = false,
  ...props
}) => {
  return (
    <div
      className={cn(
        "rounded-xl border bg-gradient-to-b from-[#131B2E] to-[#0E1524] p-4 transition-all shadow-sm",
        highlight
          ? "border-blue-700/60 shadow-blue-950/20"
          : "border-slate-800/80 hover:border-slate-700/80",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
