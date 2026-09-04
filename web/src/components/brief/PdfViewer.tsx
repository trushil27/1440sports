"use client";

import { useEffect, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

// Worker served as a static asset by webpack (no CDN); resolved from the pinned pdfjs-dist.
pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();

export function PdfViewer({ url }: { url: string }) {
  const box = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [pages, setPages] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const w = Math.floor(entries[0].contentRect.width);
      setWidth((prev) => (Math.abs(prev - w) > 2 ? w : prev));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  return (
    <div ref={box} className="w-full">
      {error ? (
        <p className="panel p-4 text-sm text-bad">{error}</p>
      ) : (
        <Document
          file={url}
          onLoadSuccess={(doc) => setPages(doc.numPages)}
          onLoadError={() => setError("The PDF could not be loaded. If you are offline, it has not been opened on this device before.")}
          loading={<p className="kicker py-8 text-center">Loading the brief…</p>}
          error={<p className="panel p-4 text-sm text-bad">The PDF could not be loaded.</p>}
        >
          {width > 0 &&
            Array.from({ length: pages }, (_, i) => (
              <Page
                key={i}
                pageNumber={i + 1}
                width={Math.min(width, 900)}
                renderTextLayer
                renderAnnotationLayer
                loading={<div style={{ height: Math.min(width, 900) * 1.414 }} className="mb-4 rounded bg-panel" />}
              />
            ))}
        </Document>
      )}
    </div>
  );
}
