'use client'

import { useMemo } from 'react'
import { HexViewer } from '@/components/HexViewer'

interface SegmentHexViewerProps {
  data: string  // base64
  height?: string
}

export function SegmentHexViewer({ data, height }: SegmentHexViewerProps) {
  const bytes = useMemo(() => {
    const bin = atob(data)
    const arr = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i)
    return arr
  }, [data])

  return <HexViewer data={bytes} height={height} />
}
