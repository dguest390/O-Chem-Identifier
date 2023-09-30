# Bond costs for each atom in the bond
SINGLE_BOND_COST = 1
DOUBLE_BOND_COST = 2
TRIPLE_BOND_COST = 3
BOND_NAMES_ARR = ['IndexZeroPlaceholder', 'Single Bond', 'Double Bond', 'Triple Bond']

# Max electrons that an atom can hold
ATOM_FULL_ELEC_COUNT = {
    'B':8, 'C':8, 'c':8, 'N': 8, 'O':8, 'F':8,
    'Si':8, 'P':8, 'S':8, 'Cl':8, 
    'Br':8, 'H':2
}

# electrons that an atom has by default
ATOM_UNBONDED_VAL_ELEC_COUNT = {
    'B':3, 'C':4, 'c':4, 'N': 5, 'O':6, 'F':7,
    'Si':4, 'P':5, 'S':6, 'Cl':7,
    'Br':7, 'H':1
}

# mapping of atom name --> chemical symbol
ATOM_NAME_TO_SYMBOL_DICT = {
	"Hydrogen":"H", "Carbon": "C",
    "Boron":"B", "Nitrogen":"N", 
    "Oxygen":"O", "Fluorine":"F",
    "Silicon":"Si", 
    "Phosphorus":"P", "Sulfur":"S", 
    "Chlorine":"Cl", "Bromine":"Br"
}

# mapping of atom chemical symbol --> name
ATOM_SYMBOL_TO_NAME_DICT = {
    "H":"Hydrogen", "C":"Carbon",
    "B":"Boron", "N":"Nitrogen",
    "O":"Oxygen", "F":"Fluorine",
    "Si":"Silicon",
    "P":"Phosphorus", "S":"Sulfur",
    "Cl":"Chlorine", "Br":"Bromine"
}

# mapping of polyatomic symbol --> name (without charges)
POLYATOMIC_SYMBOL_TO_NAME_DICT = {
    'SO4': 'Sulfate',
    'HSO4': 'Hydrogen Sulfate',
    'SO3': 'Sulfite',
    'NO3': 'Nitrate',
    'NO2': 'Nitrite',
    'PO4': 'Phosphate',
    'HPO4': "Hydrogen Phosphate",
    'H2PO4': "Dihydrogen Phosphate",
    'PO3': 'Phosphite',
    'OH': 'Hydroxide',
    'ClO4': 'Perchlorate',
    'ClO3': 'Chlorate',
    'ClO2': 'Chlorite',
    'OCl': 'Hypochlorite',
    'CN': 'Cyanide',
    'OCN': 'Cyanate',
    'SCN': 'Thiocyanate',
    'CO3': 'Carbonate',
    'C2O4': 'Oxalate'
}

# mapping of polyatomic chemical symbol without charges --> base available electrons
POLYATOMIC_UNBONDED_VAL_ELEC_COUNT = {
    'SO4': 2,
    'HSO4': 1,
    'SO3': 2,
    'NO3': 1,
    'NO2': 1,
    'PO4': 3,
    'HPO4': 2,
    'H2PO4': 1,
    'PO3': 3,
    'OH': 1,
    'ClO4': 1,
    'ClO3': 1,
    'ClO2': 1,
    'OCl': 1,
    'CN': 1,
    'OCN': 1,
    'SCN': 1,
    'CO3': 2,
    'C2O4': 2
}

# mapping of polyatomic chemical symbol without charges --> max allowed electrons
POLYATOMIC_FULL_ELEC_COUNT = {
    'SO4': 4,
    'HSO4': 2,
    'SO3': 4,
    'NO3': 2,
    'NO2': 2,
    'PO4': 6,
    'HPO4': 4,
    'H2PO4': 2,
    'PO3': 6,
    'OH': 2,
    'ClO4': 2,
    'ClO3': 2,
    'ClO2': 2,
    'OCl': 2,
    'CN': 2,
    'OCN': 2,
    'SCN': 2,
    'CO3': 4,
    'C2O4': 4
}


# mapping of front end unicode representations of polyatomics --> chemical symbol (without charges)
FRONT_END_TO_BACKEND_POLYATOMIC = {
		"SO\u2084\u00B2\u207B": "SO4",
		"HSO\u2084\u207B": "HSO4",
		"SO\u2083\u00B2\u207B": "SO3",
		"NO\u2083\u207B": "NO3",
		"NO\u2082\u207B": "NO2",
		"PO\u2084\u207B\u00B3": "PO4",
		"HPO\u2084\u00B2\u207B": "HPO4",
		"H\u2082PO\u2084\u207B": "H2PO4",
		"PO\u2083\u207B\u00B3": "PO3",
		"OH\u207B": "OH",
		"ClO\u2084\u207B": "ClO4",
		"ClO\u2083\u207B": "ClO3",
		"ClO\u2082\u207B": "ClO2",
		"\u207BOCl": "OCl",
		"CN\u207B": "CN",
		"\u207BOCN": "OCN", 
		"SCN\u207B": "SCN" ,
		"CO\u2083\u00B2\u207B": "CO3",
		"C\u2082O\u2084\u207B\u00B2": "C2O4"
}

# mapping of front end unicode representations of polyatomics --> front end unicode representations without charges (but with subscripts)
POLYATOMIC_UNICODE_CHARGES_TO_POLYATOMIC_NO_CHARGES = {
		"SO\u2084\u00B2\u207B": "SO\u2084",
		"HSO\u2084\u207B": "HSO\u2084",
		"SO\u2083\u00B2\u207B": "SO\u2083",
		"NO\u2083\u207B": "NO\u2083",
		"NO\u2082\u207B": "NO\u2082",
		"PO\u2084\u207B\u00B3": "PO\u2084",
		"HPO\u2084\u00B2\u207B": "HPO\u2084",
		"H\u2082PO\u2084\u207B": "H\u2082PO\u2084",
		"PO\u2083\u207B\u00B3": "PO\u2083",
		"OH\u207B": "OH",
		"ClO\u2084\u207B": "ClO\u2084",
		"ClO\u2083\u207B": "ClO\u2083",
		"ClO\u2082\u207B": "ClO\u2082",
		"\u207BOCl": "OCl",
		"CN\u207B": "CN",
		"\u207BOCN": "OCN", 
		"SCN\u207B": "SCN",
		"CO\u2083\u00B2\u207B": "CO\u2083",
		"C\u2082O\u2084\u207B\u00B2": "C\u2082O\u2084"
}