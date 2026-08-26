import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, spacing } from '../design/theme';
import { translate } from '../i18n/resources';
import { useAppState } from '../state/AppState';

export function OnboardingScreen() {
  const { interfaceLocale, completeOnboarding } = useAppState();
  return (
    <View style={styles.page} testID="onboarding-screen">
      <Text accessibilityRole="header" style={styles.eyebrow}>HERMES POCKET</Text>
      <Text accessibilityRole="header" style={styles.title} maxFontSizeMultiplier={2.5}>
        {translate(interfaceLocale, 'onboardingTitle')}
      </Text>
      <Text style={styles.body} maxFontSizeMultiplier={2.5}>
        {translate(interfaceLocale, 'onboardingBody')}
      </Text>
      <View style={styles.permissionCard} accessible accessibilityLabel={translate(interfaceLocale, 'permissionsTitle')}>
        <Text style={styles.cardTitle}>{translate(interfaceLocale, 'permissionsTitle')}</Text>
        <Text style={styles.body}>{translate(interfaceLocale, 'permissionsBody')}</Text>
      </View>
      <Pressable
        accessibilityRole="button"
        onPress={completeOnboarding}
        style={styles.button}
        testID="onboarding-skip">
        <Text style={styles.buttonText}>{translate(interfaceLocale, 'continueWithoutPermissions')}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: colors.paper, padding: spacing.xlarge, justifyContent: 'center' },
  eyebrow: { color: colors.amber, fontSize: 13, fontWeight: '800', letterSpacing: 2 },
  title: { color: colors.ink, fontSize: 40, fontWeight: '800', lineHeight: 46, marginTop: spacing.small },
  body: { color: colors.muted, fontSize: 17, lineHeight: 25, marginTop: spacing.medium },
  permissionCard: { backgroundColor: colors.surface, borderColor: colors.line, borderRadius: 20, borderWidth: 1, marginTop: spacing.large, padding: spacing.large },
  cardTitle: { color: colors.ink, fontSize: 20, fontWeight: '700' },
  button: { alignItems: 'center', backgroundColor: colors.teal, borderRadius: 16, marginTop: spacing.large, padding: spacing.medium },
  buttonText: { color: colors.white, fontSize: 16, fontWeight: '700', textAlign: 'center' },
});
