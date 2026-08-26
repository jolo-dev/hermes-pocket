import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, spacing } from '../design/theme';
import { translate } from '../i18n/resources';
import { useAppState } from '../state/AppState';

export function ConversationScreen() {
  const { interfaceLocale, replyLocale } = useAppState();
  return (
    <View style={styles.page} testID="conversations-screen">
      <Text accessibilityRole="header" style={styles.title}>{translate(interfaceLocale, 'conversations')}</Text>
      <View style={styles.emptyCard}>
        <Text style={styles.emptyText}>{translate(interfaceLocale, 'conversationsEmpty')}</Text>
        <Text accessibilityLabel={`Agent reply language: ${replyLocale}`} style={styles.localeBadge}>{replyLocale.toUpperCase()}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, padding: spacing.large },
  title: { color: colors.ink, fontSize: 32, fontWeight: '800' },
  emptyCard: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 20, borderWidth: 1, marginTop: spacing.large, padding: spacing.large },
  emptyText: { color: colors.muted, fontSize: 17, lineHeight: 25 },
  localeBadge: { alignSelf: 'flex-start', backgroundColor: colors.tealSoft, borderRadius: 10, color: colors.teal, fontSize: 12, fontWeight: '800', marginTop: spacing.medium, overflow: 'hidden', paddingHorizontal: 10, paddingVertical: 6 },
});
