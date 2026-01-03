import pandas as pd

def rank_weekend_cities(source_city, df, top_n=5):
    source = df[df['City'].str.lower() == source_city.lower()]
    if source.empty:
        raise ValueError("Source city not found")

    source_zone = source.iloc[0]['Zone']

    city_grouped = (
        df.groupby(['City', 'State', 'Zone'])
        .agg(
            Avg_Rating=('Google review rating', 'mean'),
            Popularity=('Number of google review in lakhs', 'sum'),
            Total_Places=('Name', 'count')
        )
        .reset_index()
    )

    city_grouped = city_grouped[city_grouped['City'].str.lower() != source_city.lower()]

    def distance_score(zone):
        if zone == source_zone:
            return 1.0
        elif zone in ['Northern', 'Western', 'Southern', 'Eastern']:
            return 0.6
        return 0.4

    city_grouped['DistanceScore'] = city_grouped['Zone'].apply(distance_score)

    city_grouped['PopularityNorm'] = (
        city_grouped['Popularity'] / city_grouped['Popularity'].max()
    )

    city_grouped['Final_Score'] = (
        city_grouped['DistanceScore'] * 0.4 +
        city_grouped['Avg_Rating'] * 0.35 +
        city_grouped['PopularityNorm'] * 0.25
    )

    city_grouped = city_grouped.sort_values(
        by='Final_Score', ascending=False
    ).head(top_n)

    return city_grouped[['City', 'State', 'Zone',
                          'Avg_Rating', 'Popularity',
                          'Total_Places', 'Final_Score']]


if __name__ == "__main__":
    df = pd.read_csv("/content/drive/MyDrive/Top Indian Places to Visit.csv")

    source_city = input("Enter source city: ").strip()

    try:
        result = rank_weekend_cities(source_city, df)
        print(f"\n ----Top Weekend Getaways from {source_city}----\n")
        print(result.to_string())
    except ValueError as e:
        print(e)
