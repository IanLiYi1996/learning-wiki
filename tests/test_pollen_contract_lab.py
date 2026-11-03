import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest


PATH = Path(__file__).resolve().parents[1] / "scripts/pollen_contract_lab.py"
SPEC = importlib.util.spec_from_file_location("pollen_contract_lab", PATH)
lab = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lab
SPEC.loader.exec_module(lab)


class GeometryAndUnits(unittest.TestCase):
    def project(self, depth=500, unit="mm", fx=500):
        return lab.backproject(420, 240, depth, fx=fx, fy=500, cx=320, cy=240, unit=unit)

    def test_metric_scale_is_explicit(self):
        self.assertEqual(self.project(), (.1, 0, .5))
        self.assertEqual(self.project(.5, "m"), (.1, 0, .5))
        self.assertEqual(self.project(500, "m"), (100, 0, 500))

    def test_relative_depth_not_silently_metric(self):
        for unit in ("relative", "", None):
            with self.assertRaises(ValueError):
                self.project(unit=unit)

    def test_invalid_geometry(self):
        for depth, fx in ((0, 500), (-1, 500), (500, 0), (True, 500),
                          (math.nan, 500), (500, math.inf)):
            with self.assertRaises(ValueError):
                self.project(depth=depth, fx=fx)

    def test_world_camera_transform_has_direction(self):
        output = lab.transform_yaw((.1, 0, .5), translation=(1, 0, 0), yaw_radians=math.pi/2)
        for actual, expected in zip(output, (1, .1, .5)):
            self.assertAlmostEqual(actual, expected)
        other = lab.transform_yaw((.1, 0, .5), translation=(0, 0, 0), yaw_radians=-math.pi/2)
        self.assertAlmostEqual(other[1], -.1)

    def test_invalid_transform_vector_or_angle(self):
        for point, shift, yaw in (([1, 2], [0, 0, 0], 0), ([1, 2, 3], [], 0),
                                  ([1, math.nan, 3], [0, 0, 0], 0),
                                  ([1, 2, 3], [0, 0, 0], math.inf)):
            with self.assertRaises(ValueError):
                lab.transform_yaw(point, translation=shift, yaw_radians=yaw)

    def test_same_quaternion_numbers_different_orders(self):
        self.assertEqual(lab.quaternion_xyzw((1, 0, 0, 0), order="wxyz"), (0, 0, 0, 1))
        self.assertEqual(lab.quaternion_xyzw((1, 0, 0, 0), order="xyzw"), (1, 0, 0, 0))
        self.assertEqual(lab.quaternion_xyzw((2, 0, 0, 0), order="wxyz"), (0, 0, 0, 1))

    def test_invalid_quaternion(self):
        for values, order in (((0, 0, 0, 0), "xyzw"), ((1, 0, 0), "xyzw"),
                              ((math.nan, 0, 0, 0), "wxyz"), ((1, 0, 0, 0), "")):
            with self.assertRaises(ValueError):
                lab.quaternion_xyzw(values, order=order)


class CoupledActuator(unittest.TestCase):
    def test_source_model_teaching_examples(self):
        self.assertEqual(lab.orbita2d_inverse((.5, .5), ratios=(1, 1)), (1, 0))
        self.assertEqual(lab.orbita2d_forward((1, 1), ratios=(1, 1)), (1, 0))
        self.assertEqual(lab.orbita2d_forward((1, -1), ratios=(1, 1)), (0, 1))

    def test_nonunit_ratios_round_trip(self):
        for output in ((0, 0), (.3, -.4), (1, 2)):
            motors = lab.orbita2d_inverse(output, ratios=(2, 3))
            result = lab.orbita2d_forward(motors, ratios=(2, 3))
            for actual, expected in zip(result, output):
                self.assertAlmostEqual(actual, expected)

    def test_shape_and_singular_ratio(self):
        for ratios in ((0, 1), (1, 0), (1,), (True, 1), (math.nan, 1)):
            for function in (lab.orbita2d_forward, lab.orbita2d_inverse):
                with self.assertRaises(ValueError):
                    function((1, 0), ratios=ratios)


class TimingAndContracts(unittest.TestCase):
    def prior(self, times=(1, 1.03, 1.1), decision=1.06, max_age=.05, a="A", b="A"):
        return lab.prior_observation(times, decision_time=decision, max_age=max_age,
                                     sensor_clock=a, policy_clock=b)

    def fixture(self):
        return lab.ActionContract(("ring", "center"), "rad", "output", "absolute_position")

    def gate(self, actual=None, expected=None, **kwargs):
        return lab.action_gate((1, 0), actual or self.fixture(), expected or self.fixture(),
                               **{"sampled_at": 1, "now": 1.01, "max_age": .1,
                                  "enabled": True, **kwargs})

    def test_prior_not_nearest_future(self):
        result = self.prior()
        self.assertEqual(result["index"], 1)
        self.assertAlmostEqual(result["age_seconds"], .03)

    def test_future_only_empty_and_stale_return_none(self):
        self.assertIsNone(self.prior((1.1,), decision=1.06))
        self.assertIsNone(self.prior(()))
        self.assertIsNone(self.prior((1,), decision=1.06))
        self.assertEqual(self.prior((1,), decision=1, max_age=0)["index"], 0)

    def test_clock_domains_do_not_compare_directly(self):
        for a, b in (("A", "B"), ("", ""), (True, True)):
            with self.assertRaises(ValueError):
                self.prior(a=a, b=b)

    def test_invalid_time_series(self):
        for times, decision, max_age in (((1, 1), 1, 1), ((2, 1), 2, 1),
                                        ((math.nan,), 1, 1), ((1,), True, 1),
                                        ((1,), 1, -1)):
            with self.assertRaises(ValueError):
                self.prior(times, decision, max_age)

    def test_valid_action_accepted_only_when_enabled(self):
        self.assertTrue(self.gate()["accepted"])
        self.assertEqual(self.gate(enabled=False)["reasons"], ["not_enabled"])

    def test_same_shape_wrong_meaning_rejected(self):
        contract = lab.ActionContract(("A", "B"), "rad", "motor", "absolute_position")
        result = self.gate(actual=contract)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reasons"], ["mismatch_names", "mismatch_frame"])

    def test_unit_and_representation_mismatch(self):
        contract = lab.ActionContract(("ring", "center"), "deg", "output", "delta_position")
        self.assertEqual(self.gate(actual=contract)["reasons"],
                         ["mismatch_unit", "mismatch_representation"])

    def test_future_and_stale_action(self):
        self.assertEqual(self.gate(now=.9)["reasons"], ["future_timestamp"])
        self.assertEqual(self.gate(now=1.25)["reasons"], ["stale"])
        self.assertTrue(self.gate(now=1, max_age=0)["accepted"])

    def test_invalid_gate_and_contract(self):
        for names in ((), ("A", "A"), ("",), ["A"]):
            with self.assertRaises(ValueError):
                lab.ActionContract(names, "rad", "motor", "absolute")
        with self.assertRaises(ValueError):
            lab.ActionContract(("A",), "", "motor", "absolute")
        for controls in ({"enabled": 1}, {"max_age": -1}, {"now": math.nan}):
            with self.assertRaises(ValueError):
                self.gate(**controls)
        with self.assertRaises(ValueError):
            lab.action_gate((1,), self.fixture(), self.fixture(), sampled_at=1,
                            now=1, max_age=1, enabled=True)

    def test_latency_has_units_and_is_not_a_safety_margin(self):
        self.assertAlmostEqual(lab.latency_displacement(.4, (.12, .08, .02)), .088)
        self.assertEqual(lab.latency_displacement(0, (0, .1)), 0)

    def test_invalid_latency_and_nonfinite_numbers(self):
        for speed, stages in ((-.1, [.1]), (True, [.1]), (.4, []),
                              (.4, [-.1]), (.4, [math.inf])):
            with self.assertRaises(ValueError):
                lab.latency_displacement(speed, stages)
        with self.assertRaises(ValueError):
            lab.finite(10 ** 400)

    def test_cli_finite_and_no_hardware_or_service_dependencies(self):
        example = json.loads(json.dumps(lab.examples(), allow_nan=False))
        self.assertEqual(example["camera_point_m"], [.1, 0, .5])
        self.assertFalse(example["stale_action"]["accepted"])
        self.assertNotRegex(PATH.read_text(), r"import (torch|mujoco|pytrio|reachy|serial|httpx)")


if __name__ == "__main__":
    unittest.main()
