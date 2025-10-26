import { useEffect, useState, useRef } from 'react';
import { HurlSSEClient, Post } from '../lib/sse';
import { ThemeToggle } from '../components/ThemeToggle';
import { useTheme } from '../contexts/ThemeContext';

export default function Home() {
  const { theme } = useTheme();
  const [posts, setPosts] = useState<Post[]>([]);
  const [mode, setMode] = useState<'emergent' | 'pure_random'>('emergent');
  const [isConnected, setIsConnected] = useState(false);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [seed, setSeed] = useState<string>('');
  // Auto-detect API URL based on environment
  // Production (hurl.lol): use same origin (nginx proxies /v1/* to backend)
  // Development (localhost): use localhost:8000 directly
  const getDefaultApiUrl = () => {
    if (typeof window === 'undefined') return 'http://localhost:8000';
    const hostname = window.location.hostname;
    if (hostname === 'hurl.lol' || hostname.endsWith('.hurl.lol')) {
      return window.location.origin;
    }
    return 'http://localhost:8000';
  };
  const [apiUrl, setApiUrl] = useState(getDefaultApiUrl());
  const [showImpact, setShowImpact] = useState(false);
  const [connectionError, setConnectionError] = useState<string>('');

  const clientRef = useRef<HurlSSEClient | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const topicOptions = [
    'ai', 'crypto', 'gaming', 'politics', 'climate', 'stocks',
    'movies', 'music', 'fitness', 'memes', 'social_media'
  ];

  useEffect(() => {
    // Initialize client
    clientRef.current = new HurlSSEClient(apiUrl);

    return () => {
      if (clientRef.current) {
        clientRef.current.disconnect();
      }
    };
  }, [apiUrl]);

  const handleConnect = () => {
    if (!clientRef.current) return;

    if (isConnected) {
      clientRef.current.disconnect();
      setIsConnected(false);
      setConnectionError('');
    } else {
      setConnectionError('');
      const options = {
        mode,
        topics: selectedTopics.length > 0 ? selectedTopics : undefined,
        seed: seed ? parseInt(seed) : undefined,
        interval: 1.0,
      };

      console.log('Starting stream with options:', options);

      clientRef.current.connect(
        (post) => {
          setPosts((prev) => [post, ...prev].slice(0, 100)); // Keep last 100
          // Auto-scroll to top
          if (scrollRef.current) {
            scrollRef.current.scrollTop = 0;
          }
        },
        (error) => {
          console.error('Connection error:', error);
          setIsConnected(false);
          setConnectionError(`Failed to connect to ${apiUrl}. Make sure the backend is running.`);
        },
        () => {
          // Only set connected when SSE connection is actually established
          console.log('Connection established successfully');
          setIsConnected(true);
          setConnectionError('');
        },
        options
      );
    }
  };

  const toggleTopic = (topic: string) => {
    setSelectedTopics((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  };

  const isNight = theme === 'night';

  return (
    <div className={`min-h-screen synth-grid scanlines transition-colors duration-300 ${
      isNight ? 'bg-synth-dark' : 'bg-synth-light'
    }`}>
      {/* Header */}
      <header className={`relative overflow-hidden py-8 border-b-4 ${
        isNight
          ? 'bg-gradient-to-r from-synth-purple via-synth-pink to-synth-cyan border-synth-pink shadow-neon-pink-strong'
          : 'bg-gradient-to-r from-synth-purple-day via-synth-pink-day to-synth-cyan-day border-synth-pink-day shadow-lg'
      }`}>
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className={`text-5xl font-bold neon-text-subtle ${
                isNight ? 'text-synth-cyan' : 'text-white'
              }`}>
                HURL
              </h1>
              <p className={`mt-2 text-lg ${
                isNight ? 'text-synth-yellow' : 'text-synth-lighter'
              }`}>
                The Internet, but <span className="font-bold italic">synthetic</span>
              </p>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-3">
            <div className={`rounded-lg p-6 sticky top-4 border-2 transition-all ${
              isNight
                ? 'bg-synth-surface/90 border-synth-pink shadow-neon-pink backdrop-blur-sm'
                : 'bg-synth-light-surface/90 border-synth-purple-day shadow-lg backdrop-blur-sm'
            }`}>
              <h2 className={`text-xl font-bold mb-4 ${
                isNight ? 'text-synth-cyan' : 'text-synth-purple-day'
              }`}>
                CONTROLS
              </h2>

              {/* Mode Toggle */}
              <div className="mb-6">
                <label className={`block text-sm font-medium mb-2 ${
                  isNight ? 'text-synth-yellow' : 'text-synth-purple-day'
                }`}>
                  Mode
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setMode('emergent')}
                    className={`flex-1 py-2 px-4 rounded font-bold transition-all ${
                      mode === 'emergent'
                        ? isNight
                          ? 'bg-gradient-to-r from-synth-purple to-synth-pink text-white shadow-neon-purple'
                          : 'bg-gradient-to-r from-synth-purple-day to-synth-pink-day text-white shadow-md'
                        : isNight
                          ? 'bg-synth-dark text-synth-cyan border border-synth-cyan/50'
                          : 'bg-synth-lighter text-synth-purple-day border border-synth-purple-day/30'
                    }`}
                  >
                    Emergent
                  </button>
                  <button
                    onClick={() => setMode('pure_random')}
                    className={`flex-1 py-2 px-4 rounded font-bold transition-all ${
                      mode === 'pure_random'
                        ? isNight
                          ? 'bg-gradient-to-r from-synth-purple to-synth-pink text-white shadow-neon-purple'
                          : 'bg-gradient-to-r from-synth-purple-day to-synth-pink-day text-white shadow-md'
                        : isNight
                          ? 'bg-synth-dark text-synth-cyan border border-synth-cyan/50'
                          : 'bg-synth-lighter text-synth-purple-day border border-synth-purple-day/30'
                    }`}
                  >
                    Random
                  </button>
                </div>
              </div>

              {/* Topics */}
              <div className="mb-6">
                <label className={`block text-sm font-medium mb-2 ${
                  isNight ? 'text-synth-yellow' : 'text-synth-purple-day'
                }`}>
                  Topics
                </label>
                <div className="flex flex-wrap gap-2">
                  {topicOptions.map((topic) => (
                    <button
                      key={topic}
                      onClick={() => toggleTopic(topic)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-all ${
                        selectedTopics.includes(topic)
                          ? isNight
                            ? 'bg-gradient-to-r from-synth-pink to-synth-magenta text-white shadow-neon-pink'
                            : 'bg-gradient-to-r from-synth-pink-day to-synth-magenta-day text-white shadow-md'
                          : isNight
                            ? 'bg-synth-dark text-synth-cyan border border-synth-cyan/30'
                            : 'bg-synth-lighter text-synth-purple-day border border-synth-purple-day/20'
                      }`}
                    >
                      {topic}
                    </button>
                  ))}
                </div>
              </div>

              {/* Seed */}
              <div className="mb-6">
                <label className={`block text-sm font-medium mb-2 ${
                  isNight ? 'text-synth-yellow' : 'text-synth-purple-day'
                }`}>
                  Seed (optional)
                </label>
                <input
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(e.target.value)}
                  placeholder="Random"
                  className={`w-full px-3 py-2 rounded border-2 transition-all ${
                    isNight
                      ? 'bg-synth-dark border-synth-cyan/50 text-synth-cyan placeholder-synth-cyan/30 focus:border-synth-cyan focus:shadow-neon-cyan'
                      : 'bg-synth-lighter border-synth-purple-day/30 text-synth-purple-day placeholder-synth-purple-day/40 focus:border-synth-purple-day'
                  }`}
                />
              </div>

              {/* Connect Button */}
              <button
                onClick={handleConnect}
                className={`w-full py-3 rounded font-bold transition-all ${
                  isConnected
                    ? isNight
                      ? 'bg-gradient-to-r from-red-600 to-red-800 text-white shadow-lg hover:shadow-xl'
                      : 'bg-gradient-to-r from-red-500 to-red-700 text-white shadow-md hover:shadow-lg'
                    : isNight
                      ? 'bg-gradient-to-r from-synth-cyan to-synth-purple text-white shadow-neon-cyan hover:shadow-neon-cyan-strong'
                      : 'bg-gradient-to-r from-synth-cyan-day to-synth-purple-day text-white shadow-md hover:shadow-lg'
                }`}
              >
                {isConnected ? '⏸ DISCONNECT' : '▶ START STREAM'}
              </button>

              {/* Connection Error */}
              {connectionError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  {connectionError}
                </div>
              )}

              {/* Impact Toggle */}
              <button
                onClick={() => setShowImpact(!showImpact)}
                className={`w-full mt-4 py-2 rounded text-sm font-medium border-2 transition-all ${
                  isNight
                    ? 'border-synth-yellow text-synth-yellow hover:bg-synth-yellow/10'
                    : 'border-synth-purple-day text-synth-purple-day hover:bg-synth-purple-day/10'
                }`}
              >
                {showImpact ? '✕ Hide' : '◈ Show'} Impact Panel
              </button>

              {/* Stats */}
              <div className={`mt-6 pt-6 border-t-2 ${
                isNight ? 'border-synth-pink/30' : 'border-synth-pink-day/30'
              }`}>
                <div className="text-sm">
                  <div className={`flex justify-between mb-2 ${
                    isNight ? 'text-synth-cyan' : 'text-synth-purple-day'
                  }`}>
                    <span>Posts:</span>
                    <span className={`font-bold ${
                      isNight ? 'text-synth-yellow' : 'text-synth-cyan-day'
                    }`}>
                      {posts.length}
                    </span>
                  </div>
                  <div className={`flex justify-between ${
                    isNight ? 'text-synth-cyan' : 'text-synth-purple-day'
                  }`}>
                    <span>Status:</span>
                    <span className={`font-bold ${
                      isConnected
                        ? isNight ? 'text-synth-cyan' : 'text-green-600'
                        : isNight ? 'text-gray-500' : 'text-gray-400'
                    }`}>
                      {isConnected ? '● LIVE' : '○ OFFLINE'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Center Panel - Feed */}
          <div className={showImpact ? 'lg:col-span-6' : 'lg:col-span-9'}>
            <div className={`rounded-lg border-2 transition-all ${
              isNight
                ? 'bg-synth-surface/90 border-synth-cyan shadow-neon-cyan backdrop-blur-sm'
                : 'bg-synth-light-surface/90 border-synth-cyan-day shadow-lg backdrop-blur-sm'
            }`}>
              <div className={`p-4 border-b-2 ${
                isNight ? 'border-synth-pink/30' : 'border-synth-pink-day/30'
              }`}>
                <h2 className={`text-xl font-bold ${
                  isNight ? 'text-synth-pink' : 'text-synth-pink-day'
                }`}>
                  FEED
                </h2>
              </div>
              <div
                ref={scrollRef}
                className="overflow-y-auto"
                style={{ maxHeight: 'calc(100vh - 300px)' }}
              >
                {posts.length === 0 ? (
                  <div className={`p-8 text-center ${
                    isNight ? 'text-synth-cyan' : 'text-synth-purple-day'
                  }`}>
                    {isConnected
                      ? '⟳ Waiting for posts...'
                      : '▶ Click "Start Stream" to begin'}
                  </div>
                ) : (
                  <div className={`${
                    isNight ? 'divide-synth-pink/20' : 'divide-synth-pink-day/20'
                  } divide-y`}>
                    {posts.map((post) => (
                      <div
                        key={post.id}
                        className={`p-4 transition-all ${
                          isNight
                            ? 'hover:bg-synth-dark/50 hover:border-l-4 hover:border-synth-cyan'
                            : 'hover:bg-synth-lighter/50 hover:border-l-4 hover:border-synth-cyan-day'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-10 h-10 rounded-full flex-shrink-0 ${
                            isNight
                              ? 'bg-gradient-to-br from-synth-purple to-synth-pink shadow-neon-pink'
                              : 'bg-gradient-to-br from-synth-purple-day to-synth-pink-day shadow-md'
                          }`} />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`font-bold text-sm ${
                                isNight ? 'text-synth-cyan' : 'text-synth-cyan-day'
                              }`}>
                                Persona {post.persona_id.slice(0, 8)}
                              </span>
                              <span className={`text-xs ${
                                isNight ? 'text-synth-yellow/70' : 'text-synth-purple-day/70'
                              }`}>
                                {new Date(post.created_at).toLocaleTimeString()}
                              </span>
                              <span
                                className={`text-xs px-2 py-0.5 rounded ${
                                  post.mode === 'emergent'
                                    ? isNight
                                      ? 'bg-synth-purple/30 text-synth-purple border border-synth-purple'
                                      : 'bg-synth-purple-day/20 text-synth-purple-day border border-synth-purple-day'
                                    : isNight
                                      ? 'bg-synth-dark text-synth-cyan border border-synth-cyan/30'
                                      : 'bg-synth-lighter text-synth-purple-day border border-synth-purple-day/30'
                                }`}
                              >
                                {post.mode}
                              </span>
                            </div>
                            <p className={`mb-2 ${
                              isNight ? 'text-synth-light' : 'text-synth-dark'
                            }`}>
                              {post.text}
                            </p>
                            <div className={`flex items-center gap-4 text-sm ${
                              isNight ? 'text-synth-cyan/70' : 'text-synth-purple-day/70'
                            }`}>
                              <span>💬 {post.metrics.replies}</span>
                              <span>❤️ {post.metrics.likes}</span>
                              <span>🔁 {post.metrics.quotes}</span>
                              <span>👁️ {post.metrics.impressions}</span>
                            </div>
                            {post.topics.length > 0 && (
                              <div className="mt-2 flex gap-1 flex-wrap">
                                {post.topics.map((topic) => (
                                  <span
                                    key={topic}
                                    className={`text-xs px-2 py-0.5 rounded ${
                                      isNight
                                        ? 'bg-synth-pink/20 text-synth-pink border border-synth-pink/50'
                                        : 'bg-synth-pink-day/20 text-synth-pink-day border border-synth-pink-day/50'
                                    }`}
                                  >
                                    #{topic}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Impact */}
          {showImpact && (
            <div className="lg:col-span-3">
              <div className={`rounded-lg p-6 sticky top-4 border-2 transition-all ${
                isNight
                  ? 'bg-synth-surface/90 border-synth-purple shadow-neon-purple backdrop-blur-sm'
                  : 'bg-synth-light-surface/90 border-synth-cyan-day shadow-lg backdrop-blur-sm'
              }`}>
                <h2 className={`text-xl font-bold mb-4 ${
                  isNight ? 'text-synth-purple' : 'text-synth-purple-day'
                }`}>
                  IMPACT
                </h2>
                <p className={`text-sm mb-4 ${
                  isNight ? 'text-synth-cyan/70' : 'text-synth-purple-day/70'
                }`}>
                  Shows how posts influence each other
                </p>
                {posts.length > 0 && posts[0].lineage.influences.length > 0 ? (
                  <div className="space-y-2">
                    <div className={`text-xs ${
                      isNight ? 'text-synth-yellow' : 'text-synth-cyan-day'
                    }`}>
                      Latest post influenced by:
                    </div>
                    {posts[0].lineage.influences.slice(0, 3).map((id) => (
                      <div
                        key={id}
                        className={`text-xs p-2 rounded border ${
                          isNight
                            ? 'bg-synth-purple/20 text-synth-purple border-synth-purple/50'
                            : 'bg-synth-purple-day/20 text-synth-purple-day border-synth-purple-day/50'
                        }`}
                      >
                        {id.slice(0, 12)}...
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className={`text-sm ${
                    isNight ? 'text-synth-cyan/50' : 'text-synth-purple-day/50'
                  }`}>
                    No influences yet...
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className={`py-6 mt-12 border-t-4 ${
        isNight
          ? 'bg-gradient-to-r from-synth-darker via-synth-surface to-synth-darker border-synth-pink'
          : 'bg-gradient-to-r from-synth-light via-synth-lighter to-synth-light border-synth-pink-day'
      }`}>
        <div className="container mx-auto px-4 text-center">
          <p className={`text-sm font-medium ${
            isNight ? 'text-synth-cyan' : 'text-synth-purple-day'
          }`}>
            © HURL • All posts are synthetic • <span className={
              isNight ? 'text-synth-pink' : 'text-synth-pink-day'
            }>Hurl responsibly</span>
          </p>
        </div>
      </footer>
    </div>
  );
}
