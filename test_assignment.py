import unittest
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import re
import pandas as pd
import numpy as np


class TestClimateEDA(unittest.TestCase):
    all_code = ""  # ✅ Explicitly define at the class level
    all_markdown = ""

    @classmethod
    def setUpClass(cls):
        """Set up test environment by executing the Jupyter notebook."""
        # Load the notebook
        with open('climate_eda.ipynb', 'r', encoding='utf-8') as f:
            cls.notebook = nbformat.read(f, as_version=4)

        # Execute the notebook
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(cls.notebook, {'metadata': {'path': '.'}})

        # Extract code and markdown cells
        cls.code_cells = [cell for cell in cls.notebook.cells if cell['cell_type'] == 'code']
        cls.markdown_cells = [cell for cell in cls.notebook.cells if cell['cell_type'] == 'markdown']

        # ✅ Ensure attributes are initialized properly
        cls.all_code = '\n'.join([cell.get('source', '') for cell in cls.code_cells]) if cls.code_cells else ""
        cls.all_markdown = '\n'.join([cell.get('source', '') for cell in cls.markdown_cells]) if cls.markdown_cells else ""

        # 🔥 Debugging output for GitHub Actions 🔥
        print("\n========= DEBUG: Extracted Notebook Code =========\n")
        print(cls.all_code[:500])  # Print only the first 500 characters for debugging
        print("\n========= DEBUG: End of Extracted Notebook Code =========\n")

        # Ensure the data file is properly loaded
        for cell in cls.code_cells:
            if 'df = pd.read_csv' in cell.get('source', ''):
                match = re.search(r'(\w+)\s*=\s*pd\.read_csv', cell['source'])
                if match:
                    cls.df_name = match.group(1)
                    break

    def test_required_libraries(self):
        """Test that all required libraries are imported."""
        required_libs = ['pandas', 'numpy', 'matplotlib', 'seaborn']
        for lib in required_libs:
            self.assertIn(f"import {lib}", self.__class__.all_code, f"Missing required import for {lib}")

    def test_data_loading(self):
        """Test that climate data is loaded."""
        self.assertIn("read_csv('data/Climate_Change_Indicators.csv')", self.__class__.all_code, "Data file not loaded correctly")

    def test_yearly_aggregation(self):
        """Test that data is aggregated by year."""
        yearly_agg_patterns = [
            r"groupby\(\s*['\"]Year['\"]\s*\)",
            r"groupby\(\s*['\"]\w+['\"]\s*\)\[['\"]\w+['\"]",
            r"resample\(\s*['\"]Y['\"]\s*\)"
        ]
        found_yearly_agg = any(re.search(pattern, self.__class__.all_code) for pattern in yearly_agg_patterns)
        self.assertTrue(found_yearly_agg, "No evidence of yearly data aggregation")

    def test_univariate_analysis(self):
        """Test for univariate analysis visualizations and statistics."""
        univariate_vis_patterns = [
            r"hist(plot)?\(",
            r"boxplot\(",
            r"plot\(",
            r"displot\(",
            r"kdeplot\("
        ]
        found_univariate_vis = any(re.search(pattern, self.__class__.all_code) for pattern in univariate_vis_patterns)
        self.assertTrue(found_univariate_vis, "No evidence of univariate visualizations")

        stats_patterns = [r"describe\(", r"mean\(", r"median\(", r"std\(", r"min\(", r"max\("]
        found_stats = any(re.search(pattern, self.__class__.all_code) for pattern in stats_patterns)
        self.assertTrue(found_stats, "No evidence of descriptive statistics calculation")

    def test_bivariate_analysis(self):
        """Test for bivariate analysis."""
        if not self.__class__.all_code:
            self.fail("all_code is not initialized or is empty.")

        bivariate_vis_patterns = [
            r"scatter(plot)?\(",
            r"reg(plot)?\(",
            r"lineplot\(",
            r"barplot\(",
            r"violinplot\(",
            r"heatmap\(",
            r"corr\("
        ]
        found_bivariate_vis = any(re.search(pattern, self.__class__.all_code) for pattern in bivariate_vis_patterns)
        self.assertTrue(found_bivariate_vis, "No evidence of bivariate visualizations")

    def test_multivariate_analysis(self):
        """Test for multivariate analysis."""
        multivariate_vis_patterns = [
            r"pairplot\(",
            r"PCA\(",
            r"heatmap\(",
            r"parallel_coordinates\(",
            r"andrews_curves\(",
            r"radviz\(",
            r"3d scatter"
        ]
        found_multivariate_vis = any(re.search(pattern, self.__class__.all_code) for pattern in multivariate_vis_patterns)
        self.assertTrue(found_multivariate_vis, "No evidence of multivariate visualizations")

    def test_conclusions_present(self):
        """Test that conclusions are present in markdown cells."""
        conclusion_patterns = [
            r"[Cc]onclusion",
            r"[Ff]inding",
            r"[Ss]ummar",
            r"[Ii]nsight",
            r"[Oo]bservation"
        ]
        found_conclusion = any(re.search(pattern, self.__class__.all_markdown) for pattern in conclusion_patterns)
        self.assertTrue(found_conclusion, "No evidence of conclusions or insights in the analysis")

    def test_min_number_of_visualizations(self):
        """Test that there are at least 5 different visualizations."""
        vis_function_patterns = [
            r"plt\.\w+\(",
            r"sns\.\w+\(",
            r"df\.\w+\.plot\("
        ]
        num_vis = sum(len(re.findall(pattern, self.__class__.all_code)) for pattern in vis_function_patterns)
        self.assertGreaterEqual(num_vis, 5, "Insufficient number of visualizations (minimum 5 required)")

    def test_climate_variables_analyzed(self):
        """Test that all climate variables are analyzed."""
        climate_vars = ['Global Average Temperature (°C)', 'CO2 Concentration (ppm)', 'Sea Level Rise (mm)', 'Arctic Ice Area (million km²)']
        for var in climate_vars:
            self.assertIn(var, self.__class__.all_code, f"Climate variable {var} not analyzed")

    def calculate_grade(self):
        """Calculate the grade based on passing tests"""
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestClimateEDA)
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_result = test_runner.run(test_suite)  # Run tests properly

        total_tests = test_result.testsRun
        passed_tests = total_tests - len(test_result.failures) - len(test_result.errors)

        # Calculate grade (out of 100)
        grade = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        return round(grade)


if __name__ == '__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestClimateEDA)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)

    # Calculate and print grade
    test_instance = TestClimateEDA()
    grade = test_instance.calculate_grade()
    print(f"\nFinal Grade: {grade}/100")

    # ✅ Debugging: Print test results in GitHub Actions
    print("\n========= DEBUG: GitHub Actions Test Results =========")
    print(f"Total Tests Run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    print("======================================================")