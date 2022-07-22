import datetime
import settings


def to_binary(string):
	return ''.join(map(lambda x: format(ord(x), settings.binary_format)[2:], string))


def to_string(binary):
	string = ""
	chars = len(binary) // settings.bits_in_byte
	for char in range(chars):
		pos = char * settings.bits_in_byte
		char_bits = binary[pos:pos + settings.bits_in_byte]
		string += chr(int(char_bits, 2))
	return string


def get_current_day():
	return datetime.datetime.now().weekday() + 1


def encrypt(string):
	binary = to_binary(string)
	shift_amount = get_current_day()
	binary = binary[-shift_amount:] + binary[:-shift_amount]
	return to_string(binary)


def decrypt(string):
	binary = to_binary(string)
	shift_amount = get_current_day()
	binary = binary[shift_amount:] + binary[:shift_amount]
	return to_string(binary)

