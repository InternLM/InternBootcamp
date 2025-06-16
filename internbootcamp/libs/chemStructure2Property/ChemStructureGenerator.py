import random
from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem.inchi import MolToInchi
from rdkit.Chem import Crippen


class InChIGenerator:
    def __init__(self, max_atoms=15, min_atoms=3, elements=None, 
                 seed=None):
        RDLogger.DisableLog('rdApp.*')
        random.seed(42) if seed is None else random.seed(seed)
        self.max_atoms = max_atoms
        self.min_atoms = min_atoms
        if elements is None:
            self.elements = ['C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I']
        else:
            self.elements = elements

    def generate_random_molecule_rdkit(self):
        """
        Generates a random molecule using RDKit's RWMol.
        Can optionally try to assign random stereochemistry.
        """

        rw_mol = Chem.RWMol()  # Editable molecule
        num_atoms_to_add = random.randint(self.min_atoms, self.max_atoms)

        if num_atoms_to_add == 0:
            return None

        # Add the first atom
        atom_symbol = random.choice(self.elements)
        rw_mol.AddAtom(Chem.Atom(atom_symbol))

        # Add subsequent atoms and connect them
        for i in range(1, num_atoms_to_add):
            if not rw_mol.GetNumAtoms(): break

            existing_atom_idx = random.randrange(rw_mol.GetNumAtoms())
            new_atom_symbol = random.choice(self.elements)
            new_atom_idx = rw_mol.AddAtom(Chem.Atom(new_atom_symbol))

            bond_type = random.choice([Chem.BondType.SINGLE, Chem.BondType.SINGLE, Chem.BondType.DOUBLE, Chem.BondType.TRIPLE])
            
            rw_mol.AddBond(existing_atom_idx, new_atom_idx, bond_type)

        # Attempt to form rings
        if rw_mol.GetNumAtoms() > 2:
            num_rings_to_try = random.randint(0, rw_mol.GetNumAtoms() // 3)
            for _ in range(num_rings_to_try):
                if rw_mol.GetNumAtoms() < 2: break
                
                atom_indices = list(range(rw_mol.GetNumAtoms()))
                if len(atom_indices) < 2: break
                
                idx1, idx2 = random.sample(atom_indices, 2)
                
                if rw_mol.GetBondBetweenAtoms(idx1, idx2) is None:
                    rw_mol.AddBond(idx1, idx2, Chem.BondType.SINGLE) # Usually single for new rings

        try:
            mol = rw_mol.GetMol()
            Chem.SanitizeMol(mol)  # Crucial: checks valency, aromaticity, etc.

            if mol.GetNumAtoms() > 0:
                # It might create non-physical or conflicting assignments.
                # InChI will represent whatever stereo is defined.
                Chem.AssignStereochemistryFrom3D(mol) # If 3D coords were present (not here)
                # Or, more directly, find potential chiral centers and assign randomly
                chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
                for center_idx, stereo_val in chiral_centers:
                    if stereo_val == '?': # Unassigned
                        atom = mol.GetAtomWithIdx(center_idx)
                        if random.choice([True, False]):
                            atom.SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CW)
                        else:
                            atom.SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CCW)
                # Re-sanitize after modifying chiral tags might be good practice
                Chem.SanitizeMol(mol)
            return mol
        except Exception as e:
            # print(f"Debug: RDKit molecule construction/sanitization failed: {e}")
            return None
               
    def generate_n_valid_inchi(self, n):
        """
        Generates N valid, unique InChI strings.
        kwargs_for_mol_gen are passed to generate_random_molecule_rdkit.
        """
        valid_inchi_set = set()
        total_attempts_overall = 0

        while len(valid_inchi_set) < n:
            attempts_for_current_inchi = 0
            generated_this_round = False
            while not generated_this_round:
                total_attempts_overall += 1
                attempts_for_current_inchi += 1
                
                mol = self.generate_random_molecule_rdkit()
                
                if mol:
                    try:
                        inchi_string = MolToInchi(mol)
                        mol = Chem.MolFromInchi(inchi_string)
                        logp = Crippen.MolLogP(mol)
                        if inchi_string and inchi_string not in valid_inchi_set:

                            valid_inchi_set.add(inchi_string)
                            generated_this_round = True
                            break  # Found one
                    except Exception as e:
                        # This can happen if the molecule is somehow malformed even after sanitization,
                        # or if InChI generation itself encounters an issue (rare).
                        print(f"Debug: MolToInchi failed: {e} for SMILES: {Chem.MolToSmiles(mol)}")
                        pass

        return list(valid_inchi_set)


class SMILESGenerator:
    def __init__(self, min_len=5, max_len=25, 
                 seed=None):
        RDLogger.DisableLog('rdApp.*')
        random.seed(42) if seed is None else random.seed(seed)
        self.min_len = min_len
        self.max_len = max_len


    def is_valid_smiles(self, smi):
        """Checks if a SMILES string is valid using RDKit."""
        if not smi:
            return False
        mol = Chem.MolFromSmiles(smi, sanitize=False)  # Parse without sanitization first
        if mol is None:
            return False
        try:
            Chem.SanitizeMol(mol)
            return True
        except Exception as e:
            return False     

    def generate_random_smiles_candidate(self):
        """
        Generates a random string that might be a SMILES string.
        This is a VERY naive generator and will produce many invalid SMILES.
        """
        # A basic set of SMILES characters
        # More comprehensive: C,c,N,n,O,o,S,s,P,p,F,Cl,Br,I,B,Si,Se,*,[nH],[nH+],[cH-],...
        # Also: -,=,#,$,:,.,(,),[,],%,0-9 (for ring closures and isotopes/charges)
        atom_chars = ['C', 'N', 'O', 'S', 'F', 'Cl', 'Br', 'I', 'P']
        aromatic_chars = ['c', 'n', 'o', 's']
        bond_chars = ['-', '=', '#']
        branch_chars = ['(', ')']
        ring_digits = [str(i) for i in range(1, 10)] # 1-9
        # More complex elements like charges, isotopes, chiral centers are harder to randomize simply
        # For simplicity, we'll stick to a subset.

        all_chars = atom_chars + aromatic_chars + bond_chars + branch_chars + ring_digits

        length = random.randint(self.min_len, self.max_len)
        candidate = ""

        candidate += random.choice(atom_chars + aromatic_chars)

        open_parentheses = 0
        open_rings = {} 

        for _ in range(length - 1):
            choices = []
            weights = []

            choices.extend(atom_chars + aromatic_chars)
            weights.extend([10] * (len(atom_chars) + len(aromatic_chars)))

            if candidate and (candidate[-1].isalpha() or candidate[-1] == ')' or candidate[-1].isdigit()):
                choices.extend(bond_chars)
                weights.extend([5] * len(bond_chars))


            if candidate and (candidate[-1].isalpha() or candidate[-1] == ')' or candidate[-1].isdigit()):
                choices.append('(')
                weights.append(3)

            if open_parentheses > 0:
                choices.append(')')
                weights.append(3)

            # Ring closures
            if candidate and (candidate[-1].isalpha() or candidate[-1] == ')'):
                # Try to close an open ring
                open_ring_digits = [d for d, status in open_rings.items() if status == 'open']
                if open_ring_digits and random.random() < 0.5: # 50% chance to close an open ring
                    digit_to_close = random.choice(open_ring_digits)
                    choices.append(digit_to_close)
                    weights.append(5)
                else: # Try to open a new ring
                    available_digits = [d for d in ring_digits if d not in open_rings or open_rings[d] == 'closed']
                    if available_digits:
                        choices.extend(available_digits)
                        weights.extend([2] * len(available_digits))
            
            if not choices: # Fallback if no valid options (e.g., after certain bonds)
                chosen_char = random.choice(atom_chars)
            else:
                chosen_char = random.choices(choices, weights=weights, k=1)[0]
            
            # Update state
            if chosen_char == '(':
                open_parentheses += 1
            elif chosen_char == ')':
                if open_parentheses > 0:
                    open_parentheses -= 1
                else:
                    continue # Don't add a closing parenthesis if none are open
            elif chosen_char in ring_digits:
                if chosen_char not in open_rings or open_rings[chosen_char] == 'closed':
                    open_rings[chosen_char] = 'open'
                elif open_rings[chosen_char] == 'open':
                    open_rings[chosen_char] = 'closed'
            
            candidate += chosen_char

        # Attempt to close any remaining open parentheses
        candidate += ')' * open_parentheses
        
        # Attempt to close any remaining open rings (very crudely)
        for digit, status in open_rings.items():
            if status == 'open':
                # Find a suitable place to close it - this is hard without graph info
                # For now, just append another atom and the digit if possible
                if candidate and (candidate[-1].isalpha() or candidate[-1] == ')'):
                    if random.random() < 0.7 and len(candidate) < self.max_len -1 : # Add another atom then close
                        candidate += random.choice(atom_chars) + digit
                    else: # Just append the digit (might be invalid)
                        candidate += digit


        return candidate

    def generate_n_valid_smiles(self, n):
        """Generates N valid, unique (canonical) SMILES strings."""
        valid_smiles_set = set()
        total_attempts_overall = 0

        print(f"Attempting to generate {n} valid SMILES (min_len={self.min_len}, max_len={self.max_len})...")
        while len(valid_smiles_set) < n:
            attempts_for_current_smiles = 0
            generated_this_round = False
            while not generated_this_round:
                total_attempts_overall += 1
                attempts_for_current_smiles += 1
                candidate = self.generate_random_smiles_candidate()
                
                if self.is_valid_smiles(candidate):
                    mol = Chem.MolFromSmiles(candidate) # Re-parse to be sure and for canonicalization
                    if mol: # Should be true if is_valid_smiles passed
                        canonical_smi = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
                        try:
                            mol = Chem.MolFromSmiles(canonical_smi)
                            logp = Crippen.MolLogP(mol)
                            if canonical_smi not in valid_smiles_set:
                                valid_smiles_set.add(canonical_smi)
                                # print(f"Generated ({len(valid_smiles_set)}/{n}): {canonical_smi} (after {attempts_for_current_smiles} attempts for this one, {total_attempts_overall} total)")
                                generated_this_round = True
                                break # Found one, move to the next
                        except Exception as e:
                            pass
           
        return list(valid_smiles_set)

if __name__ == "__main__":
    aInChIGenerator = InChIGenerator(max_atoms=15, min_atoms=3)
    inchi_10 = aInChIGenerator.generate_n_valid_inchi(10)
    print(inchi_10)
    aSMILESGenerator = SMILESGenerator(min_len=5, max_len=25)
    smiles_10 = aSMILESGenerator.generate_n_valid_smiles(10)
    print(smiles_10)