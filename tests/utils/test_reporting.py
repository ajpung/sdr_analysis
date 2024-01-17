import os
import unittest
from pathlib import Path

from rats.utils.reporting import *


class TestReportingMethods(unittest.TestCase):
    # Test report generation
    def test_create_report(self):
        # Define file parameters
        filename = "demofile.pdf"
        html_path = ".//docs//report//report.html"
        out_path = filename
        path = Path(out_path)
        # If test report exists, delete report
        if os.path.exists(out_path):
            os.remove(out_path)
        # Create RAT report
        create_report(html_path, out_path)
        # Certify file exists
        assert path.is_file()
        # Remove file after assertion
        if os.path.exists(out_path):
            os.remove(out_path)
