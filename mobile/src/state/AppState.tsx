import React, { createContext, useContext, useState, type PropsWithChildren } from 'react';
import type { components } from '../generated/api';
import type { Locale } from '../i18n/resources';

export type PrivacyRecord = components['schemas']['PrivacyRecord'];

export type AppStateSeed = {
  interfaceLocale: Locale;
  replyLocale: Locale;
  onboardingComplete: boolean;
  memoryEnabled: boolean;
  pairingPresent: boolean;
  privacyRecords: PrivacyRecord[];
};

type AppStateValue = AppStateSeed & {
  setInterfaceLocale: (locale: Locale) => void;
  setReplyLocale: (locale: Locale) => void;
  completeOnboarding: () => void;
  setMemoryEnabled: (enabled: boolean) => void;
  removePairing: () => void;
  deleteLocalRecords: () => void;
};

const defaults: AppStateSeed = {
  interfaceLocale: 'en',
  replyLocale: 'en',
  onboardingComplete: false,
  memoryEnabled: false,
  pairingPresent: false,
  privacyRecords: [],
};

const AppStateContext = createContext<AppStateValue | null>(null);

export function AppStateProvider({
  children,
  initialState,
}: PropsWithChildren<{ initialState?: Partial<AppStateSeed> }>) {
  const seed = { ...defaults, ...initialState };
  const [interfaceLocale, setInterfaceLocale] = useState(seed.interfaceLocale);
  const [replyLocale, setReplyLocale] = useState(seed.replyLocale);
  const [onboardingComplete, setOnboardingComplete] = useState(seed.onboardingComplete);
  const [memoryEnabled, setMemoryEnabled] = useState(seed.memoryEnabled);
  const [pairingPresent, setPairingPresent] = useState(seed.pairingPresent);
  const [privacyRecords, setPrivacyRecords] = useState(seed.privacyRecords);

  return (
    <AppStateContext.Provider
      value={{
        interfaceLocale,
        replyLocale,
        onboardingComplete,
        memoryEnabled,
        pairingPresent,
        privacyRecords,
        setInterfaceLocale,
        setReplyLocale,
        completeOnboarding: () => setOnboardingComplete(true),
        setMemoryEnabled,
        removePairing: () => setPairingPresent(false),
        deleteLocalRecords: () =>
          setPrivacyRecords(records =>
            records.flatMap(record => {
              if (record.location === 'local') return [];
              if (record.location === 'local_and_facade') return [{ ...record, location: 'facade' as const }];
              return [record];
            }),
          ),
      }}>
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState(): AppStateValue {
  const value = useContext(AppStateContext);
  if (!value) {
    throw new Error('useAppState must be used inside AppStateProvider');
  }
  return value;
}
