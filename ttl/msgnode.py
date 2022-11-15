from scene import *

from .commands import Command, cmd_compile
from .drawer import Drawer

from mym.descript import GetDescriptor, SequenceClassDescriptor


class MsgNode(EffectNode):
	drawer = Drawer()
	text = GetDescriptor("_text")
	# font = GetDescriptor("_font")
	anchor_point = SequenceClassDescriptor("_anchor_point", Point)
	
	def __init__(self, text, font, anchor_point=Point(0.5, 0.5), *args, **kwargs):
		EffectNode.__init__(self, *args, **kwargs)
		self.effects_enabled = False
		self._inner = Node(parent=self)
		self.anchor_point = anchor_point
		self.reset(text, font)
	
	def __setattr__(self, name, value):
		EffectNode.__setattr__(self, name, value)
		if name == "anchor_point":
			self.update_anchor()
	
	def reset(self, text, font):
		for charnode in list(self._inner.children):
			charnode.remove_from_parent()
		self._text = text
		self.font = font
		self.line_height = self.drawer.get_font(font).size * 1.15
		self._text_list = cmd_compile(text)
		self._list_index = 0
		self._text_index = 0
		self._next_pos = Point()
		self._filters = {}
		self._data_map = {}
	
	def _get_current_data(self):
		try:
			return self._text_list[self._list_index]
		except IndexError:
			return None
	
	def next(self):
		data = self._get_current_data()
		if data is None:
			self._filters = {}
			self._data_map = {}
			return False
		
		if isinstance(data, str):
			# data: String
			self._draw_text(data)
		else:
			# data: Command
			self._execute_command(data)
			self.next(raise_error)
		return True
	
	def _draw_text(self, text):
		char = text[self._text_index]
		self._draw_char(char)
		self._text_index += 1
		if len(text) > self._text_index:
			return
		self._text_index = 0
		self._next_end()
	
	def _execute_command(self, command):
		command.execute(self, *command.args, **command.kwargs)
		self._next_end()
	
	def _next_end(self):
		self._list_index += 1
		self._test_command()
	
	def _test_command(self):
		data = self._get_current_data()
		if isinstance(data, Command):
			self._execute_command(data)
	
	def _draw_char(self, char):
		font = self.drawer.get_font(self.font)
		
		if char.isspace():
			if char == '\n':
				self._next_pos.x = 0
				self._next_pos.y -= self.line_height
				return
			w = font.getsize(char)[0]
			if char == ' ':
				w *= 0.57
			self._next_pos.x += w
			return
		
		texture = self.drawer.get_texture(self.font, char)
		node = SpriteNode(
			texture,
			anchor_point=(0, 1),
			position=self._next_pos,
			parent=self._inner
		)
		for filter in self._filters.values():
			filter(node)
		self._next_pos.x += node.size.w * 0.95
		self.update_anchor()
	
	def update_anchor(self):
		x, y = self._anchor_point
		self._inner.position = self._inner.bbox.size * Vector2(-x, 1.0 - y)
	
	# cmd-interface:
	
	def add_filter(self, key, callback):
		self._filters[key] = callback
	
	def remove_filter(self, key):
		if key in self._filters:
			del self._filters[key]
			return True
		return False
	
	def get_data(self, key):
		return self._data_map.get(key)
	
	def set_data(self, key, data):
		self._data_map[key] = data
	
	def delete_data(self, key):
		if key in self._data_map:
			del self._data_map[key]
			return True
		return False
	
	def set_next_pos(self, x=None, y=None):
		next_x, next_y = self._next_pos
		if x is not None:
			next_x = x
		if y is not None:
			next_y = y
		self._next_pos = Point(next_x, next_y)
	
	def offset_next_pos(self, x, y):
		self._next_pos += Point(x, y)
