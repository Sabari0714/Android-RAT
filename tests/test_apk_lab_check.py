import os
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from builder import apk_lab_check


class ApkLabCheckTests(unittest.TestCase):
    def test_missing_apk(self):
        report = apk_lab_check.validate_apk("/does/not/exist.apk")
        self.assertFalse(report["exists"])
        self.assertFalse(report["zip_valid"])

    def test_valid_zip_apk_without_sdk_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = os.path.join(tmp, "test.apk")
            with zipfile.ZipFile(apk, "w") as archive:
                archive.writestr("AndroidManifest.xml", "test")

            with patch("builder.apk_lab_check.tool_path", return_value=None):
                report = apk_lab_check.validate_apk(apk)

            self.assertTrue(report["exists"])
            self.assertTrue(report["zip_valid"])
            self.assertIsNone(report["aligned"])
            self.assertIsNone(report["signed"])

    @patch("builder.apk_lab_check.run")
    @patch("builder.apk_lab_check.tool_path")
    def test_sdk_checks(self, tool_path, run):
        with tempfile.TemporaryDirectory() as tmp:
            apk = os.path.join(tmp, "test.apk")
            with zipfile.ZipFile(apk, "w") as archive:
                archive.writestr("AndroidManifest.xml", "test")

            tool_path.side_effect = lambda name: f"/sdk/{name}"
            run.side_effect = [
                (True, "Verification successful"),
                (True, "Verified using v1 scheme"),
            ]

            report = apk_lab_check.validate_apk(apk)

            self.assertTrue(report["aligned"])
            self.assertTrue(report["signed"])
            self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
