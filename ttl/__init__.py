__version__ = "5.0.0"
__all__ = [
	"TTLNode",
	"MsgNode",
	"Drawer",
	
	"get_drawer",
	"register_font",
	"reserve_textures",
	"apply_preset",
	
	"cmd_compile"
]

from .drawer import Drawer
from .ttlnode import TTLNode
from .msgnode import MsgNode
from .cmdbase import cmd_compile

_drawer = Drawer()
TTLNode.drawer = _drawer
MsgNode.drawer = _drawer


def get_drawer() -> Drawer:
	return _drawer


register_font = _drawer.register_font
reserve_textures = _drawer.reserve_textures
apply_preset = _drawer.apply_preset
