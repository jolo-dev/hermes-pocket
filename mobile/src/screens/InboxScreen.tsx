import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, spacing } from '../design/theme';
import { translate } from '../i18n/resources';
import { useAppState } from '../state/AppState';

export function InboxScreen() {
  const { interfaceLocale } = useAppState();
  return (
    <View style={styles.page} testID="inbox-screen">
      <Text accessibilityRole="header" style={styles.title}>{translate(interfaceLocale, 'inbox')}</Text>
      <Text style={styles.body}>{translate(interfaceLocale, 'inboxEmpty')}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, padding: spacing.large },
  title: { color: colors.ink, fontSize: 32, fontWeight: '800' },
  body: { color: colors.muted, fontSize: 17, lineHeight: 25, marginTop: spacing.large },
});
