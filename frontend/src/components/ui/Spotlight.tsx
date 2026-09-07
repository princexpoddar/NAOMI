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
        "rounded-xl border bg-[#0F0F12] p-5 transition-colors",
        highlight ? "border-rose-900/60" : "border-zinc-800/80 hover:border-zinc-700",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
