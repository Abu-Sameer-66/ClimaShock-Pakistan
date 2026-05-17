"use client";
import { useState } from "react";

const API = "https://abu-sameer-66-climashock-api.hf.space";

const DISTRICTS = [
  "Lahore","Karachi","Faisalabad","Multan",
  "Peshawar","Quetta","Islamabad","Hyderabad","Sukkur","Sialkot"
];

const EXAMPLES = [
  { label: "2022 Sukkur Floods", district: "Sukkur",    rain: "4.16", temp: "30.2", badge: "Historical Event" },
  { label: "Extreme Lahore Heat", district: "Lahore",   rain: "0.8",  temp: "42.0", badge: "Heat Stress"      },
  { label: "Normal Islamabad",    district: "Islamabad", rain: "1.2",  temp: "22.0", badge: "Baseline"         },
];

interface CascadeStep {
  step: number; event: string; detail: string; timeframe: string; severity: string;
}
interface Result {
  district: string; rain_zscore: number; temp_zscore: number;
  risk_level: string; risk_score: number; immediate_crop_pct: number;
  inflation_predicted: number; inflation_range_low: number; inflation_range_high: number;
  gdp_outlook: string; cascade_chain: CascadeStep[]; model_confidence: string;
}

const sColor = (s: string) =>
  s === "EXTREME" ? "#ff3355" : s === "HIGH" ? "#ff8800" : s === "MODERATE" ? "#E8A020" : "#00ff88";

export default function CascadePredictor() {
  const [district,    setDistrict]    = useState("Sukkur");
  const [rainfall,    setRainfall]    = useState("4.16");
  const [temperature, setTemperature] = useState("30.2");
  const [loading,     setLoading]     = useState(false);
  const [result,      setResult]      = useState<Result | null>(null);
  const [error,       setError]       = useState("");
  const [activeStep,  setActiveStep]  = useState(-1);
  const [btnHover,    setBtnHover]    = useState(false);

  const predict = async () => {
    setLoading(true); setError(""); setResult(null); setActiveStep(-1);
    try {
      const res = await fetch(`${API}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          district,
          rainfall_mm_day: parseFloat(rainfall),
          temperature_c:   parseFloat(temperature),
        }),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "Failed"); }
      const data: Result = await res.json();
      setResult(data);
      data.cascade_chain.forEach((_, i) => setTimeout(() => setActiveStep(i), i * 700 + 300));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const loadExample = (ex: typeof EXAMPLES[0]) => {
    setDistrict(ex.district);
    setRainfall(ex.rain);
    setTemperature(ex.temp);
    setResult(null);
    setActiveStep(-1);
    setError("");
  };

  const riskBg = result
    ? result.risk_level === "EXTREME" ? "rgba(255,51,85,0.06)"
    : result.risk_level === "HIGH"    ? "rgba(255,136,0,0.06)"
    : "rgba(232,160,32,0.06)"
    : "transparent";

  const riskBorder = result
    ? `1px solid ${sColor(result.risk_level)}25`
    : "1px solid rgba(232,160,32,0.12)";

  return (
    <div style={{
      background: "rgba(0,10,24,0.85)",
      border: "1px solid rgba(232,160,32,0.12)",
      borderRadius: 14, overflow: "hidden",
    }}>

      {/* header */}
      <div style={{
        padding: "18px 22px",
        borderBottom: "1px solid rgba(232,160,32,0.07)",
        background: "rgba(0,8,18,0.6)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#E8A020", boxShadow: "0 0 7px #E8A020" }}/>
          <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#E8A020", letterSpacing: "0.06em" }}>
            CASCADE PREDICTION ENGINE v1.0
          </span>
        </div>
        <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455" }}>
          LSTM + XGBoost Ensemble · MAE 3.13%
        </span>
      </div>

      <div style={{ padding: 22 }}>

        {/* quick examples */}
        <div style={{ marginBottom: 18 }}>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566", marginBottom: 8, letterSpacing: "0.06em" }}>
            QUICK EXAMPLES — CLICK TO TRY
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {EXAMPLES.map((ex) => (
              <button key={ex.label} onClick={() => loadExample(ex)}
                style={{
                  flex: 1, padding: "8px 10px", borderRadius: 7, cursor: "pointer",
                  background: district === ex.district && rainfall === ex.rain
                    ? "rgba(232,160,32,0.1)" : "rgba(0,8,20,0.6)",
                  border: district === ex.district && rainfall === ex.rain
                    ? "1px solid rgba(232,160,32,0.3)" : "1px solid rgba(255,255,255,0.04)",
                  transition: "all 0.2s", outline: "none",
                }}
                onMouseEnter={(e) => (e.currentTarget as HTMLButtonElement).style.border = "1px solid rgba(232,160,32,0.2)"}
                onMouseLeave={(e) => (e.currentTarget as HTMLButtonElement).style.border =
                  district === ex.district && rainfall === ex.rain
                    ? "1px solid rgba(232,160,32,0.3)" : "1px solid rgba(255,255,255,0.04)"}
              >
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#E8A020", marginBottom: 2 }}>
                  {ex.badge}
                </div>
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#8899aa" }}>
                  {ex.label}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* inputs */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 16 }}>
          <div>
            <label style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566", display: "block", marginBottom: 6, letterSpacing: "0.06em" }}>
              DISTRICT
            </label>
            <div style={{ position: "relative" }}>
              <select value={district} onChange={(e) => setDistrict(e.target.value)}
                style={{
                  width: "100%", padding: "10px 30px 10px 12px",
                  background: "rgba(0,8,20,0.8)", color: "#fff",
                  border: "1px solid rgba(232,160,32,0.15)", borderRadius: 8,
                  fontFamily: "'JetBrains Mono',monospace", fontSize: 12,
                  outline: "none", cursor: "pointer", appearance: "none",
                }}>
                {DISTRICTS.map((d) => <option key={d} value={d} style={{ background: "#000d1a" }}>{d}</option>)}
              </select>
              <div style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", color: "#E8A020", fontSize: 9, pointerEvents: "none" }}>▼</div>
            </div>
          </div>

          {[
            { label: "RAINFALL (mm/day)", val: rainfall, set: setRainfall, ph: "e.g. 4.16", hint: "normal: 0.5–2.0" },
            { label: "TEMPERATURE (°C)",  val: temperature, set: setTemperature, ph: "e.g. 30.2", hint: "normal: 20–35" },
          ].map((f) => (
            <div key={f.label}>
              <label style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566", display: "block", marginBottom: 6, letterSpacing: "0.06em" }}>
                {f.label}
                <span style={{ color: "#334455", marginLeft: 6 }}>({f.hint})</span>
              </label>
              <input type="number" step="0.1" value={f.val} placeholder={f.ph}
                onChange={(e) => f.set(e.target.value)}
                style={{
                  width: "100%", padding: "10px 12px",
                  background: "rgba(0,8,20,0.8)", color: "#fff",
                  border: "1px solid rgba(232,160,32,0.15)", borderRadius: 8,
                  fontFamily: "'JetBrains Mono',monospace", fontSize: 12,
                  outline: "none", boxSizing: "border-box",
                }}
                onFocus={(e) => (e.target.style.border = "1px solid rgba(232,160,32,0.5)")}
                onBlur={(e)  => (e.target.style.border = "1px solid rgba(232,160,32,0.15)")}
              />
            </div>
          ))}
        </div>

        {/* ── ENHANCED BUTTON ── */}
        <div style={{ position: "relative", marginBottom: 20 }}>
          {/* outer glow ring */}
          {!loading && (
            <div style={{
              position: "absolute", inset: -3, borderRadius: 12,
              background: "linear-gradient(135deg,#E8A020,#ff8800,#C86A00,#E8A020)",
              backgroundSize: "300% 300%",
              animation: "gradShift 3s ease infinite",
              opacity: btnHover ? 0.6 : 0.3,
              transition: "opacity 0.3s",
              zIndex: 0,
            }}/>
          )}
          <button onClick={predict} disabled={loading}
            onMouseEnter={() => setBtnHover(true)}
            onMouseLeave={() => setBtnHover(false)}
            style={{
              width: "100%", padding: "16px 24px",
              borderRadius: 10, border: "none", cursor: loading ? "not-allowed" : "pointer",
              background: loading
                ? "rgba(232,160,32,0.1)"
                : btnHover
                  ? "rgba(232,160,32,0.18)"
                  : "rgba(232,160,32,0.12)",
              color: "#E8A020",
              fontFamily: "'JetBrains Mono',monospace",
              fontSize: 13, fontWeight: 700, letterSpacing: "0.06em",
              position: "relative", zIndex: 1,
              transition: "all 0.25s ease",
              transform: btnHover && !loading ? "translateY(-1px)" : "none",
              boxShadow: btnHover && !loading ? "0 8px 30px rgba(232,160,32,0.2)" : "none",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
            }}>
            {loading ? (
              <>
                <div style={{
                  width: 16, height: 16,
                  border: "2px solid rgba(232,160,32,0.2)",
                  borderTop: "2px solid #E8A020",
                  borderRadius: "50%", animation: "spin 0.7s linear infinite",
                }}/>
                ANALYZING CASCADE...
              </>
            ) : (
              <>
                <span style={{ fontSize: 16 }}>⚡</span>
                ANALYZE CLIMATE CASCADE
                <span style={{
                  fontSize: 14,
                  transition: "transform 0.2s",
                  transform: btnHover ? "translateX(4px)" : "none",
                }}>→</span>
              </>
            )}
          </button>
        </div>

        <style>{`
          @keyframes gradShift { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
          @keyframes spin { to { transform: rotate(360deg) } }
        `}</style>

        {error && (
          <div style={{
            padding: "10px 14px", borderRadius: 8, marginBottom: 16,
            background: "rgba(255,51,85,0.08)", border: "1px solid rgba(255,51,85,0.2)",
            fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#ff3355",
          }}>
            ERROR: {error}
          </div>
        )}

        {/* ── RESULTS ── */}
        {result && (
          <div>

            {/* risk banner */}
            <div style={{
              padding: "14px 18px", borderRadius: 10, marginBottom: 14,
              background: riskBg, border: riskBorder,
              display: "flex", alignItems: "center", justifyContent: "space-between",
              position: "relative", overflow: "hidden",
            }}>
              <div style={{
                position: "absolute", top: 0, left: 0, right: 0, height: 1,
                background: `linear-gradient(90deg,transparent,${sColor(result.risk_level)}50,transparent)`,
              }}/>
              <div>
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#556677", marginBottom: 4 }}>
                  RISK ASSESSMENT — {result.district.toUpperCase()}
                </div>
                <div style={{
                  fontFamily: "'JetBrains Mono',monospace", fontWeight: 900,
                  fontSize: 28, color: sColor(result.risk_level), lineHeight: 1,
                  textShadow: `0 0 20px ${sColor(result.risk_level)}40`,
                }}>
                  {result.risk_level}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#556677", marginBottom: 4 }}>
                  RAINFALL ANOMALY
                </div>
                <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 900, fontSize: 24, color: "#E8A020" }}>
                  {result.rain_zscore > 0 ? "+" : ""}{result.rain_zscore}σ
                </div>
              </div>
            </div>

            {/* 3 metrics */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 14 }}>
              {[
                {
                  label: "IMMEDIATE CROP IMPACT",
                  val: `${result.immediate_crop_pct > 0 ? "+" : ""}${result.immediate_crop_pct}%`,
                  sub: "within 4–8 weeks",
                  color: result.immediate_crop_pct < -5 ? "#ff3355" : "#00ff88",
                },
                {
                  label: "INFLATION PREDICTED",
                  val: `${result.inflation_predicted}%`,
                  sub: `range: ${result.inflation_range_low}–${result.inflation_range_high}%`,
                  color: result.inflation_predicted > 15 ? "#ff8800" : "#E8A020",
                },
                {
                  label: "GDP OUTLOOK",
                  val: result.gdp_outlook.split(" ")[0],
                  sub: "12–24 months ahead",
                  color: result.gdp_outlook.includes("contraction") ? "#ff3355" : "#00ff88",
                },
              ].map((m) => (
                <div key={m.label} style={{
                  padding: "12px 14px", borderRadius: 8,
                  background: "rgba(0,8,20,0.7)",
                  border: "1px solid rgba(255,255,255,0.04)",
                }}>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 8, color: "#445566", marginBottom: 6, letterSpacing: "0.05em" }}>
                    {m.label}
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontWeight: 800, fontSize: 18, color: m.color, marginBottom: 3 }}>
                    {m.val}
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 8, color: "#334455" }}>
                    {m.sub}
                  </div>
                </div>
              ))}
            </div>

            {/* inflation bar */}
            <div style={{
              padding: "10px 14px", borderRadius: 8, marginBottom: 14,
              background: "rgba(0,8,20,0.5)", border: "1px solid rgba(255,255,255,0.03)",
            }}>
              <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 8, color: "#445566", marginBottom: 8, letterSpacing: "0.06em" }}>
                INFLATION PREDICTION RANGE — 80% CONFIDENCE
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#00ff88", flexShrink: 0 }}>
                  {result.inflation_range_low}%
                </span>
                <div style={{ flex: 1, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                  <div style={{
                    height: "100%", borderRadius: 2,
                    width: `${Math.min(100, (result.inflation_predicted / 40) * 100)}%`,
                    background: "linear-gradient(90deg,#00ff88,#E8A020,#ff3355)",
                    transition: "width 1.2s ease",
                  }}/>
                </div>
                <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#ff3355", flexShrink: 0 }}>
                  {result.inflation_range_high}%
                </span>
              </div>
            </div>

            {/* cascade chain */}
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566", marginBottom: 10, letterSpacing: "0.06em" }}>
                FUTURE CASCADE TIMELINE — WHAT WILL HAPPEN NEXT
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
                {result.cascade_chain.map((step, i) => (
                  <div key={i}>
                    <div style={{
                      display: "flex", gap: 12, alignItems: "flex-start",
                      padding: "10px 12px", borderRadius: 8,
                      background: activeStep >= i ? `${sColor(step.severity)}06` : "rgba(0,8,20,0.3)",
                      border: `1px solid ${activeStep >= i ? sColor(step.severity) + "20" : "rgba(255,255,255,0.02)"}`,
                      opacity: activeStep >= i ? 1 : 0.25,
                      transform: activeStep >= i ? "translateX(0)" : "translateX(-8px)",
                      transition: "all 0.5s ease",
                    }}>
                      <div style={{
                        width: 24, height: 24, borderRadius: "50%", flexShrink: 0,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontFamily: "'JetBrains Mono',monospace", fontSize: 10, fontWeight: 700,
                        background: activeStep >= i ? `${sColor(step.severity)}15` : "rgba(255,255,255,0.03)",
                        color: activeStep >= i ? sColor(step.severity) : "#445566",
                        marginTop: 1,
                      }}>{step.step}</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 2 }}>
                          <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, fontWeight: 600, color: sColor(step.severity) }}>
                            {step.event}
                          </span>
                          <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#334455" }}>
                            {step.timeframe}
                          </span>
                        </div>
                        <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#8899aa" }}>
                          {step.detail}
                        </div>
                      </div>
                    </div>
                    {i < result.cascade_chain.length - 1 && (
                      <div style={{ paddingLeft: 23, margin: "2px 0" }}>
                        <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: "rgba(232,160,32,0.2)" }}>│</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* confidence */}
            <div style={{
              padding: "8px 12px", borderRadius: 6,
              background: "rgba(0,8,20,0.4)", border: "1px solid rgba(255,255,255,0.025)",
              fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: "#445566",
            }}>
              MODEL CONFIDENCE:{" "}
              <span style={{ color: "#E8A020" }}>{result.model_confidence}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}