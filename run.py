from app import create_app # Import the app factory function from the app package

app = create_app()

if __name__ == '__main__':
    # Run the Flask development server only if this script is executed directly
    app.run(debug=True)
    # Enable debug mode for automatic reload and detailed error page
