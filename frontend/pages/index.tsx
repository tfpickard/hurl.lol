import { useEffect, useMemo, useRef, useState } from "react";
import Head from "next/head";
import { connectToStream, HurlPost } from "../lib/sse";

const API_BASE = process.env.NEXT_PUBLIC_HURL_API ?? "http://localhost:8000";

export default function Home() {
  const [mode, setMode] = useState<"pure_random" | "emergent">("pure_random");
  const [language, setLanguage] = useState("all");
  const [topic, setTopic] = useState("all");
  const [seed, setSeed] = useState("");
  const [posts, setPosts] = useState<HurlPost[]>([]);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("mode", mode);
    if (language !== "all") params.append("language", language);
    if (topic !== "all") params.append("topic", topic);
    const url = `${API_BASE}/v1/stream?${params.toString()}`;
    const source = connectToStream(
      url,
      (post) => {
        setPosts((prev) => [post, ...prev].slice(0, 200));
      },
      () => {
        console.warn("SSE connection lost");
      },
    );
    sourceRef.current = source;
    return () => {
      source.close();
      sourceRef.current = null;
    };
  }, [mode, language, topic]);

  const handleSeedSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!seed) return;
    await fetch(`${API_BASE}/v1/seed`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ seed: Number(seed) }),
    });
  };

  const impactItems = useMemo(() => posts.slice(0, 10), [posts]);

  return (
    <>
      <Head>
        <title>Hurl — The Internet, but synthetic</title>
      </Head>
      <main className="min-h-screen bg-slate-950 text-slate-50">
        <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-8">
          <h1 className="text-3xl font-bold">Hurl — The Internet, but synthetic</h1>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-widest">
            live demo
          </span>
        </header>
        <section className="mx-auto grid max-w-6xl gap-8 px-6 pb-16 md:grid-cols-[260px_minmax(0,1fr)_220px]">
          <aside className="space-y-6">
            <div>
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-widest text-slate-300">
                Mode
              </h2>
              <div className="grid grid-cols-2 gap-2">
                <button
                  className={`rounded border px-3 py-2 text-sm ${
                    mode === "emergent" ? "border-cyan-400 bg-cyan-950" : "border-slate-700"
                  }`}
                  onClick={() => setMode("emergent")}
                >
                  Emergent
                </button>
                <button
                  className={`rounded border px-3 py-2 text-sm ${
                    mode === "pure_random" ? "border-cyan-400 bg-cyan-950" : "border-slate-700"
                  }`}
                  onClick={() => setMode("pure_random")}
                >
                  Pure Random
                </button>
              </div>
            </div>
            <div>
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-widest text-slate-300">
                Filters
              </h2>
              <label className="mb-2 block text-xs uppercase tracking-widest text-slate-400">
                Topic
                <select
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-2"
                  value={topic}
                  onChange={(event) => setTopic(event.target.value)}
                >
                  <option value="all">All topics</option>
                  <option value="ai">AI</option>
                  <option value="markets">Markets</option>
                  <option value="sportsball">Sportsball</option>
                  <option value="memes">Memes</option>
                </select>
              </label>
              <label className="block text-xs uppercase tracking-widest text-slate-400">
                Language
                <select
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-2"
                  value={language}
                  onChange={(event) => setLanguage(event.target.value)}
                >
                  <option value="all">All languages</option>
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                </select>
              </label>
            </div>
            <form onSubmit={handleSeedSubmit} className="space-y-2">
              <h2 className="text-sm font-semibold uppercase tracking-widest text-slate-300">
                Global seed
              </h2>
              <input
                type="number"
                value={seed}
                placeholder="seed"
                onChange={(event) => setSeed(event.target.value)}
                className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2"
              />
              <button
                type="submit"
                className="w-full rounded border border-cyan-500 px-3 py-2 text-sm font-semibold text-cyan-300"
              >
                Set seed
              </button>
            </form>
            <button
              disabled
              className="w-full rounded border border-slate-800 px-3 py-2 text-sm text-slate-500"
            >
              Inject news shock (admin)
            </button>
          </aside>
          <section className="space-y-4">
            {posts.map((post) => (
              <article key={post.id} className="rounded border border-slate-800 bg-slate-900 p-4 shadow">
                <header className="mb-2 flex items-center justify-between text-sm text-slate-400">
                  <span>{post.persona_id}</span>
                  <span>{new Date(post.created_at).toLocaleTimeString()}</span>
                </header>
                <p className="whitespace-pre-line text-lg leading-relaxed text-slate-100">{post.text}</p>
                <footer className="mt-3 flex flex-wrap gap-3 text-xs text-slate-400">
                  <span>Mode: {post.mode}</span>
                  <span>Topics: {post.topics.join(", ")}</span>
                  <span>🔥 {post.metrics.likes}</span>
                  <span>💬 {post.metrics.replies}</span>
                  <span>🔁 {post.metrics.quotes}</span>
                </footer>
              </article>
            ))}
            {posts.length === 0 && (
              <div className="rounded border border-slate-800 bg-slate-900 p-6 text-center text-sm text-slate-400">
                Connecting to stream…
              </div>
            )}
          </section>
          <aside className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-slate-300">
              Impact panel
            </h2>
            <p className="text-xs text-slate-400">
              Lightweight visual on how fresh posts tie back to their inspirations. Each ripple is
              a reference in the lineage field.
            </p>
            <ul className="space-y-2 text-xs text-slate-300">
              {impactItems.map((post) => (
                <li key={post.id} className="rounded border border-slate-800 bg-slate-900 p-3">
                  <div className="font-mono text-[11px] uppercase text-slate-500">{post.lineage.template}</div>
                  <div className="mt-1 font-semibold text-slate-200">{post.topics.join(", ")}</div>
                  <div className="mt-2 text-slate-400">
                    Influences: {post.lineage.influences.length > 0 ? post.lineage.influences.join(", ") : "—"}
                  </div>
                </li>
              ))}
            </ul>
          </aside>
        </section>
        <footer className="bg-slate-900 py-6 text-center text-xs text-slate-500">
          © Hurl. All posts are synthetic.
        </footer>
      </main>
    </>
  );
}
