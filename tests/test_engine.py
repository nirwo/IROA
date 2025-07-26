
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.engine import get_underutilized_vms
from recommendation.engine import generate_recommendations

def test_underutilized_returns_list():
    result = get_underutilized_vms()
    assert isinstance(result, list)

def test_generate_recommendations_format():
    result = generate_recommendations()
    if result:
        assert "vm" in result[0]
        assert "suggestion" in result[0]
