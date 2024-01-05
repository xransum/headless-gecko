"""Tests for headless_geckodriver.py."""
import unittest

import headless_geckodriver


class TestHeadlessGeckodriver(unittest.TestCase):
    """Tests for headless_geckodriver.py."""

    def test_headless_geckodriver(self):
        """Test headless_geckodriver imported."""
        self.assertTrue(headless_geckodriver)
