import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)
n_rows = 200

origins = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Miami, FL']
destinations = ['Dallas, TX', 'Atlanta, GA', 'Seattle, WA', 'Denver, CO', 'Boston, MA']
statuses = ['PENDING', 'IN_TRANSIT', 'DELIVERED', 'DELAYED']

# Base Data
shipment_ids = [f'SHP-{10042+i}' for i in range(n_rows)]
origin_col = np.random.choice(origins, n_rows)
dest_col = np.random.choice(destinations, n_rows)
weights = np.random.uniform(500, 15000, n_rows).round(2)
status_col = np.random.choice(statuses, n_rows, p=[0.15, 0.35, 0.40, 0.10])
truck_ids = [f'TRK-{random.randint(100, 999)}' for _ in range(n_rows)]

# Date Generation
start_date = datetime.now() - timedelta(days=30)
scheduled_dates = [start_date + timedelta(days=random.randint(0, 45)) for _ in range(n_rows)]
actual_dates = []

for i in range(n_rows):
    if status_col[i] == 'DELIVERED':
        # Delivered on time or slightly early/late
        actual_dates.append(scheduled_dates[i] + timedelta(days=random.randint(-2, 1)))
    elif status_col[i] == 'DELAYED':
        # Delayed shipments actual delivery is past scheduled
        actual_dates.append(scheduled_dates[i] + timedelta(days=random.randint(2, 10)))
    else:
        # PENDING or IN_TRANSIT don't have actual dates yet
        actual_dates.append(pd.NaT)

# Compile DataFrame
df = pd.DataFrame({
    'shipment_id': shipment_ids,
    'origin': origin_col,
    'destination': dest_col,
    'weight_lbs': weights,
    'status': status_col,
    'scheduled_date': scheduled_dates,
    'actual_date': actual_dates,
    'truck_id': truck_ids
})

# Save to CSV
df.to_csv('shipments.csv', index=False)
print(" Generated data/shipments.csv successfully.")