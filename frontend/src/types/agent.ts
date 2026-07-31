export interface AgentRun {
  text: string | null;
  tool_colls: Array<{
    name: string;
    args: Record<string, any>;
    result: any;
  }>;
}

export interface AgentState {
  messages: Array<{
    role: 'system' | 'user' | 'assistant';
    content: string;
  }>;
  intent?: Record<string, any>;
  plan?: any;
  context?: string;
  response?: string;
  tool_results?: Array<any>;
  reflection?: Record<string, any>;
  confidence?: number;
}

export interface EnhancedLearningAgent {
  run(userMessages: Array<{role: string, content: string}>): Promise<AgentRun>;
  registerTool(tool: any): void;
  setup(): void;
}

export interface Lesson {
  id: string;
  name: string;
  description?: string;
  file: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
  isError?: boolean;
}