/**
 * Server-Sent Events (SSE) client for Hurl posts streaming.
 */

// Type definitions matching backend schemas

export interface StyleMetrics {
  emojis: number;
  hashtags: number;
  links: number;
  caps: number;
}

export interface PostLineage {
  template: string | null;
  influences: string[];
}

export interface PostMetrics {
  likes: number;
  replies: number;
  quotes: number;
  impressions: number;
}

export interface Post {
  id: string;
  text: string;
  persona_id: string;
  created_at: string;
  mode: 'emergent' | 'pure_random';
  topics: string[];
  language: string;
  style: StyleMetrics;
  lineage: PostLineage;
  metrics: PostMetrics;
  toxicity: number;
}

export interface StreamOptions {
  mode?: 'emergent' | 'pure_random';
  topics?: string[];
  persona_ids?: string[];
  language?: string[];
  toxicity_max?: number;
  seed?: number;
  interval?: number;
}

/**
 * SSE client for streaming Hurl posts.
 */
export class HurlSSEClient {
  private baseUrl: string;
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Connect to the SSE stream.
   */
  connect(
    onPost: (post: Post) => void,
    onError?: (error: Event) => void,
    options: StreamOptions = {}
  ): void {
    if (this.eventSource) {
      this.disconnect();
    }

    // Build query parameters
    const params = new URLSearchParams();
    if (options.mode) params.set('mode', options.mode);
    if (options.topics && options.topics.length > 0) {
      params.set('topics', options.topics.join(','));
    }
    if (options.persona_ids && options.persona_ids.length > 0) {
      params.set('persona_ids', options.persona_ids.join(','));
    }
    if (options.language && options.language.length > 0) {
      params.set('language', options.language.join(','));
    }
    if (options.toxicity_max !== undefined) {
      params.set('toxicity_max', options.toxicity_max.toString());
    }
    if (options.seed !== undefined) {
      params.set('seed', options.seed.toString());
    }
    if (options.interval !== undefined) {
      params.set('interval', options.interval.toString());
    }

    const url = `${this.baseUrl}/v1/stream?${params.toString()}`;

    try {
      this.eventSource = new EventSource(url);

      // Handle post events
      this.eventSource.addEventListener('post', (event: MessageEvent) => {
        try {
          const post: Post = JSON.parse(event.data);
          onPost(post);
          this.reconnectAttempts = 0; // Reset on successful message
        } catch (error) {
          console.error('Failed to parse post data:', error);
        }
      });

      // Handle connection open
      this.eventSource.onopen = () => {
        console.log('SSE connection established');
        this.reconnectAttempts = 0;
      };

      // Handle errors
      this.eventSource.onerror = (error: Event) => {
        console.error('SSE connection error:', error);

        if (onError) {
          onError(error);
        }

        // Auto-reconnect logic
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(
            `Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`
          );

          setTimeout(() => {
            this.connect(onPost, onError, options);
          }, this.reconnectDelay * this.reconnectAttempts);
        } else {
          console.error('Max reconnection attempts reached');
          this.disconnect();
        }
      };
    } catch (error) {
      console.error('Failed to create EventSource:', error);
      if (onError) {
        onError(error as Event);
      }
    }
  }

  /**
   * Disconnect from the SSE stream.
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.reconnectAttempts = 0;
      console.log('SSE connection closed');
    }
  }

  /**
   * Check if the client is currently connected.
   */
  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
  }
}
