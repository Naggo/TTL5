from PIL import Image, ImageDraw, ImageFont
from collections.abc import Sequence, Mapping
import scene

from mym.img2tex import img2tex


def getfontdata(arg) -> ImageFont.FreeTypeFont:
	"""
	Return font data based on argument.
	"""
	if isinstance(arg, ImageFont.FreeTypeFont):
		return arg
	elif isinstance(arg, str):
		return ImageFont.truetype(arg)
	elif isinstance(arg, Sequence):
		return ImageFont.truetype(*arg)
	elif isinstance(arg, Mapping):
		return ImageFont.truetype(**arg)
	else:
		raise TypeError(
			"argument must be arguments of ImageFont.truetype(), "
			"not '{}'".format(type(arg).__name__)
		)


def UnknownFontError(name: str) -> ValueError:
	return ValueError("Unknown font: '{}'".format(name))


class Drawer():
	def __init__(self):
		self.fonts = {}
		self.textures = {}
	
	def get_font(self, name) -> ImageFont.FreeTypeFont:
		return self._get_fontdata(name)[0]
	
	def get_texture(self, name, char) -> scene.Texture:
		"""
		テクスチャを参照する。無かった場合は生成する。
		"""
		textures = self._get_textures(name)
		if char not in textures:
			textures[char] = self._make_texture(name, char)
		return textures[char]
	
	def register_font(self, name, font, filtering_mode=0):
		self.fonts[name] = (getfontdata(font), filtering_mode)
		self.textures[name] = {}
	
	def has_font(self, name) -> bool:
		return name in self.fonts
	
	def reserve_textures(self, name, string):
		"""
		指定した文字のテクスチャを生成する。
		"""
		textures = self._get_textures(name)
		for char in string:
			textures[char] = self._make_texture(name, char)
	
	def apply_preset(self, name, string):
		"""
		指定した文字のテクスチャを生成し、それ以外を削除する。
		"""
		textures = self._get_textures(name)
		for key in textures.keys():
			if key not in string:
				del textures[key]
		for char in string:
			if char not in textures:
				textures[char] = self._make_texture(name, char)
	
	def remove_font(self, name=None):
		if name is not None:
			del self.fonts[name]
		else:
			self.fonts.clear()
	
	def remove_textures(self, name=None):
		if name is not None:
			del self.textures[name]
		else:
			self.textures.clear()
	
	def remove_all(self, name=None):
		self.remove_font(name)
		self.remove_textures(name)
	
	def _get_fontdata(self, name) -> tuple:
		if self.has_font(name):
			return self.fonts[name]
		raise UnknownFontError(name)
	
	def _get_textures(self, name) -> dict:
		if name not in self.textures:
			if self.has_font(name):
				self.textures[name] = {}
			else:
				raise UnknownFontError(name)
		return self.textures[name]
	
	def _make_texture(self, name, char) -> scene.Texture:
		"""
		テクスチャを生成して返す。
		"""
		if len(char) != 1:
			raise ValueError("char must be a character")
		font, filtering_mode = self._get_fontdata(name)
		size = font.getsize(char)
		img = Image.new("RGBA", size)
		draw = ImageDraw.Draw(img)
		draw.text((0, 0), char, font=font)
		tex = img2tex(img)
		tex.filtering_mode = filtering_mode
		return tex
