import pytest
from unittest.mock import patch, MagicMock
from app.ai.ai_processor import tag_article, summarize_article

@pytest.fixture
def mock_openai():
    with patch('app.ai.ai_processor.client.chat.completions.create') as mock:
        yield mock

def test_tag_article(mock_openai):
    # Mock response for tagging
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '''
    {
        "companies": ["Apple", "Microsoft"],
        "topics": ["Product Launch", "Partnership"]
    }
    '''
    mock_openai.return_value = mock_response
    
    article_text = "Apple and Microsoft announced a new partnership today..."
    result = tag_article(article_text)
    
    assert "companies" in result
    assert "topics" in result
    assert "Apple" in result["companies"]
    assert "Microsoft" in result["companies"]
    assert "Product Launch" in result["topics"]
    assert "Partnership" in result["topics"]
    
    # Verify OpenAI API was called with correct parameters
    mock_openai.assert_called_once()
    call_args = mock_openai.call_args[1]
    assert call_args["model"] == "gpt-3.5-turbo"
    assert len(call_args["messages"]) > 0

def test_summarize_article(mock_openai):
    # Mock response for summarization
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a test summary."
    mock_openai.return_value = mock_response
    
    article_text = "Long article text here..."
    result = summarize_article(article_text)
    
    assert result == "This is a test summary."
    
    # Verify OpenAI API was called with correct parameters
    mock_openai.assert_called_once()
    call_args = mock_openai.call_args[1]
    assert call_args["model"] == "gpt-4"
    assert len(call_args["messages"]) > 0

def test_tag_article_error_handling(mock_openai):
    # Mock API error
    mock_openai.side_effect = Exception("API Error")
    
    article_text = "Test article"
    result = tag_article(article_text)
    
    # Should return empty dict on error
    assert result == {"companies": [], "topics": []}

def test_summarize_article_error_handling(mock_openai):
    # Mock API error
    mock_openai.side_effect = Exception("API Error")
    
    article_text = "Test article"
    result = summarize_article(article_text)
    
    # Should return empty string on error
    assert result == "" 