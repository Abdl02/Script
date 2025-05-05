import React, { createContext, useState, useContext } from 'react';
import { TestScenario } from '@types/models';

interface AppContextType {
  currentScenario: TestScenario | null;
  setCurrentScenario: (scenario: TestScenario | null) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentScenario, setCurrentScenario] = useState<TestScenario | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <AppContext.Provider value={{
      currentScenario,
      setCurrentScenario,
      isLoading,
      setIsLoading
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};