
Inventory Management App 

### Overview
The Inventory Management App helps businesses track their stock levels, monitor sales and purchases, and generate reports for business operations. The app is designed to be user-friendly and scalable, allowing businesses of various sizes to manage their inventory efficiently.
**Note**: This project is still in development, and additional features will be added in future updates.

### Features
- Track Inventory: Manage product stock and update quantities for purchases and sales.(implemented)
- Monthly Reporting: Generate monthly stock and sales reports.(implemented)
- Supplier Management: Manage suppliers and their associated products.(planned)
- Admin Dashboard: Access real-time inventory data and reporting.(planned)

### Tech Stack
- Backend: Django (Python)
- Frontend: HTML, CSS, JavaScript
- Database: PostgreSQL

### Installation
#### Prerequisites:
- Python 3.8 or higher
- Django(will be installed when you run `pip install -r requirements.txt`)
- Git
#### Steps:
1. Clone the repository:
    git clone https://github.com/Siddo6/inventory-app.git
    cd inventory-app

2. Create and activate a virtual environment:
    python -m venv venv
    source venv/bin/activate   # For Linux/macOS
    venv\Scripts\activate      # For Windows

3. Install dependencies:
    pip install -r requirements.txt

4. Apply migrations to set up the database:
    python manage.py migrate

5. Run the development server:
    python manage.py runserver

6. Access the app at http://127.0.0.1:8000/.

### Future Enhancements
- User Roles: Add different user roles for inventory management, such as admins, managers, and staff.
- Advanced Reports: Generate more detailed reports including supplier performance and cost analysis.

### Contributing
Feel free to contribute by creating issues or submitting pull requests. Make sure to follow the standard guidelines and use feature branches for new functionality.

### License
This project is licensed under the MIT License. See the LICENSE file for details.
