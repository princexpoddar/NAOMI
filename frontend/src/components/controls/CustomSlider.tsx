import React from "react";

interface CustomSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit?: string;
  formatSign?: boolean;
  onChange: (val: number) => void;
  description?: string;
}

export const CustomSlider: React.FC<CustomSliderProps> = ({
  label,
  value,
  min,
  max,
  step,
  unit = "%",
  formatSign = true,
  onChange,
  description,
}) => {
  const percentage = ((value - min) / (max - min)) * 100;
  const sign = formatSign && value > 0 ? "+" : "";

  return (
    <div className="flex flex-col gap-1.5 py-1">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-zinc-200 tracking-tight">{label}</span>
          {description && <p className="text-[10px] text-zinc-400 font-mono">{description}</p>}
        </div>
        <span className="px-2 py-0.5 rounded-md font-mono text-xs font-bold bg-crimson-950/80 border border-crimson-600/40 text-crimson-300">
          {sign}{value}{unit}
        </span>
      </div>

      <div className="relative flex items-center py-1">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full relative z-10"
          style={{
            background: `linear-gradient(to right, #E11D48 0%, #E11D48 ${percentage}%, #27272A ${percentage}%, #27272A 100%)`,
          }}
        />
      </div>

      <div className="flex justify-between text-[9px] font-mono text-zinc-400 px-0.5">
        <span>{formatSign && min > 0 ? "+" : ""}{min}{unit}</span>
        <span>0{unit}</span>
        <span>{formatSign && max > 0 ? "+" : ""}{max}{unit}</span>
      </div>
    </div>
  );
};
