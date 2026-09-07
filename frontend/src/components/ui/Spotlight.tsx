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
        "rounded-xl border bg-gradient-to-b from-[#141419] to-[#0D0D11] p-4 transition-all shadow-sm",
        highlight
          ? "border-rose-900/70"
          : "border-zinc-800/80 hover:border-zinc-700/80",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
