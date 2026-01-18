"use client";
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, ShieldAlert, ShieldCheck, Home, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/stats")
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Failed to load stats"));
  }, []);

  if (!stats) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-400">
        <div className="flex flex-col items-center gap-2">
            <Activity className="animate-spin text-blue-500" size={32} />
            <p>Loading Analytics...</p>
        </div>
    </div>
  );

  const chartData = [
    { name: 'Threats (Fake)', value: stats.fake },
    { name: 'Verified (Real)', value: stats.real },
  ];

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center sticky top-0 z-10">
        <div className="flex items-center gap-3">
            <div className="bg-blue-600 text-white p-2 rounded-lg">
                <Activity size={20} />
            </div>
            <h1 className="text-xl font-bold text-slate-800">Satya-Check <span className="text-slate-400 font-normal">| Command Center</span></h1>
        </div>
        <Link href="/" className="flex items-center gap-2 text-slate-500 hover:text-blue-600 transition-colors text-sm font-medium">
            <ArrowLeft size={16} /> Back to Scanner
        </Link>
      </header>

      <main className="max-w-7xl mx-auto p-8">
        
        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-sm font-medium text-slate-500 uppercase tracking-wide">Total Scans</p>
                    <h3 className="text-3xl font-bold text-slate-800 mt-2">{stats.total}</h3>
                </div>
                <div className="p-3 bg-blue-50 text-blue-600 rounded-lg"><Activity size={24} /></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-sm font-medium text-slate-500 uppercase tracking-wide">Threats Blocked</p>
                    <h3 className="text-3xl font-bold text-rose-600 mt-2">{stats.fake}</h3>
                </div>
                <div className="p-3 bg-rose-50 text-rose-600 rounded-lg"><ShieldAlert size={24} /></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-sm font-medium text-slate-500 uppercase tracking-wide">Verified Real</p>
                    <h3 className="text-3xl font-bold text-emerald-600 mt-2">{stats.real}</h3>
                </div>
                <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg"><ShieldCheck size={24} /></div>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Chart Section */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-1">
            <h3 className="font-bold text-slate-800 mb-6">Veracity Overview</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Logs Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm lg:col-span-2 overflow-hidden flex flex-col">
             <div className="p-6 border-b border-slate-100">
                <h3 className="font-bold text-slate-800">Recent Activity Log</h3>
             </div>
             
             <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-slate-500 font-medium">
                    <tr>
                      <th className="p-4">Timestamp</th>
                      <th className="p-4 w-1/2">Snippet</th>
                      <th className="p-4">Verdict</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {stats.logs.map((log: any, i: number) => {
                      // LOGIC FIX: Check for FAKE or SUSPICIOUS to show Red
                      const isFake = log.verdict.includes('FAKE') || log.verdict.includes('SUSPICIOUS');
                      
                      return (
                        <tr key={i} className="hover:bg-slate-50 transition-colors">
                          <td className="p-4 text-slate-500 whitespace-nowrap">{log.date}</td>
                          <td className="p-4 font-medium text-slate-700 truncate max-w-xs" title={log.text}>{log.text}</td>
                          <td className="p-4">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                isFake ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'
                            }`}>
                              {isFake ? 'FAKE / SUSPICIOUS' : 'REAL'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
             </div>
          </div>
        </div>
      </main>
    </div>
  );
}