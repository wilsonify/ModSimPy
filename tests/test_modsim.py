import logging
import unittest

import numpy as np
import pandas as pd
import os

import pint
import modsim

import warnings

def test_smoke():
    logging.info("is anything on fire?")

class Test_ModSimSeries(unittest.TestCase):
    def test_constructor(self):
        s = modsim.ModSimSeries([1, 2, 3])
        self.assertEqual(s[0], 1)

        q = modsim.Quantity(2, modsim.UNITS.meter)
        s[q] = 4
        self.assertEqual(s[q], 4)
        self.assertEqual(s[2], 4)


class TestModSimDataFrame(unittest.TestCase):
    def test_constructor(self):
        msf = modsim.ModSimDataFrame(columns=["A", "T", "dt"])
        msf.row[1000] = [1, 2, np.nan]
        msf.row["label"] = ["4", 5, 6.0]

        col = msf.A
        self.assertIsInstance(col, modsim.ModSimSeries)
        self.assertEqual(col[1000], 1)

        col = msf.T
        self.assertIsInstance(col, modsim.ModSimSeries)
        self.assertEqual(col[1000], 2)

        col = msf.dt
        self.assertIsInstance(col, modsim.ModSimSeries)
        self.assertEqual(col["label"], 6.0)

        row = msf.row[1000]
        self.assertIsInstance(row, modsim.ModSimSeries)

        self.assertEqual(row.A, 1)
        self.assertEqual(row.T, 2)
        self.assertTrue(np.isnan(row.dt))

        self.assertEqual(row["A"], 1)
        self.assertEqual(row["T"], 2)
        self.assertTrue(np.isnan(row["dt"]))


class TestTimeFrame(unittest.TestCase):
    def test_constructor(self):
        msf = modsim.TimeFrame(columns=["A", "T", "dt"])
        msf.row[1000] = [1, 2, np.nan]
        msf.row["label"] = ["4", 5, 6.0]

        col = msf.A
        self.assertIsInstance(col, modsim.TimeSeries)

        col = msf.T
        self.assertIsInstance(col, modsim.TimeSeries)

        col = msf.dt
        self.assertIsInstance(col, modsim.TimeSeries)

        row = msf.row[1000]
        self.assertIsInstance(row, modsim.State)

        row = msf.row["label"]
        self.assertIsInstance(row, modsim.State)


class TestSweepFrame(unittest.TestCase):
    def test_constructor(self):
        msf = modsim.SweepFrame(columns=["A", "T", "dt"])
        msf.row[1000] = [1, 2, np.nan]
        msf.row["label"] = ["4", 5, 6.0]

        col = msf.A
        self.assertIsInstance(col, modsim.SweepSeries)

        col = msf.T
        self.assertIsInstance(col, modsim.SweepSeries)

        col = msf.dt
        self.assertIsInstance(col, modsim.SweepSeries)

        row = msf.row[1000]
        self.assertIsInstance(row, modsim.SweepSeries)

        row = msf.row["label"]
        self.assertIsInstance(row, modsim.SweepSeries)


class TestCartPol(unittest.TestCase):
    def test_cart2pol(self):
        theta, r = modsim.cart2pol(3, 4)
        self.assertAlmostEqual(r, 5)
        self.assertAlmostEqual(theta, 0.9272952180016122)

        theta, r, z = modsim.cart2pol(2, 2, 2)
        self.assertAlmostEqual(r, 2 * np.sqrt(2))
        self.assertAlmostEqual(theta, np.pi / 4)
        self.assertAlmostEqual(z, 2)

    def test_pol2cart(self):
        theta = 0.9272952180016122
        r = 5
        x, y = modsim.pol2cart(theta, r)
        self.assertAlmostEqual(x, 3)
        self.assertAlmostEqual(y, 4)

        angle = 45 * modsim.UNITS.degree
        r = 2 * np.sqrt(2)
        z = 2
        x, y, z = modsim.pol2cart(angle, r, z)
        self.assertAlmostEqual(x, 2)
        self.assertAlmostEqual(y, 2)
        self.assertAlmostEqual(z, 2)


class TestLinspaceLinrange(unittest.TestCase):
    def test_linspace(self):
        warnings.simplefilter("error", Warning)
        array = modsim.linspace(0, 1, 11)
        self.assertEqual(len(array), 11)
        self.assertAlmostEqual(array[0], 0)
        self.assertAlmostEqual(array[1], 0.1)
        self.assertAlmostEqual(array[10], 1.0)

        array = modsim.linspace(0, 1, 10, endpoint=False)
        self.assertEqual(len(array), 10)
        self.assertAlmostEqual(array[0], 0)
        self.assertAlmostEqual(array[1], 0.1)
        self.assertAlmostEqual(array[9], 0.9)

    def test_linrange(self):
        array = modsim.linrange(0, 1, 0.1)
        self.assertEqual(len(array), 10)
        self.assertAlmostEqual(array[0], 0)
        self.assertAlmostEqual(array[1], 0.1)
        self.assertAlmostEqual(array[9], 0.9)

        array = modsim.linrange(0, 1, 0.1, endpoint=True)
        self.assertEqual(len(array), 11)
        self.assertAlmostEqual(array[0], 0)
        self.assertAlmostEqual(array[1], 0.1)
        self.assertAlmostEqual(array[10], 1.0)


class TestAbsRelDiff(unittest.TestCase):
    def test_abs_diff(self):
        abs_diff = modsim.compute_abs_diff([1, 3, 7.5])
        self.assertEqual(len(abs_diff), 3)
        self.assertAlmostEqual(abs_diff[1], 4.5)

        ts = modsim.linrange(1950, 1960, endpoint=True)
        ps = modsim.linspace(3, 4, len(ts))
        abs_diff = modsim.compute_abs_diff(ps)
        self.assertEqual(len(abs_diff), 11)
        self.assertAlmostEqual(abs_diff[1], 0.1)

        # TODO: bring back this test when np.ediff1 is fixed
        # self.assertTrue(np.isnan(abs_diff[-1]))

        series = modsim.TimeSeries(ps, index=ts)
        abs_diff = modsim.compute_abs_diff(series)
        self.assertEqual(len(abs_diff), 11)
        self.assertAlmostEqual(abs_diff[1950], 0.1)
        # self.assertTrue(np.isnan(abs_diff[1960]))

    def test_rel_diff(self):
        rel_diff = modsim.compute_rel_diff([1, 3, 7.5])
        self.assertEqual(len(rel_diff), 3)
        self.assertAlmostEqual(rel_diff[1], 1.5)

        ts = modsim.linrange(1950, 1960, endpoint=True)
        ps = modsim.linspace(3, 4, len(ts))
        rel_diff = modsim.compute_rel_diff(ps)
        self.assertEqual(len(rel_diff), 11)
        self.assertAlmostEqual(rel_diff[0], 0.0333333333)
        # self.assertTrue(np.isnan(rel_diff[-1]))

        series = modsim.TimeSeries(ps, index=ts)
        rel_diff = modsim.compute_rel_diff(series)
        self.assertEqual(len(rel_diff), 11)
        self.assertAlmostEqual(rel_diff[1950], 0.0333333333)
        # self.assertTrue(np.isnan(rel_diff[1960]))


class TestOdeSolvers(unittest.TestCase):
    def test_run_euler(self):
        s = modsim.UNITS.second
        m = modsim.UNITS.meter

        init = modsim.State(y=2 * m)
        system = modsim.System(init=init, t_0=1 * s, t_end=3 * s)

        def slope_func(State, t, system):
            [y] = State
            dydt = y / s + t * m / s ** 2
            return [dydt]

        results, details = modsim.run_euler(system, slope_func)
        y_end = modsim.get_last_value(results.y)
        self.assertAlmostEqual(y_end, 24.9737147 * m)

    def test_run_ralston(self):
        s = modsim.UNITS.second
        m = modsim.UNITS.meter

        init = modsim.State(y=2 * m)
        system = modsim.System(init=init, t_0=1 * s, t_end=3 * s)

        def slope_func(State, t, system):
            [y] = State
            dydt = y / s + t * m / s ** 2
            return [dydt]

        results, details = modsim.run_ralston(system, slope_func)
        y_end = modsim.get_last_value(results.y)
        self.assertAlmostEqual(y_end, 25.8344700133 * m)

    def test_run_solve_ivp(self):
        s = modsim.UNITS.second
        m = modsim.UNITS.meter

        init = modsim.State(y=2 * m)
        system = modsim.System(init=init, t_0=1 * s, t_end=3 * s)

        def slope_func(State, t, system):
            [y] = State
            dydt = y + t
            return [dydt]

        results, details = modsim.run_solve_ivp(system, slope_func)
        y_end = modsim.get_last_value(results.y)
        self.assertAlmostEqual(y_end, 25.5571533)


class TestRootFinders(unittest.TestCase):
    def test_root_scalar(self):
        def func(x):
            return (x - 1) * (x - 2) * (x - 3)

        res = modsim.root_scalar(func, [0, 1.9])
        self.assertAlmostEqual(res.root, 1.0)

    def test_root_secant(self):
        def func(x):
            return (x - 1) * (x - 2) * (x - 3)

        res = modsim.root_bisect(func, [0, 1.9])
        self.assertAlmostEqual(res.root, 1.0)

        res = modsim.root_bisect(func, [0, 0.5])
        self.assertFalse(res.converged)


class TestRunInterpolate(unittest.TestCase):
    def test_has_nan(self):
        a = [1, 2, 3]
        self.assertFalse(modsim.has_nan(a))
        self.assertFalse(modsim.has_nan(np.array(a)))
        self.assertFalse(modsim.has_nan(pd.Series(a)))
        a.append(np.nan)
        self.assertTrue(modsim.has_nan(a))
        self.assertTrue(modsim.has_nan(np.array(a)))
        self.assertTrue(modsim.has_nan(pd.Series(a)))

    def test_is_strictly_increasing(self):
        a = [1, 2, 3]
        self.assertTrue(modsim.is_strictly_increasing(a))
        self.assertTrue(modsim.is_strictly_increasing(np.array(a)))
        self.assertTrue(modsim.is_strictly_increasing(pd.Series(a)))
        a.append(3)
        self.assertFalse(modsim.is_strictly_increasing(a))
        self.assertFalse(modsim.is_strictly_increasing(np.array(a)))
        self.assertFalse(modsim.is_strictly_increasing(pd.Series(a)))

    def test_interpolate(self):
        index = [1, 2, 3]
        values = np.array(index) * 2 - 1
        series = pd.Series(values, index=index)
        i = modsim.interpolate(series)
        self.assertAlmostEqual(i(1.5), 2.0)

    def test_interpolate_with_UNITS(self):
        index = [1, 2, 3]
        values = np.array(index) * 2 - 1
        series = pd.Series(values, index=index) * modsim.UNITS.meter
        i = modsim.interpolate(series)
        self.assertAlmostEqual(i(1.5), 2.0 * modsim.UNITS.meter)


class TestGradient(unittest.TestCase):
    def test_gradient(self):
        a = [1, 2, 4]
        s = modsim.TimeSeries(a)
        r = modsim.gradient(s)
        self.assertTrue(isinstance(r, modsim.TimeSeries))
        self.assertAlmostEqual(r[1], 1.5)

    def test_gradient_with_UNITS(self):
        s = modsim.SweepSeries()
        s[0] = 1 * modsim.UNITS.meter
        s[1] = 2 * modsim.UNITS.meter
        s[2] = 4 * modsim.UNITS.meter
        r = modsim.gradient(s)
        self.assertTrue(isinstance(r, modsim.SweepSeries))
        self.assertAlmostEqual(r[1], 1.5 * modsim.UNITS.meter)


class TestGolden(unittest.TestCase):
    def test_minimize(self):
        def min_func(x, system):
            return (x - system.actual_min) ** 2

        system = modsim.System(actual_min=2)
        res = modsim.minimize_golden(min_func, [0, 5], system, rtol=1e-7)
        self.assertAlmostEqual(res.x, 2)
        self.assertAlmostEqual(res.fun, 0)

    def test_maximize(self):
        def max_func(x, system):
            return -(x - system.actual_min) ** 2

        system = modsim.System(actual_min=2)
        res = modsim.maximize_golden(max_func, [0, 5], system, rtol=1e-7)
        self.assertAlmostEqual(res.x, 2)
        self.assertAlmostEqual(res.fun, 0)


class TestVector(unittest.TestCase):
    def assertArrayEqual(self, res, ans):
        self.assertTrue(isinstance(res, np.ndarray))
        self.assertTrue((res == ans).all())

    def assertVectorEqual(self, res, ans):
        self.assertTrue(isinstance(res, modsim.ModSimVector))
        self.assertTrue((res == ans).all())

    def assertVectorAlmostEqual(self, res, ans):
        [self.assertQuantityAlmostEqual(x, y) for x, y in zip(res, ans)]

    def assertQuantityAlmostEqual(self, x, y):
        self.assertEqual(modsim.UNITS(x), modsim.UNITS(y))
        self.assertAlmostEqual(modsim.magnitude(x), modsim.magnitude(y))

    def test_vector_mag(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter

        v = [3, 4]
        self.assertEqual(modsim.vector_mag(v), 5)
        v = modsim.Vector(3, 4)
        self.assertEqual(modsim.vector_mag(v), 5)
        v = modsim.Vector(3, 4) * m
        self.assertEqual(modsim.vector_mag(v), 5 * m)
        self.assertEqual(v.mag, 5 * m)

    def test_vector_mag2(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter

        v = [3, 4]
        self.assertEqual(modsim.vector_mag2(v), 25)
        v = modsim.Vector(3, 4)
        self.assertEqual(modsim.vector_mag2(v), 25)
        v = modsim.Vector(3, 4) * m
        self.assertEqual(modsim.vector_mag2(v), 25 * m * m)

    def test_vector_angle(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        ans = 0.927295218
        v = [3, 4]
        self.assertAlmostEqual(modsim.vector_angle(v), ans)
        v = modsim.Vector(3, 4)
        self.assertAlmostEqual(modsim.vector_angle(v), ans)
        v = modsim.Vector(3, 4) * m
        self.assertAlmostEqual(modsim.vector_angle(v), ans)

    def test_vector_hat(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        v = [3, 4]
        ans = [0.6, 0.8]
        self.assertArrayEqual(modsim.vector_hat(v), ans)

        v = modsim.Vector(3, 4)
        self.assertVectorEqual(modsim.vector_hat(v), ans)
        v = modsim.Vector(3, 4) * m
        self.assertVectorEqual(modsim.vector_hat(v), ans)

        v = [0, 0]
        ans = [0, 0]
        self.assertArrayEqual(modsim.vector_hat(v), ans)
        v = modsim.Vector(0, 0)
        self.assertVectorEqual(modsim.vector_hat(v), ans)
        v = modsim.Vector(0, 0) * m
        self.assertVectorEqual(modsim.vector_hat(v), ans)

    def test_vector_perp(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        v = [3, 4]
        ans = [-4, 3]
        self.assertTrue((modsim.vector_perp(v) == ans).all())
        v = modsim.Vector(3, 4)
        self.assertTrue((modsim.vector_perp(v) == ans).all())
        v = modsim.Vector(3, 4) * m
        self.assertTrue((modsim.vector_perp(v) == ans * m).all())

    def test_vector_dot(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        s = modsim.UNITS.second
        v = [3, 4]
        w = [5, 6]
        ans = 39
        self.assertAlmostEqual(modsim.vector_dot(v, w), ans)
        v = modsim.Vector(3, 4)
        self.assertAlmostEqual(modsim.vector_dot(v, w), ans)
        self.assertAlmostEqual(modsim.vector_dot(w, v), ans)

        v = modsim.Vector(3, 4) * m
        self.assertAlmostEqual(modsim.vector_dot(v, w), ans * m)
        self.assertAlmostEqual(modsim.vector_dot(w, v), ans * m)

        w = modsim.Vector(5, 6) / s
        self.assertAlmostEqual(modsim.vector_dot(v, w), ans * m / s)
        self.assertAlmostEqual(modsim.vector_dot(w, v), ans * m / s)

    def test_vector_cross_2D(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        s = modsim.UNITS.second
        ans = -2

        v = [3, 4]
        w = [5, 6]
        self.assertAlmostEqual(modsim.vector_cross(v, w), ans)
        self.assertAlmostEqual(modsim.vector_cross(w, v), -ans)

        v = modsim.Vector(3, 4)
        self.assertAlmostEqual(modsim.vector_cross(v, w), ans)
        self.assertAlmostEqual(modsim.vector_cross(w, v), -ans)

        v = modsim.Vector(3, 4) * m
        self.assertAlmostEqual(modsim.vector_cross(v, w), ans * m)
        self.assertAlmostEqual(modsim.vector_cross(w, v), -ans * m)

        w = modsim.Vector(5, 6) / s
        self.assertAlmostEqual(modsim.vector_cross(v, w), ans * m / s)
        self.assertAlmostEqual(modsim.vector_cross(w, v), -ans * m / s)

    def test_vector_cross_3D(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        s = modsim.UNITS.second
        ans = [-2, 4, -2]

        v = [3, 4, 5]
        w = [5, 6, 7]
        v_neg = [-3, -4, -5]
        w_neg = [-5, -6, -7]

        self.assertArrayEqual(modsim.vector_cross(v, w), ans)
        self.assertArrayEqual(modsim.vector_cross(w_neg, v_neg), ans)

        v = modsim.Vector(3, 4, 5)
        self.assertVectorEqual(modsim.vector_cross(v, w), ans)
        self.assertVectorEqual(modsim.vector_cross(w_neg, v_neg), ans)

        v = modsim.Vector(3, 4, 5) * m
        self.assertVectorEqual(modsim.vector_cross(v, w), ans * m)
        self.assertVectorEqual(modsim.vector_cross(w_neg, v_neg), ans * m)

        w = modsim.Vector(5, 6, 7) / s
        self.assertVectorEqual(modsim.vector_cross(v, w), ans * m / s)
        self.assertVectorEqual(modsim.vector_cross(w_neg, v_neg), ans * m / s)

    def test_scalar_proj(self):

        m = modsim.UNITS.meter
        s = modsim.UNITS.second
        ans = 4.9934383
        ans2 = 7.8

        v = [3, 4]
        w = [5, 6]
        self.assertAlmostEqual(modsim.scalar_proj(v, w), ans)
        self.assertAlmostEqual(modsim.scalar_proj(w, v), ans2)

        v = modsim.Vector(3, 4)
        self.assertAlmostEqual(modsim.scalar_proj(v, w), ans)
        self.assertAlmostEqual(modsim.scalar_proj(w, v), ans2)

        v = modsim.Vector(3, 4) * m
        self.assertQuantityAlmostEqual(modsim.scalar_proj(v, w), ans * m)
        self.assertAlmostEqual(modsim.scalar_proj(w, v), ans2)

        w = modsim.Vector(5, 6) / s
        self.assertQuantityAlmostEqual(modsim.scalar_proj(v, w), ans * m)
        self.assertQuantityAlmostEqual(modsim.scalar_proj(w, v), ans2 / s)

    def test_vector_proj(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        s = modsim.UNITS.second
        ans = [3.19672131, 3.83606557]
        ans2 = modsim.Quantity([4.68, 6.24])

        v = [3, 4]
        w = [5, 6]
        self.assertVectorAlmostEqual(modsim.vector_proj(v, w), ans)
        self.assertVectorAlmostEqual(modsim.vector_proj(w, v), ans2)

        v = modsim.Vector(3, 4)
        self.assertVectorAlmostEqual(modsim.vector_proj(v, w), ans)
        self.assertVectorAlmostEqual(modsim.vector_proj(w, v), ans2)

        v = modsim.Vector(3, 4) * m
        self.assertVectorAlmostEqual(modsim.vector_proj(v, w), ans * m)
        self.assertVectorAlmostEqual(modsim.vector_proj(w, v), ans2)

        w = modsim.Vector(5, 6) / s
        self.assertVectorAlmostEqual(modsim.vector_proj(v, w), ans * m)
        self.assertVectorAlmostEqual(modsim.vector_proj(w, v), ans2 / s)

    def test_vector_dist(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        v = [3, 4]
        w = [6, 8]
        ans = 5
        self.assertAlmostEqual(modsim.vector_dist(v, w), ans)
        self.assertAlmostEqual(modsim.vector_dist(w, v), ans)

        v = modsim.Vector(3, 4)
        self.assertAlmostEqual(modsim.vector_dist(v, w), ans)
        self.assertAlmostEqual(modsim.vector_dist(w, v), ans)

        v = modsim.Vector(3, 4) * m
        w = modsim.Vector(6, 8) * m
        self.assertAlmostEqual(modsim.vector_dist(v, w), ans * m)
        self.assertAlmostEqual(modsim.vector_dist(w, v), ans * m)

    def test_vector_diff_angle(self):
        warnings.simplefilter("error", Warning)
        m = modsim.UNITS.meter
        v = [3, 4]
        w = [5, 6]
        ans = 0.0512371674
        self.assertAlmostEqual(modsim.vector_diff_angle(v, w), ans)
        self.assertAlmostEqual(modsim.vector_diff_angle(w, v), -ans)

        v = modsim.Vector(3, 4)
        self.assertAlmostEqual(modsim.vector_diff_angle(v, w), ans)
        self.assertAlmostEqual(modsim.vector_diff_angle(w, v), -ans)

        v = modsim.Vector(3, 4) * m
        w = modsim.Vector(5, 6) * m
        self.assertAlmostEqual(modsim.vector_diff_angle(v, w), ans)
        self.assertAlmostEqual(modsim.vector_diff_angle(w, v), -ans)


class TestSeriesCopy(unittest.TestCase):
    def test_series_copy(self):
        series = modsim.TimeSeries()
        res = series.copy()
        self.assertTrue(isinstance(res, modsim.TimeSeries))


class TestMagnitudeUNITS(unittest.TestCase):
    def test_magnitudes(self):
        # scalar
        x = 5
        res = modsim.magnitudes(x)
        self.assertEqual(res, 5)
        res = modsim.magnitudes(x * modsim.UNITS.meter)
        self.assertEqual(res, 5)

        # list (result is NumPy array)
        t = [1, 2, 3]
        res = modsim.magnitudes(t)
        self.assertEqual(res, [1, 2, 3])
        res = modsim.magnitudes(t * modsim.UNITS.meter)
        self.assertTrue((res == [1, 2, 3]).all())

        # Series (result is list)
        s = modsim.ModSimSeries([1, 2, 3])
        res = modsim.magnitudes(s)
        self.assertTrue((res == [1, 2, 3]).all())
        res = modsim.magnitudes(s * modsim.UNITS.meter)
        self.assertTrue((res == [1, 2, 3]).all())

        # modsim.Quantity containing Series(result is Series)
        res = modsim.magnitudes(modsim.UNITS.meter * s)
        self.assertTrue((res == [1, 2, 3]).all())

    def test_UNITS(self):
        # scalar
        x = 5
        res = modsim.UNITS(x)
        self.assertEqual(res, 1)
        res = modsim.UNITS(x * modsim.UNITS.meter)
        self.assertEqual(res, modsim.UNITS.meter)

        # list (result is list)
        t = [1, 2, 3]
        res = modsim.UNITS(t)
        self.assertEqual(res, [1, 1, 1])
        res = modsim.UNITS(t * modsim.UNITS.meter)
        self.assertEqual(res, modsim.UNITS.meter)

        # Series (result Series)
        s = modsim.ModSimSeries([1, 2, 3])
        res = modsim.UNITS(s)
        self.assertTrue((res == [1, 1, 1]).all())

        # Series containing Quantities (result is a Series)
        res = modsim.UNITS(s * modsim.UNITS.meter)
        self.assertTrue((res == [modsim.UNITS.meter] * 3).all())

        # modsim.Quantity containing Series(result is a single Unit object)
        res = modsim.UNITS(modsim.UNITS.meter * s)
        self.assertEqual(res, modsim.UNITS.meter)


class TestPlot(unittest.TestCase):
    def test_plot(self):
        os.environ["QT_XKB_CONFIG_ROOT"] = "/usr/share/X11/xkb"

        t = [1, 2, 3]
        modsim.plot(t)

        t = [1, 2, 3] * modsim.UNITS.meter
        modsim.plot(t)

        x = [4, 5, 6]
        modsim.plot(x, t)

        x = [4, 5, 6] * modsim.UNITS.second
        modsim.plot(x, t)

        a = np.array(t)
        modsim.plot(a)

        x = np.array(x)
        modsim.plot(x, a)

        s = modsim.TimeSeries(t)
        modsim.plot(s)

        s = modsim.TimeSeries(t, x)
        modsim.plot(s)

        s = modsim.TimeSeries(a, x)
        modsim.plot(s)


if __name__ == "__main__":
    unittest.main()
