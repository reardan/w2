import sys

from tokenizer import Tokenizer
from symbol_table import *


class Compiler:
	def __init__(self, filename) -> None:
		self.symbol_table = SymbolTable()

		# mapping of filename to Tokenizer object
		self.files = {}

		# filename being compiled
		self.root_filename = filename

		# word size of the platform in bytes
		# 4 * 8 = 32 bit platforms
		self.word_size = 4

		# Current tokenizer
		self.tokenizer = None

		# Start address of the code
		self.code_position = 0x00401000

		# Current position on the stack
		self.stack_position = 0

		# code output
		self.code = []

	def compile(self):
		self.define_base_types()
		self.define_linux_syscall()
		self.linux_asm_header()
		self.init_file(self.root_filename)
		self.module()

	def define_base_types(self):
		self.symbol_table.declare(Type('void', 0))

		self.symbol_table.declare(Type('char', 1))
		self.symbol_table.declare(Type('byte', 1))

		self.symbol_table.declare(Type('int', self.word_size))
		self.symbol_table.declare(Type('int8', 1))
		self.symbol_table.declare(Type('int16', 2))
		self.symbol_table.declare(Type('int32', 4))
		self.symbol_table.declare(Type('int64', 8))

		self.symbol_table.declare(Type('uint', self.word_size))
		self.symbol_table.declare(Type('uint8', 1))
		self.symbol_table.declare(Type('uint16', 2))
		self.symbol_table.declare(Type('uint32', 4))
		self.symbol_table.declare(Type('uint64', 8))

	def define_linux_syscall(self):
		self.symbol_table.declare(Function('syscall4', 'int', 0))

	def linux_asm_header(self):
		self.code.extend([
			'format ELF executable 3',
			'entry _main',
			'',
			'syscall4:',
			'mov eax,[esp+16]',
			'mov ebx,[esp+12]',
			'mov ecx,[esp+8]',
			'mov edx,[esp+4]',
			'int 0x80',
			'ret',
			'',
			'_main:',
			'call main',
			'mov ebx,eax',
			'mov eax,1',
			'int 0x80',
			'',
			])

	def init_file(self, filename):
		self.tokenizer = Tokenizer(filename)
		print('Compiling', filename)
		self.tokenizer.read()
		self.tokenizer.nextc = self.tokenizer.get_character()

	def expect_end(self):
		self.code.append(';' + ''.join(self.tokenizer.last_line))
		if False:
			self.code.append(f' stack:{self.stack_position}')
		self.code.append('\n')
		self.tokenizer.expect_end()

	def print_tokens(self):
		while self.tokenizer.get_token():
			print('Token:', ''.join(self.tokenizer.token))

		# Print last token:
		print('Token:', ''.join(self.tokenizer.token))

	def fail(self, message):
		print('Compilation failed for file ' + self.tokenizer.filename + ':' +
			str(self.tokenizer.line_number) + ':' + str(self.tokenizer.column_number))
		print(message)
		sys.exit(1)

	def expect_type_name(self):
		token = self.tokenizer.token_string()
		type_object = self.symbol_table.lookup(token)
		if not type_object:
			self.fail('Undefined type "' + token + '"')
		if type_object.symbol_type != 'Type':
			self.fail('Symbol is a "' + type_object.symbol_type +
	    	'", expected it to be a "Type"')
		self.tokenizer.get_token()
		return type_object

	def module(self):
		self.tokenizer.get_token()
		self.symbol_table.add_scope('Module')
		# Handle imports
		# Handle variable declarations
		# Handle function declarations
		while not self.tokenizer.end_of_file:
			self.function()

	def function(self):
		type_symbol = self.expect_type_name()
		identifier = self.tokenizer.token_string()
		self.tokenizer.get_token()
		if self.tokenizer.accept('('):
			function = Function(identifier, type_symbol, self.code_position)
			self.code.append(identifier + ':')
			self.symbol_table.declare(function)
			scope_level = len(self.symbol_table.table)
			function.scope = self.symbol_table.add_scope('Function')
			# Process arguments
			while not self.tokenizer.accept(')'):
				arg_type = self.expect_type_name()
				arg_identifier = self.tokenizer.token_string()
				variable = Variable(arg_identifier, arg_type, 'Argument')
				self.symbol_table.declare(variable)
				self.tokenizer.get_token()
				self.tokenizer.accept(',')
			
			self.statement()
			# ret()  # only put in if last statement is not a return
			function.size = self.code_position - function.start_address
			self.symbol_table.table = self.symbol_table.table[0:scope_level]

	def statement(self):
		if self.tokenizer.accept(':'):
			self.symbol_table.add_scope('Inner')
			stack_position = self.stack_position
			scope_level = len(self.symbol_table.table)
			start_tab_level = self.tokenizer.tab_level
			while start_tab_level <= self.tokenizer.tab_level and self.tokenizer.nextc != '':
				self.statement()
			# add/sub esp, stack_position - self.stack_position
			self.stack_position = stack_position
			self.symbol_table.table = self.symbol_table.table[0:scope_level]
		elif self.variable_declaration():
			pass
		elif self.tokenizer.accept('if'):
			pass
		elif self.tokenizer.accept('return'):
			self.expression()
			self.fix_stack()
			self.code.append('ret')
			self.expect_end()
		else:
			self.expression()
			self.expect_end()

	def fix_stack(self):
		if self.stack_position != 0:
			self.code.append('add esp,' + str(self.stack_position))
			self.stack_position = 0

	def variable_declaration(self):
		symbol = self.symbol_table.lookup(self.tokenizer.token_string())
		if not symbol or symbol.symbol_type != 'Type':
			return False
		self.tokenizer.get_token()
		name = self.tokenizer.token_string()
		identifier = self.symbol_table.lookup(name)
		if identifier:
			# TODO: add more descriptive error message
			# including where the variable is previously declared
			self.fail('variable "' + name + '" was previously declared')
		variable = Variable(name, 'local', '')
		identifier = self.symbol_table.declare(variable)
		self.tokenizer.get_token()

		# assignment
		if self.tokenizer.accept('='):
			self.expression()
			self.binary1()
			self.expect_end()
		else:
			self.code.append('push 0')
			self.stack_position += self.word_size
		variable.stack_position = self.stack_position
		return True


	def expression(self):
		self.additive_expression()
		if self.tokenizer.accept('='):
			pass
		pass

	def assignment_expression(self):
		if self.logical_or_expression():
			return True
		self.unary_expression()
		self.assignment_operator()
		self.assignment_epxression()

	def logical_or_expression(self):
		if self.logical_and_expression():
			return True
		self.logical_or_expression()
		self.tokenizer.expect('or')
		self.logical_and_expression()

	def logical_and_expression(self):
		if self.inclusive_or_expression():
			return True
		self.logical_and_expression()
		self.tokenizer.expect('and')
		self.bitwise_or_expression()

	def bitwise_or_expression(self):
		if self.bitwise_xor_expression(self):
			return True
		self.bitwise_or_expression()
		self.tokenizer.expect('|')
		self.bitwise_xor_expression()

	def bitwise_xor_expression(self):
		if self.bitwise_and_expression():
			return True
		self.bitwise_xor_expression()
		self.tokenizer.expect('^')
		self.bitwise_and_expression()
	
	def bitwise_and_expression(self):
		if self.equality_expression():
			return True
		self.bitwise_and_expression()
		self.tokenizer.expect('&')
		self.equality_expression()

	def equality_expression(self):
		if self.relational_expression():
			return True
		self.equality_expression()
		if self.tokenizer.accept('=='):
			pass
		elif self.tokenizer.accept('!='):
			pass
		else:
			self.fail('Problem in equality_expression()')
		
		self.relational_expression()
		return True

	def relational_expression(self):
		pass
	
	def shift_expression(self):
		pass

	def binary1(self):
		self.code.append('push eax')
		self.stack_position += self.word_size

	def binary2_pop(self):
		self.code.append('pop ebx')
		self.stack_position -= self.word_size

	def additive_expression(self):
		self.multiplicative_expression()
		while True:
			if self.tokenizer.accept('+'):
				self.binary1()
				self.multiplicative_expression()
				self.binary2_pop()
				self.code.append('add eax,ebx')
			elif self.tokenizer.accept('-'):
				self.binary1()
				self.multiplicative_expression()
				self.binary2_pop()
				self.code.append('sub ebx,eax')
				self.code.append('mov eax,ebx')
			else:
				return
	
	def multiplicative_expression(self):
		self.unary_expression()
		while True:
			if self.tokenizer.accept('*'):
				self.binary1()
				self.unary_expression()
				self.binary2_pop()
				self.code.append('imul eax,ebx')
			elif self.tokenizer.accept('/'):
				self.binary1()
				self.unary_expression()
				self.code.extend([
					'mov ebx,eax',
					'pop eax',
					'xor edx,edx',
					'idiv ebx',
				])
				self.stack_position -= self.word_size
			elif self.tokenizer.accept('%'):
				self.binary1()
				self.unary_expression()
				self.code.extend([
					'mov ebx,eax',
					'pop eax',
					'xor edx,edx',
					'idiv ebx',
					'mov eax,edx',
				])
				self.stack_position -= self.word_size
			else:
				return

	def unary_expression(self):
		if self.tokenizer.accept('&'):
			pass
		if self.tokenizer.accept('*'):
			pass
		if self.tokenizer.accept('!'):
			# this seems wrong
			# should it be expression?
			# c uses cast-expression
			# gut says expression
			self.multiplicative_expression()
			self.code.append('not eax')
			return
		self.postfix_expression()

	def postfix_expression(self):
		self.primary_expression()
		if self.tokenizer.accept('('):
			# TODO: make sure last_identifier is callable
			stack_position = self.stack_position
			if not self.tokenizer.accept(')'):
				# this would be nice to have in a repeat..until
				self.expression()
				self.binary1()
				while self.tokenizer.accept(','):
					self.expression()
					self.binary1()
				self.tokenizer.expect(')')
		# mov_eax_esp_plus((stack_pos - s - 1) << word_size_log2)
		# call_eax()
		# fix_stack:
		# be_pop(stack_pos - s)
		# stack_pos = s



	def primary_expression(self):
		if self.int_literal():
			pass

		elif self.identifier():
			identifier = self.current_identifier
			if identifier.symbol_type == 'Function':
				self.code.append('call ' + identifier.name)
			elif identifier.symbol_type == 'Variable':
				if identifier.variable_type == 'local':
					self.code.append('mov eax,[esp+' + str(self.stack_position-identifier.stack_position) + ']')
				# mov eax,[0x402000]  # global variable
			else:
				self.fail('Unprocesed symbol_type: ' + identifier.symbol_type)
			self.tokenizer.get_token()
			self.current_identifier = None
			return
		
		elif self.tokenizer.accept('('):
			self.expression()
			if not self.tokenizer.peek(')'):
				self.fail('No closing parenthesis')

		# TODO: char literal?
		# TODO: string literal

		else:
			self.fail('Could not find a valid primary expression, token: ' + self.tokenizer.token_string())

		self.tokenizer.get_token()
		return True

	def int_literal(self):
		negative = False
		n = 0
		if self.tokenizer.accept('-'):
			negative = True
			# This is potentially problematic because it could
			# accept '-' without doing anything
		
		token = self.tokenizer.token
		if not token:
			return False
		first = token[0]
		if first < '0' or first > '9':
			return False
		
		for c in token:
			n = (n << 1) + (n << 3) + int(c)

		if negative:
			n = 0 - n
		
		self.code.append('mov eax,' + str(n))
		return True

	def string_literal(self):
		pass

	def identifier(self):
		token = self.tokenizer.token_string()
		# Should this be stored like this?
		self.current_identifier = self.symbol_table.lookup(token)
		return self.current_identifier

	def output_asm(self):
		output_filename = ''.join(self.root_filename.split('.')[:-1]) + '.asm'
		f = open(output_filename, 'w', encoding='utf8')
		asm = '\n'.join(self.code)
		f.write(asm)
		f.close()


def main(argv):
	if len(argv) < 2:
		print('Please provide file to compile')
		print('For example:')
		print('  $ python w.py w.test')
		return
	filename = argv[1]
	compiler = Compiler(filename)
	compiler.compile()
	compiler.output_asm()


if __name__ == '__main__':
	main(sys.argv)
