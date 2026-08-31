from manim import *
import numpy as np


config.background_color = BLACK


class SwitchedModalMonotonicAnimation(Scene):
    """Sequential modal trajectories followed by a synchronized 3-D reveal."""

    def construct(self):
        A_original = np.array([
            [-0.30, 1.40, 0.15],
            [-1.40, -0.30, 0.10],
            [0.08, 0.12, -1.20],
        ])
        A_modified = np.array([
            [-0.180, 0.372, 0.204],
            [0.000, -0.800, 0.000],
            [0.000, 0.000, -1.200],
        ])
        C = np.array([1.0, 0.6, 0.2])
        x0 = np.array([2.0, 0.5, 1.0])

        def state_function(A, initial):
            poles, vectors = np.linalg.eig(A)
            coefficients = np.linalg.solve(vectors, initial.astype(complex))

            def state(t):
                return np.real(vectors @ (coefficients * np.exp(poles * t)))

            return state

        original = state_function(A_original, x0)

        # Switch while the first descending oscillation is close to zero.
        threshold = 0.15
        samples = np.linspace(0.001, 2.0, 10000)
        values = np.array([C @ original(t) - threshold for t in samples])
        index = np.flatnonzero(values[:-1] * values[1:] < 0)[0]
        ta, tb = samples[index], samples[index + 1]
        va, vb = values[index], values[index + 1]
        switch_time = ta - va * (tb - ta) / (vb - va)
        switch_state = original(switch_time)
        post_switch = state_function(A_modified, switch_state)

        # The blue orbit is extended backward to t=0 and intersects the yellow
        # orbit exactly at the switching state.
        modified = lambda t: post_switch(t - switch_time)

        def switched(t):
            return original(t) if t <= switch_time else modified(t)

        y_original = lambda t: float(C @ original(t))
        y_modified = lambda t: float(C @ modified(t))
        y_switched = lambda t: float(C @ switched(t))

        title = Text(
            "Switching from fast oscillatory modes to a slow monotonic mode",
            font="Nimbus Roman", font_size=27, color=WHITE,
        ).to_edge(UP, buff=0.08)
        separator = Line(LEFT * 6.8, RIGHT * 6.8, color=GRAY_B, stroke_width=1)
        separator.move_to(DOWN * 0.48)

        time_axes = Axes(
            x_range=[0, 18, 3], y_range=[-3, 3, 1],
            x_length=9.2, y_length=2.55,
            axis_config={"color": WHITE, "stroke_width": 1.2,
                         "include_tip": True, "include_numbers": True,
                         "font_size": 12},
        ).move_to(LEFT * 1.25 + UP * 1.25)
        time_title = Text(
            "Superposed free output responses y(t)",
            font="Nimbus Roman", font_size=17, color=WHITE,
        ).next_to(time_axes, UP, buff=0.06)
        yellow_time = time_axes.plot(
            y_original, x_range=[0, 18, 0.025], color=YELLOW, stroke_width=2.8,
        )
        blue_time = time_axes.plot(
            y_modified, x_range=[0, 18, 0.025], color=BLUE_B, stroke_width=3.1,
        )
        red_time = time_axes.plot(
            y_switched, x_range=[0, 18, 0.025], color=RED, stroke_width=4.4,
        )
        cut_line = DashedLine(
            time_axes.c2p(switch_time, -3), time_axes.c2p(switch_time, 3),
            color=RED, stroke_width=1.7, dash_length=0.08,
        )
        cut_label = MathTex(
            rf"t_s={switch_time:.3f}\,s", color=RED, font_size=20,
        ).next_to(time_axes.c2p(switch_time, threshold), UR, buff=0.08)

        def projection(center, first, second, labels, ranges):
            axes = Axes(
                x_range=ranges[0], y_range=ranges[1],
                x_length=5.25, y_length=2.55,
                axis_config={"color": WHITE, "stroke_width": 1.1,
                             "include_tip": True, "include_numbers": True,
                             "font_size": 11},
            ).move_to(center)
            heading = MathTex(
                rf"{labels[0]}\;\mathrm{{vs.}}\;{labels[1]}",
                color=WHITE, font_size=21,
            ).next_to(axes, UP, buff=0.07)

            def curve(state, color, width):
                return ParametricFunction(
                    lambda t: axes.c2p(state(t)[first], state(t)[second]),
                    t_range=[0, 18, 0.025], color=color, stroke_width=width,
                )

            return (
                axes, heading,
                curve(original, YELLOW, 2.8),
                curve(modified, BLUE_B, 3.1),
                curve(switched, RED, 4.4),
            )

        left_axes, left_title, left_yellow, left_blue, left_red = projection(
            LEFT * 3.35 + DOWN * 2.15, 0, 1, ("x_1", "x_2"),
            ([-2.5, 2.5, 1], [-2, 2, 1]),
        )
        right_axes, right_title, right_yellow, right_blue, right_red = projection(
            RIGHT * 3.35 + DOWN * 2.15, 1, 2, ("x_2", "x_3"),
            ([-2, 2, 1], [-1.5, 1.5, 0.5]),
        )

        legend = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.45, color=YELLOW, stroke_width=3),
                   Text("Original", font_size=14)).arrange(RIGHT, buff=0.09),
            VGroup(Line(ORIGIN, RIGHT * 0.45, color=BLUE_B, stroke_width=3),
                   Text("Modified", font_size=14)).arrange(RIGHT, buff=0.09),
            VGroup(Line(ORIGIN, RIGHT * 0.45, color=RED, stroke_width=4),
                   Text("Switched", font_size=14)).arrange(RIGHT, buff=0.09),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to(RIGHT * 5.25 + UP * 1.30)

        self.add(
            title, separator, time_axes, time_title, cut_line, cut_label,
            left_axes, left_title, right_axes, right_title, legend,
        )
        self.play(
            Create(yellow_time), Create(left_yellow), Create(right_yellow),
            run_time=7.0, rate_func=linear,
        )
        self.play(
            Create(blue_time), Create(left_blue), Create(right_blue),
            run_time=7.0, rate_func=linear,
        )

        # Draw the switched orbit up to the switching intersection, pause and
        # emphasize the same state in the time plot and both phase projections.
        red_time_before = time_axes.plot(
            y_switched, x_range=[0, switch_time, 0.01],
            color=RED, stroke_width=4.4,
        )
        red_time_after = time_axes.plot(
            y_switched, x_range=[switch_time, 18, 0.025],
            color=RED, stroke_width=4.4,
        )

        def projected_segment(axes, first, second, start, end):
            return ParametricFunction(
                lambda t: axes.c2p(switched(t)[first], switched(t)[second]),
                t_range=[start, end, 0.015], color=RED, stroke_width=4.4,
            )

        left_red_before = projected_segment(
            left_axes, 0, 1, 0, switch_time,
        )
        left_red_after = projected_segment(
            left_axes, 0, 1, switch_time, 18,
        )
        right_red_before = projected_segment(
            right_axes, 1, 2, 0, switch_time,
        )
        right_red_after = projected_segment(
            right_axes, 1, 2, switch_time, 18,
        )
        self.play(
            Create(red_time_before),
            Create(left_red_before), Create(right_red_before),
            run_time=3.5, rate_func=linear,
        )

        time_intersection = Dot(
            time_axes.c2p(switch_time, threshold),
            radius=0.10, color=WHITE,
        )
        left_intersection = Dot(
            left_axes.c2p(switch_state[0], switch_state[1]),
            radius=0.10, color=WHITE,
        )
        right_intersection = Dot(
            right_axes.c2p(switch_state[1], switch_state[2]),
            radius=0.10, color=WHITE,
        )
        intersections = VGroup(
            time_intersection, left_intersection, right_intersection,
        )
        self.play(
            GrowFromCenter(time_intersection),
            GrowFromCenter(left_intersection),
            GrowFromCenter(right_intersection),
            Flash(time_intersection, color=WHITE, flash_radius=0.28),
            Flash(left_intersection, color=WHITE, flash_radius=0.28),
            Flash(right_intersection, color=WHITE, flash_radius=0.28),
            run_time=1.5,
        )
        self.wait(3.0)
        self.play(
            FadeOut(intersections),
            Create(red_time_after),
            Create(left_red_after), Create(right_red_after),
            run_time=7.0, rate_func=linear,
        )
        # Replace the two visual segments with the equivalent complete curves
        # so the later 2-D to 3-D merge remains a clean transformation.
        self.remove(
            red_time_before, red_time_after,
            left_red_before, left_red_after,
            right_red_before, right_red_after,
        )
        self.add(red_time, left_red, right_red)
        self.wait(0.5)

        # Keep both projections fixed, then merge them into one 3-D phase space.
        phase_3d_axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1], y_range=[-2.5, 2.5, 1],
            z_range=[-1.5, 1.5, 0.5],
            x_length=5.2, y_length=5.2, z_length=3.8,
            axis_config={"color": WHITE, "stroke_width": 1.0,
                         "include_tip": True},
        )
        phase_3d_axes.rotate(22 * DEGREES, axis=RIGHT)
        phase_3d_axes.rotate(-25 * DEGREES, axis=UP)
        phase_3d_axes.scale(0.70).move_to(DOWN * 2.15)
        phase_3d_title = Text(
            "Combined 3-D phase space",
            font="Nimbus Roman", font_size=18, color=WHITE,
        ).move_to(DOWN * 0.72)

        def path_3d(state, color, width):
            return ParametricFunction(
                lambda t: phase_3d_axes.c2p(*state(t)),
                t_range=[0, 18, 0.025], color=color, stroke_width=width,
            )

        phase_3d_yellow = path_3d(original, YELLOW, 2.8)
        phase_3d_blue = path_3d(modified, BLUE_B, 3.1)
        phase_3d_red = path_3d(switched, RED, 4.4)
        combined_3d = VGroup(
            phase_3d_axes, phase_3d_yellow, phase_3d_blue,
            phase_3d_red, phase_3d_title,
        )
        two_planes = VGroup(
            left_axes, left_title, left_yellow, left_blue, left_red,
            right_axes, right_title, right_yellow, right_blue, right_red,
        )
        self.play(
            ReplacementTransform(two_planes, combined_3d),
            run_time=5.0,
            rate_func=smooth,
        )

        tracker = ValueTracker(0.0)
        time_dot = always_redraw(lambda: Dot(
            time_axes.c2p(tracker.get_value(), y_switched(tracker.get_value())),
            radius=0.085, color=WHITE,
        ))
        phase_dot = always_redraw(lambda: Dot3D(
            phase_3d_axes.c2p(*switched(tracker.get_value())),
            radius=0.10, color=WHITE,
        ))
        self.play(FadeIn(time_dot), FadeIn(phase_dot), run_time=0.8)
        self.play(
            tracker.animate.set_value(18.0),
            run_time=22.0, rate_func=linear,
        )
        self.wait(1.0)
