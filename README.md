# Printer Supplies Flask Application

This is a Flask application named "Printer Supplies" that utilizes the AdminLTE theme with Bootstrap. The application is structured to provide a clean and organized way to manage printer supplies.

## Project Structure

```
Printer Supplies
├── app.py
├── config.py
├── requirements.txt
├── templates
│   ├── base.html
│   └── index.html
├── static
│   ├── css
│   └── js
└── README.md
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Printer Supplies
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage Guidelines

- The application serves as a platform to manage printer supplies.
- You can extend the functionality by adding more routes and templates as needed.
- Custom CSS and JavaScript can be added in the `static/css` and `static/js` directories respectively.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.