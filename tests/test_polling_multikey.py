import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("polling_test", ROOT / "tools" / "polling_multikey_v0.0.1.py")
polling = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = polling
SPEC.loader.exec_module(polling)


def synth(interval_s: float, batches: int = 120, per_batch: int = 3) -> list[polling.Event]:
    events = []
    for index in range(batches):
        stamp = 1000.0 + index * interval_s
        for key in range(per_batch):
            events.append(polling.Event(stamp, 4 + key, 1))
            events.append(polling.Event(stamp + 0.050, 4 + key, 0))
    return events


class AnalyzeTests(unittest.TestCase):
    def test_bluetooth_133hz(self):
        result = polling.analyze(synth(0.0075))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["classification"], "bluetooth_133hz")
        self.assertEqual(result["floor_ms"], 7.5)

    def test_usb_1000hz(self):
        result = polling.analyze(synth(0.001))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["classification"], "usb_1000hz")

    def test_bluetooth_125hz(self):
        result = polling.analyze(synth(0.0125))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["classification"], "bluetooth_90_125hz")

    def test_insufficient(self):
        result = polling.analyze(synth(0.0075, batches=3))
        self.assertEqual(result["status"], "insufficient")


class DeviceParsingTests(unittest.TestCase):
    def test_parse_devices(self):
        text = '''I: Bus=0003 Vendor=3434 Product=02d1 Version=0110
N: Name="Keychron K13 Pro Keyboard"
H: Handlers=sysrq kbd leds event19
'''
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            handle.write(text)
            path = handle.name
        try:
            devices = polling.parse_devices(path)
        finally:
            Path(path).unlink()
        self.assertEqual(devices, [("Keychron K13 Pro Keyboard", "/dev/input/event19")])

    def test_self_test(self):
        self.assertEqual(polling.self_test(), 0)


if __name__ == "__main__":
    unittest.main()
