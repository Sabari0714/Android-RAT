import unittest
from unittest.mock import patch

from builder import lab_validator


class LabValidatorTests(unittest.TestCase):
    @patch("builder.lab_validator.shutil.which")
    def test_check_tools_reports_paths(self, which):
        which.side_effect = lambda tool: f"/usr/bin/{tool}"
        tools = lab_validator.check_tools()
        self.assertEqual(tools["adb"], "/usr/bin/adb")
        self.assertEqual(tools["apksigner"], "/usr/bin/apksigner")

    @patch("builder.lab_validator.subprocess.run")
    def test_run_command_success(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = "ok\n"
        run.return_value.stderr = ""
        ok, output = lab_validator.run_command(["echo", "ok"])
        self.assertTrue(ok)
        self.assertEqual(output, "ok")

    @patch("builder.lab_validator.subprocess.run")
    def test_run_command_failure(self, run):
        run.return_value.returncode = 1
        run.return_value.stdout = ""
        run.return_value.stderr = "failed\n"
        ok, output = lab_validator.run_command(["bad-command"])
        self.assertFalse(ok)
        self.assertEqual(output, "failed")

    @patch("builder.lab_validator.subprocess.run")
    @patch("builder.lab_validator.shutil.which")
    def test_print_report_detects_online_device(self, which, run):
        which.side_effect = lambda tool: f"/usr/bin/{tool}"
        run.return_value.returncode = 0
        run.return_value.stdout = "List of devices attached\nTEST123\tdevice\n"
        run.return_value.stderr = ""
        self.assertTrue(lab_validator.print_report())

    @patch("builder.lab_validator.subprocess.run")
    @patch("builder.lab_validator.shutil.which")
    def test_print_report_rejects_offline_device(self, which, run):
        which.side_effect = lambda tool: f"/usr/bin/{tool}"
        run.return_value.returncode = 0
        run.return_value.stdout = "List of devices attached\nTEST123\toffline\n"
        run.return_value.stderr = ""
        self.assertFalse(lab_validator.print_report())


if __name__ == "__main__":
    unittest.main()
