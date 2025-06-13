from rdkit import Chem
from rdkit.Chem import Crippen
from .InChI2logPBootCamp import InChI2logPbootcamp

class InChI2MRBootCamp(InChI2logPbootcamp):

    def prompt_func(self, InChI) -> str:

        instruction = f"Given the InChI, determine the Molar Refractivity (MR) value of the material. The InChI is: {InChI}"
        instruction_following = """Let's think step by step and output the final answer within \\boxed{}.The final answer should be one float number. For example "Final Answer: \\boxed{afloat}"."""
        
        prompt = instruction + '\n' + instruction_following
        return prompt
    
        
    @classmethod 
    def _verify_correction(cls, solution, InChI)->bool:
        """
        Verify the correction of the solution.
        """ 
        mol = Chem.MolFromInchi(InChI)
        true_MR = Crippen.MolMR(mol)
        print(f"Comparing pred: {solution}, ground_truth: {true_MR}")
        return abs(true_MR - float(solution)) <= 0.01  # maybe mse or mae better?
        



