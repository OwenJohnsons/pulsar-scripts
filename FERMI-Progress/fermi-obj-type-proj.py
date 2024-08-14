#%% 
from astroquery.vizier import Vizier
import pandas as pd

  # Specify columns to retrieve, "*" means all columns
catalog_id = "IX/67"  
v = Vizier(columns=["*", "+_r"], catalog=catalog_id)
table = v.get_catalogs(catalog_id)[0]
df = table.to_pandas()
print(df.head())

# %%
