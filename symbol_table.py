class Symbol:
	def __init__(self, name, symbol_type):
		self.name = name
		self.symbol_type = symbol_type


class Type(Symbol):
	def __init__(self, name, size, signed=False):
		"""size is in bytes."""
		super().__init__(name, 'Type')
		self.size = size
		self.signed = signed


class Function(Symbol):
	def __init__(self, name, return_type, start_address):
		super().__init__(name, 'Function')
		self.return_type = return_type
		self.start_address = start_address
		# Size will be updated later once the full function size is calculated
		self.size = 0
		self.arguments = []

		# Scope is added once the function is declared
		self.scope = None


class Variable(Symbol):
	def __init__(self, name, variable_type, sub_type, pointer_level=0, array_count=0):
		super().__init__(name, 'Variable')
		self.variable_type = variable_type
		self.sub_type = sub_type
		self.pointer_level = pointer_level
		self.array_count = array_count

	def __str__(self):
		return f'Variable("{self.name}" [{self.variable_type.name}{"*" * self.pointer_level}] stack:{self.stack_position})'  

	def __repr__(self):
		return str(self)

class Scope(dict):
	def __init__(self, scope_type) -> None:
		self.scope_type = scope_type
		self.table = {}


class SymbolTable:
	def __init__(self) -> None:
		self.table = []

		# Add the root scope
		self.add_scope('global')

	def add_scope(self, scope_type):
		scope = Scope(scope_type)
		self.table.append(scope)
		return scope

	def drop_scope(self):
		return self.table.pop()

	def lookup(self, name):
		for scope in reversed(self.table):
			if name in scope:
				return scope[name]
			
		return None

	def declare(self, symbol):
		self.table[-1][symbol.name] = symbol
