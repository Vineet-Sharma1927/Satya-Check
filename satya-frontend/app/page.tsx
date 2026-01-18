"use client";
import { useState } from "react";
import { Upload, FileText, AlertTriangle, CheckCircle, HelpCircle, Loader2, ArrowRight, Shield, BarChart3 } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"text" | "image">("text");
  const [inputText, setInputText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    const endpoint = "http://127.0.0.1:5000/api/analyze";

    try {
      let response;
      if (activeTab === "text") {
        response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: inputText }),
        });
      } else {
        if (!selectedFile) return alert("Please select an image first!");
        formData.append("file", selectedFile);
        response = await fetch(endpoint, {
          method: "POST",
          body: formData,
        });
      }

      const data = await response.json();
      if (data.error) {
        alert("Error: " + data.error);
      } else {
        setResult(data);
      }
    } catch (e) {
      alert("Could not connect to backend. Is Python running?");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-100 flex flex-col items-center py-10 px-4 font-sans">

      {/* Navbar */}
      <nav className="w-full max-w-4xl flex justify-between items-center mb-10 px-6">
        <div className="flex items-center gap-2">
          <Shield className="text-blue-500" size={32} />
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">Satya-Check</h1>
        </div>
        <Link href="/dashboard" className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm px-4 py-2 rounded-full transition-all">
          <BarChart3 size={16} /> Admin Dashboard
        </Link>
      </nav>

      <div className="max-w-xl w-full bg-white text-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-700/50">

        {/* Header */}
        <div className="bg-slate-50 p-6 border-b border-slate-100 text-center">
          <h2 className="text-xl font-semibold text-slate-800">Verify News Credibility</h2>
          <p className="text-slate-500 text-sm mt-1">AI + Google Search Hybrid Verification</p>
        </div>

        {/* Tabs */}
        <div className="flex p-2 bg-slate-50 gap-2">
          <button onClick={() => setActiveTab("text")}
            className={`flex-1 py-3 rounded-lg text-sm font-medium flex justify-center items-center gap-2 transition-all ${activeTab === "text" ? "bg-white shadow-sm text-blue-600 ring-1 ring-slate-200" : "text-slate-400 hover:bg-slate-100"}`}>
            <FileText size={18} /> Paste Text
          </button>
          <button onClick={() => setActiveTab("image")}
            className={`flex-1 py-3 rounded-lg text-sm font-medium flex justify-center items-center gap-2 transition-all ${activeTab === "image" ? "bg-white shadow-sm text-blue-600 ring-1 ring-slate-200" : "text-slate-400 hover:bg-slate-100"}`}>
            <Upload size={18} /> Upload Image
          </button>
        </div>

        {/* Inputs */}
        <div className="p-6">
          {activeTab === "text" ? (
            <textarea
              className="w-full h-40 p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-slate-50 text-slate-800 resize-none"
              placeholder="Paste the news headline or text here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          ) : (
            <div className="border-2 border-dashed border-slate-300 rounded-xl h-40 flex flex-col justify-center items-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer relative">
              <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={(e) => setSelectedFile(e.target.files?.[0] || null)} accept="image/*" />
              <div className="flex flex-col items-center text-slate-400">
                <Upload size={32} className="mb-2 text-blue-500" />
                <p className="font-medium text-slate-600">{selectedFile ? selectedFile.name : "Click to Upload Screenshot"}</p>
                <p className="text-xs text-slate-400 mt-1">Supports Hindi & English</p>
              </div>
            </div>
          )}

          <button onClick={handleAnalyze} disabled={loading} className="w-full mt-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-500/30 flex justify-center items-center gap-2 transition-all active:scale-[0.98]">
            {loading ? <Loader2 className="animate-spin" /> : <>Verify Now <ArrowRight size={18} /></>}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="bg-slate-50 p-6 border-t border-slate-100 animation-fade-in">
            {/* Verdict Badge */}
            <div className={`flex items-center gap-4 p-4 rounded-xl border mb-6 ${result.color === "green" ? "bg-emerald-50 border-emerald-200 text-emerald-800" :
                result.color === "red" ? "bg-rose-50 border-rose-200 text-rose-800" :
                  "bg-amber-50 border-amber-200 text-amber-800"
              }`}>
              {result.color === "red" && <AlertTriangle className="shrink-0" size={32} />}
              {result.color === "green" && <CheckCircle className="shrink-0" size={32} />}
              {result.color === "orange" && <HelpCircle className="shrink-0" size={32} />}

              <div>
                <h2 className="text-xl font-bold">{result.verdict}</h2>
                <p className="text-xs opacity-80 mt-1">Confidence Score: {(result.fake_score > result.real_score ? result.fake_score : result.real_score)}%</p>
              </div>
            </div>
            {/* EXPLAINABLE AI SECTION */}
            {result.highlights && result.highlights.length > 0 && (
              <div className="mt-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <h3 className="text-sm font-bold text-slate-700 mb-2">🧠 AI Analysis (Why is this suspicious?)</h3>
                <p className="text-sm text-slate-600">
                  The AI flagged the following high-risk keywords often associated with misinformation:
                </p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {result.highlights.map((word: string, index: number) => (
                    <span key={index} className="px-2 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-md border border-red-200 uppercase">
                      {word}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Evidence Links */}
            {result.evidence && result.evidence.length > 0 && (
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-500"></span> Sources Found:
                </h3>
                <ul className="space-y-2">
                  {result.evidence.map((item: any, index: number) => (
                    <li key={index} className="text-sm border-b border-slate-50 last:border-0 pb-2 last:pb-0">
                      <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 font-medium hover:underline flex items-start gap-2">
                        <span className="shrink-0 mt-1">🔗</span> {item.source}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Fallback Message for Suspicious */}
            {result.verdict.includes("SUSPICIOUS") && (
              <div className="mt-4 text-xs text-rose-600 bg-rose-50 p-3 rounded border border-rose-100">
                <strong>Why Suspicious?</strong> No major trusted media outlets (BBC, NDTV, etc.) have reported this event, or the context is significantly different.
              </div>
            )}

            {result.extracted_text && (
              <details className="mt-4 text-xs text-slate-400 cursor-pointer">
                <summary className="hover:text-slate-600">View Extracted Text</summary>
                <p className="p-2 bg-slate-100 rounded mt-2 text-slate-600 font-mono">{result.extracted_text}</p>
              </details>
            )}

          </div>
        )}
      </div>
    </div>
  );
}