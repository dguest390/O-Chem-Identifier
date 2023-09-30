# Derived from https://stackoverflow.com/questions/19472530/representing-graphs-data-structure-in-python
from collections import defaultdict
from Classes.atom import Atom
from Classes.bonds import Bond	
from Classes.bonds import CovalentBond
import Classes.constants as CONSTANT

class Graph:
	def __init__(self, bonds: list[Bond] = []):
		self.graph = defaultdict(set)
		self.mapped_address = dict()
		self.mapped_address_counts = dict()
		if (len(bonds) > 0):
			self.add_bonds_via_bond_list(bonds)

	# add bonds and their associated atoms to the graph
	def add_bonds_via_bond_list(self, bonds: list[Bond]):
		for bond in bonds:
			self.add_bond_via_bond_obj(bond)

	# add bond and its associated atoms to the graph
	def add_bond_via_bond_obj(self, bond: Bond):
		atom_one, atom_two = bond.get_atoms()

		# bond class did checking for validity, so just add to graph
		self.graph[atom_one].add((atom_two, bond))  
		self.graph[atom_two].add((atom_one, bond))

		#add to mapping
		self.add_mapped_address(atom_one)
		self.add_mapped_address(atom_two)
		self.add_mapped_address(bond)
	
	# remove bonds from the Graph (molecule), preserve atoms in Graph
	def remove_bonds_via_bond_list(self, bonds: list[Bond]):
		for bond in bonds:
			self.remove_bond_via_bond_obj(bond)

	# remove bond from the Graph (molecule), preserve atoms in Graph
	def remove_bond_via_bond_obj(self, bond_to_remove: CovalentBond):
		# update electrons associated with previously bonded atoms
		bond_to_remove.unshare_electrons()
		atoms_in_bond = bond_to_remove.get_atoms()
		
		# remove bond mapping
		self.remove_mapped_address(bond_to_remove)

		# remove bond from graph
		for atom in atoms_in_bond:
			atom_bond_tuples_to_remove = []

			for atom_bond_tuple in self.graph[atom]:
				bond_in_tuple = atom_bond_tuple[1]

				if (bond_in_tuple == bond_to_remove):
					atom_bond_tuples_to_remove.append(atom_bond_tuple)

			# deletes from graph- cannot delete while iterating through set
			for atom_bond_tuple in atom_bond_tuples_to_remove:
				self.graph[atom].remove(atom_bond_tuple)
	
	# adds unbonded atoms in atom list to the graph 
	def add_nodes_via_atom_list(self, atoms: list[Atom]):
		for atom in atoms:
			self.add_node_via_atom_obj(atom)
	
	# adds unbonded atom to the graph
	def add_node_via_atom_obj(self, atom: Atom):
		# default dict does not raise key error, we only want to add atom if it DNE in graph
		exists_in_graph: bool = self.does_atom_exist_in_graph(atom)

		if not exists_in_graph:
			self.graph[atom] = set()
			self.add_mapped_address(atom)
		else:
			None

	# checks mapped address dict to determine if present since self.graph = defaultdict(set) prevents checking by keyerror
	def does_atom_exist_in_graph(self, atom:Atom) -> bool:
		hex_address = hex(id(atom))
		exists: bool

		try:
			self.mapped_address[hex_address]
			exists = True
		except KeyError:
			exists = False

		return exists

	# remove all bonds to a given passed atom, preserves that atom in the graph
	def remove_bonds_to_atom(self, reference_atom: Atom):
		# remove all bonds to a given atom, restore valence electrons to atoms- atoms are preserved, bonds are deleted
		bonds_to_atom = []

		# build bonds to the atom
		for atom_bond_tuple in self.graph[reference_atom]:
			bond = atom_bond_tuple[1]
			bonds_to_atom.append(bond)
				
		self.remove_bonds_via_bond_list(bonds_to_atom)

	# destructive, removes bonds to atoms and deletes atoms from the graph
	def delete_atoms_via_atom_list(self, atoms: list[Atom]):
		for atom in atoms:
			self.delete_atom_via_atom_object(atom)

	# destructive, removes bonds to atom and deletes atom from the graph
	def delete_atom_via_atom_object(self, atom: Atom):
		# remove bonds
		bond_list: list[Bond] = self.get_bonds_to_atom(atom)
		self.remove_bonds_via_bond_list(bond_list)

		# remove atom
		self.remove_mapped_address(atom)
		self.graph.pop(atom)

	#get a list of every atom
	def get_atom_list(self):
		return self.graph.keys()
	
	#get a list of every bond
	def get_bond_list(self):
		# iterate through keys of graph
		# check if bond is in new dictionary - try/except
		# if not, add
		# else, skip

		bond_set = set()
		for atom_bond_tuple_set in self.graph.values():
			for index, atom_bond_tuple in enumerate(atom_bond_tuple_set):
				bond_set.add(atom_bond_tuple[1])

		return list(bond_set)

	# Associates the instance of a Atom or Bond with its common name.
	# Eg: 0x443 may be a carbon atom, but this maps it to an easily identifiable english name such as Carbon 1.
	def add_mapped_address(self, entity):
		if not type(entity) == Atom:
			# is bond
			type_is = CONSTANT.BOND_NAMES_ARR[entity.get_electron_bond_cost()] # string of type
		else:
			# is atom
			type_is = entity.get_type_full()

		entity_is_mapped: bool = False
		entity_type_is_mapped: bool = False
		try:
			self.mapped_address[str(hex(id(entity)))]
			entity_is_mapped = True
		except KeyError:
			# Obj Address DNE, check count of atoms in tree
			entity_is_mapped = False

		try:
			self.mapped_address_counts[type_is]
			entity_type_is_mapped = True
		except KeyError:
			entity_type_is_mapped = False

		if not entity_type_is_mapped:
			# initialize count dictionary
			self.mapped_address_counts[type_is] = 0
		if not entity_is_mapped:
			# get and update atom count
			count = self.mapped_address_counts[type_is]
			count += 1
			self.mapped_address_counts[type_is] = count

			# map atom address to the correct atom type number
			self.mapped_address[str(hex(id(entity)))] = type_is + ' ' + str(count)

	def remove_mapped_address(self, entity):
		address = hex(id(entity))
		count: int

		# get type
		if not type(entity) == Atom:
			# bond
			type_is = CONSTANT.BOND_NAMES_ARR[entity.get_electron_bond_cost()] # string of type
		else:
			# atom
			type_is = entity.get_type_full()

		# remove mapping and decrement/remove count
		try:
			self.mapped_address.pop(address)

			count = self.mapped_address_counts[type_is]
			count -= 1

			if count <= 0:
				self.mapped_address_counts.pop(type_is)
			else:
				self.mapped_address_counts[type_is] = count
		except:
			pass

	# Returns list of bond objects connected to the passed atom
	def get_bonds_to_atom(self, atom: Atom) -> list[Bond]:
		bond_list = []
		does_atom_exist: bool = self.does_atom_exist_in_graph(atom)

		if does_atom_exist:
			set_of_atom_tuple = self.graph[atom]
			for atom_bond_tuple in set_of_atom_tuple:
				bond = atom_bond_tuple[1]
				bond_list.append(bond)
		else:
			pass

		return bond_list 

	def get_mapped_address(self):
		return self.mapped_address

	def get_mapped_address_counts(self):
		return self.mapped_address_counts

	def __str__(self):
		tempStr = ''

		for atom_as_key in self.graph.keys():
			atom_as_key_name = self.mapped_address[str(hex(id(atom_as_key)))]

			tempStr = tempStr + atom_as_key_name + '\t' + str(atom_as_key) + ' : \n{\n'

			# enumerate since sets are not iterable
			for index, tuple_of_atom_bond in enumerate(self.graph[atom_as_key]):
				tuple_atom_info = str(tuple_of_atom_bond[0])
				tuple_atom_name = self.mapped_address[str(hex(id(tuple_of_atom_bond[0])))]
				tuple_bond_info = str(tuple_of_atom_bond[1])
				tuple_bond_name = self.mapped_address[str(hex(id(tuple_of_atom_bond[1])))]

				if index == len(self.graph[atom_as_key]) - 1:
					tempStr = tempStr + "\t\t" + tuple_atom_name + '\t' + tuple_atom_info + "\t" + tuple_bond_name
				else:
					tempStr = tempStr + "\t\t" + tuple_atom_name + '\t' + tuple_atom_info + "\t" + tuple_bond_name + ",\n"
			
			tempStr += "\n}\n\n"

		return tempStr
		
