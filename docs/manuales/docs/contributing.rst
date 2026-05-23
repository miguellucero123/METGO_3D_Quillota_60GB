# 🌾 METGO 3D - Contributing Guide
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Contributing Guide
==================

This guide explains how to contribute to METGO 3D.

Getting Started
---------------

1. **Fork the Repository**: Fork the repository on GitHub
2. **Clone Your Fork**: Clone your fork locally
3. **Create a Branch**: Create a feature branch
4. **Make Changes**: Make your changes
5. **Test Changes**: Test your changes
6. **Submit Pull Request**: Submit a pull request

Development Setup
-----------------

1. **Install Dependencies**:

.. code-block:: bash

   pip install -r requirements.txt

2. **Install Development Dependencies**:

.. code-block:: bash

   pip install pytest pytest-cov flake8 black isort mypy bandit

3. **Run Tests**:

.. code-block:: bash

   python test_sistema.py

4. **Run Linting**:

.. code-block:: bash

   flake8 .
   black --check .
   isort --check-only .

Code Style
----------

Follow these coding standards:

1. **Python Style**: Follow PEP 8
2. **Line Length**: Maximum 127 characters
3. **Imports**: Use isort for import sorting
4. **Formatting**: Use black for code formatting
5. **Type Hints**: Use type hints where appropriate
6. **Docstrings**: Use Google-style docstrings

Example:

.. code-block:: python

   def process_meteorological_data(
       data: pd.DataFrame, 
       validation: bool = True
   ) -> pd.DataFrame:
       """
       Process meteorological data with validation.
       
       Args:
           data: Raw meteorological data
           validation: Whether to validate data
           
       Returns:
           Processed meteorological data
       """
       if validation:
           data = validate_data(data)
       
       return data

Testing
-------

Write tests for your changes:

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component integration
3. **System Tests**: Test complete system functionality
4. **Performance Tests**: Test performance characteristics

Example:

.. code-block:: python

   def test_data_validation():
       """Test data validation function."""
       data = pd.DataFrame({
           'temperatura_max': [25, 30, 35],
           'temperatura_min': [15, 20, 25],
           'precipitacion': [0, 5, 10]
       })
       
       result = validate_data(data)
       assert result is not None
       assert len(result) == 3

Documentation
-------------

Update documentation for your changes:

1. **Code Comments**: Add comments to complex code
2. **Docstrings**: Add docstrings to functions and classes
3. **README**: Update README if needed
4. **API Documentation**: Update API documentation
5. **User Guide**: Update user guide if needed

Example:

.. code-block:: python

   def calculate_agricultural_indices(
       data: pd.DataFrame
   ) -> pd.DataFrame:
       """
       Calculate agricultural indices for meteorological data.
       
       This function calculates various agricultural indices including
       growing degree days, thermal comfort, irrigation needs, and
       frost risk based on meteorological data.
       
       Args:
           data: Meteorological data with temperature and humidity
           
       Returns:
           Data with additional agricultural indices
           
       Raises:
           ValueError: If required columns are missing
       """
       required_columns = ['temperatura_max', 'temperatura_min']
       if not all(col in data.columns for col in required_columns):
           raise ValueError("Required columns missing")
       
       # Calculate indices
       data['grados_dia'] = np.maximum(0, data['temperatura_promedio'] - 10)
       
       return data

Pull Request Process
--------------------

1. **Create Feature Branch**:

.. code-block:: bash

   git checkout -b feature/new-feature

2. **Make Changes**: Make your changes
3. **Test Changes**: Run tests and linting
4. **Commit Changes**:

.. code-block:: bash

   git add .
   git commit -m "Add new feature"

5. **Push Changes**:

.. code-block:: bash

   git push origin feature/new-feature

6. **Create Pull Request**: Create pull request on GitHub

Pull Request Guidelines
-----------------------

1. **Clear Description**: Provide clear description of changes
2. **Reference Issues**: Reference related issues
3. **Test Coverage**: Ensure adequate test coverage
4. **Documentation**: Update documentation as needed
5. **Code Review**: Address code review feedback

Example Pull Request:

.. code-block:: markdown

   ## Description
   
   Add new agricultural index calculation function for frost risk assessment.
   
   ## Changes
   
   - Add `calculate_frost_risk` function
   - Update agricultural indices calculation
   - Add tests for new function
   - Update documentation
   
   ## Testing
   
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] System tests pass
   
   ## Documentation
   
   - [ ] Code comments added
   - [ ] Docstrings updated
   - [ ] API documentation updated

Issue Reporting
---------------

When reporting issues:

1. **Use Issue Template**: Use the provided issue template
2. **Provide Details**: Provide detailed information
3. **Include Logs**: Include relevant log files
4. **Describe Steps**: Describe steps to reproduce
5. **Expected Behavior**: Describe expected behavior

Example Issue:

.. code-block:: markdown

   ## Bug Report
   
   ### Description
   
   Data validation fails for temperature data with negative values.
   
   ### Steps to Reproduce
   
   1. Load data with negative temperatures
   2. Run data validation
   3. Observe validation failure
   
   ### Expected Behavior
   
   Data validation should handle negative temperatures correctly.
   
   ### Actual Behavior
   
   Data validation fails with ValueError.
   
   ### Environment
   
   - Python: 3.9.0
   - OS: Ubuntu 20.04
   - METGO Version: 2.0.0

Feature Requests
----------------

When requesting features:

1. **Clear Description**: Provide clear description
2. **Use Case**: Explain the use case
3. **Benefits**: Explain the benefits
4. **Implementation**: Suggest implementation approach
5. **Priority**: Indicate priority level

Example Feature Request:

.. code-block:: markdown

   ## Feature Request
   
   ### Description
   
   Add support for multiple weather data sources.
   
   ### Use Case
   
   Users need to compare data from different weather services.
   
   ### Benefits
   
   - Improved data accuracy
   - Better redundancy
   - Enhanced reliability
   
   ### Implementation
   
   - Add configuration for multiple sources
   - Implement data fusion algorithms
   - Add source comparison features

Code Review Guidelines
----------------------

When reviewing code:

1. **Check Functionality**: Verify functionality works
2. **Review Code Quality**: Check code quality
3. **Test Coverage**: Ensure adequate test coverage
4. **Documentation**: Check documentation quality
5. **Performance**: Consider performance implications

Review Checklist:

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] Performance is acceptable
- [ ] Security considerations addressed

Release Process
---------------

1. **Version Bump**: Update version numbers
2. **Changelog**: Update changelog
3. **Tests**: Run all tests
4. **Documentation**: Update documentation
5. **Release**: Create release

Example Release:

.. code-block:: bash

   # Update version
   echo "2.1.0" > VERSION
   
   # Update changelog
   # Add new features and fixes
   
   # Run tests
   python test_sistema.py
   
   # Create release
   git tag v2.1.0
   git push origin v2.1.0

Community Guidelines
--------------------

1. **Be Respectful**: Be respectful to all contributors
2. **Be Constructive**: Provide constructive feedback
3. **Be Patient**: Be patient with responses
4. **Be Helpful**: Help other contributors
5. **Be Professional**: Maintain professional behavior

For more information, see the complete documentation.



