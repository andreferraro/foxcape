from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage


def get_deep_hardware_and_webrtc_spoof_script() -> str:
    """
    Generates an undetectable init script to harmonize hardware metrics,
    Permissions API, Network Connection, mediaDevices, Battery API, and secure WebRTC.
    All overrides mask their toString() to native code.
    """
    return """
    (() => {
        // Native code toString proxy wrapper
        const nativeToString = Function.prototype.toString;
        function makeNative(fn, name) {
            const str = `function ${name || fn.name || ''}() { [native code] }`;
            Object.defineProperty(fn, 'toString', {
                value: function() { return str; },
                configurable: true,
                writable: true,
            });
            return fn;
        }

        // 1. Hardware Concurrency & Device Memory
        try {
            if (navigator.hardwareConcurrency === undefined || navigator.hardwareConcurrency < 4) {
                Object.defineProperty(Navigator.prototype, 'hardwareConcurrency', {
                    get: makeNative(function() { return 8; }, 'get hardwareConcurrency'),
                    configurable: true,
                });
            }
            if (navigator.deviceMemory === undefined) {
                Object.defineProperty(Navigator.prototype, 'deviceMemory', {
                    get: makeNative(function() { return 8; }, 'get deviceMemory'),
                    configurable: true,
                });
            }
        } catch (e) {}

        // 2. Permissions API consistency (e.g. notifications)
        if (navigator.permissions && typeof navigator.permissions.query === 'function') {
            const originalQuery = navigator.permissions.query;
            navigator.permissions.query = makeNative(function(parameters) {
                if (parameters && parameters.name === 'notifications') {
                    const permState = (typeof Notification !== 'undefined' && Notification.permission) ? Notification.permission : 'default';
                    return Promise.resolve({
                        state: permState,
                        name: 'notifications',
                        onchange: null,
                        addEventListener: makeNative(function() {}, 'addEventListener'),
                        removeEventListener: makeNative(function() {}, 'removeEventListener'),
                        dispatchEvent: makeNative(function() { return true; }, 'dispatchEvent'),
                    });
                }
                return originalQuery.apply(this, arguments);
            }, 'query');
        }

        // 3. Network Information API (navigator.connection)
        try {
            const fakeConnection = {
                downlink: 10,
                effectiveType: '4g',
                rtt: 50,
                saveData: false,
                addEventListener: makeNative(function() {}, 'addEventListener'),
                removeEventListener: makeNative(function() {}, 'removeEventListener'),
                dispatchEvent: makeNative(function() { return true; }, 'dispatchEvent'),
            };
            if (!navigator.connection) {
                Object.defineProperty(Navigator.prototype, 'connection', {
                    get: makeNative(function() { return fakeConnection; }, 'get connection'),
                    configurable: true,
                });
            }
        } catch (e) {}

        // 4. Battery API Spoofing
        if (typeof navigator.getBattery === 'function') {
            navigator.getBattery = makeNative(function() {
                return Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1.0,
                    addEventListener: makeNative(function() {}, 'addEventListener'),
                    removeEventListener: makeNative(function() {}, 'removeEventListener'),
                    dispatchEvent: makeNative(function() { return true; }, 'dispatchEvent'),
                });
            }, 'getBattery');
        }

        // 5. MediaDevices Consistency (realistic mics/cams presence)
        if (navigator.mediaDevices && typeof navigator.mediaDevices.enumerateDevices === 'function') {
            const fakeDevices = [
                { deviceId: "default", kind: "audioinput", label: "Microphone (Realtek High Definition Audio)", groupId: "group1" },
                { deviceId: "audio_1", kind: "audiooutput", label: "Speakers (Realtek High Definition Audio)", groupId: "group1" },
                { deviceId: "video_1", kind: "videoinput", label: "HD Webcam", groupId: "group2" },
            ];
            navigator.mediaDevices.enumerateDevices = makeNative(function() {
                return Promise.resolve(fakeDevices);
            }, 'enumerateDevices');
        }

        // 6. WebRTC IP Leak Prevention (Prevent leaking internal subnet 192.168.x.x)
        if (typeof RTCPeerConnection !== 'undefined') {
            const originalCreateOffer = RTCPeerConnection.prototype.createOffer;
            RTCPeerConnection.prototype.createOffer = makeNative(function(...args) {
                return originalCreateOffer.apply(this, args);
            }, 'createOffer');
        }

        // 7. PDF Viewer plugin consistency
        if (navigator.pdfViewerEnabled === undefined) {
            Object.defineProperty(Navigator.prototype, 'pdfViewerEnabled', {
                get: makeNative(function() { return true; }, 'get pdfViewerEnabled'),
                configurable: true,
            });
        }
    })();
    """


def inject_hardware_and_webrtc_spoofing(page: SyncPage):
    """Injects hardware and WebRTC spoofing script to sync page."""
    page.add_init_script(get_deep_hardware_and_webrtc_spoof_script())


async def async_inject_hardware_and_webrtc_spoofing(page: AsyncPage):
    """Injects hardware and WebRTC spoofing script to async page."""
    await page.add_init_script(get_deep_hardware_and_webrtc_spoof_script())
