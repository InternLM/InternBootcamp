from abc import ABC, abstractmethod
from typing import Dict

class BaseInstructionGenerator(ABC):
    def __init__(self,*args,**kwargs):
        self.data_source = f"bootcamp/{self.__class__.__name__.replace('InstructionGenerator', '')}"
        ...
    
    @abstractmethod
    def prompt_func(self, identity: Dict) -> str:
        pass
    
    @abstractmethod
    def case_generator(self) -> Dict:
        pass
    
                    





