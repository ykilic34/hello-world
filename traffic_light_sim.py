"""Simple visualization of traffic flow through a single traffic light.

Run with ``python traffic_light_sim.py``. Cars arrive randomly at the left
of a one-way street, stop at the traffic light when it is red, and pass
through when it is green. The simulation is purely illustrative and uses
matplotlib for a lightweight animation.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from typing import List

import matplotlib.animation as animation
import matplotlib.pyplot as plt


@dataclass
class TrafficLight:
    """Represents a simple three-state traffic light.

    The light cycles through green -> yellow -> red. Each phase lasts for a
    configurable duration and the current color can be queried from elapsed
    simulation time.
    """

    green_duration: float = 12.0
    yellow_duration: float = 3.0
    red_duration: float = 10.0

    def phase(self, time: float) -> str:
        """Return the color of the light at a given elapsed ``time``."""

        cycle = self.green_duration + self.yellow_duration + self.red_duration
        position = time % cycle
        if position < self.green_duration:
            return "green"
        if position < self.green_duration + self.yellow_duration:
            return "yellow"
        return "red"

    def allows_passing(self, time: float) -> bool:
        """Whether cars should proceed through the light at ``time``."""

        return self.phase(time) == "green"


@dataclass
class Car:
    """A car moving along a one-way street."""

    position: float = 0.0
    speed: float = 12.0  # meters per second

    def advance(self, dt: float, light_position: float, light_open: bool) -> None:
        """Advance the car by ``dt`` seconds respecting the traffic light."""

        if not light_open and self.position < light_position:
            # Stop at the light, leaving 2 meters of buffer before the stop line.
            stop_line = max(light_position - 2.0, self.position)
            distance_to_stop = stop_line - self.position
            movement = min(distance_to_stop, self.speed * dt)
        else:
            movement = self.speed * dt
        self.position += movement


class StreetSimulation:
    """Coordinates cars flowing through a single traffic light."""

    def __init__(
        self,
        light: TrafficLight,
        road_length: float = 120.0,
        light_position: float = 60.0,
        arrival_rate: float = 0.25,
        time_step: float = 0.1,
    ) -> None:
        """
        Args:
            light: TrafficLight controlling flow.
            road_length: Length of the simulated road in meters.
            light_position: Position of the traffic light along the road.
            arrival_rate: Expected cars per second entering the simulation.
            time_step: Simulation step size in seconds.
        """

        self.light = light
        self.road_length = road_length
        self.light_position = light_position
        self.arrival_rate = arrival_rate
        self.time_step = time_step
        self.cars: List[Car] = []
        self.time_elapsed = 0.0

    def spawn_cars(self) -> None:
        """Randomly add cars based on the arrival_rate."""

        # Poisson process approximation: probability of one arrival in time_step.
        if random.random() < self.arrival_rate * self.time_step:
            self.cars.append(Car())

    def step(self) -> None:
        """Advance the simulation by one time step."""

        self.spawn_cars()
        light_open = self.light.allows_passing(self.time_elapsed)
        for car in list(self.cars):
            car.advance(self.time_step, self.light_position, light_open)
        self.cars = [car for car in self.cars if car.position < self.road_length]
        self.time_elapsed += self.time_step

    # Visualization -----------------------------------------------------
    def run(self) -> None:
        """Run an animated visualization using matplotlib."""

        fig, ax = plt.subplots(figsize=(10, 3))
        ax.set_xlim(0, self.road_length)
        ax.set_ylim(-2, 2)
        ax.set_xlabel("One-way street (meters)")
        ax.get_yaxis().set_visible(False)

        light_line = ax.axvline(self.light_position, color="gray", linestyle="--")
        light_marker = ax.scatter([], [], s=300, zorder=5)
        (car_points,) = ax.plot([], [], "o", color="steelblue", markersize=8)

        def init():
            car_points.set_data([], [])
            return car_points, light_marker

        def animate(_frame: int):
            self.step()
            x_positions = [car.position for car in self.cars]
            y_positions = [0 for _ in self.cars]
            car_points.set_data(x_positions, y_positions)

            color = {
                "green": "green",
                "yellow": "gold",
                "red": "red",
            }[self.light.phase(self.time_elapsed)]
            light_line.set_color(color)
            light_marker.set_offsets([[self.light_position, 0]])
            light_marker.set_color(color)
            return car_points, light_marker

        # Roughly 30 FPS
        animation.FuncAnimation(
            fig,
            animate,
            init_func=init,
            interval=1000 * self.time_step,
            blit=True,
        )

        plt.title("Traffic light on a one-way street")
        plt.tight_layout()
        plt.show()


def main(argv: List[str]) -> int:
    # Allow optional adjustment of car arrival rate via CLI.
    arrival_rate = 0.25  # cars per second
    if len(argv) > 1:
        try:
            arrival_rate = float(argv[1])
        except ValueError:
            print("Arrival rate must be numeric (cars per second).", file=sys.stderr)
            return 1

    sim = StreetSimulation(TrafficLight(), arrival_rate=arrival_rate)
    sim.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
