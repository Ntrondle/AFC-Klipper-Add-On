# Armored Turtle Automated Filament Changer
# Wheel sensor module for RPM feedback
#
# Copyright (C) 2024 Armored Turtle
#
# This file may be distributed under the terms of the GNU GPLv3 license.
"""Standalone hall effect wheel sensor implementation."""

from configfile import error


def load_config(config):
    """Entry point for Klipper to load the wheel sensor."""
    return StandaloneWheelSensor(config)


class StandaloneWheelSensor:
    """Simple hall-effect based wheel RPM sensor."""

    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.name = config.get_name().split()[-1]
        self.pulses_per_rev = config.getfloat("pulses_per_rev", 1.0, minval=0.1)
        self.pin = config.get("pin")
        if self.pin is None:
            raise error(f"wheel_sensor {self.name}: pin must be specified")

        # pulse counter and timestamp for rpm calculation
        self._pulse_count = 0
        self._prev_state = 0
        self._last_time = self.reactor.monotonic()

        buttons = self.printer.load_object(config, "buttons")
        buttons.register_buttons([self.pin], self._edge_callback)

    def _edge_callback(self, eventtime, state):
        # count rising edges
        if not self._prev_state and state:
            self._pulse_count += 1
        self._prev_state = state

    def get_rpm(self):
        """Return tuple of (wheel_rpm, motor_rpm)."""
        now = self.reactor.monotonic()
        dt = now - self._last_time
        if dt <= 0:
            return None, None
        pulses = self._pulse_count
        self._pulse_count = 0
        self._last_time = now
        rpm = (pulses / self.pulses_per_rev) / dt * 60.0
        return rpm, rpm
