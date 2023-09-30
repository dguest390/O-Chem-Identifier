import Classes.constants as CONSTANT

class Atom(object):
	def __init__(self, atom_type: str, base_val_electrons: int = -1, shared_val_electrons: int = -1, full_electron_config: int = -1):
		# will need to restrict type to a list of predefined values else raise error
		self.atom_type = atom_type
		self.mapped_x = None
		self.mapped_y = None
		
		if Atom.is_atom(atom_type):
			try:
				self.atom_type_full = CONSTANT.ATOM_SYMBOL_TO_NAME_DICT[self.atom_type]		
				self.atom_is_polyatomic = False
			except KeyError:
				raise NameError('Atom type DNE in the ATOM_SYMBOL_TO_NAME_DICT. Atom_type: ', str(atom_type))
			
			if base_val_electrons == -1 or shared_val_electrons == -1 or full_electron_config == -1:
				try:
					self.full_electron_config = CONSTANT.ATOM_FULL_ELEC_COUNT[atom_type] # number of electrons req'd to have outer shell stable
					self.base_val_electrons = CONSTANT.ATOM_UNBONDED_VAL_ELEC_COUNT[atom_type] # valence electrons available when no bonding present
					self.shared_val_electrons = 0 # electrons shared (base - shared >= 0)
				except KeyError:
					raise NameError('Atom type DNE in the ATOM dictionary, could not create atom. Atom type: ', str(atom_type))
			else:	
				self.full_electron_config = full_electron_config # number of electrons req'd to have outer shell stable
				self.base_val_electrons = base_val_electrons # valence electrons available when no bonding present
				self.shared_val_electrons = shared_val_electrons # electrons shared (base - shared >= 0)
		elif Atom.is_polyatomic(atom_type):
			try:
				self.atom_type_full = CONSTANT.POLYATOMIC_SYMBOL_TO_NAME_DICT[self.atom_type]
				self.atom_is_polyatomic = True
			except KeyError:
				raise NameError('Atom type DNE in the POLYATOMIC_SYMBOL_TO_NAME_DICT. Atom_type: ', str(atom_type))
			
			if base_val_electrons == -1 or shared_val_electrons == -1 or full_electron_config == -1:
				try:
					self.full_electron_config = CONSTANT.POLYATOMIC_FULL_ELEC_COUNT[atom_type] # number of electrons req'd to have outer shell stable
					self.base_val_electrons = CONSTANT.POLYATOMIC_UNBONDED_VAL_ELEC_COUNT[atom_type] # valence electrons available when no bonding present
					self.shared_val_electrons = 0 # electrons shared (base - shared >= 0)
				except KeyError:
					raise NameError('Atom type DNE in the POLYATOMIC dictionary, could not create atom. Atom type: ', str(atom_type))
			else:	
				self.full_electron_config = full_electron_config # number of electrons req'd to have outer shell stable
				self.base_val_electrons = base_val_electrons # valence electrons available when no bonding present
				self.shared_val_electrons = shared_val_electrons # electrons shared (base - shared >= 0)

	@staticmethod
	def is_atom(type: str)->bool:
		is_atom_bool: bool
		try:
			CONSTANT.ATOM_SYMBOL_TO_NAME_DICT[type]
			is_atom_bool = True
		except KeyError:
			is_atom_bool = False
		
		return is_atom_bool
	
	@staticmethod
	def is_polyatomic(type: str)->bool:
		is_atom_polyatomic: bool

		try:
			CONSTANT.POLYATOMIC_SYMBOL_TO_NAME_DICT[type]
			is_atom_polyatomic = True
		except KeyError:
			is_atom_polyatomic = False
		
		return is_atom_polyatomic
	
	def get_type(self):
		return self.atom_type
	
	def get_type_full(self):
		return self.atom_type_full
		
	def get_base_val_electrons(self):
		return self.base_val_electrons

	def get_shared_val_electrons(self):
		return self.shared_val_electrons

	def get_max_valence_electrons(self):
		return self.full_electron_config
	
	def get_mapped_position(self):
		return (self.mapped_x, self.mapped_y)
	
	# update the remaining valence electron count if valid
	def set_shared_val_electrons(self, new_value: int):
		success: bool

		if  new_value >= 0 and new_value <= self.full_electron_config:
			self.shared_val_electrons = new_value
			success = True
		else:
			success = False

		return success

	def set_mapped_position(self, x, y):
		self.mapped_x = x
		self.mapped_y = y

	def __str__(self):
		tempStr = str(hex(id(self))) + " " + self.__class__.__name__ + " "

		if len(self.atom_type) == 1:
			tempStr += self.atom_type + "  "
		else:
			tempStr += self.atom_type + " "

		tempStr += str(self.base_val_electrons) + "/" + str(self.shared_val_electrons) + "/" + str(self.full_electron_config)

		return tempStr
		