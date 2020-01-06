import math
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import shapefile


data = pd.read_csv("output/data.csv")
map_df = gpd.read_file("shapefile/taxi_zones.shp")

def spatiotemporal_heatmap(map_df, locationID):

	v = data[locationID].value_counts().to_frame()[locationID].reset_index()
	v = v.rename(columns={'index':'Location_ID', locationID:'Frequency'})

	vmin, vmax = min(v['Frequency']), max(v['Frequency'])


	matrix = data.groupby(['pickup_time', locationID])['pickup_time'].count().unstack(locationID)

	loc_index = matrix.columns.tolist()
	time_index = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5]
	labels = ('06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', 
	             '19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00')

	location = []

	for i in time_index:
		loc_count = []
		for j in loc_index:
			value = matrix[j][i]
			if math.isnan(value):
				value = 0
			loc_count.append(value)

		location.append(loc_count)

	raw_data = {}

	for x in time_index:
		raw_data[labels[time_index.index(x)]] = location[time_index.index(x)]

	df = pd.DataFrame(raw_data, index=loc_index)
	df = df.reset_index().rename(columns={'index':'Location_ID'})

	merged = map_df.set_index('LocationID').join(df.set_index('Location_ID'))

	for t in labels:
		merged[t] = [0 if math.isnan(x) else x for x in merged[t]]


	for t in labels:
		print(f'processing {t}')
		fig, ax = plt.subplots(1, figsize=(10, 6))
		img = merged.plot(column=t, cmap='plasma', linewidth=0.8, ax=ax, edgecolor='0.8')

		if locationID == 'PULocationID':
			ax.set_title("Taxi pickup frequencies/hr for New Year's Eve 2018", fontsize=18, fontweight=3)
		else:
			ax.set_title("Taxi dropoff frequencies/hr for New Year's Eve 2018", fontsize=18, fontweight=3)
		
		ax.axis('off')

		sm = plt.cm.ScalarMappable(cmap='plasma', norm=plt.Normalize(vmin=vmin, vmax=vmax))
		cbar = fig.colorbar(sm)

		if labels.index(t)>=18:
			img.annotate(t,
		            xy=(0.1, .225), xycoords='figure fraction',
		            horizontalalignment='left', verticalalignment='top',
		            fontsize=35)
			img.annotate('1 Jan 2019',
		            xy=(0.1, .29), xycoords='figure fraction',
		            horizontalalignment='left', verticalalignment='top',
		            fontsize=20)
		else:
			img.annotate(t,
		            xy=(0.1, .225), xycoords='figure fraction',
		            horizontalalignment='left', verticalalignment='top',
		            fontsize=35)
			img.annotate('31 Dec 2018',
		            xy=(0.085, .285), xycoords='figure fraction',
		            horizontalalignment='left', verticalalignment='top',
		            fontsize=20)


		chart = img.get_figure()

		if locationID == 'PULocationID':
			chart.savefig('maps_pu/'+t, dpi=300)
		else:
			chart.savefig('maps_do/'+t, dpi=300)


spatiotemporal_heatmap(map_df, 'PULocationID')
spatiotemporal_heatmap(map_df, 'DOLocationID')