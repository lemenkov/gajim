##	plugins/history_window.py
##
## Gajim Team:
##	- Yann Le Boulanger <asterix@lagaule.org>
##	- Vincent Hanquez <tab@snarc.org>
##	- Nikos Kouremenos <kourem@gmail.com>
##
##	Copyright (C) 2003-2005 Gajim Team
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 2 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##

import gtk
import gtk.glade
import time

from common import gajim
from common import i18n

_ = i18n._
APP = i18n.APP
gtk.glade.bindtextdomain(APP, i18n.DIR)
gtk.glade.textdomain(APP)

GTKGUI_GLADE='gtkgui.glade'

class History_window:
	"""Class for bowser agent window:
	to know the agents on the selected server"""
	def on_history_window_destroy(self, widget):
		"""close window"""
		del self.plugin.windows['logs'][self.jid]

	def on_close_button_clicked(self, widget):
		"""When Close button is clicked"""
		widget.get_toplevel().destroy()

	def on_earliest_button_clicked(self, widget):
		start, end = self.history_buffer.get_bounds()
		self.history_buffer.delete(start, end)
		self.earliest_button.set_sensitive(False)
		self.previous_button.set_sensitive(False)
		self.forward_button.set_sensitive(True)
		self.latest_button.set_sensitive(True)
		end = 50
		if end > self.nb_line:
			end = self.nb_line
		nb, lines = gajim.logger.read(self.jid, 0, end)
		self.set_buttons_sensitivity(nb)
		for line in lines:
			self.new_line(line[0], line[1], line[2:])
		self.num_begin = 0

	def on_previous_button_clicked(self, widget):
		start, end = self.history_buffer.get_bounds()
		self.history_buffer.delete(start, end)
		self.earliest_button.set_sensitive(True)
		self.previous_button.set_sensitive(True)
		self.forward_button.set_sensitive(True)
		self.latest_button.set_sensitive(True)
		begin = self.num_begin - 50
		if begin < 0:
			begin = 0
		end = begin + 50
		if end > self.nb_line:
			end = self.nb_line
		nb, lines = gajim.logger.read(self.jid, begin, end)
		self.set_buttons_sensitivity(nb)
		for line in lines:
			self.new_line(line[0], line[1], line[2:])
		self.num_begin = begin

	def on_forward_button_clicked(self, widget):
		start, end = self.history_buffer.get_bounds()
		self.history_buffer.delete(start, end)
		self.earliest_button.set_sensitive(True)
		self.previous_button.set_sensitive(True)
		self.forward_button.set_sensitive(True)
		self.latest_button.set_sensitive(True)
		begin = self.num_begin + 50
		if begin > self.nb_line:
			begin = self.nb_line
		end = begin + 50
		if end > self.nb_line:
			end = self.nb_line
		nb, lines = gajim.logger.read(self.jid, begin, end)
		self.set_buttons_sensitivity(nb)
		for line in lines:
			self.new_line(line[0], line[1], line[2:])
		self.num_begin = begin

	def on_latest_button_clicked(self, widget):
		start, end = self.history_buffer.get_bounds()
		self.history_buffer.delete(start, end)
		self.earliest_button.set_sensitive(True)
		self.previous_button.set_sensitive(True)
		self.forward_button.set_sensitive(False)
		self.latest_button.set_sensitive(False)
		begin = self.nb_line - 50
		if begin < 0:
			begin = 0
		nb, lines = gajim.logger.read(self.jid, begin, self.nb_line)
		self.set_buttons_sensitivity(nb)
		for line in lines:
			self.new_line(line[0], line[1], line[2:])
		self.num_begin = begin

	def set_buttons_sensitivity(self, nb):
		if nb == 50:
			self.earliest_button.set_sensitive(False)
			self.previous_button.set_sensitive(False)
		if nb == self.nb_line:
			self.forward_button.set_sensitive(False)
			self.latest_button.set_sensitive(False)

	def new_line(self, date, type, data):
		"""write a new line"""
		start_iter = self.history_buffer.get_start_iter()
		end_iter = self.history_buffer.get_end_iter()
		tim = time.strftime('[%x %X] ', time.localtime(float(date)))
		self.history_buffer.insert(start_iter, tim)
		if type == 'recv':
			msg = ':'.join(data[0:])
			msg = msg.replace('\\n', '\n')
			self.history_buffer.insert_with_tags_by_name(start_iter, msg, \
				'incoming')
		elif type == 'sent':
			msg = ':'.join(data[0:])
			msg = msg.replace('\\n', '\n')
			self.history_buffer.insert_with_tags_by_name(start_iter, msg, \
				'outgoing')
		else:
			msg = ':'.join(data[1:])
			msg = msg.replace('\\n', '\n')
			self.history_buffer.insert_with_tags_by_name(start_iter, \
				_('Status is now: ') + data[0]+': ' + msg, 'status')
	
	def __init__(self, plugin, jid):
		self.plugin = plugin
		self.jid = jid
		self.nb_line = gajim.logger.get_nb_line(jid)
		xml = gtk.glade.XML(GTKGUI_GLADE, 'history_window', APP)
		self.window = xml.get_widget('history_window')
		self.history_buffer = xml.get_widget('history_textview').get_buffer()
		self.earliest_button = xml.get_widget('earliest_button')
		self.previous_button = xml.get_widget('previous_button')
		self.forward_button = xml.get_widget('forward_button')
		self.latest_button = xml.get_widget('latest_button')
		xml.signal_autoconnect(self)
		tagIn = self.history_buffer.create_tag('incoming')
		color = gajim.config.get('inmsgcolor')
		tagIn.set_property('foreground', color)
		tagOut = self.history_buffer.create_tag('outgoing')
		color = gajim.config.get('outmsgcolor')
		tagOut.set_property('foreground', color)
		tagStatus = self.history_buffer.create_tag('status')
		color = gajim.config.get('statusmsgcolor')
		tagStatus.set_property('foreground', color)
		begin = 0
		if self.nb_line > 50:
			begin = self.nb_line - 50
		nb, lines = gajim.logger.read(self.jid, begin, self.nb_line)
		self.set_buttons_sensitivity(nb)
		for line in lines:
			self.new_line(line[0], line[1], line[2:])
		self.num_begin = begin
		self.window.show_all()
