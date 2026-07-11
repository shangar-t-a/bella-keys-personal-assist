export {}

declare global {
  interface Window {
    electronAPI?: {
      platform: string;
      onOAuthCallback: (callback: (url: string) => void) => () => void;
    };
  }
}
