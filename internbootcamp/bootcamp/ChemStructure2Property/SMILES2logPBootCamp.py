from internbootcamp.bootcamp.base import Basebootcamp
from internbootcamp.libs.chemStructure2Property.ChemStructureGenerator import SMILESGenerator
from .utils import last_boxed_only_string, remove_boxed
from rdkit import Chem
from rdkit.Chem import Crippen

from .InChI2logPBootCamp import InChI2logPbootcamp

class SMILES2logPBootCamp(InChI2logPbootcamp):
    def __init__(self, num_numbers=4, min_len=5, max_len=25, 
                 seed=None):
        # super.__init__()
        self.num_numbers = num_numbers
        self.SMILESGenerator = SMILESGenerator(min_len=5, max_len=25, seed=None)
        
    def case_generator(self) -> str:
        """
        生成一组数字和目标值。
        """
        return self.SMILESGenerator.generate_n_valid_smiles(1)[0]

    def prompt_func(self,  SMILES) -> str:

        instruction = f"Given the  SMILES, determine the lipophilicity (logP) value of the material. The  SMILES is: {SMILES}"
        instruction_following = """Let's think step by step and output the final answer within \\boxed{}.The final answer should be one float number. For example "Final Answer: \\boxed{afloat}"."""
        
        prompt = instruction + '\n' + instruction_following
        return prompt

        
    @classmethod 
    def _verify_correction(cls, solution, SMILES)->bool:
        """
        Verify the correction of the solution.
        """ 
        mol = Chem.MolFromSmiles(SMILES)
        true_logp = Crippen.MolLogP(mol)
        print(f"Comparing pred: {solution}, ground_truth: {true_logp}")
        return abs(true_logp - float(solution)) <= 0.01  # maybe mse or mae better?
        



