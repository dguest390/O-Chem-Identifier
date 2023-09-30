from Classes.atom import Atom
import Classes.constants as CONSTANT


class Bond(object):
	def __init__(self, atom_one: Atom, atom_two: Atom, electron_cost: int):
		self.electron_cost = electron_cost
		if self.electron_cost == None:
			raise NotImplementedError('Bond Subclasses must define electron_cost')
		self.atoms = [atom_one, atom_two]

	def get_atoms(self):
		return self.atoms
		
	def get_electron_bond_cost(self):
		return self.electron_cost
	
	def can_atoms_form_bond(self, atom_one: Atom, atom_two: Atom) -> bool:
		raise NotImplementedError
		
	def __str__(self):
		raise NotImplementedError


class IonicBond(Bond):
	def __init(self, atom_one: Atom, atom_two: Atom):
		super().__init__(atom_one, atom_two)
		self.electron_cost = None
	
	def get_electron_bond_cost(self):
		pass

	def can_atoms_form_bond(self, atom_one: Atom, atom_two: Atom) -> bool:
		pass

	def __str__(self):
		pass


class CovalentBond(Bond):
	def __init__(self, atom_one: Atom, atom_two: Atom, electron_cost: int):
		if not CovalentBond.can_atoms_form_bond(atom_one, atom_two, electron_cost):
			atom_error_one = "\tAtom One:\t" + str(atom_one) + "\n"
			atom_error_two = "\tAtom Two:\t" + str(atom_two) + "\n"
			bond_error = "\tDesired Bond:\t" + str(self.__class__.__name__)
			raise NameError("Error: Atoms unable to bond\n\tDetails: \n" + atom_error_one + atom_error_two + bond_error)
		else:
			super().__init__(atom_one, atom_two, electron_cost)
			self.share_electrons()

	# Represents the sharing of atoms across the formed bond between the two atoms
	# Updates the electron count for participating atoms respective to bond formed
	def share_electrons(self):
		atoms = self.get_atoms()
		index = 1
		atom_error_dict = {
			1:"One",
			2:"Two"
		}

		for atom in atoms:
			atom_new_total_elec_count = atom.get_shared_val_electrons() + atom.get_base_val_electrons() + self.get_electron_bond_cost()

			if atom_new_total_elec_count > atom.get_max_valence_electrons():
				error_in_atom = "Atom " + str(atom_error_dict[index]) + " contains the problem\n"
				atom_error_one = "Atom One:\n\t" + str(atoms[0]) + "\n"
				atom_error_two = "Atom Two:\n\t" + str(atoms[1]) + "\n"
				bond_error = "Desired Bond:\n\t" + str(self.__class__.__name__) + " with cost: " + str(self.get_electron_bond_cost())
				raise NameError("Something went wrong, bond class should prevent the number of shared electrons exceeding the max amount of electrons for that given atom. Corresponds to:\n" + error_in_atom  + atom_error_one + atom_error_two + bond_error)

			atom.set_shared_val_electrons(atom.get_shared_val_electrons() + self.get_electron_bond_cost())
			index += 1
	
	# Represents the removal of a bond and the replenishing of originally shared electrons
	# Updates the electron count for participating atoms respective to bond removal
	def unshare_electrons(self):
		atoms = self.get_atoms()

		index = 1
		atom_error_dict = {
			1:"One",
			2:"Two"
		}

		for atom in atoms:
			# check to ensure not < 0
			# this should never be an issue since adding bonds prevents invalid bonding-->thus breaking valid bonds should result in valid atoms
			atom_new_shared_elec_count = atom.get_shared_val_electrons() - self.get_electron_bond_cost()

			if (atom_new_shared_elec_count < 0):
				error_in_atom = "Atom " + str(atom_error_dict[index]) + " contains the problem\n"
				atom_error_one = "Atom One:\n\t" + str(atoms[0]) + "\n"
				atom_error_two = "Atom Two:\n\t" + str(atoms[1]) + "\n"
				bond_error = "Desired Bond:\n\t" + str(self.__class__.__name__) + " with cost: " + str(self.get_electron_bond_cost())
				raise NameError("Something went wrong, bond class should prevent the number of shared electrons exceeding the max amount of electrons for that given atom. Corresponds to:\n" + error_in_atom  + atom_error_one + atom_error_two + bond_error)
			
			atom.set_shared_val_electrons(atom_new_shared_elec_count)
			index += 1


	# Method to determine impossible bonding on issues OTHER than valence electron count (eg: same atom bonded)
	@staticmethod
	def impossible_bonding(atom_one: Atom, atom_two: Atom) -> bool:
		try:
			impossible_bond: bool = False

			# cannot be the same atom instance (impossible in nature)
			if atom_one == atom_two:
				impossible_bond = True

			return impossible_bond
		except NameError:
			raise NameError("You cannot bond to the same atom!")

	# Return boolean on ability of two parameter atoms ablity to bond. Since static must include electron count (cannot self.get())
	@staticmethod
	def can_atoms_form_bond(atom_one: Atom, atom_two: Atom, electron_bond_cost: int) -> bool:
		try:
			valid_bond: bool = not CovalentBond.impossible_bonding(atom_one, atom_two)
		except NameError as e:
			raise NameError(e)
		
		atom_one_elec_remaining = atom_one.get_base_val_electrons() - atom_one.get_shared_val_electrons() - electron_bond_cost
		atom_two_elec_remaining = atom_two.get_base_val_electrons() - atom_two.get_shared_val_electrons() - electron_bond_cost

		atom_one_total_electrons = atom_one.get_base_val_electrons() + atom_one.get_shared_val_electrons() + electron_bond_cost
		atom_two_total_electrons = atom_two.get_base_val_electrons() + atom_two.get_shared_val_electrons() + electron_bond_cost

		atom_one_too_few_electrons: bool = atom_one_elec_remaining < 0
		atom_two_too_few_electrons: bool = atom_two_elec_remaining < 0
		atom_one_too_many_electrons: bool = atom_one_total_electrons > atom_one.get_max_valence_electrons()
		atom_two_too_many_electrons: bool = atom_two_total_electrons > atom_two.get_max_valence_electrons()

		if atom_one_too_few_electrons:
			raise NameError(atom_one.get_type_full() + ' does not have enough electrons to share to form the ' + CONSTANT.BOND_NAMES_ARR[electron_bond_cost].lower())
		if atom_two_too_few_electrons:
			raise NameError(atom_two.get_type_full() + ' does not have enough electrons to share to form the ' + CONSTANT.BOND_NAMES_ARR[electron_bond_cost].lower())
		if atom_one_too_many_electrons:
			raise NameError(atom_one.get_type_full() + ' has a stable outer shell with ' + str(atom_one.get_max_valence_electrons()) + ' valence electrons. Therefore, cannot accept more electrons to form ' + CONSTANT.BOND_NAMES_ARR[electron_bond_cost].lower())
		if atom_two_too_many_electrons:
			raise NameError(atom_two.get_type_full() + ' has a stable outer shell with ' + str(atom_two.get_max_valence_electrons()) + ' valence electrons. Therefore, cannot accept more electrons to form ' + CONSTANT.BOND_NAMES_ARR[electron_bond_cost].lower())

		return valid_bond

	def __str__(self):
		pass
	

class SingleBond(CovalentBond):
	def __init__(self, atom_one: Atom, atom_two: Atom):
		# hydrogen will be the only exception with 1 valence electron
		super().__init__(atom_one, atom_two, CONSTANT.SINGLE_BOND_COST)
			
	def get_electron_bond_cost(self):
		return self.electron_cost

	def __str__(self):
		return str(hex(id(self))) + " " + "Single Bond" + "=(" + str(self.atoms[0]) + ", " + str(self.atoms[1]) + ")"

class DoubleBond(CovalentBond):
	def __init__(self, atom_one: Atom, atom_two: Atom):
		super().__init__(atom_one, atom_two, CONSTANT.DOUBLE_BOND_COST)
	
	def can_atoms_form_bond(self) -> bool:
		pass
	
	def __str__(self):
		return str(hex(id(self))) + " " + "Double Bond" + "=(" + str(self.atoms[0]) + ", " + str(self.atoms[1]) + ")"

class TripleBond(CovalentBond):
	def __init__(self, atom_one: Atom, atom_two: Atom):
		super().__init__(atom_one, atom_two, CONSTANT.TRIPLE_BOND_COST)
	
	def can_atoms_form_bond(self, atom_one: Atom, atom_two: Atom) -> bool:
		pass
		
	def __str__(self):
		return str(hex(id(self))) + " " + "Triple Bond" + "=(" + str(self.atoms[0]) + ", " + str(self.atoms[1]) + ")"