import React, { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, useWindowDimensions, View, type DimensionValue } from 'react-native';
import { colors, spacing } from '../design/theme';
import { translate } from '../i18n/resources';
import { useAppState } from '../state/AppState';
import { ConversationScreen } from '../screens/ConversationScreen';
import { InboxScreen } from '../screens/InboxScreen';
import { PrivacyScreen } from '../screens/PrivacyScreen';

type Tab = 'conversations' | 'inbox' | 'privacy';

export function AppShell({ platform }: { platform: 'ios' | 'android' }) {
  const [activeTab, setActiveTab] = useState<Tab>('conversations');
  const { width } = useWindowDimensions();
  const { interfaceLocale } = useAppState();
  const wide = width >= 720;
  const tabs: Tab[] = ['conversations', 'inbox', 'privacy'];
  const content = activeTab === 'conversations' ? <ConversationScreen /> : activeTab === 'inbox' ? <InboxScreen /> : <PrivacyScreen platform={platform} />;
  const navWidth: DimensionValue = wide ? 220 : '100%';

  return (
    <View style={[styles.shell, wide && styles.shellWide]} testID={`app-shell-${platform}`}>
      <ScrollView contentContainerStyle={styles.content} style={styles.contentScroll}>{content}</ScrollView>
      <View accessibilityLabel="Primary navigation" style={[styles.navigation, wide ? styles.navigationWide : { width: navWidth }]}>
        {tabs.map(tab => (
          <Pressable
            accessibilityRole="tab"
            accessibilityState={{ selected: activeTab === tab }}
            key={tab}
            onPress={() => setActiveTab(tab)}
            style={[styles.navItem, activeTab === tab && styles.navItemSelected]}
            testID={`tab-${tab}`}>
            <Text style={[styles.navText, activeTab === tab && styles.navTextSelected]}>{translate(interfaceLocale, tab)}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  shell: { backgroundColor: colors.paper, flex: 1 },
  shellWide: { flexDirection: 'row' },
  navigation: { backgroundColor: colors.ink, flexDirection: 'row', padding: spacing.small },
  navigationWide: { flexDirection: 'column', paddingTop: spacing.xlarge, width: 220 },
  navItem: { borderRadius: 12, flex: 1, padding: 12 },
  navItemSelected: { backgroundColor: colors.teal },
  navText: { color: '#BFD0CC', fontSize: 14, fontWeight: '700', textAlign: 'center' },
  navTextSelected: { color: colors.white },
  contentScroll: { flex: 1 },
  content: { flexGrow: 1 },
});
