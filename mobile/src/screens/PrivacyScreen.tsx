import React from 'react';
import { Pressable, StyleSheet, Switch, Text, View } from 'react-native';
import { colors, spacing } from '../design/theme';
import { translate, type Locale } from '../i18n/resources';
import { useAppState } from '../state/AppState';

const locales: Locale[] = ['en', 'vi', 'de'];

function LanguagePicker({
  label,
  selected,
  onSelect,
  testID,
}: {
  label: string;
  selected: Locale;
  onSelect: (locale: Locale) => void;
  testID: string;
}) {
  return (
    <View accessible={false} style={styles.section} testID={testID}>
      <Text style={styles.sectionTitle}>{label}</Text>
      <View style={styles.choiceRow}>
        {locales.map(locale => (
          <Pressable
            accessibilityRole="button"
            accessibilityState={{ selected: locale === selected }}
            key={locale}
            onPress={() => onSelect(locale)}
            style={[styles.choice, locale === selected && styles.choiceSelected]}
            testID={`${testID}-${locale}`}>
            <Text style={[styles.choiceText, locale === selected && styles.choiceTextSelected]}>{locale.toUpperCase()}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

export function PrivacyScreen({ platform }: { platform: 'ios' | 'android' }) {
  const state = useAppState();
  const t = (key: Parameters<typeof translate>[1]) => translate(state.interfaceLocale, key);
  return (
    <View style={styles.page} testID="privacy-screen">
      <Text accessibilityRole="header" style={styles.title}>{t('privacy')}</Text>
      <LanguagePicker label={t('interfaceLanguage')} selected={state.interfaceLocale} onSelect={state.setInterfaceLocale} testID="interface-language" />
      <LanguagePicker label={t('replyLanguage')} selected={state.replyLocale} onSelect={state.setReplyLocale} testID="reply-language" />
      {platform === 'ios' ? (
        <View style={styles.section} testID="ios-context-guidance">
          <Text style={styles.sectionTitle}>{t('iosContextTitle')}</Text>
          <Text style={styles.body}>{t('iosContextBody')}</Text>
        </View>
      ) : null}
      <View style={styles.section}>
        <View style={styles.switchRow}>
          <View style={styles.switchCopy}>
            <Text style={styles.sectionTitle}>{t('memory')}</Text>
            <Text style={styles.body}>{t('memoryDescription')}</Text>
          </View>
          <Switch accessibilityLabel={t('memory')} onValueChange={state.setMemoryEnabled} testID="memory-toggle" value={state.memoryEnabled} />
        </View>
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t('localData')}</Text>
        <Text style={styles.body} testID="record-count">{t('inspectRecords')}: {state.privacyRecords.length}</Text>
        <Text style={styles.notice}>{t('remoteDeletionNotice')}</Text>
        <Pressable accessibilityRole="button" onPress={state.deleteLocalRecords} style={styles.secondaryButton} testID="delete-local-records">
          <Text style={styles.secondaryButtonText}>{t('deleteLocalRecords')}</Text>
        </Pressable>
      </View>
      <View style={styles.section}>
        <Text style={styles.body} testID="pairing-status">{state.pairingPresent ? t('paired') : t('notPaired')}</Text>
        <Pressable accessibilityRole="button" disabled={!state.pairingPresent} onPress={state.removePairing} style={styles.secondaryButton} testID="remove-pairing">
          <Text style={styles.secondaryButtonText}>{t('removePairing')}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, padding: spacing.large },
  title: { color: colors.ink, fontSize: 32, fontWeight: '800', marginBottom: spacing.small },
  section: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 16, borderWidth: 1, marginTop: spacing.medium, padding: spacing.medium },
  sectionTitle: { color: colors.ink, fontSize: 17, fontWeight: '700' },
  body: { color: colors.muted, fontSize: 15, lineHeight: 21, marginTop: 4 },
  notice: { color: colors.amber, fontSize: 13, lineHeight: 19, marginTop: spacing.small },
  choiceRow: { flexDirection: 'row', gap: spacing.small, marginTop: spacing.small },
  choice: { borderColor: colors.line, borderRadius: 10, borderWidth: 1, paddingHorizontal: 14, paddingVertical: 9 },
  choiceSelected: { backgroundColor: colors.teal, borderColor: colors.teal },
  choiceText: { color: colors.ink, fontWeight: '700' },
  choiceTextSelected: { color: colors.white },
  switchRow: { alignItems: 'center', flexDirection: 'row', gap: spacing.medium },
  switchCopy: { flex: 1 },
  secondaryButton: { borderColor: colors.teal, borderRadius: 12, borderWidth: 1, marginTop: spacing.small, padding: 12 },
  secondaryButtonText: { color: colors.teal, fontWeight: '700', textAlign: 'center' },
});
