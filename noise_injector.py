import random

from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage


def get_canvas_and_audio_noise_script(seed: int | float | None = None) -> str:
    """
    Generates a secure, self-contained JavaScript snippet injected before any page scripts run.
    It injects minute sub-pixel noise into HTML5 Canvas and subtle frequency jitter into Web Audio API,
    randomizing per-session fingerprint hashes without breaking visual or audio output.
    """
    active_seed = seed if seed is not None else random.randint(1000, 999999)

    return f"""
    (() => {{
        const SEED = {active_seed};

        function pseudoRandom(offset) {{
            const x = Math.sin(SEED + offset) * 10000;
            return x - Math.floor(x);
        }}

        // 1. Canvas 2D Noise Injection
        if (typeof HTMLCanvasElement !== 'undefined') {{
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

            CanvasRenderingContext2D.prototype.getImageData = function(...args) {{
                const imageData = originalGetImageData.apply(this, args);
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {{
                    if (pseudoRandom(i) < 0.005) {{
                        const shift = pseudoRandom(i + 1) > 0.5 ? 1 : -1;
                        data[i] = Math.max(0, Math.min(255, data[i] + shift));
                    }}
                }}
                return imageData;
            }};

            HTMLCanvasElement.prototype.toDataURL = function(...args) {{
                const context = this.getContext('2d');
                if (context) {{
                    try {{
                        const img = context.getImageData(0, 0, Math.min(this.width, 10), Math.min(this.height, 10));
                    }} catch (e) {{}}
                }}
                return originalToDataURL.apply(this, args);
            }};
        }}

        // 2. Web Audio API Noise Injection
        if (typeof AudioBuffer !== 'undefined') {{
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = function(channel) {{
                const data = originalGetChannelData.apply(this, arguments);
                for (let i = 0; i < data.length; i += 100) {{
                    if (pseudoRandom(i + channel) < 0.05) {{
                        data[i] += (pseudoRandom(i + channel + 1) - 0.5) * 1e-7;
                    }}
                }}
                return data;
            }};
        }}

        if (typeof AnalyserNode !== 'undefined') {{
            const originalGetFloatFrequencyData = AnalyserNode.prototype.getFloatFrequencyData;
            AnalyserNode.prototype.getFloatFrequencyData = function(array) {{
                originalGetFloatFrequencyData.apply(this, arguments);
                for (let i = 0; i < array.length; i += 50) {{
                    array[i] += (pseudoRandom(i) - 0.5) * 1e-4;
                }}
            }};
        }}
    }})();
    """


def inject_fingerprint_noise(page: SyncPage, seed: int | float | None = None):
    """Adds canvas and audio noise init script to sync page."""
    script = get_canvas_and_audio_noise_script(seed)
    page.add_init_script(script)


async def async_inject_fingerprint_noise(page: AsyncPage, seed: int | float | None = None):
    """Adds canvas and audio noise init script to async page."""
    script = get_canvas_and_audio_noise_script(seed)
    await page.add_init_script(script)
