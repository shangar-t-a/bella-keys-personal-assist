export interface HostBackupMetadata {
  filename: string;
  filepath: string;
  size_bytes: number;
  formatted_size: string;
  created_at: string;
}

export {}

declare global {
  interface Window {
    electronAPI?: {
      platform: string;
      selectDirectory?: () => Promise<string | null>;
      getDefaultBackupDir?: () => Promise<string>;
      listHostBackups?: (dirPath?: string) => Promise<HostBackupMetadata[]>;
      writeHostBackup?: (dirPath: string, filename: string, content: string) => Promise<HostBackupMetadata>;
      readHostBackup?: (dirPath: string, filename: string) => Promise<string>;
      deleteHostBackup?: (dirPath: string, filename: string) => Promise<boolean>;
      saveBackupFile?: (filename: string, content: string) => Promise<string | null>;
      openBackupFile?: () => Promise<{ filePath: string; filename: string; content: string } | null>;
      onOAuthCallback: (callback: (url: string) => void) => () => void;
    };
  }
}


