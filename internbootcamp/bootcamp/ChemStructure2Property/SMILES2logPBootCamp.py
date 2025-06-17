import random

from internbootcamp.bootcamp.base import Basebootcamp
from internbootcamp.libs.chemStructure2Property.ChemStructureGenerator import SMILESGenerator
from .utils import last_boxed_only_string, remove_boxed
from rdkit import Chem
from rdkit.Chem import Crippen

from .InChI2logPBootCamp import InChI2logPbootcamp

class SMILES2logPbootcamp(InChI2logPbootcamp):
    def __init__(self,min_len=5, max_len=25, 
                 seed=None):
        # super.__init__()
        self.min_len = min_len
        self.max_len = max_len
        # self.SMILESGenerator = SMILESGenerator(min_len=min_len, max_len=max_len, seed=seed)
        
    def case_generator(self) -> str:
        """
        生成一组数字和目标值。
        """
        self.SMILESGenerator = SMILESGenerator(min_len=self.min_len, max_len=self.max_len, seed=None)
        return self.SMILESGenerator.generate_n_valid_smiles(10)[random.randint(0, 9)]

    def prompt_func(self,  SMILES) -> str:

        instruction = f"Given the  SMILES, determine the lipophilicity (logP) value of the material. The  SMILES is: {SMILES}"
        instruction_following = """Let's think step by step and output the final answer within \\boxed{}.The final answer should be one float number. For example "Final Answer: \\boxed{afloat}"."""
        
        prompt = instruction + '\n' + instruction_following
        return prompt

        
    @classmethod
    def _verify_correction(cls, solution, SMILES) -> float:
        """
        Verify the correction of the solution and return a score between 0 and 1.
        The score is based on the relative error with respect to a maximum relative error of 0.1.
        """
        mol = Chem.MolFromSmiles(SMILES)
        if mol is None:
            raise ValueError("Invalid SMILES string provided.")
        
        true_logp = Crippen.MolLogP(mol)
        solution_float = float(solution)
        
        # print('true_logp: ', true_logp, ' solution_float: ', solution_float)

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
            return 1.0
            return 1 - (relative_error / max_relative_error) * 0.5 ## For RL
