#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.py3compat import *
from libopensesame import sketchpad_elements
from libopensesame.exceptions import osexception
from libopensesame.item import item
from libopensesame.generic_response import generic_response
from openexp.canvas import canvas

class sketchpad(item, generic_response):

	"""
	desc:
		The runtime part of the sketchpad item.
	"""

	description = u'Displays stimuli'

	def reset(self):

		"""See item."""

		self.var.duration = u'keypress'
		self.elements = []

	def element_module(self):

		"""
		desc:
			Determines the module to be used for the element classes. The
			runtime and GUI use different modules.

		returns:
			desc:	A module containing sketchpad-element classes
			type:	module
		"""

		return sketchpad_elements

	def from_string(self, string):

		"""
		desc:
			Parses a definition string.

		arguments:
			string:		A definition string.
		"""

		self.variables = {}
		self.comments = []
		self.reset()
		if string is None:
			return
		for line in string.split(u'\n'):
			if self.parse_variable(line):
				continue
			cmd, arglist, kwdict = self.syntax.parse_cmd(line)
			if cmd != u'draw':
				continue
			if len(arglist) == 0:
				raise osexception(u'Incomplete draw command: \'%s\'' % line)
			element_type = arglist[0]
			if not hasattr(self.element_module(), element_type):
				raise osexception(
					u'Unknown sketchpad element: \'%s\'' % element_type)
			element_class = getattr(self.element_module(), element_type)
			element = element_class(self, line)
			self.elements.append(element)
		self.elements.sort(key=lambda element: -element.z_index)

	def prepare(self):

		"""
		desc:
			Prepares the canvas.
		"""

		super(sketchpad, self).prepare()
		generic_response.prepare(self)
		self.canvas = canvas(self.experiment, color=self.var.foreground,
			background_color=self.var.background, auto_prepare=False)
		for element in self.elements:
			if element.is_shown():
				element.draw()
		self.canvas.prepare()

	def run(self):

		"""
		desc:
			Shows the canvas and implements the duration.
		"""

		self.set_item_onset(self.canvas.show())
		self.set_sri(False)
		self.process_response()

	def to_string(self):

		"""
		desc:
			Generates a string representation for the sketchpad.

		returns:
			A string representation.
		"""

		s = super(sketchpad, self).to_string()
		for element in self.elements:
			s += u'\t%s\n' % element.to_string()
		return s

	def var_info(self):

		"""
		desc:
			Returns a list of dictionaries with variable descriptions.

		returns:
			A list of (name, description) tuples.
		"""

		l = item.var_info(self)
		if self.var.get(u'duration', _eval=False, default=u'') in \
			[u'keypress', u'mouseclick']:
			l += generic_response.var_info(self)
		return l
