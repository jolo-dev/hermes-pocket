import React from 'react';
import ReactTestRenderer, { act } from 'react-test-renderer';
import { Text } from 'react-native';
import { AppRoot } from '../src/app/App';
import type { AppStateSeed } from '../src/state/AppState';

const readyState: Partial<AppStateSeed> = { onboardingComplete: true };

async function renderApp(platform: 'ios' | 'android', initialState = readyState) {
  let renderer!: ReactTestRenderer.ReactTestRenderer;
  await act(() => {
    renderer = ReactTestRenderer.create(<AppRoot initialState={initialState} platform={platform} />);
  });
  return renderer;
}

describe.each(['ios', 'android'] as const)('%s application shell', platform => {
  test('keeps interface and reply language preferences independent', async () => {
    const renderer = await renderApp(platform);
    await act(() => renderer.root.findByProps({ testID: 'tab-privacy' }).props.onPress());
    await act(() => renderer.root.findByProps({ testID: 'interface-language-de' }).props.onPress());

    expect(renderer.root.findByProps({ testID: 'privacy-screen' }).findAllByType(Text).some(node => node.props.children === 'Datenschutz')).toBe(true);
    expect(renderer.root.findByProps({ testID: 'reply-language-en' }).props.accessibilityState.selected).toBe(true);

    await act(() => renderer.root.findByProps({ testID: 'reply-language-vi' }).props.onPress());
    expect(renderer.root.findByProps({ testID: 'interface-language-de' }).props.accessibilityState.selected).toBe(true);
    expect(renderer.root.findByProps({ testID: 'reply-language-vi' }).props.accessibilityState.selected).toBe(true);
  });

  test('supports the onboarding permission-decline path', async () => {
    const renderer = await renderApp(platform, { onboardingComplete: false });
    expect(renderer.root.findByProps({ testID: 'onboarding-screen' })).toBeTruthy();
    await act(() => renderer.root.findByProps({ testID: 'onboarding-skip' }).props.onPress());
    expect(renderer.root.findByProps({ testID: `app-shell-${platform}` })).toBeTruthy();
  });

  if (platform === 'ios') {
    test('states the honest iOS context boundary', async () => {
      const renderer = await renderApp(platform);
      await act(() => renderer.root.findByProps({ testID: 'tab-privacy' }).props.onPress());
      const guidance = renderer.root.findByProps({ testID: 'ios-context-guidance' });
      const text = guidance.findAllByType(Text).map(node => node.props.children).join(' ');
      expect(text).toContain('share sheet');
      expect(text).toContain('screenshot or file');
      expect(text).toContain('direct integration');
      expect(text).toContain('browser extension');
      expect(text).toContain('does not inspect other apps');
    });
  }
});

test('local deletion preserves disclosed facade-only metadata and pairing removal is explicit', async () => {
  const renderer = await renderApp('android', {
    onboardingComplete: true,
    pairingPresent: true,
    privacyRecords: [
      { record_id: 'local-1', category: 'document', location: 'local', created_at: '2031-01-01T00:00:00Z', retention_expires_at: null },
      { record_id: 'both-1', category: 'share', location: 'local_and_facade', created_at: '2031-01-01T00:00:00Z', retention_expires_at: null },
      { record_id: 'remote-1', category: 'conversation', location: 'facade', created_at: '2031-01-01T00:00:00Z', retention_expires_at: null },
    ],
  });
  await act(() => renderer.root.findByProps({ testID: 'tab-privacy' }).props.onPress());
  await act(() => renderer.root.findByProps({ testID: 'delete-local-records' }).props.onPress());
  expect(renderer.root.findByProps({ testID: 'record-count' }).props.children).toContain(2);
  await act(() => renderer.root.findByProps({ testID: 'remove-pairing' }).props.onPress());
  expect(renderer.root.findByProps({ testID: 'remove-pairing' }).props.disabled).toBe(true);
});
