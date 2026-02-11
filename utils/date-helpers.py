"""
══════════════════════════════════════════════════════════════════════════════
DATE HELPERS - CONTACT RATE COMMERCE
══════════════════════════════════════════════════════════════════════════════
Description: Date manipulation utilities for CR analysis
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

import calendar
from datetime import datetime, date


def generate_month_options(years_back=1):
    """Generate month options for date selection"""
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    options = []
    current_year = datetime.now().year
    
    for year in range(current_year - years_back, current_year + 1):
        for i, month_name in enumerate(month_names):
            month_num = i + 1
            options.append({
                'value': f'{year}-{month_num:02d}',
                'display': f'{month_name} {year}',
                'start_date': f'{year}-{month_num:02d}-01',
                'end_date': f'{year}-{month_num:02d}-{calendar.monthrange(year, month_num)[1]:02d}'
            })
    
    return options


def detect_complete_periods(start_date_str, end_date_str, date_format='month'):
    """
    Detect complete periods between dates
    
    Args:
        start_date_str: Start date (YYYY-MM-DD)
        end_date_str: End date (YYYY-MM-DD)
        date_format: 'month' or 'quarter'
    
    Returns:
        list: Complete periods detected
    """
    start = datetime.strptime(start_date_str, '%Y-%m-%d')
    end = datetime.strptime(end_date_str, '%Y-%m-%d')
    periods = []
    
    if date_format == 'month':
        current_date = start.replace(day=1)
        while current_date <= end:
            periods.append({
                'year': current_date.year,
                'month': current_date.month,
                'key': f"{current_date.year}-{current_date.month:02d}",
                'name': calendar.month_abbr[current_date.month],
                'full_name': f"{current_date.strftime('%B')} {current_date.year}"
            })
            # Next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    return periods
