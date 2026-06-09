"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

/**
 * Wraps content and plays the `rise` keyframe the first time it scrolls into
 * view. Honours prefers-reduced-motion (shows immediately, no animation).
 */
export function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [shown, setShown] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setShown(true);
      return;
    }
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setShown(true);
          io.disconnect();
        }
      },
      { threshold: 0.12 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: shown ? undefined : 0,
        animation: shown
          ? `rise 0.7s cubic-bezier(0.16, 1, 0.3, 1) ${delay}ms both`
          : undefined,
      }}
    >
      {children}
    </div>
  );
}
