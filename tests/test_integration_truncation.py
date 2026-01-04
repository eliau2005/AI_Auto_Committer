import pytest
from unittest.mock import MagicMock, patch
from controllers.main_controller import MainController
from models.app_state import AppState
from ai_service import AIService

@pytest.fixture
def integration_setup():
    state = AppState()
    # Mock Git
    git = MagicMock()
    # Setup AI with mock client
    with patch('ai_service.ConfigManager') as MockConfig:
        config_instance = MockConfig.return_value
        config_instance.api_key = "fake_key"
        config_instance.get_api_base_url.return_value = "https://api.openai.com/v1"
        config_instance.get_provider.return_value = "openai"
        config_instance.model_name = "gpt-4o-mini"
        config_instance.get_system_prompt.return_value = None
        
        ai = AIService()
        
    ai.client = MagicMock()
    # Mock View
    view = MagicMock()
    view.diff_view = MagicMock()
    view.commit_view = MagicMock()
    
    controller = MainController(state, view, git, ai)
    
    # Patch _update_ui_safe to run immediately
    controller._update_ui_safe = lambda callback: callback()
    
    return controller, git, ai, view

def test_full_truncation_flow(integration_setup):
    controller, git, ai, view = integration_setup
    
    # 1. Setup Large Diff
    # Using a lot of words to ensure it exceeds token limit (4000)
    large_diff = "diff --git a/main.py b/main.py\n" + ("word " * 5000)
    git.get_diff.return_value = large_diff
    
    # Mock AI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Summary commit message"
    ai.client.chat.completions.create.return_value = mock_response
    
    # 2. Select files
    controller.state.selected_files = {"main.py"}
    
    # 3. Call Generate
    with patch('threading.Thread') as mock_thread:
        # Execute the target function immediately
        def side_effect(*args, **kwargs):
            target = kwargs.get('target')
            if target:
                target()
            return MagicMock()
            
        mock_thread.side_effect = side_effect
        
        controller.generate_commit_message()
        
        # Verify
        # 1. AI called with truncated diff
        call_args = ai.client.chat.completions.create.call_args
        sent_prompt = call_args.kwargs['messages'][1]['content']
        assert len(sent_prompt) < len(large_diff)
        
        # We accept either TRUNCATED (blind sacrifice), [Truncated] (budgeting), or [Remaining Diff Truncated] (hard final cut)
        assert "TRUNCATED" in sent_prompt or "[Truncated]" in sent_prompt or "SUMMARIZED" in sent_prompt or "Remaining Diff Truncated" in sent_prompt
        
        # 2. AppState updated
        assert controller.state.truncation_warning is True
        
        # 3. View updated (warning shown)
        view.diff_view.set_warning.assert_called_with(True)

def test_smart_sacrifice_integration(integration_setup):
    controller, git, ai, view = integration_setup
    
    # Setup: 
    # 1. Ignored file (large) -> Should be sacrificed/summarized
    # 2. Logic file (large) -> Should be kept as much as possible (budgeted)
    
    # We need enough content to trigger limits. Limit is 4000.
    # Use "word " pattern to ensure tiktoken doesn't compress too much.
    
    ignored_content = "diff --git a/dist/bundle.js b/dist/bundle.js\n" + ("ignored " * 2000)
    logic_content = "diff --git a/src/logic.py b/src/logic.py\n" + ("logic " * 3000)
    
    full_diff = f"{ignored_content}\n{logic_content}"
    git.get_diff.return_value = full_diff
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Smart summary"
    ai.client.chat.completions.create.return_value = mock_response
    
    controller.state.selected_files = {"dist/bundle.js", "src/logic.py"}
    
    with patch('threading.Thread') as mock_thread:
        def side_effect(*args, **kwargs):
            target = kwargs.get('target')
            if target:
                target()
            return MagicMock()
            
        mock_thread.side_effect = side_effect
        
        controller.generate_commit_message()
        
        call_args = ai.client.chat.completions.create.call_args
        sent_prompt = call_args.kwargs['messages'][1]['content']
        
        # 1. Ignored file should be summarized or blind truncated
        assert "bundle.js [SUMMARIZED]" in sent_prompt or "bundle.js [TRUNCATED]" in sent_prompt
        
        # 2. Logic file should be present but maybe budgeted
        # It shouldn't be blindly summarized/truncated at the header level if space permits.
        assert "logic.py [TRUNCATED]" not in sent_prompt
        assert "logic.py [SUMMARIZED]" not in sent_prompt
        assert "logic " * 100 in sent_prompt # Check content exists

def test_no_truncation_flow(integration_setup):
    controller, git, ai, view = integration_setup
    
    small_diff = "diff --git a/main.py b/main.py\n+ small change"
    git.get_diff.return_value = small_diff
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Small msg"
    ai.client.chat.completions.create.return_value = mock_response
    controller.state.selected_files = {"main.py"}

    with patch('threading.Thread') as mock_thread:
        def side_effect(*args, **kwargs):
            target = kwargs.get('target')
            if target:
                target()
            return MagicMock()
            
        mock_thread.side_effect = side_effect
        
        controller.generate_commit_message()
        
        assert controller.state.truncation_warning is False
        view.diff_view.set_warning.assert_called_with(False)