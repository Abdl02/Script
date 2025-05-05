import axios from 'axios';
import type { TestScenario, Field } from '../types/models';

const API_BASE_URL = 'http://localhost:5000';

export const api = {
  // Scenario operations
  async getScenarios(): Promise<string[]> {
    const response = await axios.get(`${API_BASE_URL}/api/scenarios`);
    return response.data;
  },

  async getScenario(name: string): Promise<TestScenario> {
    const response = await axios.get(`${API_BASE_URL}/api/scenarios/${name}`);
    return response.data;
  },

  async createScenario(scenario: Partial<TestScenario>): Promise<TestScenario> {
    const response = await axios.post(`${API_BASE_URL}/api/scenarios`, scenario);
    return response.data;
  },

  async runScenario(name: string): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/api/scenarios/${name}/run`);
    return response.data;
  },

  // Endpoint fields
  async getEndpointFields(endpointType: string): Promise<Field[]> {
    const response = await axios.get(`${API_BASE_URL}/api/fields/${endpointType}`);
    return response.data;
  },

  // Body templates
  async getTemplates(endpointType: string): Promise<Record<string, any>[]> {
    const response = await axios.get(`${API_BASE_URL}/api/templates/${endpointType}`);
    return response.data;
  }
};