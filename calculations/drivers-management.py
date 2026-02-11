"""
══════════════════════════════════════════════════════════════════════════════
DRIVERS MANAGEMENT - CONTACT RATE COMMERCE
══════════════════════════════════════════════════════════════════════════════
Description: Management and validation of driver values for CR calculation
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
from typing import Dict, List, Optional


# ══════════════════════════════════════════════════════════════════════════════
# DRIVERS MANAGER CLASS
# ══════════════════════════════════════════════════════════════════════════════

class DriversManager:
    """
    Manage driver values for CR calculation
    
    Structure:
        {
            'MLA': {
                '2026-01': 1500000,
                '2026-02': 1600000
            },
            'MLB': {
                '2026-01': 5000000,
                '2026-02': 5200000
            }
        }
    """
    
    def __init__(self):
        self.drivers_by_site = {}
    
    def get_driver(self, site: str, period: str) -> Optional[float]:
        """Get driver value for site and period"""
        return self.drivers_by_site.get(site, {}).get(period, None)
    
    def set_driver(self, site: str, period: str, value: float) -> None:
        """Set driver value for site and period"""
        if site not in self.drivers_by_site:
            self.drivers_by_site[site] = {}
        self.drivers_by_site[site][period] = value
    
    def get_all_drivers(self) -> Dict:
        """Get all configured drivers"""
        return self.drivers_by_site.copy()
    
    def clear_drivers(self) -> None:
        """Clear all configured drivers"""
        self.drivers_by_site.clear()
    
    def validate_drivers(self, required_sites: List[str], required_periods: List[str]) -> Dict:
        """
        Validate that all required drivers are configured
        
        Returns:
            dict: Validation summary with missing drivers
        """
        missing = []
        
        for site in required_sites:
            for period in required_periods:
                driver = self.get_driver(site, period)
                if driver is None or driver <= 0:
                    missing.append({'site': site, 'period': period})
        
        return {
            'is_valid': len(missing) == 0,
            'missing_count': len(missing),
            'missing_drivers': missing
        }


# REFERENCES:
# - Contact Rate calc: /calculations/contact-rate.py
# - Business context: /docs/business-context.md
"""
