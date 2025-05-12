#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Bot API Module
-----------------------
Provides API integration and data processing capabilities for the Enhanced Telegram Bot.

This module handles API interactions with Telegram and other services,
as well as data processing for bot functionality.
"""

import os
import sys
import logging
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramAPI:
    """
    Handles interactions with the Telegram Bot API.
    
    This class provides methods for sending messages, media, and other content
    through the Telegram Bot API, as well as handling webhook setup and updates.
    """
    
    def __init__(self, token: str):
        """
        Initialize the Telegram API handler.
        
        Args:
            token: Telegram Bot API token
        """
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.file_url = f"https://api.telegram.org/file/bot{token}"
        self.session = requests.Session()
        
        # Verify token validity
        self.verify_token()
        
        logger.info("Telegram API initialized")
    
    def verify_token(self) -> bool:
        """
        Verify that the provided token is valid.
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            response = self.session.get(f"{self.api_url}/getMe")
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Invalid token: {data.get('description', 'Unknown error')}")
                return False
            
            bot_info = data.get("result", {})
            logger.info(f"Bot verified: {bot_info.get('username')} (ID: {bot_info.get('id')})")
            return True
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return False
    
    def get_updates(self, offset: int = None, limit: int = 100, timeout: int = 30) -> List[Dict]:
        """
        Get updates from Telegram Bot API.
        
        Args:
            offset: Identifier of the first update to be returned
            limit: Maximum number of updates to be retrieved
            timeout: Timeout in seconds for long polling
            
        Returns:
            List of update objects
        """
        params = {
            "limit": limit,
            "timeout": timeout,
        }
        
        if offset is not None:
            params["offset"] = offset
        
        try:
            response = self.session.get(f"{self.api_url}/getUpdates", params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error getting updates: {data.get('description', 'Unknown error')}")
                return []
            
            return data.get("result", [])
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def send_message(self, chat_id: Union[int, str], text: str, parse_mode: str = None,
                    disable_web_page_preview: bool = None, disable_notification: bool = None,
                    reply_to_message_id: int = None, reply_markup: Dict = None) -> Dict:
        """
        Send a text message to a chat.
        
        Args:
            chat_id: Unique identifier for the target chat
            text: Text of the message to be sent
            parse_mode: Mode for parsing entities in the message text
            disable_web_page_preview: Disables link previews for links in this message
            disable_notification: Sends the message silently
            reply_to_message_id: If the message is a reply, ID of the original message
            reply_markup: Additional interface options
            
        Returns:
            Sent message object
        """
        params = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if parse_mode is not None:
            params["parse_mode"] = parse_mode
        
        if disable_web_page_preview is not None:
            params["disable_web_page_preview"] = disable_web_page_preview
        
        if disable_notification is not None:
            params["disable_notification"] = disable_notification
        
        if reply_to_message_id is not None:
            params["reply_to_message_id"] = reply_to_message_id
        
        if reply_markup is not None:
            params["reply_markup"] = json.dumps(reply_markup)
        
        try:
            response = self.session.post(f"{self.api_url}/sendMessage", json=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error sending message: {data.get('description', 'Unknown error')}")
                return {}
            
            return data.get("result", {})
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {}
    
    def send_photo(self, chat_id: Union[int, str], photo: Union[str, bytes],
                  caption: str = None, parse_mode: str = None,
                  disable_notification: bool = None, reply_to_message_id: int = None,
                  reply_markup: Dict = None) -> Dict:
        """
        Send a photo to a chat.
        
        Args:
            chat_id: Unique identifier for the target chat
            photo: Photo to send (file_id, URL, or file content)
            caption: Photo caption
            parse_mode: Mode for parsing entities in the caption
            disable_notification: Sends the message silently
            reply_to_message_id: If the message is a reply, ID of the original message
            reply_markup: Additional interface options
            
        Returns:
            Sent message object
        """
        params = {
            "chat_id": chat_id,
        }
        
        if caption is not None:
            params["caption"] = caption
        
        if parse_mode is not None:
            params["parse_mode"] = parse_mode
        
        if disable_notification is not None:
            params["disable_notification"] = disable_notification
        
        if reply_to_message_id is not None:
            params["reply_to_message_id"] = reply_to_message_id
        
        if reply_markup is not None:
            params["reply_markup"] = json.dumps(reply_markup)
        
        try:
            if isinstance(photo, str) and (photo.startswith("http") or photo.startswith("file://")):
                # Photo is a URL
                params["photo"] = photo
                response = self.session.post(f"{self.api_url}/sendPhoto", json=params)
            elif isinstance(photo, str) and len(photo) < 100:
                # Photo is likely a file_id
                params["photo"] = photo
                response = self.session.post(f"{self.api_url}/sendPhoto", json=params)
            else:
                # Photo is a file or file content
                files = {
                    "photo": photo if isinstance(photo, bytes) else open(photo, "rb"),
                }
                response = self.session.post(f"{self.api_url}/sendPhoto", data=params, files=files)
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error sending photo: {data.get('description', 'Unknown error')}")
                return {}
            
            return data.get("result", {})
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return {}
    
    def send_document(self, chat_id: Union[int, str], document: Union[str, bytes],
                     caption: str = None, parse_mode: str = None,
                     disable_notification: bool = None, reply_to_message_id: int = None,
                     reply_markup: Dict = None) -> Dict:
        """
        Send a document to a chat.
        
        Args:
            chat_id: Unique identifier for the target chat
            document: Document to send (file_id, URL, or file content)
            caption: Document caption
            parse_mode: Mode for parsing entities in the caption
            disable_notification: Sends the message silently
            reply_to_message_id: If the message is a reply, ID of the original message
            reply_markup: Additional interface options
            
        Returns:
            Sent message object
        """
        params = {
            "chat_id": chat_id,
        }
        
        if caption is not None:
            params["caption"] = caption
        
        if parse_mode is not None:
            params["parse_mode"] = parse_mode
        
        if disable_notification is not None:
            params["disable_notification"] = disable_notification
        
        if reply_to_message_id is not None:
            params["reply_to_message_id"] = reply_to_message_id
        
        if reply_markup is not None:
            params["reply_markup"] = json.dumps(reply_markup)
        
        try:
            if isinstance(document, str) and (document.startswith("http") or document.startswith("file://")):
                # Document is a URL
                params["document"] = document
                response = self.session.post(f"{self.api_url}/sendDocument", json=params)
            elif isinstance(document, str) and len(document) < 100:
                # Document is likely a file_id
                params["document"] = document
                response = self.session.post(f"{self.api_url}/sendDocument", json=params)
            else:
                # Document is a file or file content
                files = {
                    "document": document if isinstance(document, bytes) else open(document, "rb"),
                }
                response = self.session.post(f"{self.api_url}/sendDocument", data=params, files=files)
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error sending document: {data.get('description', 'Unknown error')}")
                return {}
            
            return data.get("result", {})
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            return {}
    
    def get_file(self, file_id: str) -> Dict:
        """
        Get information about a file and prepare it for downloading.
        
        Args:
            file_id: File identifier to get info about
            
        Returns:
            File object with file_path
        """
        params = {
            "file_id": file_id,
        }
        
        try:
            response = self.session.get(f"{self.api_url}/getFile", params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error getting file: {data.get('description', 'Unknown error')}")
                return {}
            
            return data.get("result", {})
        except Exception as e:
            logger.error(f"Error getting file: {e}")
            return {}
    
    def download_file(self, file_path: str, destination: str = None) -> Optional[bytes]:
        """
        Download a file from Telegram.
        
        Args:
            file_path: File path as returned by get_file
            destination: Optional destination path to save the file
            
        Returns:
            File content as bytes if destination is None, otherwise None
        """
        try:
            response = self.session.get(f"{self.file_url}/{file_path}")
            response.raise_for_status()
            
            if destination:
                with open(destination, "wb") as f:
                    f.write(response.content)
                logger.info(f"File downloaded to {destination}")
                return None
            else:
                return response.content
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    def set_webhook(self, url: str, certificate: str = None, max_connections: int = 40,
                   allowed_updates: List[str] = None) -> bool:
        """
        Set a webhook for receiving updates.
        
        Args:
            url: HTTPS URL to send updates to
            certificate: Public key certificate for self-signed certificates
            max_connections: Maximum allowed number of simultaneous HTTPS connections
            allowed_updates: List of update types to receive
            
        Returns:
            True if webhook was set successfully, False otherwise
        """
        params = {
            "url": url,
            "max_connections": max_connections,
        }
        
        if allowed_updates is not None:
            params["allowed_updates"] = json.dumps(allowed_updates)
        
        files = {}
        if certificate:
            files["certificate"] = open(certificate, "rb")
        
        try:
            if files:
                response = self.session.post(f"{self.api_url}/setWebhook", data=params, files=files)
            else:
                response = self.session.post(f"{self.api_url}/setWebhook", json=params)
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error setting webhook: {data.get('description', 'Unknown error')}")
                return False
            
            logger.info(f"Webhook set to {url}")
            return True
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    def delete_webhook(self) -> bool:
        """
        Delete the webhook.
        
        Returns:
            True if webhook was deleted successfully, False otherwise
        """
        try:
            response = self.session.get(f"{self.api_url}/deleteWebhook")
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error deleting webhook: {data.get('description', 'Unknown error')}")
                return False
            
            logger.info("Webhook deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False
    
    def get_webhook_info(self) -> Dict:
        """
        Get current webhook status.
        
        Returns:
            WebhookInfo object
        """
        try:
            response = self.session.get(f"{self.api_url}/getWebhookInfo")
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok", False):
                logger.error(f"Error getting webhook info: {data.get('description', 'Unknown error')}")
                return {}
            
            return data.get("result", {})
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            return {}


class DataProcessor:
    """
    Processes data for the Telegram bot.
    
    This class handles data processing, analysis, and transformation
    for the bot's functionality.
    """
    
    def __init__(self):
        """Initialize the data processor."""
        self.nlp_enabled = False
        self.sentiment_analysis_enabled = False
        self.translation_enabled = False
        
        # Try to import optional NLP libraries
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.nlp_enabled = True
            logger.info("NLP functionality enabled")
        except ImportError:
            logger.warning("NLTK not available, NLP functionality disabled")
        
        try:
            import textblob
            self.sentiment_analysis_enabled = True
            logger.info("Sentiment analysis enabled")
        except ImportError:
            logger.warning("TextBlob not available, sentiment analysis disabled")
        
        try:
            import googletrans
            self.translation_enabled = True
            logger.info("Translation functionality enabled")
        except ImportError:
            logger.warning("Googletrans not available, translation functionality disabled")
        
        logger.info("Data processor initialized")
    
    def process_message(self, message: str) -> str:
        """
        Process a message and generate a response.
        
        Args:
            message: Message text to process
            
        Returns:
            Response text
        """
        # Simple keyword-based response for demonstration
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! How can I help you today?"
        
        if "help" in message_lower:
            return "I can assist you with various tasks. Use /help to see available commands."
        
        if "thank" in message_lower:
            return "You're welcome! Is there anything else I can help with?"
        
        if "bye" in message_lower or "goodbye" in message_lower:
            return "Goodbye! Have a great day!"
        
        # Analyze sentiment if enabled
        if self.sentiment_analysis_enabled and len(message) > 5:
            sentiment = self.analyze_sentiment(message)
            if sentiment > 0.5:
                return "I'm glad you're feeling positive! How can I assist you further?"
            elif sentiment < -0.5:
                return "I'm sorry to hear that. Is there anything I can do to help?"
        
        # Default response
        return "I received your message. Use /help to see what I can do."
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze the sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score (-1.0 to 1.0, where -1 is very negative and 1 is very positive)
        """
        if not self.sentiment_analysis_enabled:
            return 0.0
        
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0
    
    def translate_text(self, text: str, target_language: str = 'en') -> str:
        """
        Translate text to the target language.
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Translated text
        """
        if not self.translation_enabled:
            return text
        
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, dest=target_language)
            return result.text
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text
    
    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        if not self.nlp_enabled:
            return []
        
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            
            # Tokenize and remove stopwords
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(text.lower())
            filtered_words = [word for word in word_tokens if word.isalnum() and word not in stop_words]
            
            # Count word frequencies
            freq_dist = nltk.FreqDist(filtered_words)
            
            # Return most common words
            return [word for word, _ in freq_dist.most_common(num_keywords)]
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def summarize_text(self, text: str, sentences: int = 3) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: Text to summarize
            sentences: Number of sentences in the summary
            
        Returns:
            Summarized text
        """
        if not self.nlp_enabled or len(text) < 100:
            return text
        
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import sent_tokenize, word_tokenize
            
            # Tokenize sentences and words
            stop_words = set(stopwords.words('english'))
            sentences_list = sent_tokenize(text)
            
            if len(sentences_list) <= sentences:
                return text
            
            # Calculate word frequencies
            word_frequencies = {}
            for word in word_tokenize(text.lower()):
                if word.isalnum() and word not in stop_words:
                    if word not in word_frequencies:
                        word_frequencies[word] = 1
                    else:
                        word_frequencies[word] += 1
            
            # Normalize frequencies
            max_frequency = max(word_frequencies.values()) if word_frequencies else 1
            for word in word_frequencies:
                word_frequencies[word] = word_frequencies[word] / max_frequency
            
            # Calculate sentence scores
            sentence_scores = {}
            for i, sentence in enumerate(sentences_list):
                for word in word_tokenize(sentence.lower()):
                    if word in word_frequencies:
                        if i not in sentence_scores:
                            sentence_scores[i] = word_frequencies[word]
                        else:
                            sentence_scores[i] += word_frequencies[word]
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:sentences]
            top_sentences = sorted(top_sentences, key=lambda x: x[0])
            
            # Combine sentences
            summary = ' '.join([sentences_list[i] for i, _ in top_sentences])
            return summary
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return text


class ExternalServiceAPI:
    """
    Handles interactions with external services.
    
    This class provides methods for integrating with external APIs
    and services for enhanced bot functionality.
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize the external service API handler.
        
        Args:
            api_keys: Dictionary of API keys for external services
        """
        self.api_keys = api_keys or {}
        self.session = requests.Session()
        logger.info("External service API initialized")
    
    def get_weather(self, location: str) -> Dict:
        """
        Get weather information for a location.
        
        Args:
            location: Location name or coordinates
            
        Returns:
            Weather information
        """
        if "weather" not in self.api_keys:
            logger.warning("Weather API key not provided")
            return {"error": "Weather API key not configured"}
        
        api_key = self.api_keys["weather"]
        url = f"https://api.openweathermap.org/data/2.5/weather"
        
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {"error": str(e)}
    
    def get_news(self, query: str = None, category: str = None, country: str = "us") -> Dict:
        """
        Get news articles.
        
        Args:
            query: Search query
            category: News category
            country: Country code
            
        Returns:
            News articles
        """
        if "news" not in self.api_keys:
            logger.warning("News API key not provided")
            return {"error": "News API key not configured"}
        
        api_key = self.api_keys["news"]
        url = "https://newsapi.org/v2/top-headlines"
        
        params = {
            "apiKey": api_key,
            "country": country,
        }
        
        if query:
            params["q"] = query
        
        if category:
            params["category"] = category
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return {"error": str(e)}
    
    def translate(self, text: str, target_language: str, source_language: str = None) -> Dict:
        """
        Translate text using a translation API.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Translation result
        """
        if "translate" not in self.api_keys:
            logger.warning("Translation API key not provided")
            return {"error": "Translation API key not configured"}
        
        api_key = self.api_keys["translate"]
        url = "https://translation.googleapis.com/language/translate/v2"
        
        params = {
            "key": api_key,
            "q": text,
            "target": target_language,
        }
        
        if source_language:
            params["source"] = source_language
        
        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {"error": str(e)}
    
    def search_images(self, query: str, count: int = 5) -> Dict:
        """
        Search for images.
        
        Args:
            query: Search query
            count: Number of images to return
            
        Returns:
            Image search results
        """
        if "search" not in self.api_keys:
            logger.warning("Search API key not provided")
            return {"error": "Search API key not configured"}
        
        api_key = self.api_keys["search"]
        search_engine_id = self.api_keys.get("search_engine_id", "")
        
        if not search_engine_id:
            logger.warning("Search engine ID not provided")
            return {"error": "Search engine ID not configured"}
        
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "searchType": "image",
            "num": min(count, 10),
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching images: {e}")
            return {"error": str(e)}


def main():
    """Main function for testing the API module."""
    # Get bot token from environment variable
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    # Create API instance
    api = TelegramAPI(token)
    
    # Test API connection
    if not api.verify_token():
        logger.error("Failed to verify token")
        sys.exit(1)
    
    # Get webhook info
    webhook_info = api.get_webhook_info()
    logger.info(f"Current webhook: {webhook_info.get('url', 'Not set')}")
    
    # Create data processor
    processor = DataProcessor()
    
    # Test data processing
    test_message = "Hello, I'm feeling great today! Can you help me with something?"
    response = processor.process_message(test_message)
    logger.info(f"Test message: {test_message}")
    logger.info(f"Response: {response}")
    
    if processor.sentiment_analysis_enabled:
        sentiment = processor.analyze_sentiment(test_message)
        logger.info(f"Sentiment: {sentiment}")
    
    if processor.nlp_enabled:
        keywords = processor.extract_keywords(test_message)
        logger.info(f"Keywords: {keywords}")
    
    logger.info("API module test completed successfully")


if __name__ == "__main__":
    main()
