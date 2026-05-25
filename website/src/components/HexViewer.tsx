"use client";

import { useState, useMemo } from "react";

const COLS = 16;
const GROUP = 8;

function h2(n: number) {
  return n.toString(16).toUpperCase().padStart(2, "0");
}

function isPrintable(b: number) {
  return b >= 0x20 && b < 0x7f;
}

function formatSize(n: number): string {
  const hex = n.toString(16).toUpperCase();
  if (n < 1024) return `${n} B (0x${hex})`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(2)} KB (0x${hex})`;
  return `${(n / (1024 * 1024)).toFixed(2)} MB (0x${hex})`;
}

function offWidth(len: number) {
  return Math.max(3, Math.ceil(Math.log(Math.max(len, 1)) / Math.log(16)));
}

interface InspectorProps {
  data: Uint8Array;
  cursor: number | null;
  littleEndian: boolean;
  onToggleEndian: (v: boolean) => void;
}

function Inspector({ data, cursor, littleEndian, onToggleEndian }: InspectorProps) {
  const values = useMemo(() => {
    if (cursor === null || cursor >= data.length) return null;
    const view = new DataView(data.buffer, data.byteOffset, data.byteLength);
    const rem = data.byteLength - cursor;
    const byte = data[cursor];

    const safe = <T,>(n: number, fn: () => T): T | null => (rem >= n ? fn() : null);
    const fmt = (v: number | bigint | null) => (v === null ? "—" : String(v));
    const fmtF = (v: number | null, p: number) =>
      v === null ? "—" : isFinite(v) ? v.toPrecision(p) : String(v);

    return {
      binary: byte.toString(2).padStart(8, "0"),
      int8: fmt(view.getInt8(cursor)),
      uint8: fmt(view.getUint8(cursor)),
      int16: fmt(safe(2, () => view.getInt16(cursor, littleEndian))),
      uint16: fmt(safe(2, () => view.getUint16(cursor, littleEndian))),
      int32: fmt(safe(4, () => view.getInt32(cursor, littleEndian))),
      uint32: fmt(safe(4, () => view.getUint32(cursor, littleEndian))),
      int64: fmt(safe(8, () => view.getBigInt64(cursor, littleEndian))),
      uint64: fmt(safe(8, () => view.getBigUint64(cursor, littleEndian))),
      float32: fmtF(
        safe(4, () => view.getFloat32(cursor, littleEndian)),
        7,
      ),
      float64: fmtF(
        safe(8, () => view.getFloat64(cursor, littleEndian)),
        10,
      ),
    };
  }, [cursor, data, littleEndian]);

  const rows = values
    ? ([
        ["Binary", values.binary],
        ["Int8", values.int8],
        ["Uint8", values.uint8],
        ["Int16", values.int16],
        ["Uint16", values.uint16],
        ["Int32", values.int32],
        ["Uint32", values.uint32],
        ["Int64", values.int64],
        ["Uint64", values.uint64],
        ["Float32", values.float32],
        ["Float64", values.float64],
      ] as [string, string][])
    : [];

  return (
    <div className="w-52 shrink-0 border-l border-[#333] p-3 space-y-1 select-none">
      <div className="text-[#858585] font-semibold mb-2 text-[11px]">Inspector</div>
      <div className="text-[11px] text-[#606060]">
        Offset:{" "}
        {cursor !== null ? (
          <span className="text-[#d4d4d4]">0x{cursor.toString(16).toUpperCase()}</span>
        ) : (
          "none"
        )}
      </div>
      {values ? (
        <div className="space-y-0.5 pt-1">
          {rows.map(([label, val]) => (
            <div key={label} className="flex justify-between gap-2 text-[11px]">
              <span className="text-[#606060] shrink-0">{label}</span>
              <span className="text-[#d4d4d4] font-mono truncate text-right">{val}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-[11px] text-[#444] pt-1">Select a byte to inspect</div>
      )}
      <div className="pt-2 mt-2 border-t border-[#333]">
        <label className="flex items-center gap-2 cursor-pointer text-[11px]">
          <input
            type="checkbox"
            checked={littleEndian}
            onChange={(e) => onToggleEndian(e.target.checked)}
            className="w-3 h-3 accent-blue-500"
          />
          <span className="text-[#606060]">Little Endian</span>
        </label>
      </div>
    </div>
  );
}

export interface HexViewerProps {
  data: Uint8Array;
  height?: string;
}

export function HexViewer({ data, height = "420px" }: HexViewerProps) {
  const [cursor, setCursor] = useState<number | null>(null);
  const [littleEndian, setLittleEndian] = useState(true);

  const ow = offWidth(data.length);
  const rowCount = Math.ceil(data.length / COLS);

  function handleByte(idx: number, hasData: boolean) {
    if (!hasData) return;
    setCursor((prev) => (prev === idx ? null : idx));
  }

  return (
    <div className="flex font-mono text-xs bg-[#1e1e1e] text-[#d4d4d4] rounded-lg overflow-hidden border border-[#333]">
      {/* Scrollable hex area */}
      <div className="flex-1 overflow-auto" style={{ height }}>
        {/* Column header */}
        <div className="sticky top-0 flex items-center px-3 py-1.5 bg-[#252526] border-b border-[#333] text-[#505050] select-none z-10">
          <span className="shrink-0" style={{ width: `${ow}ch` }} />
          <span className="w-3 shrink-0" />
          {Array.from({ length: COLS }, (_, i) => (
            <span
              key={i}
              className={`shrink-0 text-center${i === GROUP - 1 ? " mr-2" : ""}`}
              style={{ width: "3ch" }}
            >
              {h2(i)}
            </span>
          ))}
          <span className="ml-4 text-[#505050]">ASCII</span>
        </div>

        {/* Data rows */}
        {Array.from({ length: rowCount }, (_, row) => {
          const offset = row * COLS;
          return (
            <div key={row} className="flex items-center px-3 py-px hover:bg-[#272727]">
              {/* Offset */}
              <span className="text-[#505050] shrink-0 select-none" style={{ width: `${ow}ch` }}>
                {offset.toString(16).toUpperCase().padStart(ow, "0")}
              </span>

              <span className="w-3 shrink-0" />

              {/* Hex bytes */}
              <div className="flex shrink-0">
                {Array.from({ length: COLS }, (_, col) => {
                  const idx = offset + col;
                  const hasData = idx < data.length;
                  const byte = hasData ? data[idx] : null;
                  const selected = idx === cursor;

                  return (
                    <span
                      key={col}
                      className={[
                        "shrink-0 text-center rounded cursor-pointer",
                        col === GROUP - 1 ? "mr-2" : "",
                        selected
                          ? "bg-blue-600 text-white"
                          : byte === null
                            ? ""
                            : byte === 0
                              ? "text-[#404040] hover:bg-[#2e2e2e]"
                              : "hover:bg-[#2e2e2e]",
                      ].join(" ")}
                      style={{ width: "3ch" }}
                      onClick={() => handleByte(idx, hasData)}
                    >
                      {byte !== null ? h2(byte) : ""}
                    </span>
                  );
                })}
              </div>

              {/* ASCII */}
              <div className="ml-4 pl-3 border-l border-[#2a2a2a] flex text-[#606060]">
                {Array.from({ length: COLS }, (_, col) => {
                  const idx = offset + col;
                  const hasData = idx < data.length;
                  const byte = hasData ? data[idx] : null;
                  const selected = idx === cursor;

                  return (
                    <span
                      key={col}
                      className={[
                        "cursor-pointer rounded",
                        selected ? "bg-blue-600 text-white" : hasData ? "hover:bg-[#2e2e2e]" : "",
                      ].join(" ")}
                      onClick={() => handleByte(idx, hasData)}
                    >
                      {byte !== null ? (isPrintable(byte) ? String.fromCharCode(byte) : ".") : " "}
                    </span>
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Footer */}
        <div className="sticky bottom-0 px-3 py-1 text-right text-[#505050] text-[11px] border-t border-[#333] bg-[#1e1e1e]">
          {formatSize(data.length)}
        </div>
      </div>

      {/* Inspector */}
      <Inspector
        data={data}
        cursor={cursor}
        littleEndian={littleEndian}
        onToggleEndian={setLittleEndian}
      />
    </div>
  );
}
