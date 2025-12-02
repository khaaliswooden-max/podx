import os
import sys
from dotenv import load_dotenv

def test_environment_variables():
    load_dotenv()
    assert os.getenv('PODX_ENV') == 'development'
    assert os.getenv('XDOP_COMPLIANCE_LEVEL') == 'strict'

def test_python_version():
    assert sys.version_info >= (3, 11)

def test_imports():
    import requests
    import numpy
    assert requests
    assert numpy
