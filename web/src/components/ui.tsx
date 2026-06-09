"use client";

import { useEffect, useRef, useState } from "react";

/* ---- Flag chip (flagcdn, supports home nations) ---- */
export function Flag({
  iso2,
  alt,
  className = "",
}: {
  iso2: string;
  alt: string;
  className?: string;
}) {
  return (
    <span
      className={`relative inline-block overflow-hidden bg-ink-2 ring-1 ring-line-strong ${className}`}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={`https://flagcdn.com/${iso2}.svg`}
        alt={alt}
        loading="lazy"
        className="absolute inset-0 h-full w-full object-cover"
      />
    </span>
  );
}

/* ---- Animated probability bar ---- */
export function ProbBar({
  value,
  max = 1,
  tone = "lime",
  delay = 0,
  height = 8,
}: {
  value: number;
  max?: number;
  tone?: "lime" | "gold" | "dim";
  delay?: number;
  height?: number;
}) {
  const w = Math.max(0, Math.min(1, value / max)) * 100;
  const color =
    tone === "gold"
      ? "var(--color-gold)"
      : tone === "dim"
        ? "var(--color-ink-3)"
        : "var(--color-lime)";
  const glow =
    tone === "gold"
      ? "0 0 16px var(--color-gold-soft)"
      : tone === "lime"
        ? "0 0 16px var(--color-lime-soft)"
        : "none";
  return (
    <div
      className="w-full overflow-hidden rounded-full"
      style={{ height, background: "var(--color-ink-2)" }}
    >
      <div
        className="bar-fill h-full rounded-full"
        style={{
          width: `${w}%`,
          background: color,
          boxShadow: glow,
          animationDelay: `${delay}ms`,
        }}
      />
    </div>
  );
}

/* ---- Count-up number, triggered when scrolled into view ---- */
export function CountUp({
  value,
  decimals = 0,
  suffix = "",
  duration = 1200,
  className = "",
}: {
  value: number;
  decimals?: number;
  suffix?: string;
  duration?: number;
  className?: string;
}) {
  const [v, setV] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const started = useRef(false);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setV(value);
      return;
    }
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !started.current) {
          started.current = true;
          const start = performance.now();
          const tick = (now: number) => {
            const p = Math.min(1, (now - start) / duration);
            setV(value * (1 - Math.pow(1 - p, 3)));
            if (p < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.4 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [value, duration]);

  const text =
    decimals === 0 ? Math.round(v).toLocaleString() : v.toFixed(decimals);
  return (
    <span ref={ref} className={`tnum ${className}`}>
      {text}
      {suffix}
    </span>
  );
}

/* ---- Drifting field of simulation "worlds" (canvas background) ---- */
export function DotField() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let raf = 0;
    let W = 0;
    let H = 0;
    let dpr = 1;
    let dots: { x: number; y: number; r: number; a: number; vx: number; vy: number }[] = [];

    const init = () => {
      dpr = Math.min(2, window.devicePixelRatio || 1);
      W = canvas.width = Math.floor(window.innerWidth * dpr);
      H = canvas.height = Math.floor(window.innerHeight * dpr);
      canvas.style.width = window.innerWidth + "px";
      canvas.style.height = window.innerHeight + "px";
      const count = Math.min(160, Math.floor((window.innerWidth * window.innerHeight) / 13000));
      dots = Array.from({ length: count }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        r: (Math.random() * 1.3 + 0.3) * dpr,
        a: Math.random() * 0.5 + 0.12,
        vx: (Math.random() - 0.5) * 0.05 * dpr,
        vy: (Math.random() - 0.5) * 0.05 * dpr,
      }));
    };

    let t = 0;
    const paint = (animate: boolean) => {
      ctx.clearRect(0, 0, W, H);
      t += 0.016;
      for (const d of dots) {
        if (animate) {
          d.x = (d.x + d.vx + W) % W;
          d.y = (d.y + d.vy + H) % H;
        }
        const tw = animate ? 0.55 + 0.45 * Math.sin(t * 0.7 + d.x * 0.01) : 0.7;
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(205,242,78,${(d.a * tw * 0.5).toFixed(3)})`;
        ctx.fill();
      }
      if (animate) raf = requestAnimationFrame(() => paint(true));
    };

    init();
    paint(!reduced);
    const onResize = () => init();
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
    };
  }, []);

  return (
    <canvas
      ref={ref}
      aria-hidden
      className="pointer-events-none fixed inset-0"
      style={{ zIndex: 0 }}
    />
  );
}
