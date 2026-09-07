import React from "react";

interface ShinyTextProps {
  text: string;
  className?: string;
}

export const ShinyText: React.FC<ShinyTextProps> = ({
  text,
  className = "",
}) => {
  return <span className={className}>{text}</span>;
};
