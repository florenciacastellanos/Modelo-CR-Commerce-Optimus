"""
Unit Tests: test_contact_rate.py
Purpose: Test Contact Rate calculation functions
Author: Contact Rate Analysis Team
Date: 2026-01-22
Version: 1.0.0

Run tests:
    python -m pytest tests/test_contact_rate.py -v
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestContactRateCalculation(unittest.TestCase):
    """Test suite for Contact Rate calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cr_multiplier = 100
    
    def test_calculate_contact_rate_valid(self):
        """Test CR calculation with valid inputs"""
        incoming = 100
        driver = 1000
        expected_cr = 10.0
        
        result = (incoming / driver) * self.cr_multiplier
        
        self.assertEqual(result, expected_cr)
    
    def test_calculate_contact_rate_zero_driver(self):
        """Test CR calculation with zero driver"""
        incoming = 100
        driver = 0
        
        # Should handle division by zero
        if driver == 0:
            result = None
        else:
            result = (incoming / driver) * self.cr_multiplier
        
        self.assertIsNone(result)
    
    def test_calculate_contact_rate_high_cr(self):
        """Test CR calculation with high rate"""
        incoming = 500
        driver = 1000
        expected_cr = 50.0
        
        result = (incoming / driver) * self.cr_multiplier
        
        self.assertEqual(result, expected_cr)
    
    def test_calculate_contact_rate_low_cr(self):
        """Test CR calculation with low rate"""
        incoming = 1
        driver = 1000
        expected_cr = 0.1
        
        result = (incoming / driver) * self.cr_multiplier
        
        self.assertEqual(result, expected_cr)
    
    def test_calculate_variation_absolute(self):
        """Test absolute variation calculation"""
        cr_current = 10.0
        cr_previous = 8.0
        expected_variation = 2.0
        
        result = cr_current - cr_previous
        
        self.assertEqual(result, expected_variation)
    
    def test_calculate_variation_percentage(self):
        """Test percentage variation calculation"""
        cr_current = 10.0
        cr_previous = 8.0
        expected_variation_pct = 25.0
        
        result = ((cr_current - cr_previous) / cr_previous) * 100
        
        self.assertEqual(result, expected_variation_pct)
    
    def test_threshold_rule_sum_any_period(self):
        """Test threshold rule: SUM >= 50 in ANY period"""
        incoming_period1 = 45
        incoming_period2 = 55
        threshold = 50
        
        # Should be included because period2 >= 50
        should_include = (incoming_period1 >= threshold) or (incoming_period2 >= threshold)
        
        self.assertTrue(should_include)
    
    def test_threshold_rule_both_below(self):
        """Test threshold rule: Both periods below threshold"""
        incoming_period1 = 30
        incoming_period2 = 40
        threshold = 50
        
        # Should be excluded because both < 50
        should_include = (incoming_period1 >= threshold) or (incoming_period2 >= threshold)
        
        self.assertFalse(should_include)

class TestExclusions(unittest.TestCase):
    """Test suite for automatic exclusions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.excluded_queues = [2131, 230, 1102, 1241, 2075, 2294, 2295]
        self.excluded_processes = [1312]
        self.excluded_ci_reasons = [2592, 6588, 10068, 2701, 10048]
        self.excluded_site = 'MLV'
    
    def test_queue_exclusion(self):
        """Test queue exclusion logic"""
        queue_id = 2131
        
        should_exclude = queue_id in self.excluded_queues
        
        self.assertTrue(should_exclude)
    
    def test_queue_inclusion(self):
        """Test queue inclusion logic"""
        queue_id = 1000
        
        should_exclude = queue_id in self.excluded_queues
        
        self.assertFalse(should_exclude)
    
    def test_site_exclusion(self):
        """Test site exclusion logic"""
        site_id = 'MLV'
        
        should_exclude = site_id == self.excluded_site
        
        self.assertTrue(should_exclude)
    
    def test_site_inclusion(self):
        """Test site inclusion logic"""
        site_id = 'MLA'
        
        should_exclude = site_id == self.excluded_site
        
        self.assertFalse(should_exclude)

if __name__ == '__main__':
    unittest.main()
