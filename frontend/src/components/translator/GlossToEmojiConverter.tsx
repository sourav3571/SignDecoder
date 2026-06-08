"use client";



import React, {
  useState,
  useEffect,
  useCallback,
  useRef,
  useMemo,
} from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Copy,
  Check,
  RotateCcw,
  Clock,
  ChevronDown,
  ChevronUp,
  Star,
  Download,
  Share2,
  Settings,
  Keyboard,
  X,
  MessageCircle,
  Link2,
  Activity,
  TrendingUp,
  BookOpen,
  Volume2,
  VolumeX,
} from "lucide-react";





interface ConversionResult {
  id: string;
  input: string;
  emoji: string;
  timestamp: number;
  isFavorite: boolean;
}

interface AppStats {
  total: number;
  today: number;
  lastDate: string;
}

interface AppSettings {
  animationsEnabled: boolean;
  soundEnabled: boolean;
}

interface ToastItem {
  id: number;
  message: string;
  type: "success" | "error" | "info";
}

export interface GlossToEmojiConverterProps {
  glossText?: string;
}





const API_URL = "/api/convert-to-emoji";
const MAX_HIST = 10;
const SK = { history: "sd_emoji_history", stats: "sd_emoji_stats", settings: "sd_emoji_settings" } as const;

const EXAMPLES = [
  "I eat breakfast morning",
  "She drink coffee daily",
  "Boy run school fast",
  "Family celebrate birthday",
  "He read book night",
  "We go market today",
  "Doctor help sick person",
  "Rain fall heavy outside",
] as const;

const SHORTCUTS = [
  { keys: ["Ctrl", "Enter"], label: "Convert gloss to emoji" },
  { keys: ["Ctrl", "Shift", "C"], label: "Copy emoji result" },
  { keys: ["Ctrl", "Shift", "E"], label: "Export as PNG" },
  { keys: ["Ctrl", "Shift", "S"], label: "Open share menu" },
  { keys: ["F"], label: "Toggle favourite on result" },
  { keys: ["H"], label: "Toggle history" },
  { keys: ["?"], label: "Show this help" },
  { keys: ["Esc"], label: "Close any open panel" },
] as const;





function lsGet<T>(k: string, fb: T): T {
  if (typeof window === "undefined") return fb;
  try { const r = localStorage.getItem(k); return r ? JSON.parse(r) : fb; }
  catch { return fb; }
}
function lsSet(k: string, v: unknown) {
  if (typeof window === "undefined") return;
  try { localStorage.setItem(k, JSON.stringify(v)); } catch { }
}
function todayStr() { return new Date().toISOString().slice(0, 10); }
function relTime(ts: number): string {
  const d = Date.now() - ts;
  if (d < 60_000) return "just now";
  if (d < 3_600_000) return `${Math.floor(d / 60_000)}m ago`;
  if (d < 86_400_000) return `${Math.floor(d / 3_600_000)}h ago`;
  return new Date(ts).toLocaleDateString();
}
function makeId() { return Math.random().toString(36).slice(2, 9) + Date.now().toString(36); }





function tone(freq: number, dur = 0.2, vol = 0.06) {
  try {

    const C = new (window.AudioContext || (window as any).webkitAudioContext)() as AudioContext;
    const o = C.createOscillator(), g = C.createGain();
    o.type = "sine"; o.frequency.setValueAtTime(freq, C.currentTime);
    g.gain.setValueAtTime(vol, C.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, C.currentTime + dur);
    o.connect(g); g.connect(C.destination); o.start(); o.stop(C.currentTime + dur);
  } catch { }
}
const sfx = {
  click: () => tone(880, 0.07, 0.04),
  copy: () => tone(1046, 0.1, 0.04),
  success: () => { tone(523, 0.14, 0.07); setTimeout(() => tone(659, 0.14, 0.06), 110); setTimeout(() => tone(784, 0.22, 0.05), 220); },
  star: () => tone(1318, 0.09, 0.04),
};





async function exportAsPng(input: string, emoji: string) {
  const W = 880, H = 380;
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H;
  const ctx = cv.getContext("2d")!;


  ctx.fillStyle = "#FAFAF9"; ctx.fillRect(0, 0, W, H);


  ctx.fillStyle = "#0F172A"; ctx.fillRect(0, 0, W, 6);


  ctx.fillStyle = "#0F172A"; ctx.font = "bold 22px Arial";
  ctx.fillText("ML Emoji Translation", 40, 56);


  ctx.strokeStyle = "#E7E5E4"; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(40, 72); ctx.lineTo(W - 40, 72); ctx.stroke();


  ctx.fillStyle = "#A8A29E"; ctx.font = "bold 10px Arial";
  ctx.fillText("GLOSS INPUT", 40, 100);


  ctx.fillStyle = "#1C1917"; ctx.font = "16px 'Courier New', monospace";
  ctx.fillText(input.length > 75 ? input.slice(0, 75) + "…" : input, 40, 124);


  ctx.fillStyle = "#A8A29E"; ctx.font = "bold 10px Arial";
  ctx.fillText("EMOJI SEQUENCE", 40, 164);


  ctx.font = "48px serif";
  const tokens = emoji.split(/\s+/).filter(Boolean);
  const sp = Math.min(72, (W - 80) / Math.max(tokens.length, 1));
  tokens.forEach((e, i) => ctx.fillText(e, 40 + i * sp, 228));


  ctx.fillStyle = "#F5F5F4"; ctx.fillRect(0, H - 44, W, 44);
  ctx.strokeStyle = "#E7E5E4"; ctx.beginPath(); ctx.moveTo(0, H - 44); ctx.lineTo(W, H - 44); ctx.stroke();
  ctx.fillStyle = "#A8A29E"; ctx.font = "11px Arial";
  ctx.fillText("SignDecoder · ML-Generated Emoji Sequence", 40, H - 16);
  ctx.save(); ctx.textAlign = "right";
  ctx.fillText(new Date().toLocaleDateString(), W - 40, H - 16);
  ctx.restore();

  const a = document.createElement("a");
  a.download = `signdeocder-${Date.now()}.png`;
  a.href = cv.toDataURL(); a.click();
}





interface Particle { x: number; y: number; vx: number; vy: number; color: string; size: number; alpha: number; decay: number; rotation: number; rotSpeed: number; rect: boolean; }

function ConfettiCanvas({ animKey }: { animKey: number }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const raf = useRef<number>(0);
  const pts = useRef<Particle[]>([]);

  useEffect(() => {
    if (animKey === 0) return;
    const cv = ref.current; if (!cv) return;
    cv.width = window.innerWidth; cv.height = window.innerHeight;
    const ctx = cv.getContext("2d")!;
    const COLORS = ["#a78bfa", "#f0abfc", "#fb7185", "#fbbf24", "#34d399", "#60a5fa", "#f9a8d4"];
    pts.current = Array.from({ length: 80 }, () => ({
      x: Math.random() * cv.width, y: cv.height * 0.45 + Math.random() * 60,
      vx: (Math.random() - 0.5) * 10, vy: -(Math.random() * 14 + 7),
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      size: Math.random() * 9 + 4, alpha: 1, decay: Math.random() * 0.014 + 0.009,
      rotation: Math.random() * Math.PI * 2, rotSpeed: (Math.random() - 0.5) * 0.18,
      rect: Math.random() > 0.5,
    }));
    const draw = () => {
      ctx.clearRect(0, 0, cv.width, cv.height);
      pts.current = pts.current.filter(p => p.alpha > 0.01);
      for (const p of pts.current) {
        p.x += p.vx; p.vy += 0.38; p.y += p.vy; p.alpha -= p.decay; p.rotation += p.rotSpeed;
        ctx.save(); ctx.globalAlpha = p.alpha; ctx.fillStyle = p.color;
        ctx.translate(p.x, p.y); ctx.rotate(p.rotation);
        if (p.rect) ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
        else { ctx.beginPath(); ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2); ctx.fill(); }
        ctx.restore();
      }
      if (pts.current.length > 0) raf.current = requestAnimationFrame(draw);
      else ctx.clearRect(0, 0, cv.width, cv.height);
    };
    raf.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf.current);
  }, [animKey]);

  return <canvas ref={ref} aria-hidden className="pointer-events-none fixed inset-0 w-full h-full z-[9998]" />;
}





function ToastStack({ items, remove }: { items: ToastItem[]; remove: (id: number) => void }) {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[9999] flex flex-col-reverse gap-2 items-center pointer-events-none">
      <AnimatePresence>
        {items.map(t => (
          <motion.div key={t.id}
            initial={{ opacity: 0, y: 24, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.9 }}
            onAnimationComplete={() => setTimeout(() => remove(t.id), 2600)}
            className={`px-5 py-2.5 rounded-full text-[13px] font-medium shadow-lg border
              ${t.type === "error"
                ? "bg-white text-red-600 border-red-200"
                : t.type === "info"
                  ? "bg-white text-text-secondary border-border"
                  : "bg-accent text-white border-accent"
              }`}
          >
            {t.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}





function ShortcutsModal({ onClose }: { onClose: () => void }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-[1000] flex items-center justify-center p-4" onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      <motion.div
        initial={{ scale: 0.94, y: 16, opacity: 0 }}
        animate={{ scale: 1, y: 0, opacity: 1 }}
        exit={{ scale: 0.94, y: 16, opacity: 0 }}
        transition={{ type: "spring", stiffness: 400, damping: 28 }}
        onClick={e => e.stopPropagation()}
        className="relative w-full max-w-md bg-white border border-border rounded-md shadow-xl overflow-hidden"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div className="flex items-center gap-2.5">
            <Keyboard size={15} className="text-text-secondary" />
            <span className="text-[15px] font-semibold text-text-primary">Keyboard Shortcuts</span>
          </div>
          <button onClick={onClose} className="w-7 h-7 rounded-full bg-surface-elevated hover:bg-border-strong/40 flex items-center justify-center transition-colors">
            <X size={13} className="text-text-secondary" />
          </button>
        </div>
        <div className="px-6 py-5 flex flex-col gap-3.5">
          {SHORTCUTS.map((s, i) => (
            <div key={i} className="flex items-center justify-between">
              <span className="text-[13px] text-text-secondary">{s.label}</span>
              <div className="flex items-center gap-1 ml-4 flex-shrink-0">
                {s.keys.map((k, j) => (
                  <React.Fragment key={k}>
                    {j > 0 && <span className="text-text-muted text-[11px]">+</span>}
                    <kbd className="px-2 py-0.5 text-[11px] font-bold text-text-secondary bg-surface-elevated border border-border rounded-sm font-mono">
                      {k}
                    </kbd>
                  </React.Fragment>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="px-6 pb-5 text-center text-[11px] text-text-muted">
          Press <kbd className="px-1 text-text-muted bg-surface-elevated border border-border rounded text-[10px] font-mono">Esc</kbd> to close
        </div>
      </motion.div>
    </motion.div>
  );
}





function SettingsPanel({ settings, onChange, onClose }: {
  settings: AppSettings; onChange: (s: AppSettings) => void; onClose: () => void;
}) {
  const toggle = (k: keyof AppSettings) => onChange({ ...settings, [k]: !settings[k] });
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
      className="mt-3 bg-surface-elevated border border-border rounded-sm p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">Preferences</span>
        <button onClick={onClose} className="w-5 h-5 flex items-center justify-center text-text-muted hover:text-text-primary transition-colors">
          <X size={11} />
        </button>
      </div>
      <div className="flex flex-col gap-3">
        <ToggleRow label="Animations" desc="Stagger bounce effects" icon={<Activity size={13} />} checked={settings.animationsEnabled} onChange={() => toggle("animationsEnabled")} />
        <ToggleRow label="Sound Effects" desc="Subtle audio on actions" icon={settings.soundEnabled ? <Volume2 size={13} /> : <VolumeX size={13} />} checked={settings.soundEnabled} onChange={() => toggle("soundEnabled")} />
      </div>
    </motion.div>
  );
}

function ToggleRow({ label, desc, icon, checked, onChange }: { label: string; desc: string; icon: React.ReactNode; checked: boolean; onChange: () => void }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2.5">
        <span className="text-text-muted">{icon}</span>
        <div>
          <p className="text-[13px] text-text-primary font-medium">{label}</p>
          <p className="text-[11px] text-text-muted">{desc}</p>
        </div>
      </div>
      <button
        onClick={onChange} role="switch" aria-checked={checked}
        className={`relative w-9 h-5 rounded-full transition-colors duration-200 ${checked ? "bg-accent" : "bg-border-strong"}`}
      >
        <motion.span
          animate={{ x: checked ? 17 : 2 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className="absolute top-[3px] left-0 w-[14px] h-[14px] rounded-full bg-white shadow-sm block"
        />
      </button>
    </div>
  );
}





function ShareModal({ input, emoji, onClose, onToast }: {
  input: string; emoji: string; onClose: () => void;
  onToast: (msg: string, type: ToastItem["type"]) => void;
}) {
  const text = `ISL gloss "${input}" → emojis: ${emoji}\n\n— SignDecoder`;
  const opts = [
    { label: "Twitter / X", icon: <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>, action: () => { window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, "_blank"); onClose(); } },
    { label: "WhatsApp", icon: <MessageCircle size={15} />, action: () => { window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank"); onClose(); } },
    { label: "Copy as Text", icon: <Link2 size={15} />, action: () => { navigator.clipboard.writeText(text); onToast("Copied! 📋", "success"); onClose(); } },
  ];
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="fixed inset-0 z-[1000] flex items-center justify-center p-4" onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      <motion.div
        initial={{ scale: 0.94, y: 16, opacity: 0 }} animate={{ scale: 1, y: 0, opacity: 1 }}
        exit={{ scale: 0.94, y: 16, opacity: 0 }}
        transition={{ type: "spring", stiffness: 400, damping: 28 }}
        onClick={e => e.stopPropagation()}
        className="relative w-full max-w-sm bg-white border border-border rounded-md shadow-xl p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <span className="flex items-center gap-2 text-[15px] font-semibold text-text-primary"><Share2 size={14} className="text-text-secondary" /> Share Result</span>
          <button onClick={onClose} className="w-7 h-7 rounded-full bg-surface-elevated hover:bg-border flex items-center justify-center transition-colors"><X size={13} className="text-text-secondary" /></button>
        </div>
        <div className="bg-surface-elevated border border-border rounded-sm px-4 py-3 mb-4">
          <p className="text-[11px] text-text-muted uppercase tracking-widest font-bold mb-1">Preview</p>
          <p className="text-[12px] text-text-secondary leading-relaxed line-clamp-3">{text}</p>
        </div>
        <div className="flex flex-col gap-2">
          {opts.map(o => (
            <button key={o.label} onClick={o.action}
              className="flex items-center gap-3 px-4 py-2.5 rounded-sm border border-border text-text-secondary text-[13px] font-medium hover:bg-surface-elevated transition-colors"
            >
              <span className="text-text-muted">{o.icon}</span>{o.label}
            </button>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}





function IconBtn({ id, onClick, icon, title, active = false }: { id?: string; onClick: () => void; icon: React.ReactNode; title?: string; active?: boolean }) {
  return (
    <button id={id} onClick={onClick} title={title}
      className={`w-7 h-7 rounded-sm flex items-center justify-center border transition-all duration-150
        ${active ? "bg-accent text-white border-accent" : "bg-surface-elevated border-border text-text-secondary hover:border-border-strong hover:text-text-primary"}`}
    >{icon}</button>
  );
}

function ActionBtn({ id, onClick, icon, label, title, active = false }: { id?: string; onClick: () => void; icon: React.ReactNode; label: string; title?: string; active?: boolean }) {
  return (
    <motion.button id={id} onClick={onClick} title={title} whileHover={{ y: -1 }} whileTap={{ scale: 0.96 }}
      className={`flex flex-col items-center justify-center gap-1 py-2 rounded-sm border text-[10px] font-bold uppercase tracking-wide transition-all
        ${active ? "bg-accent text-white border-accent" : "bg-surface-elevated border-border text-text-secondary hover:bg-white hover:border-border-strong hover:text-text-primary"}`}
    >
      {icon}<span>{label}</span>
    </motion.button>
  );
}





let _tid = 0;

export default function GlossToEmojiConverter({ glossText = "" }: GlossToEmojiConverterProps) {


  const [text, setText] = useState(glossText || "");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [confettiKey, setConfettiKey] = useState(0);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const [history, setHistory] = useState<ConversionResult[]>([]);
  const [settings, setSettings] = useState<AppSettings>({ animationsEnabled: true, soundEnabled: false });
  const [stats, setStats] = useState<AppStats>({ total: 0, today: 0, lastDate: todayStr() });

  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [showExamples, setShowExamples] = useState(false);


  useEffect(() => {
    setHistory(lsGet<ConversionResult[]>(SK.history, []));
    setSettings(lsGet<AppSettings>(SK.settings, { animationsEnabled: true, soundEnabled: false }));
    const s = lsGet<AppStats>(SK.stats, { total: 0, today: 0, lastDate: todayStr() });
    if (s.lastDate !== todayStr()) { s.today = 0; s.lastDate = todayStr(); }
    setStats(s);
  }, []);

  useEffect(() => { lsSet(SK.settings, settings); }, [settings]);


  const emojiTokens = useMemo(() => result?.emoji ? result.emoji.split(/\s+/).filter(Boolean) : [], [result]);
  const favoriteCount = useMemo(() => history.filter(h => h.isFavorite).length, [history]);
  const anim = settings.animationsEnabled;


  const toast = useCallback((message: string, type: ToastItem["type"] = "info") => {
    const id = ++_tid;
    setToasts(p => [...p, { id, message, type }]);
    setTimeout(() => setToasts(p => p.filter(t => t.id !== id)), 3400);
  }, []);

  const bumpStats = useCallback(() => {
    setStats(prev => {
      const next: AppStats = { total: prev.total + 1, today: prev.lastDate === todayStr() ? prev.today + 1 : 1, lastDate: todayStr() };
      lsSet(SK.stats, next); return next;
    });
  }, []);

  const pushHistory = useCallback((item: ConversionResult) => {
    setHistory(prev => {
      const u = [item, ...prev.filter(h => h.id !== item.id)].slice(0, MAX_HIST);
      lsSet(SK.history, u); return u;
    });
  }, []);

  const toggleFav = useCallback((id: string) => {
    setHistory(prev => {
      const u = prev.map(h => h.id === id ? { ...h, isFavorite: !h.isFavorite } : h);
      lsSet(SK.history, u);
      setResult(r => r?.id === id ? { ...r, isFavorite: !r.isFavorite } : r);
      return u;
    });
    if (settings.soundEnabled) sfx.star();
  }, [settings.soundEnabled]);


  const handleConvert = useCallback(async (text: string) => {
    if (!text.trim()) { toast("No gloss text — translate something first.", "info"); return; }
    setIsLoading(true); setError(null); setResult(null);
    if (settings.soundEnabled) sfx.click();
    try {
      const res = await fetch(API_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: text.trim() }) });
      if (!res.ok) { const b = await res.json().catch(() => ({})); throw new Error(b?.detail ?? `Server error ${res.status}`); }
      const data = await res.json();
      const item: ConversionResult = { id: makeId(), input: data.input, emoji: data.emoji, timestamp: Date.now(), isFavorite: false };
      setResult(item); pushHistory(item); bumpStats();
      // setTimeout(() => setConfettiKey(k => k + 1), 200);
      toast("Succesfull Compiled ✅", "success");
      if (settings.soundEnabled) sfx.success();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setError(msg); toast(`Error: ${msg}`, "error");
    } finally { setIsLoading(false); }
  }, [toast, pushHistory, bumpStats, settings.soundEnabled]);


  useEffect(() => {
    setText(glossText);
    if (glossText.trim()) {
      handleConvert(glossText);
    }
  }, [glossText, handleConvert]);


  const handleCopy = useCallback(() => {
    if (!result?.emoji) return;
    navigator.clipboard.writeText(result.emoji).then(() => {
      setCopied(true); toast("Emojis copied!", "success");
      if (settings.soundEnabled) sfx.copy();
      setTimeout(() => setCopied(false), 2000);
    });
  }, [result, toast, settings.soundEnabled]);


  const handleExport = useCallback(async () => {
    if (!result) return;
    try { await exportAsPng(result.input, result.emoji); toast("Image saved! 📸", "success"); }
    catch { toast("Export failed — try again.", "error"); }
  }, [result, toast]);


  useEffect(() => {
    const fn = (e: KeyboardEvent) => {
      const ctrl = e.ctrlKey || e.metaKey;
      const editing = ["INPUT", "TEXTAREA"].includes((e.target as HTMLElement).tagName);
      if (e.key === "Escape") { setShowShortcuts(false); setShowShare(false); setShowSettings(false); return; }
      if (ctrl && e.key === "Enter") { e.preventDefault(); handleConvert(text); }
      if (!editing) {
        if (e.key === "?" || e.key === "/") { e.preventDefault(); setShowShortcuts(v => !v); }
        if (e.key === "h" || e.key === "H") setShowHistory(v => !v);
        if ((e.key === "f" || e.key === "F") && result) toggleFav(result.id);
      }
      if (ctrl && e.shiftKey && e.key === "C") { e.preventDefault(); handleCopy(); }
      if (ctrl && e.shiftKey && e.key === "E") { e.preventDefault(); handleExport(); }
      if (ctrl && e.shiftKey && e.key === "S" && result) { e.preventDefault(); setShowShare(true); }
    };
    window.addEventListener("keydown", fn);
    return () => window.removeEventListener("keydown", fn);
  }, [text, result, handleConvert, handleCopy, handleExport, toggleFav]);





  return (
    <>
      {/* <ConfettiCanvas animKey={confettiKey} /> */}
      <ToastStack items={toasts} remove={id => setToasts(p => p.filter(t => t.id !== id))} />

      <AnimatePresence>
        {showShortcuts && <ShortcutsModal onClose={() => setShowShortcuts(false)} />}
      </AnimatePresence>
      <AnimatePresence>
        {showShare && result && (
          <ShareModal input={result.input} emoji={result.emoji} onClose={() => setShowShare(false)} onToast={toast} />
        )}
      </AnimatePresence>

      { }
      <div className="flex items-center justify-between mb-4">
        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
          ML Emoji Translation
        </span>

        { }
        <div className="flex items-center gap-3">
          { }
          <span className="hidden sm:flex items-center gap-2.5 text-[11px] text-text-muted">
            <span className="flex items-center gap-1"><TrendingUp size={10} className="text-accent" />{stats.total} total</span>
            <span className="w-px h-3 bg-border" />
            <span className="flex items-center gap-1"><Activity size={10} className="text-accent" />{stats.today} today</span>
          </span>

          <div className="flex items-center gap-1">
            <IconBtn id="shortcuts-btn" onClick={() => setShowShortcuts(true)} icon={<Keyboard size={12} />} title="Keyboard shortcuts (?)" />
            <IconBtn id="settings-btn" onClick={() => setShowSettings(v => !v)} icon={<Settings size={12} />} title="Settings" active={showSettings} />
          </div>
        </div>
      </div>

      { }
      <AnimatePresence>
        {showSettings && (
          <SettingsPanel settings={settings} onChange={setSettings} onClose={() => setShowSettings(false)} />
        )}
      </AnimatePresence>

      { }
      <div className="mb-4">
        <button id="toggle-examples-btn" onClick={() => setShowExamples(v => !v)}
          className="flex items-center gap-1.5 text-[11px] font-bold text-text-muted hover:text-text-secondary uppercase tracking-[0.08em] transition-colors mb-2"
        >
          <BookOpen size={11} />
          Example Prompts
          {showExamples ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
        </button>
        <AnimatePresence>
          {showExamples && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
              <div className="grid grid-cols-2 gap-1.5 pb-1">
                {EXAMPLES.map(p => (
                  <button key={p} onClick={() => { setText(p.toUpperCase()); handleConvert(p); }} title={p}
                    className="text-left px-3 py-2 rounded-sm bg-surface-elevated border border-border hover:bg-white hover:border-border-strong text-[11px] text-text-secondary hover:text-text-primary font-mono truncate transition-all"
                  >{p}</button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      { }
      <div className="relative overflow-hidden bg-white border border-border rounded-md px-4 py-3 mb-4 shadow-sm focus-within:border-accent transition-colors">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value.toUpperCase())}
          placeholder="TYPE GLOSS WORDS HERE (e.g. YESTERDAY HOME I PIZZA EAT)..."
          className="w-full bg-transparent border-0 outline-none resize-none font-mono text-[14px] text-text-primary tracking-wide placeholder-text-muted focus:ring-0 focus:outline-none"
          rows={3}
        />
        {text.trim() && (
          <button
            onClick={() => setText("")}
            className="absolute top-2 right-2 text-text-muted hover:text-text-primary transition-colors text-[10px] uppercase font-bold tracking-wider"
          >
            Clear
          </button>
        )}
      </div>

      { }
      <motion.button id="convert-to-emoji-btn"
        onClick={() => handleConvert(text)}
        disabled={isLoading || !text.trim()}
        whileHover={!isLoading && text.trim() ? { y: -1 } : {}}
        whileTap={!isLoading && text.trim() ? { scale: 0.98 } : {}}
        className="w-full mb-4 py-3 rounded-sm font-medium text-[14px] text-white bg-accent hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2.5 shadow-xs"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-4 w-4 text-white/70" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Processing…
          </>
        ) : (
          <>
            <Sparkles size={14} />
            Convert to Emoji
            <kbd className="ml-0.5 px-1.5 py-0.5 text-[10px] bg-white/15 rounded-sm font-mono text-white/70">⌃↵</kbd>
          </>
        )}
      </motion.button>

      { }
      <AnimatePresence>
        {error && (
          <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="rounded-sm bg-red-50 border border-red-200 px-4 py-3 mb-4"
          >
            <p className="text-[13px] text-red-700 font-medium">⚠ {error}</p>
            <p className="text-[11px] text-red-500 mt-0.5">Check that the backend is running at localhost:8000</p>
          </motion.div>
        )}
      </AnimatePresence>

      { }
      <AnimatePresence mode="wait">
        {result ? (
          <motion.div key={result.id} initial={anim ? { opacity: 0, y: 10 } : {}} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>

            { }
            <div className="bg-surface-elevated border border-border rounded-sm px-5 py-5 mb-3 min-h-[80px] flex items-center justify-center">
              {emojiTokens.length > 0 ? (
                <div className="flex flex-wrap gap-3 justify-center">
                  {emojiTokens.map((e, i) => (
                    <motion.span key={`${e}-${i}-${result.id}`}
                      initial={anim ? { opacity: 0, scale: 0.2, y: 16 } : {}}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      transition={anim ? { delay: i * 0.09, type: "spring", stiffness: 450, damping: 14 } : {}}
                      className="text-3xl md:text-4xl select-none cursor-default hover:scale-110 transition-transform"
                      aria-label={`emoji ${i + 1}`}
                    >{e}</motion.span>
                  ))}
                </div>
              ) : (
                <p className="text-text-muted text-[13px] italic">No emojis returned — try a different gloss.</p>
              )}
            </div>

            { }
            <div className="grid grid-cols-5 gap-2">
              <ActionBtn id="copy-emoji-btn" onClick={handleCopy} icon={copied ? <Check size={13} className="text-highlight" /> : <Copy size={13} />} label={copied ? "Copied" : "Copy"} title="Copy (Ctrl+Shift+C)" />
              <ActionBtn id="favorite-emoji-btn" onClick={() => toggleFav(result.id)} icon={<Star size={13} className={result.isFavorite ? "fill-current" : ""} />} label={result.isFavorite ? "Saved" : "Save"} title="Favourite (F)" active={result.isFavorite} />
              <ActionBtn id="export-emoji-btn" onClick={handleExport} icon={<Download size={13} />} label="Export" title="Export PNG (Ctrl+Shift+E)" />
              <ActionBtn id="share-emoji-btn" onClick={() => setShowShare(true)} icon={<Share2 size={13} />} label="Share" title="Share (Ctrl+Shift+S)" />
              <ActionBtn id="reset-emoji-btn" onClick={() => { setResult(null); setError(null); }} icon={<RotateCcw size={13} />} label="Reset" title="Clear" />
            </div>
          </motion.div>
        ) : !error && !isLoading ? (
          <motion.p key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="text-center py-4 text-[13px] text-text-muted"
          >
            Translate text above, then click <strong className="text-text-secondary">Convert to Emoji</strong>.
          </motion.p>
        ) : null}
      </AnimatePresence>

      { }
      {history.length > 0 && (
        <div className="mt-6 pt-5 border-t border-border">
          <button id="toggle-history-btn" onClick={() => setShowHistory(v => !v)}
            className="flex items-center gap-2 w-full text-[11px] font-bold text-text-muted hover:text-text-secondary uppercase tracking-[0.08em] transition-colors"
          >
            <Clock size={11} />
            History ({history.length})
            {favoriteCount > 0 && (
              <span className="flex items-center gap-0.5 text-accent">
                <Star size={9} className="fill-accent" />{favoriteCount}
              </span>
            )}
            <span className="ml-auto">{showHistory ? <ChevronUp size={10} /> : <ChevronDown size={10} />}</span>
          </button>

          <AnimatePresence>
            {showHistory && (
              <motion.ul initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mt-3 flex flex-col gap-1.5 overflow-hidden">
                {history.map((item, idx) => (
                  <motion.li key={item.id} initial={anim ? { opacity: 0, x: -8 } : {}} animate={{ opacity: 1, x: 0 }} transition={anim ? { delay: idx * 0.025 } : {}}>
                    <div className="flex items-center gap-2.5 rounded-sm bg-surface-elevated hover:bg-white border border-border px-3 py-2.5 cursor-pointer transition-colors group"
                      onClick={() => { setResult(item); setError(null); }}
                    >
                      <button onClick={e => { e.stopPropagation(); toggleFav(item.id); }} title="Toggle favourite"
                        className={`shrink-0 transition-colors ${item.isFavorite ? "text-accent" : "text-text-muted hover:text-accent"}`}
                      >
                        <Star size={11} className={item.isFavorite ? "fill-current" : ""} />
                      </button>
                      <div className="flex-1 min-w-0">
                        <p className="font-mono text-[11px] text-text-muted truncate group-hover:text-text-secondary transition-colors">{item.input}</p>
                        <p className="text-[16px] leading-snug mt-0.5">{item.emoji}</p>
                      </div>
                      <span className="text-[10px] text-text-muted shrink-0">{relTime(item.timestamp)}</span>
                    </div>
                  </motion.li>
                ))}
              </motion.ul>
            )}
          </AnimatePresence>
        </div>
      )}
    </>
  );
}
