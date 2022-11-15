from scene import *

from .drawer import Drawer

from mym.descript import SequenceClassDescriptor


class TTLNode(EffectNode):
	drawer = Drawer()
	anchor_point = SequenceClassDescriptor("_anchor_point", Point)
	
	def __init__(self, text, font, anchor_point=Point(0.5, 0.5), *args, **kwargs):
		EffectNode.__init__(self, *args, **kwargs)
		self._suspend_updates = True
		self.effects_enabled = False
		self._inner = Node(parent=self)
		self._rendered_text = None
		self.text = text
		self.font = font
		self.anchor_point = anchor_point
		self._suspend_updates = False
		self.update_children()
	
	def __setattr__(self, name, value):
		EffectNode.__setattr__(self, name, value)
		if name == 'font':
			try:
				if not isinstance(value, str):
					raise TypeError('Font name must be a string')
			except TypeError:
				raise TypeError('Expected a font name')
		if name == 'font' or (name == 'text' and value != self._rendered_text):
			self.update_children()
		if name == 'anchor_point' and not self._suspend_updates:
			self.update_anchor()
		
	def update_children(self):
		if self._suspend_updates:
			return
		
		font_name = self.font
		get_tex = self.drawer.get_texture
		inner = self._inner
		
		for charnode in list(inner.children):
			charnode.remove_from_parent()
		
		next_pos = Point()
		font = self.drawer.get_font(font_name)
		line_height = font.size * 1.15
		
		for char in self.text:
			if char.isspace():
				if char == '\n':
					next_pos.x = 0
					next_pos.y -= line_height
					continue
				w = font.getsize(char)[0]
				if char == ' ':
					w *= 0.57
				next_pos.x += w
				continue
			
			texture = get_tex(font_name, char)
			node = SpriteNode(
				texture,
				anchor_point=(0, 1),
				position=next_pos,
				parent=inner
			)
			next_pos.x += node.size.w * 0.95
		self._rendered_text = self.text
		self.update_anchor()
	
	def update_anchor(self):
		x, y = self._anchor_point
		self._inner.position = self._inner.bbox.size * Point(-x, 1.0 - y)
