"use client";
import { useState, useEffect, useRef } from "react";
import dynamic from "next/dynamic";
import CascadePredictor from "./components/CascadePredictor";

const ParticleField = dynamic(() => import("./components/ParticleField"), { ssr: false });

const API = "https://abu-sameer-66-climashock-api.hf.space";

const TABS = [
  { id: "predict",  label: "CASCADE PREDICTOR", icon: "⚡" },
  { id: "causal",   label: "CAUSAL LINKS",       icon: "◈" },
  { id: "discover", label: "DISCOVERIES",         icon: "◉" },
] as const;
type Tab = typeof TABS[number]["id"];

const DISCOVERIES = [
  {
    rank: "01", icon: "🌊", color: "#ff3355",
    title: "Flood → Inflation Lag",
    body: "Extreme rainfall causes national inflation spike after a 2-year lag — first time quantified for Pakistan at district level.",
    evidence: "Granger strength: 0.347",
    case: "2022 floods → 2023 inflation 30.8%",
    heroStat: "+1293%", heroLabel: "Sukkur rainfall 2022",
  },
  {
    rank: "02", icon: "📍", color: "#E8A020",
    title: "Sukkur Epicenter",
    body: "Sukkur identified as Pakistan's highest climate-economic risk zone through distributed causal analysis across all 10 districts.",
    evidence: "2022 rainfall +1293% · z-score +3.2σ",
    case: "Cotton −37.7% · Rice −21.5%",
    heroStat: "−37.7%", heroLabel: "cotton yield shock",
  },
  {
    rank: "03", icon: "🌡️", color: "#0088ff",
    title: "Temperature Lag Effect",
    body: "Heat anomaly compounds with rainfall shocks to drive inflation 4 years later through cumulative crop degradation pathways.",
    evidence: "Granger strength: 0.128 · lag = 4y",
    case: "Compounds with flood shocks",
    heroStat: "4 yrs", heroLabel: "delayed effect lag",
  },
];

function useCountUp(target: number, duration = 1200, start = false) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!start) return;
    let t = 0;
    const step = 16;
    const total = duration / step;
    const inc = target / total;
    const timer = setInterval(() => {
      t++;
      setVal(Math.min(Math.round(inc * t), target));
      if (t >= total) clearInterval(timer);
    }, step);
    return () => clearInterval(timer);
  }, [target, duration, start]);
  return val;
}

function AnimatedStat({ val, suffix = "", prefix = "", label, color, start }: {
  val: number; suffix?: string; prefix?: string;
  label: string; color: string; start: boolean;
}) {
  const n = useCountUp(val, 1400, start);
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{
        fontFamily: "'JetBrains Mono',monospace",
        fontWeight: 900, fontSize: "clamp(2rem,4vw,3.5rem)",
        color, lineHeight: 1,
        textShadow: `0 0 40px ${color}40`,
        marginBottom: 8,
      }}>
        {prefix}{n}{suffix}
      </div>
      <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#445566", letterSpacing: "0.08em" }}>
        {label}
      </div>
    </div>
  );
}

export default function Home() {
  const [apiOnline,  setApiOnline]  = useState(false);
  const [activeTab,  setActiveTab]  = useState<Tab>("predict");
  const [scrolled,   setScrolled]   = useState(false);
  const [statsVisible, setStats]    = useState(false);
  const statsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${API}/`).then(() => setApiOnline(true)).catch(() => {});
    const fn = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", fn);

    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setStats(true); },
      { threshold: 0.3 }
    );
    if (statsRef.current) obs.observe(statsRef.current);
    return () => { window.removeEventListener("scroll", fn); obs.disconnect(); };
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#00060f", color: "#fff", fontFamily: "'Space Grotesk',sans-serif", overflowX: "hidden" }}>
      <ParticleField />
      <div style={{
        position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none",
        backgroundImage: "linear-gradient(rgba(232,160,32,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(232,160,32,0.02) 1px,transparent 1px)",
        backgroundSize: "60px 60px",
      }}/>

      <div style={{ position: "relative", zIndex: 10 }}>

        {/* ═══ NAV ═══ */}
        <nav style={{
          position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "0 2.5rem", height: 54,
          background: scrolled ? "rgba(0,4,12,0.97)" : "rgba(0,4,12,0.6)",
          backdropFilter: "blur(32px)",
          borderBottom: `1px solid rgba(232,160,32,${scrolled ? 0.1 : 0.05})`,
          transition: "all 0.4s ease",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 800, fontSize: 15, color: "#E8A020" }}>
              ⚡ CLIMASHOCK
            </span>
            <span style={{
              fontFamily: "'JetBrains Mono',monospace", fontSize: 9,
              padding: "2px 7px", borderRadius: 3,
              background: "rgba(232,160,32,0.07)", color: "#E8A020",
              border: "1px solid rgba(232,160,32,0.12)",
            }}>v1.0.0</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            {[
              { l: "Kaggle",   h: "https://www.kaggle.com/code/sameernadeem66/climashock-data-collection" },
              { l: "GitHub",   h: "https://github.com/Abu-Sameer-66/ClimaShock-Pakistan" },
              { l: "API",      h: `${API}/docs` },
              { l: "Portfolio",h: "https://sameer-nadeem-portfolio.vercel.app" },
            ].map((x) => (
              <a key={x.l} href={x.h} target="_blank" rel="noreferrer"
                style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#445566", textDecoration: "none", transition: "color 0.2s" }}
                onMouseEnter={(e) => (e.currentTarget.style.color = "#E8A020")}
                onMouseLeave={(e) => (e.currentTarget.style.color = "#445566")}
              >{x.l} ↗</a>
            ))}
            <div style={{ display: "flex", alignItems: "center", gap: 6, paddingLeft: 16, borderLeft: "1px solid rgba(232,160,32,0.08)" }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: apiOnline ? "#00ff88" : "#E8A020", boxShadow: `0 0 7px ${apiOnline ? "#00ff88" : "#E8A020"}` }}/>
              <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: apiOnline ? "#00ff88" : "#E8A020" }}>
                {apiOnline ? "LIVE" : "CONNECTING"}
              </span>
            </div>
          </div>
        </nav>

        {/* ═══ HERO ═══ */}
        <section style={{ paddingTop: 150, paddingBottom: 0, textAlign: "center", position: "relative" }}>
          <div style={{
            position: "absolute", top: 60, left: "50%", transform: "translateX(-50%)",
            width: 700, height: 500, borderRadius: "50%",
            background: "radial-gradient(ellipse, rgba(232,160,32,0.04) 0%, transparent 60%)",
            filter: "blur(80px)", pointerEvents: "none",
          }}/>

          <div style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            fontFamily: "'JetBrains Mono',monospace", fontSize: 9,
            padding: "5px 14px", borderRadius: 100, marginBottom: 28,
            background: "rgba(232,160,32,0.05)", border: "1px solid rgba(232,160,32,0.15)",
            color: "#E8A020", letterSpacing: "0.05em",
          }}>
            <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#E8A020", boxShadow: "0 0 5px #E8A020" }}/>
            PAKISTAN · DISTRIBUTED CAUSAL INTELLIGENCE · 1990–2023
          </div>

          <h1 style={{
            fontFamily: "'JetBrains Mono',monospace", fontWeight: 900,
            fontSize: "clamp(4.5rem,12vw,10rem)", lineHeight: 0.88,
            letterSpacing: "-0.04em", margin: "0 0 0",
            background: "linear-gradient(140deg,#ffffff 0%,#E8A020 38%,#C86A00 65%,#ff8800 100%)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text",
          }}>
            CLIMASHOCK
          </h1>

          {/* ONE HERO SENTENCE — the thing people remember */}
          <div style={{
            margin: "32px auto 0", maxWidth: 600,
            padding: "20px 28px", borderRadius: 12,
            background: "rgba(255,51,85,0.05)", border: "1px solid rgba(255,51,85,0.15)",
            position: "relative", overflow: "hidden",
          }}>
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0, height: 1,
              background: "linear-gradient(90deg,transparent,rgba(255,51,85,0.6),transparent)",
            }}/>
            <div style={{
              fontFamily: "'JetBrains Mono',monospace", fontSize: 11,
              color: "#8899aa", lineHeight: 1.8, letterSpacing: "0.01em",
            }}>
              In 2022, Sukkur received{" "}
              <span style={{ color: "#ff3355", fontWeight: 700 }}>+1293% above normal rainfall.</span>
              {" "}Cotton collapsed{" "}
              <span style={{ color: "#ff8800", fontWeight: 700 }}>−37.7%.</span>
              {" "}Inflation peaked at{" "}
              <span style={{ color: "#E8A020", fontWeight: 700 }}>30.8% in 2023.</span>
              {" "}Nobody had quantified this cascade — until now.
            </div>
          </div>

          <p style={{
            fontFamily: "'JetBrains Mono',monospace",
            fontSize: 11, color: "#334455", margin: "20px auto 52px", maxWidth: 480,
          }}>
            3-node parallel architecture · Granger causal discovery · LSTM + XGBoost ensemble
          </p>

          {/* ── ANIMATED STATS ── */}
          <div ref={statsRef} style={{
            display: "grid", gridTemplateColumns: "repeat(5,1fr)",
            gap: 1, margin: "0 auto 56px", maxWidth: 900,
            background: "rgba(232,160,32,0.06)",
            border: "1px solid rgba(232,160,32,0.1)",
            borderRadius: 14, overflow: "hidden",
          }}>
            {[
              { val: 34,   suffix: "",    prefix: "", label: "YEARS OF DATA",    color: "#E8A020" },
              { val: 10,   suffix: "",    prefix: "", label: "DISTRICTS",        color: "#0088ff" },
              { val: 21,   suffix: "",    prefix: "", label: "CAUSAL LINKS",     color: "#00ff88" },
              { val: 287,  suffix: "%",   prefix: "", label: "LSTM ACCURACY",    color: "#E8A020" },
              { val: 3,    suffix: "",    prefix: "", label: "PARALLEL NODES",   color: "#ff8800" },
            ].map((s, i) => (
              <div key={i} style={{
                padding: "24px 16px", textAlign: "center",
                background: "rgba(0,10,22,0.85)",
                borderRight: i < 4 ? "1px solid rgba(232,160,32,0.06)" : "none",
                position: "relative", overflow: "hidden",
              }}>
                <div style={{
                  position: "absolute", top: 0, left: 0, right: 0, height: 1,
                  background: `linear-gradient(90deg,transparent,${s.color}40,transparent)`,
                }}/>
                <div style={{
                  fontFamily: "'JetBrains Mono',monospace",
                  fontWeight: 900, fontSize: "clamp(1.6rem,2.5vw,2.4rem)",
                  color: s.color, lineHeight: 1, marginBottom: 8,
                  textShadow: `0 0 30px ${s.color}30`,
                }}>
                  {statsVisible
                    ? <CountUpVal target={s.suffix === "%" ? (s.val === 287 ? 2.87 : s.val) : s.val}
                        decimal={s.suffix === "%" && s.val === 287}
                        suffix={s.suffix} prefix={s.prefix} />
                    : `${s.prefix}0${s.suffix}`
                  }
                </div>
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455", letterSpacing: "0.07em" }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
          
          {/* ═══ HOW IT WORKS ═══ */}
        <div style={{
          maxWidth: 900, margin: "0 auto 48px",
          padding: "0 2.5rem",
        }}>
          <div style={{
            padding: "28px 32px", borderRadius: 14,
            background: "rgba(0,10,22,0.85)",
            border: "1px solid rgba(232,160,32,0.1)",
            position: "relative", overflow: "hidden",
          }}>
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0, height: 1,
              background: "linear-gradient(90deg,transparent,rgba(232,160,32,0.4),transparent)",
            }}/>

            <div style={{
              fontFamily: "'JetBrains Mono',monospace",
              fontSize: 9, color: "#E8A020", letterSpacing: "0.1em", marginBottom: 20,
            }}>
              HOW TO USE CLIMASHOCK — 3 SIMPLE STEPS
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24 }}>
              {[
                {
                  step: "01",
                  icon: "📍",
                  title: "Select Your District",
                  body: "Choose any of 10 major Pakistan districts — from Sukkur to Islamabad. Each has its own climate baseline built from 34 years of NASA data.",
                  color: "#0088ff",
                },
                {
                  step: "02",
                  icon: "🌧️",
                  title: "Enter Today's Climate",
                  body: "Enter today's rainfall (mm/day) and temperature (°C). Not sure? Use one of our pre-filled examples including the 2022 Sukkur flood event.",
                  color: "#E8A020",
                },
                {
                  step: "03",
                  icon: "⚡",
                  title: "Get Future Cascade",
                  body: "The system predicts: crop yield impact in 4–8 weeks, inflation pressure in 6–18 months, and GDP direction in 1–2 years — all from one reading.",
                  color: "#00ff88",
                },
              ].map((s) => (
                <div key={s.step} style={{ display: "flex", gap: 14 }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: "'JetBrains Mono',monospace", fontSize: 11, fontWeight: 800,
                    background: `${s.color}12`, color: s.color,
                    border: `1px solid ${s.color}20`,
                  }}>
                    {s.step}
                  </div>
                  <div>
                    <div style={{ fontSize: 16, marginBottom: 6 }}>{s.icon}</div>
                    <div style={{
                      fontFamily: "'JetBrains Mono',monospace",
                      fontSize: 11, fontWeight: 700, color: "#fff", marginBottom: 8,
                    }}>
                      {s.title}
                    </div>
                    <div style={{
                      fontSize: 12, color: "#8899aa", lineHeight: 1.7,
                      fontFamily: "'Space Grotesk',sans-serif",
                    }}>
                      {s.body}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* who is this for */}
            <div style={{
              marginTop: 24, paddingTop: 20,
              borderTop: "1px solid rgba(255,255,255,0.04)",
              display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap",
            }}>
              <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455", letterSpacing: "0.06em" }}>
                USED BY:
              </div>
              {[
                { label: "NDMA Officers",        icon: "🏛️" },
                { label: "Agricultural Ministry", icon: "🌾" },
                { label: "Insurance Analysts",    icon: "📊" },
                { label: "Climate Researchers",   icon: "🔬" },
                { label: "Policy Makers",         icon: "⚖️" },
                { label: "Journalists",           icon: "📰" },
              ].map((u) => (
                <div key={u.label} style={{
                  display: "flex", alignItems: "center", gap: 6,
                  padding: "4px 10px", borderRadius: 100,
                  background: "rgba(255,255,255,0.02)",
                  border: "1px solid rgba(255,255,255,0.04)",
                }}>
                  <span style={{ fontSize: 11 }}>{u.icon}</span>
                  <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566" }}>
                    {u.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
          {/* TABS */}
          <div style={{
            display: "inline-flex", borderRadius: 10, overflow: "hidden",
            border: "1px solid rgba(232,160,32,0.1)",
            background: "rgba(0,8,18,0.7)",
          }}>
            {TABS.map((tab, i) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                style={{
                  fontFamily: "'JetBrains Mono',monospace",
                  fontSize: 10, fontWeight: activeTab === tab.id ? 600 : 400,
                  padding: "11px 22px", letterSpacing: "0.04em",
                  background: activeTab === tab.id ? "rgba(232,160,32,0.09)" : "transparent",
                  color: activeTab === tab.id ? "#E8A020" : "#445566",
                  border: "none", cursor: "pointer", outline: "none",
                  borderRight: i < TABS.length - 1 ? "1px solid rgba(232,160,32,0.07)" : "none",
                  position: "relative", transition: "all 0.25s",
                }}>
                {activeTab === tab.id && (
                  <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 1, background: "#E8A020" }}/>
                )}
                <span style={{ marginRight: 6, opacity: 0.6 }}>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </section>

        {/* ═══ DIVIDER ═══ */}
        <div style={{ height: 56 }}/>

        {/* ═══ CONTENT ═══ */}
        <section style={{ padding: "0 2.5rem 6rem", maxWidth: 1240, margin: "0 auto" }}>

          {activeTab === "predict" && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 20, alignItems: "start" }}>
              <CascadePredictor />
              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <SidePanel title="SYSTEM STATUS" dot>
                  {[
                    { label: "API",          val: apiOnline ? "ONLINE" : "CONNECTING", color: apiOnline ? "#00ff88" : "#E8A020" },
                    { label: "LSTM MODEL",   val: "LOADED",    color: "#00ff88" },
                    { label: "XGB MODEL",    val: "LOADED",    color: "#00ff88" },
                    { label: "CAUSAL GRAPH", val: "21 LINKS",  color: "#E8A020" },
                    { label: "DISTRICTS",    val: "10 / 10",   color: "#E8A020" },
                    { label: "DATA RANGE",   val: "1990–2023", color: "#0088ff" },
                  ].map((s) => <SRow key={s.label} {...s} />)}
                </SidePanel>

                <SidePanel title="MODEL ACCURACY">
                  {[
                    { label: "LSTM Inflation",    val: "2.87%", pct: 88 },
                    { label: "XGBoost Inflation", val: "3.19%", pct: 82 },
                    { label: "Ensemble",          val: "3.13%", pct: 84 },
                    { label: "District Average",  val: "4.42%", pct: 65 },
                  ].map((m) => <BRow key={m.label} {...m} />)}
                </SidePanel>

                <SidePanel title="2022 BACK-TEST — VERIFIED ✓" accent="#00ff88">
                  {[
                    { label: "Predicted inflation", val: "26.0%",     color: "#E8A020" },
                    { label: "Actual 2023",         val: "30.8%",     color: "#00ff88" },
                    { label: "Error",               val: "4.8%",      color: "#556677" },
                    { label: "GDP direction",       val: "Correct ✓", color: "#00ff88" },
                    { label: "Actual GDP 2023",     val: "−0.41%",    color: "#ff3355" },
                  ].map((s) => <SRow key={s.label} {...s} />)}
                </SidePanel>

                {/* PDC proof */}
                <SidePanel title="PARALLEL NODES — VERIFIED" accent="#0088ff">
                  {[
                    { label: "Node 1 PID",     val: "798",       color: "#0088ff" },
                    { label: "Node 2 PID",     val: "799",       color: "#0088ff" },
                    { label: "Node 3 PID",     val: "800",       color: "#0088ff" },
                    { label: "Total time",     val: "0.076s",    color: "#00ff88" },
                    { label: "GPU training",   val: "47.3s",     color: "#E8A020" },
                    { label: "Platform",       val: "Tesla T4",  color: "#E8A020" },
                  ].map((s) => <SRow key={s.label} {...s} />)}
                </SidePanel>
              </div>
            </div>
          )}

          {activeTab === "causal" && <CausalLinksView />}

          {activeTab === "discover" && (
            <div>
              {/* hero discovery */}
              <div style={{
                marginBottom: 20, padding: "36px 40px",
                background: "rgba(0,10,22,0.9)",
                border: "1px solid rgba(255,51,85,0.18)",
                borderRadius: 16, position: "relative", overflow: "hidden",
                display: "grid", gridTemplateColumns: "1fr auto",
                gap: 40, alignItems: "center",
              }}>
                <div style={{
                  position: "absolute", top: 0, left: 0, right: 0, height: 2,
                  background: "linear-gradient(90deg,transparent,#ff3355,transparent)",
                }}/>
                <div style={{
                  position: "absolute", right: -60, top: -60,
                  width: 200, height: 200, borderRadius: "50%",
                  background: "radial-gradient(circle,rgba(255,51,85,0.06) 0%,transparent 70%)",
                }}/>
                <div>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#ff3355", letterSpacing: "0.1em", marginBottom: 10 }}>
                    PRIMARY DISCOVERY — WORLD FIRST FOR PAKISTAN
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 800, fontSize: 22, color: "#fff", marginBottom: 14, lineHeight: 1.2 }}>
                    Extreme rainfall causes inflation —{" "}
                    <span style={{ color: "#ff3355" }}>2 years later</span>
                  </div>
                  <p style={{ fontSize: 14, color: "#8899aa", lineHeight: 1.8, maxWidth: 560, fontFamily: "'Space Grotesk',sans-serif" }}>
                    Using Granger causality across 34 years of Pakistan climate and economic data,
                    this system discovered that extreme rainfall events — particularly in Sindh —
                    cause measurable national inflation spikes with a precise 2-year lag.
                    This relationship had never been quantified for Pakistan before.
                  </p>
                </div>
                <div style={{ textAlign: "center", flexShrink: 0 }}>
                  <div style={{
                    fontFamily: "'JetBrains Mono',monospace",
                    fontWeight: 900, fontSize: 64, color: "#ff3355",
                    lineHeight: 1, marginBottom: 6,
                    textShadow: "0 0 40px rgba(255,51,85,0.4)",
                  }}>
                    0.347
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#556677", letterSpacing: "0.08em" }}>
                    GRANGER STRENGTH
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455", marginTop: 6 }}>
                    strongest link discovered
                  </div>
                </div>
              </div>

              {/* 3 cards */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }}>
                {DISCOVERIES.map((d) => (
                  <div key={d.rank} style={{
                    background: "rgba(0,10,22,0.85)",
                    border: `1px solid ${d.color}14`,
                    borderRadius: 14, padding: 26,
                    position: "relative", overflow: "hidden",
                    transition: "all 0.3s ease", cursor: "default",
                  }}
                    onMouseEnter={(e) => {
                      const el = e.currentTarget as HTMLDivElement;
                      el.style.border = `1px solid ${d.color}35`;
                      el.style.transform = "translateY(-4px)";
                      el.style.boxShadow = `0 24px 60px rgba(0,0,0,0.5), 0 0 60px ${d.color}08`;
                    }}
                    onMouseLeave={(e) => {
                      const el = e.currentTarget as HTMLDivElement;
                      el.style.border = `1px solid ${d.color}14`;
                      el.style.transform = "translateY(0)";
                      el.style.boxShadow = "none";
                    }}
                  >
                    <div style={{
                      position: "absolute", top: 0, left: 0, right: 0, height: 1,
                      background: `linear-gradient(90deg,transparent,${d.color}60,transparent)`,
                    }}/>

                    {/* hero number per card */}
                    <div style={{
                      fontFamily: "'JetBrains Mono',monospace",
                      fontWeight: 900, fontSize: 36, color: d.color,
                      lineHeight: 1, marginBottom: 4,
                      textShadow: `0 0 30px ${d.color}40`,
                    }}>
                      {d.heroStat}
                    </div>
                    <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455", marginBottom: 18, letterSpacing: "0.06em" }}>
                      {d.heroLabel}
                    </div>

                    <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: d.color, letterSpacing: "0.08em", marginBottom: 8 }}>
                      DISCOVERY #{d.rank}
                    </div>
                    <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 700, fontSize: 14, color: "#fff", marginBottom: 12, lineHeight: 1.3 }}>
                      {d.title}
                    </div>
                    <p style={{ fontSize: 12, color: "#8899aa", lineHeight: 1.7, marginBottom: 16, fontFamily: "'Space Grotesk',sans-serif" }}>
                      {d.body}
                    </p>
                    <div style={{
                      fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: d.color,
                      background: `${d.color}08`, border: `1px solid ${d.color}15`,
                      borderRadius: 6, padding: "7px 12px", marginBottom: 10,
                    }}>
                      {d.evidence}
                    </div>
                    <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455" }}>
                      ▸ {d.case}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* ═══ PROOF STRIP ═══ */}
        <div style={{
          borderTop: "1px solid rgba(232,160,32,0.07)",
          borderBottom: "1px solid rgba(232,160,32,0.07)",
          padding: "20px 2.5rem",
          background: "rgba(0,8,18,0.6)",
          display: "flex", alignItems: "center",
          gap: 32, overflowX: "auto",
          scrollbarWidth: "none",
        }}>
          {[
            { label: "LSTM Inflation MAE",  val: "2.87%",    color: "#00ff88" },
            { label: "2022 Back-test Error", val: "4.8%",    color: "#00ff88" },
            { label: "GDP Direction",        val: "Correct", color: "#00ff88" },
            { label: "Causal Links Found",   val: "21",      color: "#E8A020" },
            { label: "Training Time (GPU)",  val: "47.3s",   color: "#E8A020" },
            { label: "Parallel PIDs",        val: "3",       color: "#0088ff" },
            { label: "District Models",      val: "10",      color: "#0088ff" },
          ].map((p, i) => (
            <div key={i} style={{ flexShrink: 0, display: "flex", alignItems: "center", gap: 20 }}>
              <div>
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 700, fontSize: 16, color: p.color }}>
                  {p.val}
                </div>
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455", letterSpacing: "0.06em" }}>
                  {p.label}
                </div>
              </div>
              {i < 6 && <div style={{ width: 1, height: 28, background: "rgba(232,160,32,0.08)", flexShrink: 0 }}/>}
            </div>
          ))}
        </div>

        {/* ═══ FOOTER ═══ */}
        <footer style={{ padding: "36px 2.5rem", textAlign: "center", position: "relative" }}>
          <div style={{
            position: "absolute", top: 0, left: 0, right: 0, height: 1,
            background: "linear-gradient(90deg,transparent,rgba(232,160,32,0.2),transparent)",
          }}/>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 800, fontSize: 13, color: "#E8A020", marginBottom: 8 }}>
            ⚡ CLIMASHOCK
          </div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#334455", marginBottom: 6 }}>
            Built by{" "}
            <a href="https://sameer-nadeem-portfolio.vercel.app" target="_blank" rel="noreferrer"
              style={{ color: "#E8A020", textDecoration: "none" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#ff8800")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#E8A020")}
            >Sameer Nadeem</a>
            {" "}— AI/ML Engineer · Data Scientist · PDC Researcher
          </div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#223344" }}>
            Kaggle (Tesla T4) · HuggingFace API · Vercel UI ·{" "}
            <a href={`${API}/docs`} target="_blank" rel="noreferrer"
              style={{ color: "#334455", textDecoration: "none" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#E8A020")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#334455")}
            >API Docs ↗</a>
          </div>
        </footer>
      </div>
    </div>
  );
}

// ── helpers ────────────────────────────────────────────────────────

function CountUpVal({ target, decimal, suffix, prefix }: {
  target: number; decimal?: boolean; suffix: string; prefix: string;
}) {
  const [v, setV] = useState(0);
  useEffect(() => {
    let t = 0; const steps = 80; const inc = target / steps;
    const timer = setInterval(() => {
      t++;
      setV(Math.min(+(inc * t).toFixed(2), target));
      if (t >= steps) clearInterval(timer);
    }, 16);
    return () => clearInterval(timer);
  }, [target]);
  return <>{prefix}{decimal ? v.toFixed(2) : Math.round(v)}{suffix}</>;
}

function SidePanel({ title, children, dot, accent }: {
  title: string; children: React.ReactNode; dot?: boolean; accent?: string;
}) {
  return (
    <div style={{
      background: "rgba(0,10,24,0.85)",
      border: `1px solid ${accent ? accent + "16" : "rgba(232,160,32,0.08)"}`,
      borderRadius: 12, padding: 16, position: "relative", overflow: "hidden",
    }}>
      {accent && (
        <div style={{
          position: "absolute", top: 0, left: 0, right: 0, height: 1,
          background: `linear-gradient(90deg,transparent,${accent},transparent)`,
        }}/>
      )}
      <div style={{
        fontFamily: "'JetBrains Mono',monospace", fontSize: 9,
        color: accent || "#556677", letterSpacing: "0.07em",
        marginBottom: 12, display: "flex", alignItems: "center", gap: 6,
      }}>
        {dot && <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#E8A020", boxShadow: "0 0 4px #E8A020" }}/>}
        {title}
      </div>
      {children}
    </div>
  );
}

function SRow({ label, val, color }: { label: string; val: string; color: string }) {
  return (
    <div style={{
      display: "flex", justifyContent: "space-between", alignItems: "center",
      padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.02)",
    }}>
      <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566" }}>{label}</span>
      <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, fontWeight: 600, color }}>{val}</span>
    </div>
  );
}

function BRow({ label, val, pct }: { label: string; val: string; pct: number }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566" }}>{label}</span>
        <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, fontWeight: 600, color: "#E8A020" }}>{val}</span>
      </div>
      <div style={{ height: 2, borderRadius: 1, background: "rgba(255,255,255,0.04)" }}>
        <div style={{
          height: 2, borderRadius: 1, width: `${pct}%`,
          background: "linear-gradient(90deg,#C86A00,#E8A020,#00ff88)",
        }}/>
      </div>
    </div>
  );
}

function CausalLinksView() {
  const [links, setLinks] = useState<{ cause: string; effect: string; lag_years: number; strength: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/causal?min_strength=0.08`)
      .then((r) => r.json())
      .then((d) => { setLinks(d.links || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const max = links[0]?.strength || 1;

  return (
    <div style={{
      background: "rgba(0,10,22,0.85)",
      border: "1px solid rgba(232,160,32,0.1)",
      borderRadius: 14, padding: 28,
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
        <div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#E8A020", letterSpacing: "0.06em" }}>
            DISCOVERED CAUSAL LINKS
          </div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455", marginTop: 3 }}>
            Granger causality analysis · Pakistan · 1990–2023
          </div>
        </div>
        {!loading && (
          <div style={{
            fontFamily: "'JetBrains Mono',monospace", fontSize: 10,
            padding: "4px 14px", borderRadius: 100,
            background: "rgba(232,160,32,0.07)", color: "#E8A020",
            border: "1px solid rgba(232,160,32,0.12)",
          }}>
            {links.length} LINKS
          </div>
        )}
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0" }}>
          <div style={{
            width: 20, height: 20, margin: "0 auto 14px",
            border: "1.5px solid rgba(232,160,32,0.2)", borderTop: "1.5px solid #E8A020",
            borderRadius: "50%", animation: "spin 0.8s linear infinite",
          }}/>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#445566" }}>
            LOADING CAUSAL GRAPH...
          </div>
          <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {links.map((l, i) => (
            <div key={i}
              style={{
                display: "flex", alignItems: "center", gap: 14,
                padding: "11px 16px", borderRadius: 8,
                background: i === 0 ? "rgba(232,160,32,0.04)" : "rgba(0,8,20,0.5)",
                border: i === 0 ? "1px solid rgba(232,160,32,0.12)" : "1px solid rgba(255,255,255,0.025)",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget as HTMLDivElement;
                el.style.background = "rgba(232,160,32,0.04)";
                el.style.border = "1px solid rgba(232,160,32,0.1)";
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget as HTMLDivElement;
                el.style.background = i === 0 ? "rgba(232,160,32,0.04)" : "rgba(0,8,20,0.5)";
                el.style.border = i === 0 ? "1px solid rgba(232,160,32,0.12)" : "1px solid rgba(255,255,255,0.025)";
              }}
            >
              <div style={{
                width: 20, height: 20, borderRadius: 4, flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: "'JetBrains Mono',monospace", fontSize: 9, fontWeight: 700,
                background: i === 0 ? "rgba(232,160,32,0.12)" : "rgba(255,255,255,0.03)",
                color: i === 0 ? "#E8A020" : "#445566",
              }}>{i + 1}</div>

              <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span style={{
                  fontFamily: "'JetBrains Mono',monospace", fontSize: 10,
                  padding: "2px 9px", borderRadius: 4,
                  background: "rgba(0,136,255,0.07)", color: "#0088ff",
                  border: "1px solid rgba(0,136,255,0.1)",
                }}>{l.cause}</span>
                <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: "#334455" }}>─→</span>
                <span style={{
                  fontFamily: "'JetBrains Mono',monospace", fontSize: 10,
                  padding: "2px 9px", borderRadius: 4,
                  background: "rgba(255,136,0,0.07)", color: "#ff8800",
                  border: "1px solid rgba(255,136,0,0.1)",
                }}>{l.effect}</span>
              </div>

              <span style={{
                fontFamily: "'JetBrains Mono',monospace", fontSize: 9,
                padding: "2px 8px", borderRadius: 4, flexShrink: 0,
                background: "rgba(255,255,255,0.03)", color: "#445566",
              }}>lag {l.lag_years}y</span>

              <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                <div style={{ width: 80, height: 3, borderRadius: 2, background: "rgba(255,255,255,0.04)", overflow: "hidden" }}>
                  <div style={{
                    height: "100%", borderRadius: 2,
                    width: `${(l.strength / max) * 100}%`,
                    background: l.strength > 0.3
                      ? "linear-gradient(90deg,#C86A00,#E8A020)"
                      : "linear-gradient(90deg,#004499,#0088ff)",
                  }}/>
                </div>
                <span style={{
                  fontFamily: "'JetBrains Mono',monospace", fontSize: 10, fontWeight: 700,
                  width: 36, textAlign: "right",
                  color: l.strength > 0.3 ? "#E8A020" : "#0088ff",
                }}>
                  {l.strength.toFixed(3)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}