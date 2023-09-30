from Classes.graph import Graph
from Classes.bonds import Bond, SingleBond, DoubleBond, TripleBond
from Classes.atom import Atom
import Classes.constants as CONSTANT

class mapped_node:
	def __init__(self, x: int, y: int, width: int, height: int, type_is: str = 'unknown'):
		self.x = x
		self.y = y
		self.width = width
		self.height = height

		# set coordinate properties
		self.top_left_x = self.x
		self.top_left_y = self.y

		self.top_right_x = self.x + self.width
		self.top_right_y = self.y

		self.bottom_left_x = self.x
		self.bottom_left_y = self.y + self.height

		self.bottom_right_x = self.x + self.width
		self.bottom_right_y = self.y + self.height

		self.type_is = type_is
		self.related_edges = set()
	
	def contained_in_boundaries(self, x: float, y: float):
			matched: bool = False
			contained_within_x: bool = x > self.top_left_x and x < self.top_right_x
			contained_within_y: bool = y > self.top_left_y and y < self.bottom_left_y

			if contained_within_x and contained_within_y:
				matched = True

			return matched
	
	def __str__(self):
		temp_str = 'x: ' + str(self.x) + ', y: ' + str(self.y) + ', w: ' + str(self.width) + ', h: ' + str(self.height) + ', type: ' + self.type_is
		return temp_str
		

class mapped_edge:
	def __init__(self, x1: float, y1: float, x2: float, y2: float, perimeter_width: int, perimeter_height: int, type_is: str= 'unknown'):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.x_mid = abs(self.x1 - self.x2) + max(self.x1, self.x2)
		self.y_mid = abs(self.y1 - self.y2) + max(self.y1, self.y2)
		self.slope = (self.y2 -self.y1)/(self.x1 - self.x2)
		self.type_is = type_is

		self.perimeter_height = perimeter_height
		self.perimeter_width = perimeter_width
		# Perimeter box around the cartesian start point for the edge
		self.perimeter_start_point = {
			"top_left_x":(self.x1 - (self.perimeter_width/2)),		"top_left_y":(self.y1 - (self.perimeter_height/2)),
			"top_right_x":(self.x1 + (self.perimeter_width/2)),	"top_right_y":(self.y1 - (self.perimeter_height/2)),
			"bottom_left_x":(self.x1 - (self.perimeter_width/2)),	"bottom_left_y":(self.y1  + (self.perimeter_height/2)),
			"bottom_right_x":(self.x1 + (self.perimeter_width/2)),	"bottom_right_y":(self.y1 + (self.perimeter_height/2))
		   }
		# Perimeter box around the cartesian end point for the edge
		self.perimeter_end_point = {
			"top_left_x":(self.x2 - (self.perimeter_width/2)),		"top_left_y":(self.y2 - (self.perimeter_height/2)),
			"top_right_x":(self.x2 + (self.perimeter_width/2)),	"top_right_y":(self.y2 - (self.perimeter_height/2)),
			"bottom_left_x":(self.x2 - (self.perimeter_width/2)),	"bottom_left_y":(self.y2  + (self.perimeter_height/2)),
			"bottom_right_x":(self.x2 + (self.perimeter_width/2)),	"bottom_right_y":(self.y2 + (self.perimeter_height/2))
		   }
		# Perimeter box around the cartesian mid point for the edge
		self.perimeter_mid_point = {
			"top_left_x":(self.x_mid - (self.perimeter_width/2)),		"top_left_y":(self.y_mid - (self.perimeter_height/2)),
			"top_right_x":(self.x_mid + (self.perimeter_width/2)),	"top_right_y":(self.y_mid - (self.perimeter_height/2)),
			"bottom_left_x":(self.x_mid - (self.perimeter_width/2)),	"bottom_left_y":(self.y_mid  + (self.perimeter_height/2)),
			"bottom_right_x":(self.x_mid + (self.perimeter_width/2)),	"bottom_right_y":(self.y_mid + (self.perimeter_height/2))
		   }
		# Contains edges that are related in double or triple bonding
		self.related_edges = set()
		self.related_nodes = set()

	# Determines if passed cartesian point exist within the edge's start or end perimeter boxes
	def contained_within_perimeter_endpoints(self, x: float, y: float):
			matched: bool = False
			
			contained_within_x_perimeter_one: bool = x > self.perimeter_start_point["top_left_x"] and x < self.perimeter_start_point["top_right_x"]
			contained_within_y_perimeter_one: bool = y > self.perimeter_start_point['top_left_y'] and y < self.perimeter_start_point['bottom_left_y']
			contained_within_x_perimeter_two: bool = x > self.perimeter_end_point['top_left_x'] and x < self.perimeter_end_point['top_right_x']
			contained_within_y_perimeter_two: bool = y > self.perimeter_end_point['top_left_y'] and y < self.perimeter_end_point['bottom_left_y']

			if \
			contained_within_x_perimeter_one and contained_within_y_perimeter_one or \
			contained_within_x_perimeter_two and contained_within_y_perimeter_two:
				matched = True

			return matched
	
	# Determines if passed cartesian point exist within the edge's midpoint perimeter box
	def contained_within_perimeter_midpoint(self, x: float, y: float):
			matched: bool = False
			
			contained_within_x_perimeter_one: bool = \
				x > self.perimeter_mid_point["top_left_x"] - 20 and \
				x < self.perimeter_mid_point["top_right_x"] + 20
			contained_within_y_perimeter_one: bool = \
				y > self.perimeter_mid_point['top_left_y'] - 20 and \
				y < self.perimeter_mid_point['bottom_left_y'] + 20
	
			if contained_within_x_perimeter_one and contained_within_y_perimeter_one:
				matched = True

			return matched
	
	# Determines type edge, should only be used after processing functions are applied (eg: minmize_bond_list_by_midpoint)
	def determine_type(self):
		if len(self.related_edges) == 0:
			self.type_is = 'Single Bond'
		elif len(self.related_edges) == 1:
			self.type_is = 'Double Bond'
		elif len(self.related_edges) == 2:
			self.type_is = 'Triple Bond'
		else:
			self.type_is = 'Error'

	# Updates the edge's "related_edges" property (via midpoint analysis)
	# to contain only those edges most likely to contribute to double or triple bonding
	def minimize_bond_list_by_midpoint(self):
		matched_midpoint_edges = set()

		for edge in self.related_edges:
			if self.contained_within_perimeter_midpoint(edge.x_mid, edge.y_mid):
				matched_midpoint_edges.add(edge)
		
		self.related_edges = matched_midpoint_edges


	def __str__(self):
		temp_str = '(' + str(self.x1) + ', ' + str(self.y1) + '), ' + '(' + str(self.x2) + ', ' + str(self.y2) + ') m=' + str(self.slope) + ' type:' + self.type_is
		return temp_str
			

def translate_molecule(mapped_edge_arr: list[mapped_edge], mapped_node_arr: list[mapped_node])->Graph:
	bonds = []
	partial_bonded_structures = []
	unbound_atoms = []
	node_atom_dict = dict()

	for node in mapped_node_arr:
		if (Atom.is_atom(node.type_is) or Atom.is_polyatomic(node.type_is)):
			# Node is single atom or polyatomic (treated as one atom)
			
			atom_to_map = Atom(node.type_is)
			atom_to_map.set_mapped_position((node.top_left_x+node.bottom_right_x)/2, (node.top_left_y+node.bottom_right_y)/2)
			unbound_atoms.append(atom_to_map)
			node_atom_dict[node] = atom_to_map # map node-->atom for bonding later
		else:
			# multiple atoms but not polyatomic, breakup into individual atoms and connect those atoms via bonding

			type_list = breakup_multi_atom_node(node)
			main_atom_type = probable_main_atom(type_list)
			atoms_in_node: list[Atom] = []

			# create main atom, remove from list, and connect to node
			main_atom = Atom(main_atom_type)
			main_atom.set_mapped_position((node.top_left_x+node.bottom_right_x)/2, (node.top_left_y+node.bottom_right_y)/2)
			type_list.remove(main_atom_type)
			node_atom_dict[node] = main_atom # will be the connecting atom of the partial structure to the overall molecule

			# create atom list for function, connect_atoms_to_main
			for letter in type_list:
				try:
					atoms_in_node.append(Atom(letter))
				except NameError:
					pass

			# store partial structures to be combined later
			partial_bonded_structures.append(connect_atoms_to_main(atoms_in_node, main_atom))

			# main atom needs to connect to overall structure
			unbound_atoms.append(main_atom)
	
	# connect edges to nodes (now represented as atoms)
	for edge in mapped_edge_arr:
		if len(edge.related_nodes) == 2:
			try:
				# set used, unordered, therfore enumerate
				for index, node in enumerate(edge.related_nodes):
					if index == 0:
						node_one = node
					if index == 1:
						node_two = node

				# get atom from node, create bond
				if edge.type_is == 'Single Bond':
					bonds.append(SingleBond(node_atom_dict[node_one], node_atom_dict[node_two]))
				elif edge.type_is == 'Double Bond':
					bonds.append(DoubleBond(node_atom_dict[node_one], node_atom_dict[node_two]))
				elif edge.type_is == 'Triple Bond':
					try:
						bonds.append(TripleBond(node_atom_dict[node_one], node_atom_dict[node_two]))
					except:
						pass
			except KeyError:
				pass
			except:
				pass
		else:
			pass


	# combine into one bond list
	for bond_list in partial_bonded_structures:
		for bond in bond_list:
			bonds.append(bond)
	
	# produce graph
	recognized_graph = Graph(bonds)
	recognized_graph.add_nodes_via_atom_list(unbound_atoms)

	#remove unbonded carbons
	#atoms_to_remove = []
	#list_of_atoms = recognized_graph.get_atom_list()
	#for atom in list_of_atoms:
	#	if atom.get_type() == "C" and len(recognized_graph.get_bonds_to_atom(atom)) == 0:
	#		atoms_to_remove.append(atom)
	#recognized_graph.delete_atoms_via_atom_list(atoms_to_remove)

	return recognized_graph

	
def breakup_multi_atom_node(node: mapped_node)-> list[Atom]:
	explicit_node_type: list[str] = []
	n_digits = 1
	index = len(node.type_is) - 1

	# create explicit representation of the atoms in the string. Eg: instead of H2Cl2-->[H, H, Cl, Cl]
	while (index >= 0):
		if (node.type_is[index].isdigit()):
			n_digits = int(node.type_is[index])
			index -= 1
		else:
			try:
				# 1-char atom symbol
				CONSTANT.ATOM_SYMBOL_TO_NAME_DICT[node.type_is[index]]
				for value in range(0, n_digits, 1):
					explicit_node_type.append(node.type_is[index])
				index -= 1
			except KeyError:
				# 2-char atom symbol
				if index >= 1:
					CONSTANT.ATOM_SYMBOL_TO_NAME_DICT[str(node.type_is[index-1]) + str(node.type_is[index])]
					for value in range(0, n_digits, 1):
						explicit_node_type.append(str(node.type_is[index-1]) + str(node.type_is[index]))
					index = index - 2
			finally:
				n_digits = 1

	return explicit_node_type

def probable_main_atom(atom_list: list[str]) -> str:
	bonding_atom = ''

	probable_bonding_count = {
		'C':0,
		'N':0,
		'O':0,
		'S': 0,
		'B': 0,
		'P': 0
	}

	for letter in atom_list:
		try:
			atom_count = probable_bonding_count[letter]
			atom_count += 1
			probable_bonding_count[letter] = atom_count
		except KeyError:
			# not bonding atom, do nothing
			pass
			

	# Anticipated bonding precedence
	if probable_bonding_count['C'] > 0:
		bonding_atom = 'C'
	elif probable_bonding_count['N'] > 0:
		bonding_atom = 'N'
	elif probable_bonding_count['O'] > 0:
		bonding_atom = 'O'
	elif probable_bonding_count['P'] > 0:
		bonding_atom = 'P'
	elif probable_bonding_count['S'] > 0:
		bonding_atom = 'S'
	elif probable_bonding_count['B'] > 0:
		bonding_atom = 'B'

	return bonding_atom

def connect_atoms_to_main(atoms_to_connect:list[Atom], main_atom: Atom)->list[Bond]:
	bond_list = []

	# for now, bond everything to main. Should cover the majority of cases.
	for atom in atoms_to_connect:
		try:
			bond_list.append(SingleBond(main_atom, atom))
		except:
			break

	return bond_list