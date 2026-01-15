export enum WSEventType {
  // Connection
  CONNECT = 'connection:connect',
  DISCONNECT = 'connection:disconnect',
  CONNECTION_CONFIRMED = 'connection:confirmed',
  SUBSCRIPTION_CONFIRMED = 'subscription:confirmed',
  ERROR = 'connection:error',

  // Deployment Events
  DEPLOYMENT_STARTED = 'deployment:started',
  DEPLOYMENT_PROGRESS = 'deployment:progress',
  DEPLOYMENT_LOG = 'deployment:log',
  DEPLOYMENT_RESOURCE_CHANGE = 'deployment:resource_change',
  DEPLOYMENT_COMPLETED = 'deployment:completed',
  DEPLOYMENT_FAILED = 'deployment:failed',

  // Resource Events
  RESOURCE_CREATED = 'resource:created',
  RESOURCE_UPDATED = 'resource:updated',
  RESOURCE_DELETED = 'resource:deleted',
  RESOURCE_STATUS_CHANGE = 'resource:status_change',

  // Stack Events
  STACK_CREATED = 'stack:created',
  STACK_UPDATED = 'stack:updated',
  STACK_DELETED = 'stack:deleted',

  // File Events
  FILE_CHANGED = 'file:changed',
}

export interface WSEvent<T = any> {
  type: WSEventType | string;
  timestamp: string;
  data: T;
  metadata?: {
    stackName?: string;
    deploymentId?: string;
    userId?: string;
  };
}

export interface DeploymentStartedEvent {
  deploymentId: string;
  stackName: string;
  operation: 'up' | 'destroy' | 'preview';
  estimatedDuration?: number;
}

export interface DeploymentProgressEvent {
  deploymentId: string;
  progress: number; // 0-100
  currentStep: string;
  totalSteps: number;
  completedSteps: number;
  message: string;
}

export interface DeploymentLogEvent {
  deploymentId: string;
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
  context?: Record<string, any>;
}

export interface ResourceChangeEvent {
  deploymentId: string;
  resourceUrn: string;
  resourceType: string;
  resourceName: string;
  changeType: 'create' | 'update' | 'delete' | 'same';
  oldState?: any;
  newState?: any;
  diff?: any;
}

export interface DeploymentCompletedEvent {
  deploymentId: string;
  stackName: string;
  duration: number;
  summary: {
    created: number;
    updated: number;
    deleted: number;
    unchanged: number;
  };
  outputs: Record<string, any>;
}

export interface ResourceStatusChangeEvent {
  stackName: string;
  resourceUrn: string;
  status: 'creating' | 'ready' | 'updating' | 'deleting' | 'failed';
  health?: 'healthy' | 'degraded' | 'unhealthy';
  message?: string;
}

export interface SubscribeStackRequest {
  stackName: string;
}

export interface SubscribeDeploymentRequest {
  deploymentId: string;
}
