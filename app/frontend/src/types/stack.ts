export interface StackSummary {
  name: string;
  current: boolean;
  last_update: string | null;
  resource_count: number;
  url: string | null;
}

export interface StackConfig {
  provider: string;
  region: string;
  app_image: string;
  [key: string]: any;
}

export interface StackInfo {
  name: string;
  config: Record<string, any>;
  outputs: Record<string, any>;
  last_update: string | null;
  resource_count: number;
  url: string | null;
}

export interface Resource {
  urn: string;
  type: string;
  id: string | null;
  parent: string | null;
  dependencies: string[];
  properties: Record<string, any>;
  inputs: Record<string, any>;
}

export interface CreateStackRequest {
  name: string;
  config?: Record<string, string>;
}

export interface UpdateStackConfigRequest {
  config: Record<string, string>;
}

export interface DeploymentSummary {
  created: number;
  updated: number;
  deleted: number;
  unchanged: number;
}

export interface DeploymentResult {
  deployment_id: string;
  stack_name: string;
  operation: 'preview' | 'up' | 'destroy' | 'refresh';
  status: 'running' | 'completed' | 'failed';
  summary: DeploymentSummary | null;
  outputs: Record<string, any>;
  error: string | null;
}

export type StackOperation = 'preview' | 'up' | 'destroy' | 'refresh';
