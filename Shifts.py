import calendar
from collections import defaultdict
from datetime import datetime, timedelta
import random
import csv
import os


def normalize_date_format(date_str):
    """Convert different date formats to unified YYYY-MM-DD format"""
    if not date_str or not date_str.strip():
        return ""

    date_str = date_str.strip()

    # If already in correct format
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            pass

    # Try different formats
    formats_to_try = [
        "%m/%d/%Y",  # MM/DD/YYYY
        "%d/%m/%Y",  # DD/MM/YYYY
        "%Y/%m/%d",  # YYYY/MM/DD
        "%m-%d-%Y",  # MM-DD-YYYY
        "%d-%m-%Y",  # DD-MM-YYYY
        "%Y-%m-%d",  # YYYY-MM-DD
        "%m/%d/%y",  # MM/DD/YY
        "%d/%m/%y",  # DD/MM/YY
    ]

    for fmt in formats_to_try:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue

    print(f"⚠️  Could not parse date: {date_str}")
    return date_str  # Return original if parsing failed


def get_month_year():
    """Get month and year from user"""
    while True:
        try:
            year = int(input("Enter year (e.g., 2025): "))
            month = int(input("Enter month (1-12): "))
            if 1 <= month <= 12:
                return year, month
            else:
                print("Month must be between 1 and 12")
        except ValueError:
            print("Please enter valid numbers")


def save_configuration_csv(participants, participant_constraints, users_with_fewer_shifts, filename):
    """Save configuration to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['name', 'weekday_blocks', 'date_blocks', 'fewer_shifts'])

            # Data for each participant
            for participant in participants:
                weekday_blocks, date_blocks = participant_constraints[participant]

                # Convert lists to semicolon-separated strings
                weekday_str = ';'.join(map(str, weekday_blocks)) if weekday_blocks else ''

                # Save dates in protected format (with apostrophe at start to prevent auto-conversion)
                if date_blocks:
                    protected_dates = [f"'{date}" for date in date_blocks]
                    date_str = ';'.join(protected_dates)
                else:
                    date_str = ''

                fewer_shifts = 'YES' if participant in users_with_fewer_shifts else 'NO'

                writer.writerow([participant, weekday_str, date_str, fewer_shifts])

        print(f"✓ Configuration saved to file: {filename}")
        print("💡 Tip: If you open the file in Excel, dates are protected from auto-conversion")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False


def load_configuration_csv(filename):
    """Load configuration from CSV file"""
    try:
        participants = []
        participant_constraints = {}
        users_with_fewer_shifts = []

        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row['name'].strip()
                participants.append(name)

                # Parse weekday_blocks
                weekday_str = row['weekday_blocks'].strip()
                weekday_blocks = []
                if weekday_str:
                    try:
                        weekday_blocks = [int(x.strip()) for x in weekday_str.split(';') if x.strip()]
                    except ValueError as e:
                        print(f"⚠️  Error parsing weekdays for {name}: {e}")

                # Parse date_blocks with different format handling
                date_str = row['date_blocks'].strip()
                date_blocks = []
                if date_str:
                    raw_dates = [x.strip() for x in date_str.split(';') if x.strip()]
                    for raw_date in raw_dates:
                        # Remove protective apostrophe if exists
                        if raw_date.startswith("'"):
                            raw_date = raw_date[1:]

                        # Normalize the date
                        normalized_date = normalize_date_format(raw_date)
                        if normalized_date and normalized_date not in date_blocks:
                            date_blocks.append(normalized_date)

                participant_constraints[name] = (weekday_blocks, date_blocks)

                # Check fewer_shifts
                if row['fewer_shifts'].strip().upper() == 'YES':
                    users_with_fewer_shifts.append(name)

        print(f"✓ Configuration loaded from file: {filename}")

        # Display loaded dates to verify they are correct
        print("\n📅 Loaded dates:")
        for name, (_, date_blocks) in participant_constraints.items():
            if date_blocks:
                print(f"  {name}: {', '.join(date_blocks[:3])}{'...' if len(date_blocks) > 3 else ''}")

        return participants, participant_constraints, users_with_fewer_shifts

    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return None, None, None
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None, None, None


def list_config_files():
    """Display list of available configuration files"""
    config_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if config_files:
        print("\nAvailable configuration files:")
        for i, filename in enumerate(config_files, 1):
            print(f"{i}. {filename}")
        return config_files
    else:
        print("No configuration files found in directory")
        return []


def choose_config_source():
    """Choose configuration source - new or from file"""
    print("\n=== Configuration Source ===")
    print("1. New configuration")
    print("2. Load from existing file")

    while True:
        choice = input("Choose option (1/2): ").strip()
        if choice == '1':
            return 'new'
        elif choice == '2':
            return 'load'
        else:
            print("Invalid choice")


def get_participants():
    """Get list of participants"""
    participants = []
    print("\nEnter participant names (type 'done' to finish):")
    while True:
        name = input("Participant name: ").strip()
        if name.lower() == 'done':
            break
        if name and name not in participants:
            participants.append(name)
        elif name in participants:
            print("Name already exists in list")

    if len(participants) < 2:
        print("Must have at least 2 participants")
        return get_participants()

    return participants


def get_date_input(prompt):
    """Get date from user"""
    while True:
        try:
            date_str = input(f"{prompt} (format: YYYY-MM-DD): ")
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")


def get_weekday_constraints():
    """Get weekday constraints"""
    weekdays = {
        '1': (6, 'Sunday'),
        '2': (0, 'Monday'),
        '3': (1, 'Tuesday'),
        '4': (2, 'Wednesday'),
        '5': (3, 'Thursday')
    }

    print("Select weekdays for constraint:")
    for key, (_, name) in weekdays.items():
        print(f"{key}. {name}")

    blocked_weekdays = []
    while True:
        choice = input("Enter day number (or 'done' to finish): ").strip()
        if choice.lower() == 'done':
            break
        if choice in weekdays:
            weekday_num, weekday_name = weekdays[choice]
            if weekday_num not in blocked_weekdays:
                blocked_weekdays.append(weekday_num)
                print(f"Added {weekday_name}")
            else:
                print("Day already selected")
        else:
            print("Invalid choice")

    return blocked_weekdays


def get_date_range():
    """Get date range"""
    print("Enter date range:")
    start_date = get_date_input("Start date")
    end_date = get_date_input("End date")

    # Create list of dates in range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if start > end:
        print("Start date must be before end date")
        return get_date_range()

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates


def get_participant_constraints(name):
    """Get constraints for participant"""
    print(f"\nSetting constraints for {name}:")
    print("1. Fixed weekday constraint")
    print("2. Date range constraint")
    print("3. Specific date constraint")
    print("4. No constraints")

    weekday_blocks = []
    date_blocks = []

    while True:
        choice = input("Choose constraint type (or 'done' to finish): ").strip()

        if choice.lower() == 'done':
            break
        elif choice == '1':
            weekdays = get_weekday_constraints()
            weekday_blocks.extend(weekdays)
        elif choice == '2':
            dates = get_date_range()
            date_blocks.extend(dates)
        elif choice == '3':
            date = get_date_input("Enter date")
            if date not in date_blocks:
                date_blocks.append(date)
        elif choice == '4':
            break
        else:
            print("Invalid choice")

    return weekday_blocks, date_blocks


def get_fewer_shifts_users(participants):
    """Select participants who will get fewer shifts"""
    print(f"\nWould you like to select up to 2 participants who will get fewer shifts?")
    print("Available participants:")
    for i, name in enumerate(participants, 1):
        print(f"{i}. {name}")

    choice = input("Yes/No: ").strip().lower()
    if choice not in ['yes', 'y']:
        return []

    selected = []
    while len(selected) < 2:
        try:
            choice = input(f"Select participant number (or 'done' to finish): ").strip()
            if choice.lower() == 'done':
                break

            idx = int(choice) - 1
            if 0 <= idx < len(participants):
                name = participants[idx]
                if name not in selected:
                    selected.append(name)
                    print(f"Selected: {name}")
                else:
                    print("Participant already selected")
            else:
                print("Invalid number")
        except ValueError:
            print("Enter valid number")

    return selected


def get_excluded_days(year, month):
    """Get additional days to exclude (holidays)"""
    print(f"\nAre there additional days in {month}/{year} to exclude from scheduling?")
    choice = input("Yes/No: ").strip().lower()

    if choice not in ['yes', 'y']:
        return []

    excluded = []
    print("Enter dates to exclude (type 'done' to finish):")
    while True:
        date_input = input("Date (YYYY-MM-DD) or 'done': ").strip()
        if date_input.lower() == 'done':
            break

        try:
            # Check that date is valid and in correct month
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
            if date_obj.year == year and date_obj.month == month:
                if date_input not in excluded:
                    excluded.append(date_input)
                    print(f"Added: {date_input}")
                else:
                    print("Date already added")
            else:
                print(f"Date must be in {month}/{year}")
        except ValueError:
            print("Invalid date format")

    return excluded


def get_week_number(date_str):
    """Get week number of date"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.isocalendar()[1]


def is_consecutive_days(date1, date2):
    """Check if two dates are consecutive days"""
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return abs((d2 - d1).days) == 1


def calculate_target_shifts(total_shifts, participants, users_with_fewer_shifts):
    """Calculate target shifts for each participant according to new rules"""
    num_participants = len(participants)
    base_shifts = total_shifts // num_participants
    remainder = total_shifts % num_participants

    target_shifts = {participant: base_shifts for participant in participants}

    # If there's remainder, need to reduce shifts from some participants
    if remainder > 0:
        # Number of participants who will get extra shift
        participants_with_extra = num_participants - remainder

        # List of candidates for shift reduction (in priority order)
        reduction_candidates = []

        # First the people selected for fewer shifts
        for user in users_with_fewer_shifts:
            if user in participants:
                reduction_candidates.append(user)

        # Then other participants randomly
        remaining_participants = [p for p in participants if p not in users_with_fewer_shifts]
        random.shuffle(remaining_participants)
        reduction_candidates.extend(remaining_participants)

        # Reduce shift from first candidates
        for i in range(participants_with_extra):
            if i < len(reduction_candidates):
                target_shifts[reduction_candidates[i]] -= 1

    return target_shifts


def analyze_day_constraints(day, participants, participant_constraints):
    """Analyze constraints for specific day"""
    date_obj = datetime.strptime(day, "%Y-%m-%d")
    weekday = date_obj.weekday()

    blocked_users = []
    available_users = []

    for participant in participants:
        weekday_blocks, date_blocks = participant_constraints[participant]

        is_blocked = False
        block_reasons = []

        # Check weekday constraint
        if weekday in weekday_blocks:
            is_blocked = True
            weekday_names = {6: 'Sunday', 0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday'}
            block_reasons.append(f"{weekday_names.get(weekday, weekday)}")

        # Check specific date constraint
        if day in date_blocks:
            is_blocked = True
            block_reasons.append("specific date")

        if is_blocked:
            blocked_users.append((participant, block_reasons))
        else:
            available_users.append(participant)

    return available_users, blocked_users


def generate_shifts_constraint(year, month, participants, participant_constraints,
                               users_with_fewer_shifts, excluded_days):
    """Generate shift assignments with constraints"""

    num_days = calendar.monthrange(year, month)[1]
    valid_weekdays = [6, 0, 1, 2, 3]  # Sunday to Thursday

    # Create list of valid shift days
    shift_days = []
    for d in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{d:02d}"
        weekday = calendar.weekday(year, month, d)

        if weekday in valid_weekdays and date_str not in excluded_days:
            shift_days.append(date_str)

    if not shift_days:
        print("No valid shift days in this month!")
        return {}, {}, []

    total_shifts = len(shift_days)

    # Calculate target shifts according to new rules
    target_shifts = calculate_target_shifts(total_shifts, participants, users_with_fewer_shifts)

    # Map constraints for each day
    day_to_blocked_users = {}
    constraint_warnings = []

    for day in shift_days:
        available_users, blocked_users = analyze_day_constraints(day, participants, participant_constraints)
        day_to_blocked_users[day] = set(user for user, _ in blocked_users)

        # Check if all participants are blocked
        if len(available_users) == 0:
            day_name = datetime.strptime(day, "%Y-%m-%d").strftime("%A")

            warning = f"⚠️  {day} ({day_name}): All participants are blocked!"
            for user, reasons in blocked_users:
                warning += f"\n    {user}: {', '.join(reasons)}"
            constraint_warnings.append(warning)

    # Sort days by constraint level (most constrained first)
    sorted_shift_days = sorted(shift_days,
                               key=lambda d: len(day_to_blocked_users[d]),
                               reverse=True)

    # Assign shifts
    shifts = defaultdict(list)
    assigned_count = defaultdict(int)

    for day in sorted_shift_days:
        blocked = day_to_blocked_users[day]

        # Available participants (not blocked and haven't exceeded target)
        available = []
        for participant in participants:
            if (participant not in blocked and
                    assigned_count[participant] < target_shifts[participant]):

                # Check week constraint - not same week
                week_conflict = False
                current_week = get_week_number(day)
                for assigned_day in shifts[participant]:
                    if get_week_number(assigned_day) == current_week:
                        week_conflict = True
                        break

                # Check consecutive days constraint
                consecutive_conflict = False
                for assigned_day in shifts[participant]:
                    if is_consecutive_days(day, assigned_day):
                        consecutive_conflict = True
                        break

                if not week_conflict and not consecutive_conflict:
                    available.append(participant)

        # If no available with new constraints, try without week constraint
        if not available:
            for participant in participants:
                if (participant not in blocked and
                        assigned_count[participant] < target_shifts[participant]):

                    # Only consecutive days check
                    consecutive_conflict = False
                    for assigned_day in shifts[participant]:
                        if is_consecutive_days(day, assigned_day):
                            consecutive_conflict = True
                            break

                    if not consecutive_conflict:
                        available.append(participant)

        # If still no available, allow one extra shift
        if not available:
            for participant in participants:
                if (participant not in blocked and
                        assigned_count[participant] < target_shifts[participant] + 1):

                    # Only consecutive days check
                    consecutive_conflict = False
                    for assigned_day in shifts[participant]:
                        if is_consecutive_days(day, assigned_day):
                            consecutive_conflict = True
                            break

                    if not consecutive_conflict:
                        available.append(participant)

        # If still no available, take anyone not blocked and not consecutive
        if not available:
            for participant in participants:
                if participant not in blocked:
                    consecutive_conflict = False
                    for assigned_day in shifts[participant]:
                        if is_consecutive_days(day, assigned_day):
                            consecutive_conflict = True
                            break

                    if not consecutive_conflict:
                        available.append(participant)

        # If still no available, take anyone not blocked (extreme case)
        if not available:
            available = [p for p in participants if p not in blocked]

        if not available:
            shifts["Cannot assign"].append(day)
            continue

        # Choose participant with fewest shifts
        min_assigned = min(assigned_count[p] for p in available)
        candidates = [p for p in available if assigned_count[p] == min_assigned]

        chosen = random.choice(candidates)
        shifts[chosen].append(day)
        assigned_count[chosen] += 1

    return shifts, target_shifts, constraint_warnings


def display_loaded_config(participants, participant_constraints, users_with_fewer_shifts):
    """Display loaded configuration"""
    print("\n=== Loaded Configuration ===")
    print(f"Participants: {', '.join(participants)}")

    print("\nConstraints:")
    weekday_names = {6: 'Sunday', 0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday'}

    for name, (weekday_blocks, date_blocks) in participant_constraints.items():
        constraints = []
        if weekday_blocks:
            weekday_names_list = [weekday_names.get(w, str(w)) for w in weekday_blocks]
            constraints.append(f"weekdays: {', '.join(weekday_names_list)}")
        if date_blocks:
            constraints.append(f"dates: {', '.join(date_blocks[:3])}{'...' if len(date_blocks) > 3 else ''}")

        if constraints:
            print(f"  {name}: {' | '.join(constraints)}")
        else:
            print(f"  {name}: no constraints")

    if users_with_fewer_shifts:
        print(f"\nParticipants with fewer shifts: {', '.join(users_with_fewer_shifts)}")


def main():
    print("=== Shift Scheduling System ===\n")

    # Get month and year
    year, month = get_month_year()

    # Choose configuration source
    config_source = choose_config_source()

    if config_source == 'load':
        # Load from file
        config_files = list_config_files()
        if not config_files:
            print("No configuration files available. Switching to new configuration...")
            config_source = 'new'
        else:
            while True:
                try:
                    choice = input("Select file number or enter filename: ").strip()

                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(config_files):
                            filename = config_files[idx]
                            break
                    else:
                        if not choice.endswith('.csv'):
                            choice += '.csv'
                        if os.path.exists(choice):
                            filename = choice
                            break
                        else:
                            print(f"File {choice} not found")
                            continue

                    print("Invalid choice")
                except ValueError:
                    print("Enter valid number or filename")

            participants, participant_constraints, users_with_fewer_shifts = load_configuration_csv(filename)

            if participants is None:
                print("Switching to new configuration...")
                config_source = 'new'
            else:
                display_loaded_config(participants, participant_constraints, users_with_fewer_shifts)

    if config_source == 'new':
        # New configuration
        participants = get_participants()

        # Get constraints for each participant
        participant_constraints = {}
        for participant in participants:
            weekday_blocks, date_blocks = get_participant_constraints(participant)
            participant_constraints[participant] = (weekday_blocks, date_blocks)

        # Select participants with fewer shifts
        users_with_fewer_shifts = get_fewer_shifts_users(participants)

        # Ask about saving configuration
        save_choice = input("\nWould you like to save the configuration to a file? (yes/no): ").strip().lower()
        if save_choice in ['yes', 'y']:
            filename = input("Enter filename (without extension): ").strip()
            if not filename.endswith('.csv'):
                filename += '.csv'
            save_configuration_csv(participants, participant_constraints, users_with_fewer_shifts, filename)

    # Get additional excluded days (always asked as it depends on month/year)
    excluded_days = get_excluded_days(year, month)

    # Generate shift assignments
    print("\n=== Calculating shift assignments... ===")
    shifts, target_shifts, constraint_warnings = generate_shifts_constraint(
        year, month, participants, participant_constraints,
        users_with_fewer_shifts, excluded_days
    )

    # Display constraint warnings
    if constraint_warnings:
        print("\n🚨 Constraint Warnings:")
        print("=" * 50)
        for warning in constraint_warnings:
            print(warning)
        print("=" * 50)

    # Display results
    print(f"\n=== Shift Schedule for {month}/{year} ===")

    # List of shifts sorted by date
    all_shifts = []
    for participant, days in shifts.items():
        for day in days:
            all_shifts.append((day, participant))

    all_shifts.sort(key=lambda x: x[0])

    print("\nShift Schedule:")
    print("-" * 40)
    for day, participant in all_shifts:
        try:
            day_name = datetime.strptime(day, "%Y-%m-%d").strftime("%A")
            week_num = get_week_number(day)
            print(f"{day} ({day_name}, week {week_num}): {participant}")
        except:
            print(f"{day}: {participant}")

    print(f"\nShifts per participant:")
    print("-" * 25)
    for participant in participants:
        actual = len(shifts.get(participant, []))
        print(f"{participant}: {actual}")

    total_assigned = sum(len(days) for days in shifts.values() if days != ["Cannot assign"])
    print(f"\nTotal shifts assigned: {total_assigned}")

    # Check for problems
    if "Cannot assign" in shifts:
        print(f"\n⚠️  Days that could not be assigned:")
        for day in shifts["Cannot assign"]:
            print(f"  - {day}")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")