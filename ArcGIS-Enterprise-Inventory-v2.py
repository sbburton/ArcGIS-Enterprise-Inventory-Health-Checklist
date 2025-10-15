from arcgis.gis import GIS
from datetime import datetime
import pandas as pd

# --------------------------------------
# 1. CONNECT TO PORTAL
# --------------------------------------
gis = GIS("https://yourportal.domain.com/portal", "your_admin_user", "your_password")

inventory = {}

# --------------------------------------
# 2. PORTAL INFO
# --------------------------------------
props = gis.properties
inventory['Portal'] = {
    'Title': props.portalName,
    'Version': props.currentVersion,
    'ID': props.id,
    'Is Multi-Tenant': props.get('isPortalMultitenant', False),
    'Time Retrieved': datetime.now().isoformat()
}

# --------------------------------------
# 3. USERS (COUNT BY ROLE)
# --------------------------------------
users = gis.users.search(max_users=1000)
role_counts = {}

for user in users:
    role = user.role
    role_counts[role] = role_counts.get(role, 0) + 1

inventory['Users Summary'] = role_counts
inventory['Total Users'] = len(users)

# --------------------------------------
# 4. GROUPS
# --------------------------------------
groups = gis.groups.search(max_groups=1000)
inventory['Groups'] = {
    'Total Groups': len(groups),
    'Group Titles': [group.title for group in groups[:10]]  # preview first 10
}

# --------------------------------------
# 5. FEDERATED SERVERS
# --------------------------------------
inventory['Federated Servers'] = []
hosting_server_id = None
hosting_status = "⚠️ Not Configured"

# Try to get hosting server ID (if it exists)
system_props = gis.admin.system.properties
if 'hostingServer' in system_props:
    hosting_server_id = system_props['hostingServer']['serverId']
    hosting_status = system_props['hostingServer'].get('serverURL', 'Available but no URL')

inventory['Hosting Server'] = hosting_status

# Loop through federated servers
for server in gis.admin.servers.list():
    server_id = server.properties.get('id', 'Unknown')
    role = 'Hosting Server' if server_id == hosting_server_id else 'Federated Server'

    inventory['Federated Servers'].append({
        'URL': server.url,
        'Role': role,
        'Machines': server.machines
    })

# --------------------------------------
# 6. DATA STORES
# --------------------------------------
datastores = gis.admin.data_stores.list()
ds_list = []

for ds in datastores:
    ds_list.append({
        'Type': ds.datastore_type,
        'Mode': ds.mode,
        'Status': ds.status,
        'Machines': ds.machines,
        'ID': ds.id
    })

inventory['Data Stores'] = ds_list

# --------------------------------------
# 7. SUMMARY REPORT
# --------------------------------------
summary_rows = {
    'Section': [],
    'Key': [],
    'Value': []
}

def flatten(d, section):
    for k, v in d.items():
        if isinstance(v, list):
            summary_rows['Section'].append(section)
            summary_rows['Key'].append(k)
            summary_rows['Value'].append(f"{len(v)} items")
        elif isinstance(v, dict):
            summary_rows['Section'].append(section)
            summary_rows['Key'].append(k)
            summary_rows['Value'].append(str(v))
        else:
            summary_rows['Section'].append(section)
            summary_rows['Key'].append(k)
            summary_rows['Value'].append(v)

flatten(inventory['Portal'], 'Portal')
flatten(inventory['Users Summary'], 'Users')
flatten(inventory['Groups'], 'Groups')
flatten({'Hosting Server': inventory['Hosting Server']}, 'Servers')
flatten({'Federated Servers': inventory['Federated Servers']}, 'Servers')
flatten({'Data Stores': inventory['Data Stores']}, 'Data Stores')

# Print summary
df = pd.DataFrame(summary_rows)
print(df.to_string(index=False))

# Optionally save to CSV
df.to_csv("arcgis_enterprise_inventory_summary.csv", index=False)
