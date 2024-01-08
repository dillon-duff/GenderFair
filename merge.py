import pdb
import pandas as pd
import numpy as np
df1 = pd.read_csv("990-Top-12-6.csv")
df2 = pd.read_csv("Candid-Top-12-6.csv")


m = pd.merge(df1, df2, on='ein', how='outer')

m['org'] = np.where(pd.notnull(m['org_name_x']),
                    m['org_name_x'], m['org_name_y'])

m['total_revenue'] = m['total_revenue_x'].combine_first(m['total_revenue_y'])

m['ein'] = m['ein'].astype(int)

m = m.sort_values('total_revenue', ascending=False)

selected_columns = m[['org', 'total_revenue', 'ein']]
selected_columns.to_csv('output.csv', index=False)

pdb.set_trace()
