export interface FileInfo {
  path: string;
  name: string;
  size: number;
  modified: number;
  type: 'file' | 'directory';
  extension: string;
}

export interface DirectoryTree {
  name: string;
  path: string;
  type: 'file' | 'directory';
  extension?: string;
  size?: number;
  children: DirectoryTree[];
}

export interface FileContent {
  path: string;
  content: string;
  size: number;
}

export interface UpdateFileRequest {
  content: string;
  validate?: boolean;
}

export interface CreateFileRequest {
  path: string;
  content: string;
  validate?: boolean;
}

export interface ValidationResult {
  valid: boolean;
  error?: string;
  line?: number;
  offset?: number;
  text?: string;
}
