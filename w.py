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

	def print_tokens(self):
		while self.tokenizer.get_token():
			print('Token:', ''.join(self.tokenizer.token))

		# Print last token:
		print('Token:', ''.join(self.tokenizer.token))

	def fail(self, message):
		print('Compilation failed for file ' + self.tokenizer.filename + ':' +
			self.tokenizer.line_number + ':' + self.tokenizer.column_number)
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
			
		elif self.tokenizer.accept('if'):
			pass
		elif self.tokenizer.accept('return'):
			self.expression()
			# TODO: Fix stack
			self.code.append('ret')
			self.tokenizer.expect_end()
		else:
			self.expression()
			self.tokenizer.expect_end()

	def expression(self):
		self.bitwise_or_expression()
		if self.tokenizer.accept('='):
			pass
		pass

	def bitwise_or_expression(self):
		self.primary_expression()

	def primary_expression(self):
		if self.int_literal():
			pass

		elif self.identifier():
			# mov eax,[esp+x]  # argument / local variable
			# mov eax,[0x402000]  # global variable
			print('identifier', self.identifier)
			self.tokenizer.get_token()
			self.current_identifier = None
			return
		
		elif self.tokenizer.accept('('):
			self.expression()
			if not self.tokenizer.peek(')'):
				self.fail('No closing parenthesis')

		else:
			self.fail('Could not find a valid primary expression, token: ' + self.tokenizer.token_string())

		# TODO: char literal?
		# TODO: string literal

		self.tokenizer.get_token()
		return

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
		return True

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
