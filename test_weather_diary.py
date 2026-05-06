import unittest
import json
import os
import tempfile
from datetime import datetime
class TestWeatherDiaryValidation(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.append('.')
        from weather_diary import WeatherDiary
        import tkinter as tk
        self.root = tk.Tk()
        self.app = WeatherDiary(self.root)
    def tearDown(self):
        self.root.destroy()
    def test_validate_date_valid(self):
        valid_dates = ["2024-12-25", "2024-01-01", "1999-12-31"]
        for date in valid_dates:
            self.assertTrue(self.app.validate_date(date))
    def test_validate_date_invalid(self):
        invalid_dates = ["25-12-2024", "2024/12/25", "2024-13-01", "2024-12-32", "invalid", ""]
        for date in invalid_dates:
            self.assertFalse(self.app.validate_date(date))
    def test_validate_temperature_valid(self):
        valid_temps = ["25", "-10", "0", "36.6", "-5.5", "100"]
        for temp in valid_temps:
            is_valid, value = self.app.validate_temperature(temp)
            self.assertTrue(is_valid)
            self.assertIsInstance(value, (int, float))
    def test_validate_temperature_invalid(self):
        invalid_temps = ["abc", "25°C", "", " ", "one hundred", "12,5"]
        for temp in invalid_temps:
            is_valid, _ = self.app.validate_temperature(temp)
            self.assertFalse(is_valid)
    def test_temperature_boundary_values(self):
        boundaries = ["-273.15", "-273.16", "999", "1000"]
        for temp in boundaries:
            is_valid, _ = self.app.validate_temperature(temp)
            self.assertTrue(is_valid)
class TestJSONOperations(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.test_data = [
            {
                "date": "2024-12-25",
                "temperature": 25.5,
                "description": "Sunny day",
                "precipitation": "Нет"
            },
            {
                "date": "2024-12-26",
                "temperature": -5.0,
                "description": "Snowy",
                "precipitation": "Да"
            }
        ]
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    def test_save_to_json(self):
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=4)
        self.assertTrue(os.path.exists(self.temp_file.name))
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, self.test_data)
    def test_load_from_json(self):
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=4)
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["date"], "2024-12-25")
        self.assertEqual(loaded_data[1]["temperature"], -5.0)
    def test_empty_json_handling(self):
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            json.dump([], f)
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, [])
    def test_corrupted_json_handling(self):
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write("{corrupted json}")
        with self.assertRaises(json.JSONDecodeError):
            with open(self.temp_file.name, 'r', encoding='utf-8') as f:
                json.load(f)
class TestFilterOperations(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"date": "2024-12-25", "temperature": 25.0, "description": "Sunny", "precipitation": "Нет"},
            {"date": "2024-12-25", "temperature": 15.0, "description": "Cloudy", "precipitation": "Нет"},
            {"date": "2024-12-26", "temperature": -5.0, "description": "Snow", "precipitation": "Да"},
            {"date": "2024-12-27", "temperature": 10.0, "description": "Rain", "precipitation": "Да"}
        ]
    def test_filter_by_date(self):
        filtered = [r for r in self.records if r["date"] == "2024-12-25"]
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["temperature"], 25.0)
        self.assertEqual(filtered[1]["temperature"], 15.0)
    def test_filter_by_temperature_above(self):
        threshold = 10.0
        filtered = [r for r in self.records if r["temperature"] > threshold]
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r["temperature"] > threshold for r in filtered))
    def test_filter_by_date_and_temperature(self):
        filtered = [r for r in self.records 
                   if r["date"] == "2024-12-25" and r["temperature"] > 20.0]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["temperature"], 25.0)
    def test_filter_no_results(self):
        filtered = [r for r in self.records if r["date"] == "2025-01-01"]
        self.assertEqual(len(filtered), 0)
    def test_filter_boundary_temperature(self):
        filtered = [r for r in self.records if r["temperature"] > 10.0]
        self.assertEqual(len(filtered), 2)
        filtered_strict = [r for r in self.records if r["temperature"] > 25.0]
        self.assertEqual(len(filtered_strict), 0)
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestWeatherDiaryValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterOperations))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)