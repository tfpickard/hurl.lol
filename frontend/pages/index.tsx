import { useEffect, useState, useRef } from 'react';
import { HurlSSEClient, Post } from '../lib/sse';

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [mode, setMode] = useState<'emergent' | 'pure_random'>('emergent');
  const [isConnected, setIsConnected] = useState(false);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [seed, setSeed] = useState<string>('');
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [showImpact, setShowImpact] = useState(false);

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
    } else {
      const options = {
        mode,
        topics: selectedTopics.length > 0 ? selectedTopics : undefined,
        seed: seed ? parseInt(seed) : undefined,
        interval: 1.0,
      };

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
        },
        options
      );

      setIsConnected(true);
    }
  };

  const toggleTopic = (topic: string) => {
    setSelectedTopics((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-pink-600 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold">Hurl</h1>
          <p className="text-purple-100 mt-2">The Internet, but synthetic</p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow p-6 sticky top-4">
              <h2 className="text-xl font-bold mb-4">Controls</h2>

              {/* Mode Toggle */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Mode</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setMode('emergent')}
                    className={`flex-1 py-2 px-4 rounded ${
                      mode === 'emergent'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    Emergent
                  </button>
                  <button
                    onClick={() => setMode('pure_random')}
                    className={`flex-1 py-2 px-4 rounded ${
                      mode === 'pure_random'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    Random
                  </button>
                </div>
              </div>

              {/* Topics */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Topics</label>
                <div className="flex flex-wrap gap-2">
                  {topicOptions.map((topic) => (
                    <button
                      key={topic}
                      onClick={() => toggleTopic(topic)}
                      className={`px-3 py-1 rounded text-sm ${
                        selectedTopics.includes(topic)
                          ? 'bg-pink-600 text-white'
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {topic}
                    </button>
                  ))}
                </div>
              </div>

              {/* Seed */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Seed (optional)</label>
                <input
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(e.target.value)}
                  placeholder="Random"
                  className="w-full px-3 py-2 border rounded"
                />
              </div>

              {/* Connect Button */}
              <button
                onClick={handleConnect}
                className={`w-full py-3 rounded font-bold ${
                  isConnected
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {isConnected ? 'Disconnect' : 'Start Stream'}
              </button>

              {/* Impact Toggle */}
              <button
                onClick={() => setShowImpact(!showImpact)}
                className="w-full mt-4 py-2 border rounded text-sm"
              >
                {showImpact ? 'Hide' : 'Show'} Impact Panel
              </button>

              {/* Stats */}
              <div className="mt-6 pt-6 border-t">
                <div className="text-sm text-gray-600">
                  <div className="flex justify-between mb-2">
                    <span>Posts:</span>
                    <span className="font-bold">{posts.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span
                      className={`font-bold ${
                        isConnected ? 'text-green-600' : 'text-gray-400'
                      }`}
                    >
                      {isConnected ? 'Live' : 'Offline'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Center Panel - Feed */}
          <div className={showImpact ? 'lg:col-span-6' : 'lg:col-span-9'}>
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-xl font-bold">Feed</h2>
              </div>
              <div
                ref={scrollRef}
                className="overflow-y-auto"
                style={{ maxHeight: 'calc(100vh - 300px)' }}
              >
                {posts.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    {isConnected
                      ? 'Waiting for posts...'
                      : 'Click "Start Stream" to begin'}
                  </div>
                ) : (
                  <div className="divide-y">
                    {posts.map((post) => (
                      <div key={post.id} className="p-4 hover:bg-gray-50">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-bold text-sm">
                                Persona {post.persona_id.slice(0, 8)}
                              </span>
                              <span className="text-gray-500 text-xs">
                                {new Date(post.created_at).toLocaleTimeString()}
                              </span>
                              <span
                                className={`text-xs px-2 py-0.5 rounded ${
                                  post.mode === 'emergent'
                                    ? 'bg-purple-100 text-purple-700'
                                    : 'bg-gray-100 text-gray-700'
                                }`}
                              >
                                {post.mode}
                              </span>
                            </div>
                            <p className="text-gray-900 mb-2">{post.text}</p>
                            <div className="flex items-center gap-4 text-sm text-gray-500">
                              <span>💬 {post.metrics.replies}</span>
                              <span>❤️ {post.metrics.likes}</span>
                              <span>🔁 {post.metrics.quotes}</span>
                              <span>👁️ {post.metrics.impressions}</span>
                            </div>
                            {post.topics.length > 0 && (
                              <div className="mt-2 flex gap-1">
                                {post.topics.map((topic) => (
                                  <span
                                    key={topic}
                                    className="text-xs px-2 py-0.5 bg-pink-50 text-pink-700 rounded"
                                  >
                                    {topic}
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
              <div className="bg-white rounded-lg shadow p-6 sticky top-4">
                <h2 className="text-xl font-bold mb-4">Impact</h2>
                <p className="text-sm text-gray-600 mb-4">
                  Shows how posts influence each other
                </p>
                {posts.length > 0 && posts[0].lineage.influences.length > 0 ? (
                  <div className="space-y-2">
                    <div className="text-xs text-gray-500">
                      Latest post influenced by:
                    </div>
                    {posts[0].lineage.influences.slice(0, 3).map((id) => (
                      <div key={id} className="text-xs p-2 bg-purple-50 rounded">
                        {id.slice(0, 12)}...
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">
                    No influences yet...
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">© Hurl. All posts are synthetic. Hurl responsibly.</p>
        </div>
      </footer>
    </div>
  );
}
