## Description

Given a set of meetings, each with a required set of attendees, their availability times, and available meeting rooms with capacities, the Meeting Scheduling Problem (MSP) with the objective of maximizing attendee participation aims to find a schedule that avoids conflicts and maximizes the total number of attendees across all scheduled meetings. If a meeting cannot be scheduled due to constraints, it should be omitted from the schedule.

## Submission Format

The answer should be a list of tuples, where each tuple represents a scheduled meeting. Each tuple should contain: (meeting_id, room_id, start_time). The meetings should be ordered by start time. If no meetings can be scheduled, return an empty list.

## Example Input
```
meetings = {
0: {"attendees": [0, 1, 2], "duration": 60}, # Meeting ID 0, requires attendees 0, 1, and 2, duration 60 minutes
1: {"attendees": [1, 3], "duration": 30}, # Meeting ID 1, requires attendees 1 and 3, duration 30 minutes
2: {"attendees": [0, 2, 3], "duration": 90} # Meeting ID 2, requires attendees 0, 2, and 3, duration 90 minutes
}

attendee_availability = {
0: [(900, 1700)], # Attendee 0 is available from 9:00 to 17:00 (represented as minutes from midnight)
1: [(900, 1200), (1300, 1700)], # Attendee 1 is available from 9:00 to 12:00 and 13:00 to 17:00
2: [(900, 1700)], # Attendee 2 is available from 9:00 to 17:00
3: [(1000, 1400)] # Attendee 3 is available from 10:00 to 14:00
}

rooms = {
0: 5, # Room 0 has a capacity of 5
1: 3 # Room 1 has a capacity of 3
}
```

## Example Output
```
Answer: [(0, 0, 900), (1, 1, 1000), (2, 0, 1020)] 
# Example solution maximizing attendees. Meeting 0 (3 attendees), Meeting 1 (2 attendees), Meeting 2 (3 attendees) = 8 total attendees. Times adjusted slightly to fit and demonstrate potential output format. This is one possible optimal solution; others may exist.
```
