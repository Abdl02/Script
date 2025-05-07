import axios from 'axios';
import type { TestScenario, Field } from 'types/models';

const API_BASE_URL = 'http://127.0.0.1:8000';

axios.interceptors.request.use(request => {
  console.log('Request:', request.method?.toUpperCase(), request.url);
  return request;
});

axios.interceptors.response.use(
  response => {
    console.log('Response:', response.status, response.config.url);
    return response;
  },
  error => {
    console.error('API Error:', error.message, error.config?.url);
    return Promise.reject(error);
  }
);

export const api = {
  async getEnvironments(): Promise<Record<string, any>> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/environments`);
      return response.data;
    } catch (error) {
      console.error('Error fetching environments:', error);
      // Return default environment if API fails
      return {
        "localDev": {
          "url": "http://localhost:8099",
          "type": "localDev"
        }
      };
    }
  },

  async validateScenario(name: string): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/scenarios/${name}/validate`);
      return response.data;
    } catch (error) {
      console.error(`Error validating scenario ${name}:`, error);
      return { valid: false, message: "Validation failed" };
    }
  },

  async getBodyTemplates(endpointType: string): Promise<Record<string, any>> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/templates/body/${endpointType}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching body templates for ${endpointType}:`, error);
      return {};
    }
  },

  async saveBodyTemplate(endpointType: string, name: string, body: any): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/templates/body/${endpointType}`, {
        name,
        body
      });
      return response.data;
    } catch (error) {
      console.error('Error saving body template:', error);
      throw error;
    }
  },

  async getScenarios(): Promise<string[]> {
    try {
      console.log('Fetching scenarios from:', `${API_BASE_URL}/api/scenarios`);
      const response = await axios.get(`${API_BASE_URL}/api/scenarios`);
      console.log('Scenarios response:', response.data);

      if (Array.isArray(response.data)) {
        return response.data.filter(item => typeof item === 'string');
      } else if (response.data && typeof response.data === 'object') {
        const scenarios = response.data.scenarios || [];
        return Array.isArray(scenarios) ? scenarios.filter(item => typeof item === 'string') : [];
      }

      return [];
    } catch (error) {
      console.error('Error fetching scenarios:', error);
      return [];
    }
  },

  async getScenario(name: string): Promise<TestScenario> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/scenarios/${name}`);
      return {
        name: response.data.name,
        id: response.data.id || `id_${name}`,
        description: response.data.description || '',
        version: response.data.version || '1.0.0',
        created_at: response.data.created_at || new Date().toISOString(),
        updated_at: response.data.updated_at || new Date().toISOString(),
        requests: response.data.requests || []
      };
    } catch (error) {
      console.error(`Error fetching scenario ${name}:`, error);
      // Return a default scenario to prevent UI errors
      return {
        name: name,
        id: `id_${name}`,
        description: 'Error loading scenario details',
        version: '1.0.0',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        requests: []
      };
    }
  },

  async createScenario(scenario: Partial<TestScenario>): Promise<any> {
    try {
      const requestData = {
        name: scenario.name,
        id: scenario.id || `id_${scenario.name}_${Date.now()}`,
        description: scenario.description || '',
        version: scenario.version || '1.0.0',
        requests: scenario.requests || []
      };

      console.log('Creating scenario:', requestData);
      const response = await axios.post(`${API_BASE_URL}/api/scenarios`, requestData);
      console.log('Create scenario response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error creating scenario:', error);
      throw error;
    }
  },

  async fetchBodyFields(endpointType: string, url: string): Promise<any> {
    try {
      console.log(`Fetching fields for ${endpointType} with URL: ${url}`);
     const response = await axios.post(`${API_BASE_URL}/item/fields/${endpointType}`, { url });

      if (response.data && response.data.fields) {
       return response.data;
      }
     return { fields: [], message: "No fields returned" };
    } catch (error) {
     console.error(`Error fetching fields for ${endpointType}:`, error);
      throw error;
    }
  },

  async runScenario(name: string, environment: string = 'localDev'): Promise<any> {
  try {
    const requestData = {
      environment: environment,
    };
    const response = await axios.post(`${API_BASE_URL}/api/scenarios/${name}/run`, requestData);
    return response.data;
  } catch (error) {
    console.error(`Error running scenario ${name}:`, error);
    return { success: false, message: "Execution failed" };
  }
},

  async getEndpointFields(endpointType: string): Promise<Field[]> {
    try {
      console.log(`Fetching fields for ${endpointType} from ${API_BASE_URL}/item/fields/${endpointType}`);
      const response = await axios.get(`${API_BASE_URL}/item/fields/${endpointType}`);
      console.log('Fields response:', response.data);

      if (!response.data || !Array.isArray(response.data) || response.data.length === 0) {
        console.warn(`No fields returned for ${endpointType}, using defaults`);

        // Return default fields for api-specs
        if (endpointType === 'api-specs') {
          return [
            { path: 'name', type: 'string', required: true },
            { path: 'description', type: 'string' },
            { path: 'contextPath', type: 'string' },
            { path: 'backendServiceUrl', type: 'string' },
            { path: 'status', type: 'string' },
            { path: 'type', type: 'string' },
            { path: 'style', type: 'string' },
            { path: 'authType', type: 'string' },
            { path: 'metaData.version', type: 'string' },
            { path: 'metaData.owner', type: 'string' },
            { path: 'addVersionToContextPath', type: 'boolean' }
          ];
        }

        return [
          { path: 'name', type: 'string', required: true },
          { path: 'description', type: 'string' }
        ];
      }

      // Convert API response to match our Field interface
      return response.data.map((item: any) => ({
        path: item.path || item.name || '',
        type: item.type || 'string',
        required: !!item.required
      }));
    } catch (error) {
      console.error(`Error fetching fields for ${endpointType}:`, error);

      // Return default fields instead of throwing
      if (endpointType === 'api-specs') {
        return [
          { path: 'name', type: 'string', required: true },
          { path: 'description', type: 'string' },
          { path: 'contextPath', type: 'string' },
          { path: 'backendServiceUrl', type: 'string' },
          { path: 'status', type: 'string' }
        ];
      }

      return [
        { path: 'name', type: 'string', required: true },
        { path: 'description', type: 'string' }
      ];
    }
  },

  async getTemplates(endpointType: string): Promise<Record<string, any>[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/templates/${endpointType}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching templates for ${endpointType}:`, error);
      return [];
    }
  },
};