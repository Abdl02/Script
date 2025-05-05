export const getValueAtPath = (obj: any, path: string): any => {
  return path.split('.').reduce((acc, part) => {
    if (part.includes('[') && part.includes(']')) {
      const fieldName = part.split('[')[0];
      const index = parseInt(part.split('[')[1].replace(']', ''));
      return acc?.[fieldName]?.[index];
    }
    return acc?.[part];
  }, obj);
};

export const setValueAtPath = (obj: any, path: string, value: any): any => {
  const parts = path.split('.');
  let current = obj;

  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i];
    if (part.includes('[') && part.includes(']')) {
      const fieldName = part.split('[')[0];
      const index = parseInt(part.split('[')[1].replace(']', ''));
      if (!current[fieldName]) current[fieldName] = [];
      if (!current[fieldName][index]) current[fieldName][index] = {};
      current = current[fieldName][index];
    } else {
      if (!current[part]) current[part] = {};
      current = current[part];
    }
  }

  const lastPart = parts[parts.length - 1];
  if (lastPart.includes('[') && lastPart.includes(']')) {
    const fieldName = lastPart.split('[')[0];
    const index = parseInt(lastPart.split('[')[1].replace(']', ''));
    if (!current[fieldName]) current[fieldName] = [];
    current[fieldName][index] = value;
  } else {
    current[lastPart] = value;
  }

  return obj;
};