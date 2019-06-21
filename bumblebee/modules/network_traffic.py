#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Displays network traffic
"""

import psutil
import netifaces

import bumblebee.input
import bumblebee.output
import bumblebee.engine
import bumblebee.util

class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config)

        try:
            self._bandwidth = BandwidthInfo()

            self._download_tx = self._bandwidth.bytes_recv()
            self._upload_tx = self._bandwidth.bytes_sent()
        except:
            pass

    def update(self, widgets):
        try:
            download_tx = self._bandwidth.bytes_recv()
            upload_tx = self._bandwidth.bytes_sent()

            download_rate = (download_tx - self._download_tx)
            upload_rate = (upload_tx - self._upload_tx)

            self.update_widgets(widgets, download_rate, upload_rate)

            self._download_tx, self._upload_tx = download_tx, upload_tx
        except:
            pass

    def update_widgets(self, widgets, download_rate, upload_rate):
        del widgets[:]

        widgets.extend((
            TrafficWidget(text=download_rate, icon=''),
            TrafficWidget(text=upload_rate, icon='')
        ))


class BandwidthInfo(object):
    def bytes_recv(self):
        return self.bandwidth().bytes_recv

    def bytes_sent(self):
        return self.bandwidth().bytes_sent

    def bandwidth(self):
        io_counters = self.io_counters()
        return io_counters[self.default_network_adapter()]

    def default_network_adapter(self):
        gateway = netifaces.gateways()['default']

        if (len(gateway) == 0):
            raise 'No default gateway found'

        return gateway[netifaces.AF_INET][1]

    def io_counters(self):
        return psutil.net_io_counters(pernic=True)


class TrafficWidget(object):
    def __new__(self, text, icon):
        widget = bumblebee.output.Widget()
        widget.set('theme.minwidth', '00000000KiB/s')
        widget.full_text(self.humanize(text, icon))

        return widget

    @staticmethod
    def humanize(text, icon):
        humanized_byte_format = bumblebee.util.bytefmt(text)
        return '{0} {1}/s'.format(icon, humanized_byte_format)
