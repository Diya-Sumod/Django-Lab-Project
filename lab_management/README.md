# Lab Management Dashboard

A Django-based web application for managing server clusters, tracking incidents, and monitoring lab infrastructure.

## Features

- **Dashboard Overview**: Real-time view of all clusters, servers, and incidents
- **Excel Import**: Easily import server data from Excel files
- **Cluster Management**: Organize servers into clusters with ownership details
- **Incident Tracking**: Monitor and track incidents with severity levels
- **Server Details**: Comprehensive server information including iDRAC credentials
- **API Integration**: RESTful API for external incident tracking systems
- **Search Functionality**: Quick search across servers and incidents
- **Responsive Design**: Modern, mobile-friendly interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd lab_management
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Usage

### Importing Excel Data

1. Navigate to the dashboard
2. Click "Import Excel Data"
3. Upload your Excel file with the following columns:
   - ROLE (Master, Worker, Storage, GPU, Network)
   - SERVER MODEL
   - GENERATION
   - SERVICE TAG (required)
   - IDRAC IP
   - IDRAC CREDS (format: username:password)
   - BMC MAC ADDRESS
   - PXE MAC ADDRESS

### Managing Clusters

- View all clusters on the main dashboard
- Each cluster shows server count, GPU information, and incident status
- Click on a cluster to see detailed information

### Tracking Incidents

- Add incidents manually through the web interface
- Use the API endpoint for external system integration
- Incidents are automatically linked to servers via service tags

### API Integration

External systems can post incident updates to:
```
POST /api/incidents/
```

Parameters:
- `incident_id`: Unique incident identifier
- `service_tag`: Server service tag
- `title`: Incident title
- `description`: Incident description
- `severity`: low/medium/high/critical
- `status`: open/investigating/resolved/closed
- `external_site`: URL to external tracking system

## Models

### Cluster
- `name`: Cluster name (unique)
- `owner`: Cluster owner
- `description`: Optional description
- `gpu_count`: Number of GPUs
- `gpu_type`: Type of GPUs
- `ib_band`: InfiniBand bandwidth

### Server
- `cluster`: Foreign key to Cluster
- `role`: Server role (Master, Worker, Storage, GPU, Network)
- `server_model`: Server model name
- `generation`: Server generation
- `service_tag`: Unique service tag
- `idrac_ip`: iDRAC IP address
- `idrac_username/password`: iDRAC credentials
- `bmc_mac_address`: BMC MAC address
- `pxe_mac_address`: PXE MAC address

### Incident
- `incident_id`: Unique incident identifier
- `title`: Incident title
- `description`: Detailed description
- `severity`: Severity level (low/medium/high/critical)
- `status`: Current status (open/investigating/resolved/closed)
- `service_tag`: Foreign key to Server
- `external_site`: External tracking URL

## Configuration

### Database

The application uses SQLite by default. To use MySQL, update the `DATABASES` setting in `lab_management/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lab_management',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Static Files

For production, configure static file serving:

```python
STATIC_URL = '/static/'
STATIC_ROOT = '/path/to/static/files/'
```

Run:
```bash
python manage.py collectstatic
```

## Development

### Adding New Features

1. Create models in `dashboard/models.py`
2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Create views in `dashboard/views.py`
4. Add URLs in `dashboard/urls.py`
5. Create templates in `dashboard/templates/dashboard/`

### Testing

Run tests:
```bash
python manage.py test
```

## Security

- iDRAC passwords are stored in the database (consider encryption for production)
- API endpoint is CSRF-protected for web requests
- Admin interface available for management

## Support

For issues and questions, please contact the development team.

## License

[Add your license information here]
