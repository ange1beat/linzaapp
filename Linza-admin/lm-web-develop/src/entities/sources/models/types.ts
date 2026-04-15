export enum SourceType {
  Telegram = "telegram",
  VK = "vk",
  OK = "ok",
  Web = "web",
}

export enum SourceLastResult {
  Success = "success",
  Error = "error",
}

export enum SourceExecutionStatus {
  InProgress = "inprogress",
  Planned = "planned",
  NotConfigure = "notconfigure",
  Stopped = "stopped",
}

export interface ISource {
  id: string;
  created: string;
  modified: string;
  title: string;
  description: string;
  iconUri: string;
  type: SourceType.Web | SourceType.OK | SourceType.VK | SourceType.Telegram;
  url: string;
  updateInterval: number;
  isActive: boolean;
  isAutoCreated: boolean;
  config: { [key: string]: never };
  account: { [key: string]: never };
  timezone: string;
  updated: string;
  lastResult?: SourceLastResult.Error | SourceLastResult.Success;
  nextLaunch: number;
  executionStatus:
    | SourceExecutionStatus.InProgress
    | SourceExecutionStatus.Planned
    | SourceExecutionStatus.NotConfigure
    | SourceExecutionStatus.Stopped;
}
