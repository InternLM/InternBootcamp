from internbootcamp.bootcamp.base import Basebootcamp
from internbootcamp.libs.chemStructure2Property.ChemStructureGenerator import InChIGenerator
from .utils import last_boxed_only_string, remove_boxed
from rdkit import Chem
from rdkit.Chem import Crippen


class InChI2logPbootcamp(Basebootcamp):
    def __init__(self, num_numbers=4, max_atoms=15, min_atoms=3, elements=None, seed=None):
        # super.__init__()
        self.num_numbers = num_numbers
        self.InChIGenerator = InChIGenerator(max_atoms=max_atoms, min_atoms=min_atoms, elements=elements, seed=seed)
        
    def case_generator(self) -> str:
        """
        生成一组数字和目标值。
        """
        return self.InChIGenerator.generate_n_valid_inchi(1)[0]

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
    def _verify_correction(cls, solution, InChI)->bool:
        """
        Verify the correction of the solution.
        """ 
        mol = Chem.MolFromInchi(InChI)
        true_logp = Crippen.MolLogP(mol)
        print(f"Comparing pred: {solution}, ground_truth: {true_logp}")
        return abs(true_logp - float(solution)) <= 0.01  # maybe mse or mae better?
        



