import ast
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

class NpMeetingScheduleRewardCalculator(BaseRewardCalculator):
    @classmethod
    def extract_output(cls, response: str) -> dict:
        if "Answer:" not in response:
            return {"format": False, "answer": False, "str": "invalid answer: no 'Answer:' in answer"}
        
        schedule_str = response.split("Answer:")[-1].strip()

        try:
            # ast.literal_eval is safer than eval
            schedule = ast.literal_eval(schedule_str)
            if not isinstance(schedule, list):
                return {"format": True, "answer": False, "str": "Answer should be a list of tuples."}
            
            # Validate the structure of each item in the list
            for item in schedule:
                if not (isinstance(item, tuple) and len(item) == 3 and 
                        all(isinstance(i, int) for i in item)):
                    return {"format": True, "answer": False, "str": "Each item in the schedule must be a tuple of three integers."}

            return {"format": True, "answer": True, "str": str(schedule)}

        except (ValueError, SyntaxError):
            return {"format": True, "answer": False, "str": "Invalid list/tuple format in answer."}

    @classmethod
    def _calculate_score(cls, extracted_output: dict, identity: dict) -> float:
        format_reward = 1.0 if extracted_output.get('format', False) else -1.0
        
        if not extracted_output.get('answer', False):
            answer_reward = -1.5
            return format_reward + answer_reward
        
        meetings_data = identity["question"]["meetings"]
        attendee_availability = identity["question"]["attendee_availability"]
        rooms = identity["question"]["rooms"]
        
        try:
            schedule = ast.literal_eval(extracted_output["str"])
        except (ValueError, SyntaxError):
            return format_reward - 1.5

        # --- VALIDATION ---
        # 1. Check for valid IDs and room capacity
        scheduled_meetings = set()
        for meeting_id, room_id, start_time in schedule:
            if str(meeting_id) not in meetings_data or str(room_id) not in rooms:
                return format_reward - 1.5 # Invalid ID
            if len(meetings_data[str(meeting_id)]["attendees"]) > rooms[str(room_id)]:
                return format_reward - 1.5 # Exceeds capacity
            if meeting_id in scheduled_meetings:
                return format_reward - 1.5 # Duplicate meeting scheduled
            scheduled_meetings.add(meeting_id)

        # 2. Check for overlaps (room and attendee)
        room_schedules = {room_id: [] for room_id in rooms}
        attendee_schedules = {attendee_id: [] for attendee_id in attendee_availability}

        for meeting_id, room_id, start_time in schedule:
            duration = meetings_data[str(meeting_id)]["duration"]
            end_time = start_time + duration
            
            # Room overlap check
            for _, other_start, other_end in room_schedules[str(room_id)]:
                if start_time < other_end and end_time > other_start:
                    return format_reward - 1.5
            room_schedules[str(room_id)].append((meeting_id, start_time, end_time))

            # Attendee availability and overlap check
            for attendee_id in meetings_data[str(meeting_id)]["attendees"]:
                # Availability
                is_available = any(avail_start <= start_time and end_time <= avail_end 
                                   for avail_start, avail_end in attendee_availability[str(attendee_id)])
                if not is_available:
                    return format_reward - 1.5

                # Overlap with other meetings for this attendee
                for _, other_start, other_end in attendee_schedules[str(attendee_id)]:
                    if start_time < other_end and end_time > other_start:
                        return format_reward - 1.5
                attendee_schedules[str(attendee_id)].append((meeting_id, start_time, end_time))

        # --- SCORING ---
        total_attendees_scheduled = sum(len(meetings_data[str(m_id)]["attendees"]) for m_id, _, _ in schedule)
        
        ground_truth = identity.get("ground_truth")
        if ground_truth is not None and ground_truth > 0:
            answer_reward = total_attendees_scheduled / ground_truth
        elif ground_truth == 0:
            answer_reward = 1.0 if total_attendees_scheduled == 0 else 0.0
        else:
            answer_reward = 0.0

        return format_reward + answer_reward

    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict) -> float:
        return cls._calculate_score(extracted_output, identity)
