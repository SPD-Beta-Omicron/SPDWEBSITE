from datetime import datetime, timedelta
import pytz

def get_next_dst_change():
    """Get the next Daylight Saving Time transition date."""
    tz = pytz.timezone('America/Chicago')
    now = datetime.now(tz)
    current_year = now.year
    
    transitions = []
    
    # Calculate DST transitions for current and next year
    for year in [current_year, current_year + 1]:
        # Spring forward: 2nd Sunday in March at 2 AM
        spring = datetime(year, 3, 8, 2, 0)
        spring += timedelta(days=(6 - spring.weekday()) % 7)
        spring = tz.localize(spring)
        
        # Fall back: 1st Sunday in November at 2 AM
        fall = datetime(year, 11, 1, 2, 0)
        fall += timedelta(days=(6 - fall.weekday()) % 7)
        fall = tz.localize(fall, is_dst=True)  # Before falling back
        
        transitions.extend([spring, fall])
    
    # Return next future transition
    future_transitions = [t for t in transitions if t > now]
    return min(future_transitions) if future_transitions else None