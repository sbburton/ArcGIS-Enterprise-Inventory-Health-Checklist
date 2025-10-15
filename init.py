from arcgis.gis import GIS
from datetime import datetime

# Establish a connection to your portal
# Replace with your credentials and portal URL
portal_url = "https://yourportal.domain.com/portal"
username = "your_admin_username"
password = "your_password"
gis = GIS(portal_url, username, password)

# Start collecting system info
inventory = {}

# 1. Portal Information
portal_props = gis.properties
inventory['Portal'] = {
    'Title': portal_props.portalName,
    'Version': portal_props.currentVersion,
    'Mode': portal_props.mode,
    'Is Multi-Tenant': portal_props.get('isPortalMultitenant', False),
    'Portal ID': portal_props.id,
    'Time Retrieved': datetime.now().isoformat()
}

# 2. Federated Servers
inventory['Federated Servers'] = []
for server in gis.admin.servers.list():
    inventory['Federated Servers'].append({
        'URL': server.url,
        'Role': server.role,
        'Is Hosting Server': 'Yes' if server.is_hosting_server else 'No'
    })

# 3. Hosting Server
hosting = gis.admin.system.hosting_servers
if hosting:
    inventory['Hosting Server'] = hosting[0]
else:
    inventory['Hosting Server'] = '⚠️ Not Configured'

# 4. Web Adaptors
web_adaptors = gis.admin.web_adaptors.list()
inventory['Web Adaptors'] = []
for wa in web_adaptors:
    inventory['Web Adaptors'].append({
        'Name': wa.webAdaptorName,
        'Component': wa.component,
        'URL': wa.webAdaptorURL,
        'Machine': wa.machineName
    })

# 5. Data Stores
datastores = gis.admin.data_stores.list()
inventory['Data Stores'] = []
for store in datastores:
    inventory['Data Stores'].append({
        'Type': store.datastore_type,
        'Mode': store.mode,
        'Status': store.status,
        'Machines': store.machines,
        'ID': store.id
    })

# Output a summary as a DataFrame-like format
import pandas as pd
summary_data = {
    'Section': [],
    'Key': [],
    'Value': []
}

def flatten_dict(d, section_name):
    for key, value in d.items():
        if isinstance(value, list):
            summary_data['Section'].append(section_name)
            summary_data['Key'].append(key)
            summary_data['Value'].append(f"{len(value)} items")
        else:
            summary_data['Section'].append(section_name)
            summary_data['Key'].append(key)
            summary_data['Value'].append(value)

flatten_dict(inventory['Portal'], 'Portal')
flatten_dict({'Hosting Server': inventory['Hosting Server']}, 'Hosting Server')
flatten_dict({'Federated Servers': inventory['Federated Servers']}, 'Federated Servers')
flatten_dict({'Web Adaptors': inventory['Web Adaptors']}, 'Web Adaptors')
flatten_dict({'Data Stores': inventory['Data Stores']}, 'Data Stores')

df = pd.DataFrame(summary_data)

import ace_tools as tools; tools.display_dataframe_to_user(name="ArcGIS Enterprise Inventory Summary", dataframe=df)
