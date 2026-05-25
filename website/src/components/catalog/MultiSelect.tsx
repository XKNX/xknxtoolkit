"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

interface Option {
  value: string;
  label: string;
}

interface MultiSelectProps {
  options: Option[];
  value: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  className?: string;
}

export default function MultiSelect({
  options,
  value,
  onChange,
  placeholder = "All",
  className,
}: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const [rect, setRect] = useState<DOMRect | null>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  function handleToggleOpen() {
    if (!open) setRect(buttonRef.current?.getBoundingClientRect() ?? null);
    setOpen((o) => !o);
  }

  useEffect(() => {
    if (!open) return;
    function handleClick(e: MouseEvent) {
      if (
        !buttonRef.current?.contains(e.target as Node) &&
        !panelRef.current?.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  function toggle(val: string) {
    onChange(value.includes(val) ? value.filter((v) => v !== val) : [...value, val]);
  }

  const label = value.length === 0 ? placeholder : `${value.length} selected`;

  return (
    <div className={className}>
      <button
        ref={buttonRef}
        type="button"
        onClick={handleToggleOpen}
        className="w-full flex items-center gap-1 border border-fd-border rounded bg-fd-popover text-fd-foreground px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-fd-ring"
      >
        <span className="flex-1 text-left truncate">{label}</span>
        <span className="text-fd-muted-foreground shrink-0">▾</span>
      </button>

      {open &&
        rect &&
        createPortal(
          <div
            ref={panelRef}
            style={{
              position: "fixed",
              top: rect.bottom + 4,
              left: rect.left,
              minWidth: rect.width,
              zIndex: 9999,
            }}
            className="bg-fd-popover border border-fd-border rounded shadow-lg max-h-52 overflow-y-auto"
          >
            {options.map((opt) => (
              <label
                key={opt.value}
                className="flex items-center gap-2 px-3 py-1.5 text-xs text-fd-foreground hover:bg-fd-accent cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  className="accent-fd-primary shrink-0"
                  checked={value.includes(opt.value)}
                  onChange={() => toggle(opt.value)}
                />
                <span className="truncate">{opt.label}</span>
              </label>
            ))}
          </div>,
          document.body,
        )}
    </div>
  );
}
