"""### 谜题描述
1.Each puzzle contains a number of elements and attributes, and a description of them.
2.The descriptions are usually presented in the form of clues, each of which provides part of the information, and all of which are true and do not contradict each other.
3.The information provided by the clues needs to be combined and analyzed to match elements to attributes.Example questions are as follows:

<example 0>
1.Vlietmolen is owned by the Van Dijk family.
2.Westmolen was built 23 years after the Visser family's windmill.
3.The De Jong family's house was built 23 years before Zemelmolen.
4.Westmolen was built in 1752.

Output four entries, each containing three fields in order: Years, Windmills, Families (no header needed). Separate the fields with spaces and the entries with commas. 
Arrange the entries in order: the first field is 1683,1706,1729,1752 respectively.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 0>

<example 1>
1.The exhibit from Denmark was held sometime after the armor exhibit.
2.The exhibit from Swaziland was held 1 month after the ceramics exhibit.
3.The basketry exhibit is either April's exhibit or the presentation from Chile.
4.The ceramics presentation took place in January.
5.The glassware presentation was from Jamaica.

The output should contain four entries, each containing three fields in order: Months Exhibits Countries (the header does not need to be given), the fields separated by spaces, and the entries separated by commas.
Arrange the entries in order: the first field is January, February, March, April.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 1>

<example 2>
1.The person who used the sugar-free diet lost 4 more pounds than the dieter who used the caveman diet.
2.Mandy used the sugar-free diet.
3.The friend who used the caveman diet lost somewhat more pounds than Eula.
4.Eula is either the dieter who used the gluten-free diet or the friend who used the caveman diet.
5.Barbara lost 7 lbs.

The output should contain 4 entries, each containing three fields in order: PoundsLost Names Diets (table header need not be given), fields separated by spaces and entries separated by commas.
Arrange the entries in order: the first field is 3,5,7,9 respectively.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 2>

<example 3>
1.The bird that finished fourth was #118.
2.#126 finished 1 place after Kermit.
3.#134 was either Ozzy or the ostrich that finished third.
4.The runner that finished third was either #126 or Stretch.
5.#120 finished sometime after Ozzy.

The output should contain four entries, each of which contains three fields in order:Placement Ostriches Numbers (the header of the table does not need to be given), the fields are separated by spaces and the entries are separated by commas.
Placement entries in order: first, second, third, fourth for the first field respectively.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 3>

<example 4>
1.Vicki's client, Beulah and the client who paid $150 were all different clients.
2.Misty's client was either Eula or Inez.
3.Nancy's client paid more than Kara's client.
4.Debra paid 10 dollars less than Inez.
5.Debra paid 20 dollars less than Misty's client.

The output should contain four entries, each containing three fields in order: Prices Clients Masseuses (the header does not need to be given), the fields separated by spaces and the entries separated by commas.
Arrange the entries in order: the first field is $150, $160, $170 and $180 respectively.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 4>

<example 5>
1.Kendra didn't win the leadership badge.
2.Wendy won the swimming badge.
3.Elaine won the first aid badge.
4.Wendy was awarded before Tara.
5.The youngster who won the theater badge was awarded 1 spot after the scout who won the first aid badge.
6.The youngster who won the dance badge was awarded 1 spot before the girl who won the leadership badge.
7.Elaine was awarded 2 spots after the youngster who won the leadership badge.

The output should contain five entries, each containing three fields in order: Orders Girls Badges (the header does not need to be given), the fields separated by spaces and the entries separated by commas.
Arrange the entries in order: the first field is first,second,third,fourth,fifth respectively.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 5>

<example 6>
1.Of Gibbs v Kintz and the March 24 case, one was the 2-7 decision and the other was the 4-5 decision.
2.Zamora v Pibb wasn't the 7-2 decision.
3.Of the 7-2 decision and Omar v Powers, one was on March 31 and the other was on March 3.
4.Watts v Yang was sometime before the 7-2 decision.
5.Watts v Yang was on March 17.
6.The 8-1 decision was 2 weeks after the 5-4 decision.
7.The March 10 proceeding was the 2-7 decision.

The output should contain five entries, each containing three fields in order: Dates Cases Decisions (the table header does not need to be given), the fields separated by spaces and the entries separated by commas.
Arrange the entries in order: 3,10,17,24,31 for the first field.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 6>

<example 7>
1.The Gralax will launch 1 month after the rocket developed by Rubicorp.
2.Of the Cornick and the rocket that will launch in March, one is made by Rubicorp and the other is made by Techtrin.
3.The Athios will launch 1 month before the Cornick.
4.The Exatris, the rocket developed by SpaceZen

The output should contain four entries, each containing three fields in order: Months Names Companies (the header does not need to be given), the fields separated by spaces and the entries separated by commas.
Arrange the entries in order: the first field is January, February, March, April.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 7>

<example 8>
1.Cynthia was hired by Haynes Inc..
2.Nadine was hired by Velez & York.
3.Of Rosalie and the Haynes Inc. hire, one was hired on March 18th and the other was hired on March 21st.
4.Rosalie was hired 3 days after the Green & Hayes hire.

The output should contain four entries, each containing three fields in order: Dates Names LawFirms (the header of the table does not need to be given), the fields separated by spaces and the entries separated by commas.
Arrange the entries in order: the first field is 12th, 15th, 18th, 21st respectively.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 8>

<example 9>
1.The client who ordered the dragon roll ordered the teriyaki roll.
2.Of the customer who ordered the tiger roll and Hector, one paid $11.50 and the other ordered the futomaki roll.
3.Of Virginia and Ramona, one paid $15.50 and the other ordered the rainbow roll.
4.Virginia is either the person who ordered the rainbow roll or the person who ordered the spider roll.
5.The customer who ordered the dragon roll, Virginia, and Ramona are three different people.
6.Hector didn't order the teriyaki roll.
7.The person who ordered the firecracker roll paid $9.50.

The output should contain 4 entries, each containing 4 fields in order: Prices Roll1 Roll2 Customers (the table header does not need to be given), with the fields separated by spaces and the entries separated by commas.
Arrange the entries in order: the first field is $9.50, $11.50, $13.50, $15.50.
Finally, enclose the entire answer in double brackets, like this: [[...]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from bootcamp import Basebootcamp

class KorPuzzleLogicPuzzlebootcamp(Basebootcamp):
    def __init__(self, num_entries=4, years=None, attributes=None):
        super().__init__()
        self.num_entries = num_entries
        self.years = years or [1683, 1706, 1729, 1752]
        self.attributes = attributes or {
            'windmills': ["Vlietmolen", "Westmolen", "Zemelmolen", "Other"],
            'families': ["Van Dijk", "Visser", "De Jong", "Other Family"]
        }
    
    def case_generator(self):
        # Shuffle attributes while maintaining year order
        shuffled_attrs = {
            'windmills': random.sample(self.attributes['windmills'], k=self.num_entries),
            'families': random.sample(self.attributes['families'], k=self.num_entries)
        }
        
        # Create correct assignments
        assignments = [
            {
                'year': self.years[i],
                'windmill': shuffled_attrs['windmills'][i],
                'family': shuffled_attrs['families'][i]
            } for i in range(self.num_entries)
        ]
        
        # Generate valid clues based on assignments
        clues = self._generate_clues(assignments)
        
        return {
            'assignments': assignments,
            'clues': clues,
            'years_order': self.years.copy()
        }

    def _generate_clues(self, assignments):
        clues = []
        year_map = {a['year']: a for a in assignments}
        
        # Generate direct assignment clue
        direct = random.choice(assignments)
        clues.append(f"{direct['windmill']} is owned by the {direct['family']} family.")
        
        # Generate year difference clue
        for i in range(len(assignments)-1):
            if assignments[i+1]['year'] - assignments[i]['year'] == 23:
                clues.append(f"{assignments[i+1]['windmill']} was built 23 years after the {assignments[i]['family']} family's windmill.")
                break
        
        # Generate inverse year difference clue
        for i in range(1, len(assignments)):
            if assignments[i]['year'] - assignments[i-1]['year'] == 23:
                clues.append(f"The {assignments[i-1]['family']} family's house was built 23 years before {assignments[i]['windmill']}.")
                break
        
        # Add fixed year clue
        fixed_year = random.choice(assignments)
        clues.append(f"{fixed_year['windmill']} was built in {fixed_year['year']}.")
        
        return clues[:4]  # Ensure exactly 4 clues

    @staticmethod
    def prompt_func(question_case):
        clues = "\n".join([f"{i+1}. {clue}" for i, clue in enumerate(question_case['clues'])])
        return f"""Solve this logic puzzle:

{clues}

Output {len(question_case['years_order'])} entries with: Years Windmills Families.
Order years as {','.join(map(str, question_case['years_order']))}.
Format: [[entry1 entry2 entry3, ...]]"""

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].replace('\n', ' ').strip()
        entries = [e.strip() for e in last_match.split(',')]
        return [entry.split() for entry in entries if len(entry.split()) == 3]

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            correct = {(a['year']): (a['windmill'], a['family']) 
                      for a in identity['assignments']}
            
            for entry in solution:
                year = int(entry[0])
                if str(year) not in map(str, correct.keys()):
                    return False
                windmill, family = correct[year]
                if (entry[1], entry[2]) != (windmill, family):
                    return False
            return True
        except:
            return False

# 使用示例
if __name__ == "__main__":
    bootcamp = KorPuzzleLogicPuzzlebootcamp()
    case = bootcamp.case_generator()
    prompt = KorPuzzleLogicPuzzlebootcamp.prompt_func(case)
    print(prompt)
