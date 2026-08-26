import React from 'react';
import { Platform, StatusBar, StyleSheet } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { AppShell } from '../navigation/AppShell';
import { OnboardingScreen } from '../screens/OnboardingScreen';
import { AppStateProvider, type AppStateSeed, useAppState } from '../state/AppState';

function AppContent({ platform }: { platform: 'ios' | 'android' }) {
  const { onboardingComplete } = useAppState();
  return onboardingComplete ? <AppShell platform={platform} /> : <OnboardingScreen />;
}

export function AppRoot({
  initialState,
  platform = Platform.OS === 'ios' ? 'ios' : 'android',
}: {
  initialState?: Partial<AppStateSeed>;
  platform?: 'ios' | 'android';
}) {
  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" />
      <SafeAreaView style={styles.safeArea}>
        <AppStateProvider initialState={initialState}>
          <AppContent platform={platform} />
        </AppStateProvider>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({ safeArea: { flex: 1 } });

export default function App() {
  return <AppRoot />;
}
