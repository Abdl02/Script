export interface TestScenario {
  name: string;
  id: string;
  description: string;
  version: string;
  created_at: string;
  updated_at: string;
  requests: APIRequest[];
}

export interface APIRequest {
  name: string;
  method: string;
  url: string;
  headers: Record<string, string>;
  body: any;
  save_as?: string;
  assertions: Assertion[];
}

export interface Assertion {
  type: 'status_code' | 'json_path' | 'response_body_contains';
  value: string;
  path?: string;
}

export interface Field {
  path: string;
  type: string;
  required?: boolean;
}