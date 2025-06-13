from internbootcamp.bootcamp.base import Basebootcamp
from internbootcamp.libs.chemStructure2Property.ChemStructureGenerator import SMILESGenerator
from .utils import last_boxed_only_string, remove_boxed
from rdkit import Chem
from rdkit.Chem import Crippen

from .SMILES2logPBootCamp import SMILES2logPBootCamp

class SMILES2MRBootCamp(SMILES2logPBootCamp):



    def prompt_func(self,  SMILES) -> str:

        instruction = f"Given the  SMILES, determine the Molar Refractivity (MR) value of the material. The  SMILES is: {SMILES}"
        instruction_following = """Let's think step by step and output the final answer within \\boxed{}.The final answer should be one float number. For example "Final Answer: \\boxed{afloat}"."""
        
        prompt = instruction + '\n' + instruction_following
        return prompt

        
    @classmethod 
    def _verify_correction(cls, solution, SMILES)->bool:
        """
        Verify the correction of the solution.
        """ 
        mol = Chem.MolFromSmiles(SMILES)
        true_MR = Crippen.MolMR(mol)
        print(f"Comparing pred: {solution}, ground_truth: {true_MR}")
        return abs(true_MR - float(solution)) <= 0.01  # maybe mse or mae better?
        



