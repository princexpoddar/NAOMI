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
        <span className="text-slate-300 font-medium">{label}</span>
        <span className="font-mono text-[11px] font-semibold text-blue-300 bg-blue-950/80 border border-blue-800/50 px-1.5 py-0.2 rounded">
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
            background: `linear-gradient(to right, #2563EB 0%, #2563EB ${percentage}%, #1E293B ${percentage}%, #1E293B 100%)`,
          }}
        />
      </div>
    </div>
  );
};
