from manim import *
import numpy as np


config.background_color = BLACK


class ModalDecomposition3DSnapshot(ThreeDScene):
    """Static summary: free response, 3-D phase space and modal basis."""

    def construct(self):
        # Coupled 3x3 oscillatory system from the participation notebook.
        A = np.array([[-0.30, 1.40, 0.15],
                      [-1.40, -0.30, 0.10],
                      [0.08, 0.12, -1.20]])
        B = np.array([1.0, 0.5, 0.25])
        C = np.array([1.0, 0.6, 0.2])
        x0 = np.array([2.0, 0.5, 1.0])

        eigenvalues, eigenvectors = np.linalg.eig(A)
        eigenvectors_inv = np.linalg.inv(eigenvectors)

        def state(t, initial=x0):
            modal_initial = eigenvectors_inv @ initial.astype(complex)
            modal_state = modal_initial * np.exp(eigenvalues * t)
            return np.real(eigenvectors @ modal_state)

        def output(t):
            return float(C @ state(t))

        title = Text(
            "Time response and modal decomposition",
            font="Times New Roman", font_size=28, color=WHITE,
        ).to_edge(UP, buff=0.10)

        # Top-left: free output response.
        time_axes = Axes(
            x_range=[0, 18, 3], y_range=[-3, 3, 1],
            x_length=6.2, y_length=2.55,
            axis_config={"color": WHITE, "stroke_width": 1.4,
                         "include_tip": True, "include_numbers": True,
                         "font_size": 14},
        ).move_to(LEFT * 3.65 + UP * 1.75)
        time_tracker = ValueTracker(0.0)
        response = always_redraw(lambda: time_axes.plot(
            output,
            x_range=[0, max(0.001, time_tracker.get_value()), 0.035],
            color=YELLOW,
            stroke_width=3.0,
        ))
        response_dot = always_redraw(lambda: Dot(
            time_axes.c2p(time_tracker.get_value(), output(time_tracker.get_value())),
            radius=0.055,
            color=YELLOW,
        ))
        response_title = Text(
            "Original system: free response y(t)",
            font="Times New Roman", font_size=17, color=WHITE,
        ).next_to(time_axes, UP, buff=0.05)
        time_label = MathTex(r"t\,[s]", color=WHITE, font_size=20).next_to(
            time_axes.x_axis.get_end(), DOWN, buff=0.05)
        amplitude_label = Text(
            "amplitude", font="Times New Roman", font_size=13, color=WHITE,
        ).next_to(time_axes.y_axis, UP, buff=0.02)

        # Top-right: original state-space model.
        model = VGroup(
            Text("ORIGINAL SISO MODEL", font="Times New Roman",
                 font_size=20, color=WHITE),
            MathTex(
                r"\dot{x}=\begin{bmatrix}"
                r"-0.30&1.40&0.15\\"
                r"-1.40&-0.30&0.10\\"
                r"0.08&0.12&-1.20"
                r"\end{bmatrix}x+"
                r"\begin{bmatrix}1\\0.5\\0.25\end{bmatrix}u",
                color=WHITE, font_size=24,
            ),
            MathTex(
                r"y=\begin{bmatrix}1.00&0.60&0.20\end{bmatrix}x+0u",
                color=WHITE, font_size=24,
            ),
            MathTex(r"u(t)=0,\qquad x(0)=[2.0,\,0.5,\,1.0]^T",
                    color=WHITE, font_size=21),
            MathTex(r"\lambda(A)=-0.294\pm1.396j,\;-1.213",
                    color=WHITE, font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        model.scale(min(5.65 / model.width, 2.28 / model.height))
        model.move_to(RIGHT * 3.55 + UP * 1.70)
        model_box = RoundedRectangle(
            width=6.25, height=2.75, corner_radius=0.08,
            color=WHITE, stroke_width=1.2,
        ).move_to(RIGHT * 3.55 + UP * 1.73)

        # Bottom-left: 3-D phase portrait projected by a fixed camera.
        phase_axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-3, 3, 1],
            x_length=4.5, y_length=4.5, z_length=3.6,
            axis_config={"color": WHITE, "stroke_width": 1.15,
                         "include_tip": True},
        )
        # Initial view: nearly normal to the oscillatory x1-x2 modal plane,
        # with enough tilt left to make the third dimension visible.
        phase_axes.rotate(angle=24 * DEGREES, axis=RIGHT)
        phase_axes.rotate(angle=-18 * DEGREES, axis=UP)
        phase_axes.scale(0.72).move_to(LEFT * 3.55 + DOWN * 1.75)

        phase_title = Text(
            "3-D PHASE SPACE", font="Times New Roman", font_size=19,
            color=WHITE,
        ).move_to(LEFT * 4.45 + DOWN * 0.32)
        axis_labels = VGroup(
            MathTex("x_1", color=WHITE, font_size=18).next_to(
                phase_axes.x_axis.get_end(), RIGHT, buff=0.02),
            MathTex("x_2", color=WHITE, font_size=18).next_to(
                phase_axes.y_axis.get_end(), LEFT, buff=0.04),
            MathTex("x_3", color=WHITE, font_size=18).next_to(
                phase_axes.z_axis.get_end(), UP, buff=0.02),
        )
        phase_curve = always_redraw(lambda: ParametricFunction(
            lambda t: phase_axes.c2p(*state(t, x0)),
            t_range=[0, max(0.001, time_tracker.get_value()), 0.035],
            color=YELLOW,
            stroke_width=2.8,
        ))
        phase_dot = always_redraw(lambda: Dot3D(
            phase_axes.c2p(*state(time_tracker.get_value(), x0)),
            radius=0.055,
            color=YELLOW,
        ))
        origin_dot = Dot3D(phase_axes.c2p(0, 0, 0), radius=0.05, color=WHITE)

        # Bottom-right: eigenvalues, eigenvectors and modal matrix.
        modal = VGroup(
            Text("MODAL DECOMPOSITION", font="Times New Roman",
                 font_size=20, color=WHITE),
            MathTex(
                r"\lambda_1=-0.294+1.396j,\quad"
                r"\lambda_2=-0.294-1.396j,\quad"
                r"\lambda_3=-1.213",
                color=WHITE, font_size=23,
            ),
            MathTex(
                r"m_1=\begin{bmatrix}-0.707\\0.003-0.705j\\-0.061+0.001j\end{bmatrix},\quad "
                r"m_2=m_1^*,\quad "
                r"m_3=\begin{bmatrix}0.001\\-0.107\\0.994\end{bmatrix}",
                color=WHITE, font_size=24,
            ),
            MathTex(r"M=\begin{bmatrix}m_1&m_2&m_3\end{bmatrix},\qquad x=Mq",
                    color=WHITE, font_size=26),
            MathTex(r"\dot q=\Lambda q,\qquad \Lambda=M^{-1}AM",
                    color=WHITE, font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        modal.scale_to_fit_width(6.15).move_to(RIGHT * 3.45 + DOWN * 1.68)

        divider_h = Line(LEFT * 7.0, RIGHT * 7.0, color=GRAY_B,
                         stroke_width=1.0).move_to(DOWN * 0.05)
        divider_v_top = Line(UP * 1.35, DOWN * 1.35, color=GRAY_B,
                             stroke_width=1.0).move_to(UP * 1.72)
        divider_v_bottom = Line(UP * 1.65, DOWN * 1.65, color=GRAY_B,
                                stroke_width=1.0).move_to(DOWN * 1.75)

        self.add(
            title, divider_h, divider_v_top, divider_v_bottom,
            time_axes, response, response_dot, response_title,
            time_label, amplitude_label,
            model_box, model,
            phase_axes, phase_title, axis_labels, phase_curve, phase_dot,
            origin_dot, modal,
        )
        # Both traces evolve with the same physical-time parameter.
        self.play(
            time_tracker.animate.set_value(18.0),
            run_time=20.0,
            rate_func=linear,
        )
        self.wait(0.8)

        # Freeze the completed traces, then rotate only the 3-D phase-space
        # objects. All equations and the time-response panel remain fixed.
        response.clear_updaters()
        response_dot.clear_updaters()
        phase_curve.clear_updaters()
        phase_dot.clear_updaters()
        phase_group = VGroup(
            phase_axes, axis_labels, phase_curve, phase_dot, origin_dot,
        )
        self.play(
            Rotate(
                phase_group,
                angle=TAU,
                axis=UP,
                about_point=phase_axes.c2p(0, 0, 0),
            ),
            run_time=8.0,
            rate_func=smooth,
        )
        self.wait(1.0)
