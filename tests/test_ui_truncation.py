import pytest
from models.app_state import AppState

def test_app_state_truncation():
    state = AppState()
    # Check default
    assert state.truncation_warning is False
    
    # Check update
    state.truncation_warning = True
    assert state.truncation_warning is True
    
    # Check type validation
    with pytest.raises(TypeError):
        state.truncation_warning = "yes"
