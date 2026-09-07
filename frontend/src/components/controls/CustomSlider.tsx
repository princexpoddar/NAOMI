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
}) => {
  const percentage = ((value - min) / (max - min)) * 100;
  const sign = formatSign && value > 0 ? "+" : "";

  return (
    <div className="flex flex-col gap-1 py-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-zinc-300 font-medium">{label}</span>
        <span className="font-mono text-[11px] font-semibold text-rose-300 bg-rose-950/70 border border-rose-800/40 px-1.5 py-0.2 rounded">
          {sign}{value}{unit}
        </span>
      </div>

      <div className="relative flex items-center py-0.5">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full"
          style={{
            background: `linear-gradient(to right, #BE123C 0%, #BE123C ${percentage}%, #27272A ${percentage}%, #27272A 100%)`,
          }}
        />
      </div>
    </div>
  );
};
