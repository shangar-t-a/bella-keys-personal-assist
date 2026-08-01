export {}

declare global {
  interface Window {
    electronAPI?: {
      platform: string;
      selectDirectory?: () => Promise<string | null>;
      onOAuthCallback: (callback: (url: string) => void) => () => void;
    };

  }
}
