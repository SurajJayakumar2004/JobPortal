#!/usr/bin/env python3
import http.server
import socketserver
import os
import mimetypes
from urllib.parse import urlparse

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for Single Page Applications that serves index.html for all routes"""
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Remove query parameters for file checking
        file_path = path.lstrip('/')
        
        # If it's a static file, serve it normally
        if file_path.startswith('static/') or file_path in ['manifest.json', 'favicon.ico', 'robots.txt']:
            return super().do_GET()
        
        # If it's the root path or index.html, serve it normally
        if file_path == '' or file_path == 'index.html':
            return super().do_GET()
        
        # For all other routes (React Router routes), serve index.html
        self.path = '/index.html'
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == "__main__":
    PORT = 3002
    
    # Change to the build directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(script_dir, 'build'))
    
    with socketserver.TCPServer(("", PORT), SPAHandler) as httpd:
        print(f"Serving SPA at http://localhost:{PORT}")
        httpd.serve_forever()
