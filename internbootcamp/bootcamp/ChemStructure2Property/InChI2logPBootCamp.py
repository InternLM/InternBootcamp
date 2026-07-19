import random

from internbootcamp.bootcamp.base import Basebootcamp
from internbootcamp.libs.chemStructure2Property.ChemStructureGenerator import InChIGenerator
from internbootcamp.bootcamp.ChemStructure2Property.utils import last_boxed_only_string, remove_boxed
from rdkit import Chem
from rdkit.Chem import Crippen


class InChI2logPbootcamp(Basebootcamp):
    def __init__(self, max_atoms=15, min_atoms=3, elements=None, seed=None):
        # super.__init__()
        self.max_atoms = max_atoms
        self.min_atoms = min_atoms
        # self.InChIGenerator = InChIGenerator(max_atoms=max_atoms, min_atoms=min_atoms, elements=elements, seed=seed)
        # self.tolerance_factor = tolerance_factor # 1 for 1% error consider true, 0.1 for 0.1% error true, 10 for 10% error

    def case_generator(self) -> str:
        """
        生成一组数字和目标值。
        """
        self.InChIGenerator = InChIGenerator(max_atoms=self.max_atoms, min_atoms=self.min_atoms, elements=None, seed=None)
        inchis = self.InChIGenerator.generate_n_valid_inchi(1)
        # print(inchis)
        # print(n)
        return inchis[0]

    def prompt_func(self, InChI) -> str:

        instruction = f"Given the InChI, determine the lipophilicity (logP) value of the material. The InChI is: {InChI}"
        instruction_following = """Let's think step by step and output the final answer within \\boxed{}.The final answer should be one float number. For example "Final Answer: \\boxed{afloat}"."""
        
        prompt = instruction + '\n' + instruction_following
        return prompt
    
    @staticmethod
    def extract_output(output):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        output = last_boxed_only_string(output)
        if output is None:
            return None
        return remove_boxed(output)
        
    @classmethod
    def _verify_correction(cls, solution, InChI) -> float:
        """
        Verify the correction of the solution and return a score between 0 and 1.
        The score is based on the relative error with respect to a maximum relative error of 0.1.
        """
        mol = Chem.MolFromInchi(InChI)
        true_logp = Crippen.MolLogP(mol)
        solution_float = float(solution)

        # Handle case where true_logp is 0
        if true_logp == 0:
            # If true_logp is 0, we check how close the solution is to 0
            relative_error = abs(solution_float)
        else:
            # Calculate the relative error
            relative_error = abs(true_logp - solution_float) / abs(true_logp)

        # Define the maximum allowed relative error
        max_relative_error = 0.1

        # Calculate the score based on the relative error
        if relative_error >= max_relative_error:
            return 0.0  # Error is too large, score is 0
        else:
            # Linear interpolation: score decreases linearly from 1 to 0 as error goes from 0 to max_relative_error
            # return 1.0 
            return 1 - (relative_error / max_relative_error) * 0.5 ## For RL
        
if __name__ == "__main__":
    bootcamp = InChI2logPbootcamp()
    while True:
        case = bootcamp.case_generator()
        print('case')
        print(case)
        input()