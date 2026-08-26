package com.hermespocket.screenhelp

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent

/**
 * Disabled foundation for Android Screen Help. The future opt-in flow must enable
 * the component and open a bounded capture session before this service reads data.
 */
class ScreenHelpAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Intentionally no event collection, node access, gestures, or bridge events.
    }

    override fun onInterrupt() = Unit
}
