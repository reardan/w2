class Tokenizer:
	def __init__(self, filename) -> None:
		self.filename = filename
		self.source = ''
		self.source_index = 0
		self.nextc = ''
		self.token = []
		self.line_number = 1
		self.column_number = 1
		self.last_line = []
		self.line = []
		self.tab_level = 0
		self.token_newline = False

	def get_char(self):
		# End of stream
		if self.source_index >= len(self.source):
			return ''
		# Get next char from 
		char = self.source[self.source_index]
		self.source_index = self.source_index + 1
		return char
	
	def get_character(self):
		c = self.get_char()

		# Handle newline
		if c == '\n':
			self.tab_level = 0
			self.line_number += 1
			self.last_line = self.line
			self.line = []
		# Append to line
		else:
			self.line.append(c)

		# Handle tab
		if self.nextc == '\t':
			self.tab_level += 1

		return c

	def take_char(self):
		self.token.append(self.nextc)
		self.nextc = self.get_character()

	def read_until_end(self):
		while self.nextc != '\n' and self.nextc != '':
			self.take_char()
		# self.token.append('\0')

	def token_string(self):
		return ''.join(self.token)

	def get_token(self):
		self.token_newline = False
		w = True
		while True:
			w = False

			# Handle end of file
			if self.nextc == '':
				self.token_newline = True
				return

			# Handle whitespace
			while (self.nextc == ' ') or (self.nextc == '\t') or (self.nextc == '\n'):
				if self.nextc == '\n':
					self.token_newline = True
				
				self.nextc = self.get_character()
			
			self.token = []

			# Identifiers and Numbers
			# This should potentially be split up
			# E.g. could have '123asdf' which is not valid
			while self.nextc.isalnum():
				self.take_char()

			# Operators
			if len(self.token) == 0:
				while self.nextc in ['<', '=', '>', '|', '&', '!']:
					self.take_char()

			if len(self.token) == 0:
				if self.nextc in ['+', '-', '/', '%', '*']:
					self.take_char()

			# Braces (not used?)
			if len(self.token) == 0:
				if self.nextc in ['(', ')', ':']:
					self.take_char()

			# Strings (including comments)
			if len(self.token) == 0:
				# Basic Strings
				if self.nextc in ['`', '"', "'"]:
					string_char = self.nextc
					self.take_char()
					while self.nextc != string_char:
						self.take_char()
					self.take_char()

				# TODO: Block Strings

				# Line Comments
				elif self.nextc == '#':
					self.take_char()
					self.nextc = self.get_character()
					while self.nextc != '\n':
						self.nextc = self.get_character()
					w = True

			return self.source_index < len(self.source)
		
	def peek(self, string):
		if len(string) != len(self.token):
			return False
		for i in range(len(string)):
			if string[i] != self.token[i]:
				return False
		return True
	
	def accept(self, string):
		if self.peek(string):
			self.get_token()
			return True
		return False
	
	def accept_or_newline(self, string):
		if self.peek(string) or self.token_newline:
			self.get_token()
			return True
		return False
	
	def expect(self, string):
		if not self.accept(string):
			raise '"' + string + '" expected, found "' + ''.join(self.token) + '"'

	def expect_or_newline(self, string):
		if not self.accept(string) and not self.token_newline:
			raise Exception('"' + string +
		   '" or newline expected, found "' + ''.join(self.token) + '"' +
		   'on line ' + str(self.line_number)
			 )

	def expect_end(self):
		self.expect_or_newline(';')

	def read(self):
		f = open(self.filename, 'r', encoding='utf8')
		self.source = f.read()
		f.close()
