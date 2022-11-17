import re


__all__ = ["Command", "get_cmd", "cmd_register", "cmd_compile"]


commands = {}


def args2str(args, kwargs):
	if args:
		result = ", ".join(repr(v) for v in args)
	else:
		result = ''
	if kwargs:
		if args:
			result += ", "
		result += ", ".join(
			"%s=%s" % (repr(k), repr(v)) for k, v in kwargs.items())
	return result


class Command():
	__slots__ = ["args", "kwargs"]
	_key = "!_Key"
	
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs
	
	def compile(self, *args, **kwargs):
		pass
	
	def execute(self, node, *args, **kwargs):
		pass
	
	def end(self, node, *args, **kwargs):
		pass
	
	def __str__(self):
		args = args2str(self.args, self.kwargs)
		if args:
			return "<{key}:{args}>".format(key=self._key, args=args.replace('>', '\>'))
		else:
			return "<{}>".format(self._key)
	
	def __repr__(self):
		args = args2str(self.args, self.kwargs)
		return "{cls}({args})".format(cls=type(self).__name__, args=args)


class EndCommand(Command):
	def __init__(self, cmd, *args, **kwargs):
		if isinstance(cmd, str):
			cmd = get_cmd(cmd)
		super().__init__(cmd, *args, **kwargs)
	
	def execute(self, node, cmd, *args, **kwargs):
		cmd.end(self, node, *args, **kwargs)
	
	def __str__(self):
		cmd = self.args[0]
		args = args2str(self.args[1:], self.kwargs)
		if args:
			return "</{key}:{args}>".format(key=cmd._key, args=args.replace('>', '\>'))
		else:
			return "</{}>".format(cmd._key)
	
	def __repr__(self):
		args = args2str((self.args[0]._key,) + self.args[1:], self.kwargs)
		return "{cls}({args})".format(cls=type(self).__name__, args=args)


def get_cmd(key: str) -> Command:
	return commands[key.strip()]


def cmd_register(key: str):
	if not isinstance(key, str):
		raise TypeError(
			"Missing arguments: key"
			"  Usage: @cmd_register(key: str)")
	key = key.strip()
	
	def decorator(cls):
		commands[key] = cls
		cls._key = key
		return cls
	return decorator


def _make_cmd(cmd: Command, args: str):
	"""
	コンストラクターあるいはcallableオブジェクトーに文字列の引数を渡す。
	引数の評価に失敗した場合、文字列をそのまま渡す。
	"""
	try:
		return eval("_cmd({})".format(args), {"__builtins__": {}}, {"_cmd": cmd})
	except (NameError, SyntaxError):
		return cmd(args.strip())


def _end_cmd_fromtext(text: str) -> EndCommand:
	if ':' in text:
		key, text_args = text.split(':', 1)
		args, kwargs = _make_cmd(lambda *args, **kwargs: (args, kwargs), text_args)
		return EndCommand(get_cmd(key), *args, **kwargs)
	else:
		return EndCommand(get_cmd(text))


def cmd_fromtext(text: str) -> Command:
	text = text[1:-1].replace('\>', '>')
	
	# end-command
	if text.startswith('/'):
		return _end_cmd_fromtext(text[1:])
	
	if ':' in text:
		key, text_args = text.split(':', 1)
		return _make_cmd(get_cmd(key), text_args)
	else:
		return get_cmd(text)()


def cmd_compile(string: str) -> list:
	"""
	<key> -> command
	<key:args> -> command with args
	</key> -> end-command
	<!key> -> nothing(comment)
	"""
	ptn = re.compile(r"((?<!\\)<.*?[^\\]>)", re.DOTALL)
	result = []
	for text in ptn.split(string):
		if text:
			if ptn.fullmatch(text):
				if text[1] != '!':
					cmd = cmd_fromtext(text)
					contents = cmd.compile(*cmd.args, **cmd.kwargs)
					if contents is None:
						result.append(cmd)
					elif isinstance(contents, list):
						result.extend(contents)
					else:
						result.append(contents)
			else:
				result.append(text.replace('\<', '<'))
	return result
