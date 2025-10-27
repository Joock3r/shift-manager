# Shift Scheduling System

A Python-based shift scheduling system that automatically assigns work shifts to team members while respecting various constraints and ensuring fair distribution.

## Features

- **Automatic Shift Assignment**: Distributes shifts fairly among participants
- **Flexible Constraints**: Support for weekday blocks, date ranges, and specific date exclusions
- **CSV Configuration**: Save and load team configurations for reuse
- **Conflict Prevention**: Prevents consecutive shifts and multiple shifts in the same week
- **Holiday Support**: Exclude specific dates (holidays, company events, etc.)
- **Fair Distribution**: Ensures balanced workload with option for some participants to have fewer shifts

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only built-in Python libraries)

## Installation

1. Clone this repository:
bash
git clone https://github.com/yourusername/shift-scheduling-system.git
cd shift-scheduling-system

## Running

python shift_scheduler.py

## Usage
1. Quick Start
2. Run the program
3. Enter the year and month for scheduling
4. Choose "New configuration" for first-time setup
5. Enter participant names
6. Set constraints for each participant (optional)
7. Select participants who should get fewer shifts (optional)
8. Add any excluded dates (holidays, etc.)
9. Review the generated schedule

## Configuration Options
The system supports two main workflows:
1. New Configuration
Enter all settings manually
Option to save configuration to CSV file for future use

2. Load from CSV
Load previously saved team configuration
Only need to specify month/year and excluded dates

CSV file Structure
The CSV file should have the following columns:
Column	Description	Format	Example
name	Participant name	Text	John Smith
weekday_blocks	Blocked weekdays	Numbers separated by ;	6;0;3
date_blocks	Blocked specific dates	Dates separated by ;	'2025-01-15;'2025-01-20
fewer_shifts	Should get fewer shifts	YES or NO	NO

Weekday Numbers
6 = Sunday
0 = Monday
1 = Tuesday
2 = Wednesday
3 = Thursday
Note: Only Sunday-Thursday are valid work days

Date Format
Use YYYY-MM-DD format
Prefix dates with ' (apostrophe) to prevent Excel auto-formatting
Separate multiple dates with ; (semicolon)

## Example
name,weekday_blocks,date_blocks,fewer_shifts
John Smith,6;0,'2025-01-15;'2025-01-20;'2025-01-25,NO
Jane Doe,,'2025-01-10;'2025-01-22,YES
Mike Johnson,1;3,'2025-01-05,NO
Sarah Wilson,6,,NO
Tom Brown,,'2025-01-12;'2025-01-13;'2025-01-14,YES
