#!/usr/bin/env python3
"""
LINE Bot Runner Script
Run this script to start the LINE chatbot server
"""

from line_bot import app

if __name__ == "__main__":
    print("Starting LINE Bot Server...")
    print("Make sure to set your LINE_ACCESS_TOKEN in the .env file")
    print("Webhook URL should be: https://your-domain.com/callback")
    app.run(host='0.0.0.0', port=5000, debug=True)