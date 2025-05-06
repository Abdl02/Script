import axios from 'axios';
import type { TestScenario, Field } from 'types/models';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const api = {
    async getEnvironments(): Promise<Record<string, any>> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/environments`);
      return response.data;
    } catch (error) {
      console.error('Error fetching environments:', error);
      throw error;
    }
  },

  async validateScenario(name: string): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/scenarios/${name}/validate`);
      return response.data;
    } catch (error) {
      console.error(`Error validating scenario ${name}:`, error);
      throw error;
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
      console.log('Response:', response.data);
      return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
      console.error('Error fetching scenarios:', error);
      throw error;
    }
  },

  async getScenario(name: string): Promise<TestScenario> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/scenarios/${name}`);
      return {
        name: response.data.name,
        id: response.data.id || '',
        description: response.data.description || '',
        version: response.data.version || '1.0.0',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        requests: []
      };
    } catch (error) {
      console.error(`Error fetching scenario ${name}:`, error);
      throw error;
    }
  },

  async createScenario(scenario: Partial<TestScenario>): Promise<any> {
    try {
      // Send only the data the backend expects
      const requestData = {
        name: scenario.name,
        id: scenario.id,
        description: scenario.description,
        version: scenario.version,
        requests: scenario.requests
      };

      console.log('Creating scenario:', requestData);
      const response = await axios.post(`${API_BASE_URL}/api/scenarios`, requestData);
      console.log('Response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error creating scenario:', error);
      throw error;
    }
  },

  async runScenario(name: string): Promise<any> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/scenarios/${name}/run`, {});
      return response.data;
    } catch (error) {
      console.error(`Error running scenario ${name}:`, error);
      throw error;
    }
  },

  async getEndpointFields(endpointType: string): Promise<Field[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/fields/${endpointType}`);
      // Convert response to match our Field interface
      return response.data.map((item: any) => ({
        path: item.path || item.name || '',
        type: item.type || 'string',
        required: item.required || false
      }));
    } catch (error) {
      console.error(`Error fetching fields for ${endpointType}:`, error);
      throw error;
    }
  },

  async getTemplates(endpointType: string): Promise<Record<string, any>[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/templates/${endpointType}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching templates for ${endpointType}:`, error);
      throw error;
    }
  },
};