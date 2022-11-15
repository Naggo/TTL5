from scene import *
import colorsys

from .cmdbase import *


@cmd_register('c')
class ColorCommand(Command):
	"""色を変更する"""
	
	def __init__(self, color):
		super().__init__(color)
	
	def execute(self, node, color):
		def filter(charnode):
			charnode.color = color
		node.add_filter('c', filter)
	
	def end(self, node):
		node.remove_filter('c')


@cmd_register('C')
class ShortColorCommand(ColorCommand):
	"""色を変更する(省略)"""
	
	_colors = {
		'R': "#ff0000",
		'G': "#00ff00",
		'B': "#0000ff",
		"C": "#00ffff",
		"M": "#ff00ff",
		"Y": "#ffff00",
		"0": "#000000",
		"W": "#ffffff"
	}
	
	def compile(self, color):
		return ColorCommand(self._colors[str(color).upper()])


@cmd_register('f')
class FontCommand(Command):
	"""フォントを変更する"""
	
	def __init__(self, font):
		super().__init__(font)
	
	def execute(self, node, font):
		node.set_data('f', node.font)
		node.font = font
	
	def end(self, node):
		data = node.get_data('f')
		if data is not None:
			node.font = data


@cmd_register('lh')
class LineHeightCommand(Command):
	"""行の高さを変更する"""
	
	def __init__(self, height=None):
		super().__init__(height)
	
	def execute(self, node, height):
		node.set_data('lh', node.line_height)
		if height is None:
			height = node.drawer.get_font(node.font).size * 1.15
		node.line_height = height
	
	def end(self, node):
		data = node.get_data('lh')
		if data is not None:
			node.line_height = data


@cmd_register('m')
class MoveCommand(Command):
	"""文字の位置を移動する"""
	
	def __init__(self, x, y):
		super().__init__(x, y)
	
	def execute(self, node, x, y):
		pos = node.get_data('m')
		if pos is None:
			px = py = 0
		else:
			px, py = pos
		node.set_data('m', (px+x, py+y))
		node.offset_next_pos(x, y)
	
	def end(self, node):
		pos = node.get_data('m')
		if pos is not None:
			node.offset_next_pos(-pos[0], -pos[1])


@cmd_register('rbc')
class RainbowColorCommand(Command):
	"""虹色にする"""
	
	def __init__(self, idx=0):
		super().__init__(idx)
	
	def execute(self, node, idx):
		def generator(i):
			while True:
				yield colorsys.hsv_to_rgb(i / 12, 1, 1)
				i = (i + 1) % 12
		rainbow_gen = generator(idx % 12)
		
		def filter(charnode):
			charnode.color = next(rainbow_gen)
		node.add_filter('rb', filter)
	
	def end(self, node):
		node.remove_filter('rb')
