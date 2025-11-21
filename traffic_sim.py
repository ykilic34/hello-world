"""Visualize traffic light behavior on a one-way street with random arriving cars.

Run with ``python traffic_sim.py`` to open an animated Matplotlib window that shows:
* A traffic light switching between green and red phases.
* Cars entering from the left at a random rate and stopping at the light when needed.

This is intentionally lightweight and self contained so it can be run from the CLI
without extra dependencies beyond Matplotlib.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

import matplotlib.pyplot as plt
from matplotlib import animation


@dataclass
class TrafficLight:
    """Simple traffic light with fixed green/red durations."""

    green_duration: int
    red_duration: int

    def is_green(self, tick: int) -> bool:
        phase = tick % (self.green_duration + self.red_duration)
        return phase < self.green_duration


@dataclass
class Car:
    position: float
    speed: float

    def step(self, light: TrafficLight, dt: float, stop_line: float, tick: int) -> None:
        """Advance the car, stopping at the light when it is red."""

        distance_to_stop = stop_line - self.position
        if distance_to_stop <= 0:
            # Past the stop line; keep moving forward.
            self.position += self.speed * dt
            return

        if light.is_green(tick):
            self.position += self.speed * dt
            return

        # Light is red; if we would cross the line this step, clamp to the line.
        step_distance = self.speed * dt
        if step_distance >= distance_to_stop:
            self.position = stop_line
        else:
            self.position += step_distance


class Simulation:
    def __init__(self,
                 road_length: float = 120.0,
                 stop_line: float = 60.0,
                 car_speed: float = 20.0,
                 spawn_rate: float = 0.35,
                 time_step: float = 0.1,
                 seed: int | None = 13) -> None:
        if stop_line >= road_length:
            raise ValueError("Stop line must be within the road length.")

        self.road_length = road_length
        self.stop_line = stop_line
        self.car_speed = car_speed
        self.spawn_rate = spawn_rate
        self.time_step = time_step
        self.tick = 0
        self.cars: List[Car] = []
        if seed is not None:
            random.seed(seed)

        self.light = TrafficLight(green_duration=40, red_duration=30)

        # Visualization setup
        self.fig, self.ax = plt.subplots(figsize=(9, 3))
        self.car_scat = self.ax.scatter([], [], s=120, c="#0077b6")
        self.light_indicator = self.ax.scatter([], [], s=300, marker="s")
        self.ax.axvline(self.stop_line, color="#999", linestyle="--", linewidth=1)
        self.ax.set_xlim(0, self.road_length)
        self.ax.set_ylim(-2, 2)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_title("One-way traffic with random arrivals")

    def spawn_car(self) -> None:
        """Spawn a new car at position 0 with base speed."""
        if random.random() < self.spawn_rate:
            self.cars.append(Car(position=0.0, speed=self.car_speed))

    def update(self, _frame: int) -> None:
        self.spawn_car()

        # Move each car and drop any that leave the scene.
        for car in list(self.cars):
            car.step(self.light, self.time_step, self.stop_line, self.tick)
        self.cars = [c for c in self.cars if c.position <= self.road_length]

        # Update scatter plots for cars and the light.
        positions = [car.position for car in self.cars]
        self.car_scat.set_offsets([(x, 0) for x in positions])

        if self.light.is_green(self.tick):
            color, status = "green", "Green"
        else:
            color, status = "red", "Red"
        self.light_indicator.set_offsets([(self.stop_line, 1)])
        self.light_indicator.set_color(color)
        self.ax.set_xlabel(f"Tick: {self.tick} | Light: {status} | Cars on road: {len(self.cars)}")

        self.tick += 1

    def run(self) -> animation.FuncAnimation:
        return animation.FuncAnimation(
            self.fig,
            self.update,
            interval=1000 * self.time_step,
            blit=False,
            repeat=False,
        )


def main() -> None:
    sim = Simulation()
    anim = sim.run()
    plt.show()
    # Keep reference to prevent garbage collection when running outside notebooks
    return anim


if __name__ == "__main__":
    main()
