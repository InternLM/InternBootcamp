import random
import time
from collections import defaultdict
from typing import Dict, Any, Optional, List, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.NP.prompt_md import extract_markdown_content_NP, get_prompt

class MeetingSchedulerSolver:
    def __init__(self, meetings, attendee_availability, rooms, timeout=60):
        self.meetings = {int(k): v for k, v in meetings.items()}
        self.attendee_availability = {int(k): v for k, v in attendee_availability.items()}
        self.rooms = {int(k): v for k, v in rooms.items()}
        self.timeout = timeout
        self.start_time = None
        self.best_schedule = []
        self.best_score = 0

    @staticmethod
    def _is_overlapping(start1, end1, start2, end2):
        return max(start1, start2) < min(end1, end2)

    def _get_attendee_free_slots(self, attendees, duration):
        if not attendees: return []
        
        attendees_int = [int(a) for a in attendees]
        common_slots = self.attendee_availability.get(attendees_int[0], [])
        
        for attendee_id in attendees_int[1:]:
            next_slots = self.attendee_availability.get(attendee_id, [])
            intersected_slots, i, j = [], 0, 0
            while i < len(common_slots) and j < len(next_slots):
                s1, e1 = common_slots[i]
                s2, e2 = next_slots[j]
                overlap_s, overlap_e = max(s1, s2), min(e1, e2)
                if overlap_s < overlap_e:
                    intersected_slots.append((overlap_s, overlap_e))
                if e1 < e2: i += 1
                else: j += 1
            common_slots = intersected_slots
        return [(s, e) for s, e in common_slots if e - s >= duration]

    def _construct_schedule(self):
        current_schedule, unscheduled_meetings = [], list(self.meetings.keys())
        room_bookings, attendee_bookings = defaultdict(list), defaultdict(list)
        
        while unscheduled_meetings:
            candidate_placements = []
            for meeting_id in unscheduled_meetings:
                meeting = self.meetings[meeting_id]
                attendees, duration, num_attendees = meeting['attendees'], meeting['duration'], len(meeting['attendees'])
                suitable_rooms = [r_id for r_id, cap in self.rooms.items() if cap >= num_attendees]
                common_slots = self._get_attendee_free_slots(attendees, duration)
                
                placement_found = False
                for room_id in suitable_rooms:
                    for slot_start, slot_end in common_slots:
                        time = slot_start
                        while time + duration <= slot_end:
                            end_time = time + duration
                            room_conflict = any(self._is_overlapping(time, end_time, s, e) for s, e in room_bookings.get(room_id, []))
                            if room_conflict: time += 1; continue
                            
                            attendee_conflict = any(self._is_overlapping(time, end_time, s, e) for att in attendees for s, e in attendee_bookings.get(att, []))
                            if not attendee_conflict:
                                score = num_attendees / duration if duration > 0 else num_attendees
                                candidate_placements.append({"meeting_id": meeting_id, "room_id": room_id, "start_time": time, "score": score})
                                placement_found = True
                                break
                            time += 1
                        if placement_found: break
                    if placement_found: break

            if not candidate_placements: break
            
            candidate_placements.sort(key=lambda x: x['score'], reverse=True)
            max_score = candidate_placements[0]['score']
            rcl = [p for p in candidate_placements if p['score'] >= max_score * 0.8]
            chosen = random.choice(rcl)
            
            m_id, r_id, s_time = chosen['meeting_id'], chosen['room_id'], chosen['start_time']
            e_time = s_time + self.meetings[m_id]['duration']
            
            current_schedule.append((m_id, r_id, s_time))
            room_bookings[r_id].append((s_time, e_time))
            for att in self.meetings[m_id]['attendees']: attendee_bookings[att].append((s_time, e_time))
            unscheduled_meetings.remove(m_id)
        return current_schedule

    def solve(self):
        self.start_time = time.time()
        # A simplified single-pass GRASP-like approach for efficiency in generation
        schedule = self._construct_schedule()
        score = sum(len(self.meetings[m_id]['attendees']) for m_id, _, _ in schedule)
        
        if score > self.best_score:
            self.best_score = score
            self.best_schedule = schedule
            
        return sorted(self.best_schedule, key=lambda x: x[2]), self.best_score


class NpMeetingScheduleInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "meeting-schedule"
        self.params = kwargs

    def case_generator(self) -> Dict[str, Any]:
        p = self.params
        num_meetings = random.randint(*p["num_meetings"])
        num_attendees = random.randint(*p["num_attendees"])
        num_rooms = random.randint(*p["num_rooms"])

        meetings = {str(i): {"attendees": sorted(random.sample(range(num_attendees), k=random.randint(2, min(num_attendees, p["max_attendees_per_meeting"])))), "duration": random.choice(p["durations"])} for i in range(num_meetings)}
        
        availability = {}
        for i in range(num_attendees):
            if random.random() > p["fragmented_availability_chance"]:
                availability[str(i)] = [(p["time_window"][0], p["time_window"][1])]
            else:
                availability[str(i)] = [(p["time_window"][0], p["lunch_time"][0]), (p["lunch_time"][1], p["time_window"][1])]
        
        rooms = {str(i): random.randint(*p["capacity_range"]) for i in range(num_rooms)}
        
        problem = {"meetings": meetings, "attendee_availability": availability, "rooms": rooms}
        
        solver = MeetingSchedulerSolver(meetings, availability, rooms, timeout=5)
        _, ground_truth = solver.solve()

        return {"difficulty": self.difficulty, "question": problem, "ground_truth": ground_truth}

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        md_file = "internbootcamp/bootcamps/NP/meeting_schedule/meeting-schedule.md"
        task_info = extract_markdown_content_NP(md_file)
        
        q = identity["question"]
        question_str = f"meetings = {q['meetings']}\n\nattendee_availability = {q['attendee_availability']}\n\nrooms = {q['rooms']}"
            
        prompt = get_prompt(self.task_type, task_info, question_str)
        return prompt

if __name__ == "__main__":
    generator = NpMeetingScheduleInstructionGenerator(difficulty="easy")
    identity = generator.case_generator()
    print("Generated Identity:")
    print(identity)
    prompt = generator.prompt_func(identity)
    print("\nGenerated Prompt:")
    print(prompt)
