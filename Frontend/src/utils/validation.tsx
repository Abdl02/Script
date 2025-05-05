import {TestScenario} from "types/models";

export const validateScenario = (scenario: Partial<TestScenario>): string[] => {
  const errors: string[] = [];

  if (!scenario.name) errors.push('Scenario name is required');
  if (!scenario.id) errors.push('Scenario ID is required');
  if (!scenario.description) errors.push('Scenario description is required');
  if (!scenario.version) errors.push('Scenario version is required');

  if (scenario.requests && scenario.requests.length === 0) {
    errors.push('At least one request is required');
  }

  scenario.requests?.forEach((request, index) => {
    if (!request.name) errors.push(`Request ${index + 1}: Name is required`);
    if (!request.method) errors.push(`Request ${index + 1}: Method is required`);
    if (!request.url) errors.push(`Request ${index + 1}: URL is required`);
  });

  return errors;
};