from collections.abc import Sequence, Mapping
from scene import *
import sound
import time
A = Action

from mym.ttl import MsgNode
from mym.ttl.cmdbase import Command, cmd_register


__all__ = ["AutoMsgNode", "add_commands"]


class AutoMsgNode(MsgNode):
	def reset(self, text, font):
		self.auto_stop()
		MsgNode.reset(self, text, font)
		self.interval = 0.033
		self._frame_count = 0.0
		self.set_soundeffect(None)
	
	def auto_start(self):
		if self._list_index == 0:
			self._test_command()
		act = A.repeat_forever(A.call(self._auto))
		self.run_action(act, "_AutoNext")
	
	def _auto(self):
		self._frame_count += self.scene.dt
		if self._frame_count > 0.0:
			self._play_effect()
			if not self.next():
				self.auto_stop()
				return
			self._frame_count -= self.interval
			while self._frame_count > 0.0:
				if not self.next():
					self.auto_stop()
					return
				self._frame_count -= self.interval
	
	def auto_stop(self):
		self.remove_action("_AutoNext")
	
	def set_soundeffect(self, *args, **kwargs):
		if not (args or kwargs) or args[0] is None:
			self._play_effect = lambda: None
		else:
			self._play_effect = lambda: sound.play_effect(*args, **kwargs)
	
	def set_cpf(self, characters_per_frame):
		self.interval = (self.scene.view.frame_interval / 60) / characters_per_frame


def add_commands():
	@cmd_register('i')
	class IntervalCommand(Command):
		"""表示間隔を変更する"""
		
		def __init__(self, interval):
			super().__init__(interval)
		
		def execute(self, node, interval):
			node.interval = interval
