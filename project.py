import pandas as pd

def load(path):
    df = pd.read_csv(path)
    return df

def explore(df_left,df_right):
    #shape
    print(df_left.shape)
    print(df_right.shape)
    # col name
    print(f"df_left columns: {list(df_left.columns)}")
    print(f"df_right columns: {list(df_right.columns)}")
    # duplicate company id (the results show no duplicate id)
    print(sum(df_left['entity_id'].duplicated()))
    print(sum(df_right['business_id'].duplicated()))
    # df_left.head()
    df_left.sample(8)
    # df_right.head()
    df_right.sample(8)
    pass

def cleaning_zipcode_df_left(df_left):
    df_left["postal_code"].dtype
    # replace na with 0 in "postal_code"
    df_left["postal_code"] = df_left["postal_code"].fillna(0)
    # convert df_left["postal_code"] to string due to leading and trailing 0s
    df_left["zip_code_str"] = df_left["postal_code"].astype(int).astype(str)
    # count the length of zip codes
    df_left["zip_code_str"].map(len).value_counts()
    # examine row with zip code length of 6
    df_left[df_left["zip_code_str"].map(len) == 6]
    # change the above zip code to 33614 after varification based on city and state
    df_left['zip_code_str'] = df_left['zip_code_str'].replace('336140', '33614')
    # fill the leading 0 in zip code
    df_left["zip_code_str"] = df_left["zip_code_str"].str.zfill(5)
    #count the length of zip codes again, now all "zip_code_string" are 5 digit strings
    df_left["zip_code_str"].map(len).value_counts()
    return df_left

def cleaning_zipcode_df_right(df_right):
    df_right["zip_code"].dtype
    # count the length of zip codes
    df_right["zip_code"].map(len).value_counts()
    # examine row with zip code length of 7
    df_right[df_right["zip_code"].map(len) == 7]
    # remove trailing -- in zip_code
    df_right['zip_code'] = df_right['zip_code'].apply(lambda x: x.replace('-', '') if len(x)==7 else x)
    # length of 10 are due to extended ZIP+4 code
    df_right[df_right["zip_code"].map(len) == 10].sample(3)
    # examine row with zip code length of 9 (maybe due to data entry error)
    df_right[df_right["zip_code"].map(len) == 9]
    # keep only the first five digit of 9/10-digit zip_code because df_left only contains 5 digits
    # so it's no meaning to keep the extended digits
    df_right['zip_code'] = df_right['zip_code'].apply(lambda x: x[:5] if len(x) in [9, 10] else x)
    # the zip_code column is clean now
    df_right["zip_code"].map(len).value_counts()
    return df_right

import string
# Define a lambda function to remove punctuation from a string
remove_punct = lambda x: x.translate(str.maketrans('', '', string.punctuation))

def cleaning_data_df_left(df_left):
    # Convert all strings to lower case
    df_left = df_left.applymap(lambda s:s.lower() if type(s) == str else s)
    # Merge address, city, state into a single column
    df_left['address_combined'] = df_left.apply(lambda row: ' '.join(row[['address', 'city', 'state']].astype(str)), axis=1)
    # Drop unnecessary columns
    df_left.drop(['postal_code','categories'], axis=1, inplace=True)
    # Remove punctuation from the "name" and "address_combined" columns in both datasets
    df_left["name"] = df_left["name"].apply(remove_punct)
    df_left["address_combined"] = df_left["address_combined"].apply(remove_punct)
    df_left.nunique()
    df_left.head()
    return df_left

def cleaning_data_df_right(df_right):
    # Convert all strings to lower case
    df_right = df_right.applymap(lambda s:s.lower() if type(s) == str else s)
    # Merge address, city, state into a single column
    df_right['address_combined'] = df_right.apply(lambda row: ' '.join(row[['address', 'city', 'state']].astype(str)), axis=1)
    # Drop unnecessary column
    df_right.drop(['size'], axis=1, inplace=True)
    # Remove punctuation from the "name" and "address_combined" columns in both datasets
    df_right["name"] = df_right["name"].apply(remove_punct)
    df_right["address_combined"] = df_right["address_combined"].apply(remove_punct)
    df_right.nunique()
    df_right.head()
    return df_right

def Data_Exploration_with_Visualizations_df_left(data,df_left):
    # The number of cities are differnet between the two datasets.
    dfmap_left = df_left[['zip_code_str', 'entity_id']]
    dfmap_left.head()
    import folium
    # Create the map
    map_left = folium.Map(location=[37, -102], zoom_start=5)
    dfmap_left.info()
    # Rename the column names in the additional dataset
    dfmap_left = dfmap_left.rename(columns={'zip_code_str': 'ZIP', 'entity_id': 'entity_id'})
    # Convert the 'Zip Code' column to a string data type in both dataframes
    dfmap_left['ZIP'] = dfmap_left['ZIP'].astype(str)
    data['ZIP'] = data['ZIP'].astype(str)
    # Merge the datasets on the 'Zip Code' column
    merged_left = pd.merge(dfmap_left, data, on='ZIP')
    # Add markers for each zip code with additional data
    for index, row in merged_left.iterrows():
        folium.Marker(location=[row['LAT'], row['LNG']], popup=row['entity_id']).add_to(map_left)
    # Display the map of dfmap_left dataset
    map_left
    # Display the heatmap of the both datasets 
    # Create a heatmap layer based on the merged dataset
    from folium.plugins import HeatMap
    # Create a list of latitude and longitude coordinates from the merged dataset
    coordinates = merged_left[['LAT', 'LNG']].values.tolist()
    # Create a heatmap layer using the coordinates
    heatmap_left = HeatMap(coordinates, name='Heatmap_left', show=False)
    # Add the heatmap layer to the map
    heatmap_left = heatmap_left.add_to(map_left)
    # Display the heatmaps
    heatmap_left
    pass

def Data_Exploration_with_Visualizations_df_right(data,df_right):
    # The number of cities are differnet between the two datasets.
    dfmap_right = df_right[['zip_code', 'business_id']]
    dfmap_right.head()
    import folium
    # Create the map
    map_right = folium.Map(location=[37, -102], zoom_start=5)
    dfmap_right.info()
    # Rename the column names in the additional dataset
    dfmap_right = dfmap_right.rename(columns={'zip_code': 'ZIP', 'business_id': 'business_id'})

    # Convert the 'Zip Code' column to a string data type
    dfmap_right['ZIP'] = dfmap_right['ZIP'].astype(str)

    # Merge the datasets on the 'Zip Code' column
    merged_right = pd.merge(dfmap_right, data, on='ZIP')
    # Add markers for each zip code with additional data
    for index, row in merged_right.iterrows():
        folium.Marker(location=[row['LAT'], row['LNG']], popup=row['business_id']).add_to(map_right)
    # Display the map of dfmap_left dataset
    map_right
    # Display the heatmap of the both datasets 
    # Create a heatmap layer based on the merged dataset
    from folium.plugins import HeatMap
    # Create a list of latitude and longitude coordinates from the merged dataset
    coordinates = merged_left[['LAT', 'LNG']].values.tolist()
    # Create a heatmap layer using the coordinates
    heatmap_right = HeatMap(coordinates, name='Heatmap_right', show=False)
    # Add the heatmap layer to the map
    heatmap_right = heatmap_right.add_to(map_right)
    # Display the heatmaps
    heatmap_right
    pass

def inner_join(df_left,df_right):
    # Merge address_combined and postal_code into a single column
    df_left['address_combined_with_zip'] = df_left.apply(lambda row: ' '.join(row[['address_combined', 'zip_code_str']].astype(str)), axis=1)
    df_right['address_combined_with_zip'] = df_right.apply(lambda row: ' '.join(row[['address_combined', 'zip_code']].astype(str)), axis=1)
    import string
    # Remove punctuation from the "address_combined_with_zip" column in both datasets
    df_left["address_combined_with_zip"] = df_left["address_combined_with_zip"].apply(remove_punct)
    df_right["address_combined_with_zip"] = df_right["address_combined_with_zip"].apply(remove_punct)
    # Remove duplicated spaces from the "address_combined_with_zip" column in both datasets
    df_left["address_combined_with_zip"] = df_left.apply(lambda row: " ".join(row["address_combined_with_zip"].split()), axis=1)
    df_right["address_combined_with_zip"] = df_right.apply(lambda row: " ".join(row["address_combined_with_zip"].split()), axis=1)
    # Remove duplicated spaces from the "name" column in both datasets
    df_left["name"] = df_left.apply(lambda row: " ".join(row["name"].split()), axis=1)
    df_right["name"] = df_right.apply(lambda row: " ".join(row["name"].split()), axis=1)
    df_left.head()
    df_right.head()
    # inner join
    df_perfect_match = pd.merge(df_left, df_right, on=['name', 'address_combined_with_zip'], how='inner')
    cols = ["entity_id","business_id","name","address_combined_with_zip"]
    df_perfect_match[cols]
    # number of perfect match
    print(f"Number of perfect match: {len(df_perfect_match)}")
    return df_perfect_match

import matplotlib.pyplot as plt

def bucketing_strategy_by_zip_code(df_left, df_right):
    # count unique zip codes
    unique_zips_left = set(df_left["zip_code_str"])
    unique_zips_right = set(df_right["zip_code"])
    
    # count by zip code
    counts_left = df_left["zip_code_str"].value_counts()
    counts_right = df_right["zip_code"].value_counts()
    
    # plot histograms of counts
    counts_left.plot(kind="hist", bins=50)
    plt.show()
    
    counts_right.plot(kind="hist", bins=50)
    plt.show()
    
    # print summary statistics for counts
    left_summary = {
        ">500": (counts_left > 500).sum(),
        ">200": (counts_left > 200).sum(),
        ">100": (counts_left > 100).sum(),
        ">50": (counts_left > 50).sum(),
        ">5": (counts_left > 5).sum(),
        "<5": (counts_left < 5).sum()
    }
    
    right_summary = {
        ">500": (counts_right > 500).sum(),
        ">200": (counts_right > 200).sum(),
        ">100": (counts_right > 100).sum(),
        ">50": (counts_right > 50).sum(),
        ">5": (counts_right > 5).sum(),
        "<5": (counts_right < 5).sum()
    }
    
    print("Left summary:")
    for k, v in left_summary.items():
        print(f"{k}: {v}")
    
    print("Right summary:")
    for k, v in right_summary.items():
        print(f"{k}: {v}")
    
    return left_summary, right_summary

from fuzzywuzzy import fuzz

# Define a function with difflib
def matching_algo_difflib(left_row, right_row):
    # Concatenate the relevant columns into a single string for each record
    left_string = left_row["name"] + left_row["address_combined"]
    right_string = right_row["name"] + right_row["address_combined"]
    
    # Calculate the matching score using the SequenceMatcher class from the difflib module
    matcher = difflib.SequenceMatcher(None, left_string.lower(), right_string.lower())
    return matcher.ratio()

# Define a function with fuzzywuzzy
def matching_algo_fuzzywuzzy(left_row, right_row):
    name_similarity = fuzz.token_sort_ratio(left_row['name'], right_row['name'])
    address_similarity = fuzz.token_sort_ratio(left_row['address_combined'], right_row['address_combined'])
    confidence = 0.6 * name_similarity + 0.4 * address_similarity
    return confidence

def create_empty_match_lists():
    # Create empty lists to store the match results from difflib and fuzzywuzzy
    match_list_difflib = []
    match_list_fuzzywuzzy = []
    return match_list_difflib, match_list_fuzzywuzzy

def zip_code_counts_over_200(df_left, df_right, counts_left, counts_right):
    # Create empty lists to store the match results from difflib and fuzzywuzzy
    match_list_difflib, match_list_fuzzywuzzy = create_empty_match_lists()

    # zip codes in df_left with counts > 200
    df_left_zip_codes_gt_200 = counts_left[counts_left > 200].index.tolist()
    
    # Iterate over the zip codes
    for zip_code in df_left_zip_codes_gt_200:
        if zip_code in counts_right.index:
            # Filter the rows in df_left and df_right by the zip code
            df_left_zip = df_left[df_left["zip_code_str"] == zip_code]
            df_right_zip = df_right[df_right["zip_code"] == zip_code]
            # Iterate over each pair of records
            for left_index, left_row in df_left_zip.iterrows():
                for right_index, right_row in df_right_zip.iterrows():
                    # Calculate the matching score for this pair of records
                    matching_score_difflib = matching_algo_difflib(left_row, right_row)
                    matching_score_fuzzywuzzy = matching_algo_fuzzywuzzy(left_row, right_row)

                    if matching_score_fuzzywuzzy > 80:
                        match_list_fuzzywuzzy.append((left_row['entity_id'],right_row['business_id'], matching_score_fuzzywuzzy/100))
                        # add matching record to the difflib_list
                        match_list_difflib.append((left_row['entity_id'], right_row['business_id'], matching_score_difflib))
                        
    # check match score for first 20 rows using difflib
    print(match_list_difflib[:20])
    # check match score for first 20 rows using Fuzzywuzzy
    print(match_list_fuzzywuzzy[:20])
    return match_list_difflib, match_list_fuzzywuzzy

def zip_code_counts_from_100_to_200(data, df_left, df_right, counts_left, counts_right, match_list_difflib, match_list_fuzzywuzzy):
    # zip codes in df_left with counts 100-200
    df_left_zip_codes_100_to_200 = counts_left[(counts_left > 100) & (counts_left <= 200)].index.tolist()
    # Iterate over the zip codes
    for zip_code in df_left_zip_codes_100_to_200:
        if zip_code in counts_right.index:
            # Filter the rows in df_left and df_right by the zip code
            df_left_zip = df_left[df_left["zip_code_str"] == zip_code]
            df_right_zip = df_right[df_right["zip_code"] == zip_code]

            # Iterate over each pair of records
            for left_index, left_row in df_left_zip.iterrows():
                for right_index, right_row in df_right_zip.iterrows():
                    # Calculate the matching score for this pair of records
                    matching_score_difflib = matching_algo_difflib(left_row, right_row)
                    matching_score_fuzzywuzzy = matching_algo_fuzzywuzzy(left_row, right_row)

                    if matching_score_fuzzywuzzy > 80:
                        match_list_fuzzywuzzy.append((left_row['entity_id'], right_row['business_id'], matching_score_fuzzywuzzy/100))
                        # add matching record to the difflib_list
                        match_list_difflib.append((left_row['entity_id'], right_row['business_id'], matching_score_difflib))

    return match_list_difflib, match_list_fuzzywuzzy

def zip_code_counts_from_5_to_100(data, df_left):
    # zip codes in df_left with counts 5-100
    df_left_zip_codes_5_to_100 = counts_left[(counts_left > 5) & (counts_left <=100)].index.tolist()
    # Iterate over the zip codes
    for zip_code in df_left_zip_codes_5_to_100:
        if zip_code in counts_right.index:
            # Filter the rows in df_left and df_right by the zip code
            df_left_zip = df_left[df_left["zip_code_str"] == zip_code]
            df_right_zip = df_right[df_right["zip_code"] == zip_code]
        
            # Iterate over each pair of records
            for left_index, left_row in df_left_zip.iterrows():
                for right_index, right_row in df_right_zip.iterrows():
                    # Calculate the matching score for this pair of records
                    matching_score_difflib = calculate_matching_score_difflib(left_row,right_row)
                    # use fuzzywuzzy to calculate score
                    matching_score_fuzzywuzzy = calculate_matching_score_fuzzywuzzy(left_row, right_row)

                    if matching_score_fuzzywuzzy > 80:
                        match_list_fuzzywuzzy.append((left_row['entity_id'], right_row['business_id'], matching_score_fuzzywuzzy/100))
                        # add matching record to the difflib_list
                        match_list_difflib.append((left_row['entity_id'], right_row['business_id'], matching_score_difflib))
    return match_list_fuzzywuzzy, match_list_difflib
            
def zip_code_counts_from_0_to_5(data, df_left):
    # zip codes in df_left with counts <=5
    df_left_zip_codes_lt_5 = counts_left[counts_left <= 5].index.tolist()
    match_list_fuzzywuzzy = []
    match_list_difflib = []
    # Iterate over the zip codes -> 1s include fuzzywuzzy
    for zip_code in df_left_zip_codes_lt_5:
        if zip_code in counts_right.index:
            # Filter the rows in df_left and df_right by the zip code
            df_left_zip = df_left[df_left["zip_code_str"] == zip_code]
            df_right_zip = df_right[df_right["zip_code"] == zip_code]
            
            # Iterate over each pair of records
            for left_index, left_row in df_left_zip.iterrows():
                for right_index, right_row in df_right_zip.iterrows():
                    # Calculate the matching score for this pair of records
                    matching_score_difflib = calculate_matching_score_difflib(left_row, right_row)
                    
                    # use fuzzywuzzy to calculate score
                    matching_score_fuzzywuzzy = calculate_matching_score_fuzzywuzzy(left_row, right_row)

                    if matching_score_fuzzywuzzy > 80:
                        match_list_fuzzywuzzy.append((left_row['entity_id'], right_row['business_id'], matching_score_fuzzywuzzy/100))

                    # add matching record to the difflib_list
                    match_list_difflib.append((left_row['entity_id'], right_row['business_id'], matching_score_difflib))
    
    return match_list_fuzzywuzzy, match_list_difflib
            
def examine_matching_score_using_difflib(match_list):
    # sort list in descending order
    match_list_difflib.sort(key=lambda x: x[2], reverse=True)
    # examine match_list top 20
    match_list_difflib[:20]
    # distribution of matching_score
    import matplotlib.pyplot as plt
    # Extract matching scores from the match_list
    scores = [score for _, _, score in match_list_difflib]
    # Plot a histogram of the scores
    plt.hist(scores, bins=30)
    plt.xlabel('Matching Score_difflib')
    plt.ylabel('Frequency')
    plt.title('Distribution of Matching Scores (difflib)')
    plt.show()
    # distribution of matching_score > 0.8
    import matplotlib.pyplot as plt
    # Extract matching scores from the match_list
    scores = [score for _, _, score in match_list_difflib if score >= 0.8]
    # Plot a histogram of the scores
    plt.hist(scores, bins=30)
    plt.xlabel('Matching Score_difflib')
    plt.ylabel('Frequency')
    plt.title('Distribution of Matching Scores (difflib)')
    plt.show()
    # number of perfect match based on current algorithm is 351
    num_perfect_matches_difflib = 0

    for match in match_list_difflib:
        if match[2] == 1:
            num_perfect_matches_difflib += 1
    print("Number of perfect matches:", num_perfect_matches_difflib)
    return num_perfect_matches_difflib


def examine_matching_score_using_fuzzywuzzy(match_list):
    # sort list in descending order
    match_list_fuzzywuzzy.sort(key=lambda x: x[2], reverse=True)
    # examine match_list top 20
    match_list_fuzzywuzzy[:20]
    # distribution of matching_score
    import matplotlib.pyplot as plt
    # Extract matching scores from the match_list
    scores = [score for _, _, score in match_list_fuzzywuzzy]
    # Plot a histogram of the scores
    plt.hist(scores, bins=30)
    plt.xlabel('Matching Score_fuzzywuzzy')
    plt.ylabel('Frequency')
    plt.title('Distribution of Matching Scores (fuzzywuzzy)')
    plt.show()
    # number of perfect match based on current algorithm is 
    num_perfect_matches_fuzzywuzzy = 0

    for match in match_list_fuzzywuzzy:
        if match[2] == 1:
            num_perfect_matches_fuzzywuzzy += 1
    print("Number of perfect matches:", num_perfect_matches_fuzzywuzzy)
    return num_perfect_matches_fuzzywuzzy

    
def examine_difference_in_results_from_two_algo(match_list_difflib,
                                                match_list_fuzzywuzzy):
    # Examine the results from difflib
    perfect_matches_difflib = []
    for match in match_list_difflib:
        if match[2] == 1:
            perfect_matches_difflib.append(match)
    
    # Examine the results from fuzzywuzzy
    perfect_matches_fuzzywuzzy = []
    for match in match_list_fuzzywuzzy:
        if match[2] == 1:
            perfect_matches_fuzzywuzzy.append(match)
    
    # Perfect match only in fuzzywuzzy
    perfect_matches_fuzzywuzzy_only = [match 
                                       for match in perfect_matches_fuzzywuzzy
                                       if match not in perfect_matches_difflib]
    
    # fuzzywuzzy has 9 perfect match records more than difflib
    print(len(perfect_matches_fuzzywuzzy_only))
    
    # the perfect match records that only exist in fuzzywuzzy result
    print(perfect_matches_fuzzywuzzy_only)
    
    # Examine (14930, 28497, 1.0)
    print(df_left[df_left["entity_id"] == 14930])
    print(df_right[df_right["business_id"] == 28497])
    
    # Examine (12023, 22650, 1.0)
    print(df_left[df_left["entity_id"] == 12023])
    print(df_right[df_right["business_id"] == 22650])
    
    pass

def output_results_to_csv(match_list_difflib, match_list_fuzzywuzzy):
    # Get the length of the match_list generated by difflib.SequenceMatcher
    num_matches_difflib = len(match_list_difflib)
    # filtering the list of tuples with matching_score > 0.8
    match_list_difflib_gt_80pct = [(match[0], match[1], round(match[2], 2)) 
                                   for match in match_list_difflib if match[2] > 0.8]
    match_list_difflib_gt_80pct.sort(key=lambda x: x[2], reverse=True)
    # Get the length of the match_list generated by difflib.SequenceMatcher, 
    # where the matching score is greater than or equal to 0.8
    num_matches_gt_80pct_difflib = len(match_list_difflib_gt_80pct)
    # export filtered list to a csv file
    import csv
    with open('matching_score_difflib.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # writing header row
        writer.writerow(['entity_id', 'business_id', 'matching_score'])  
        # writing filtered tuples
        writer.writerows(match_list_difflib_gt_80pct) 
    # Get the length of the match_list generated by fuzzywuzzy
    num_matches_fuzzywuzzy = len(match_list_fuzzywuzzy)
    # export match_list_fuzzywuzzy to a csv file
    with open('matching_score_fuzzywuzzy.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # writing header row
        writer.writerow(['entity_id', 'business_id', 'matching_score'])
        # writing filtered tuples
        writer.writerows(match_list_fuzzywuzzy)  
    return num_matches_difflib, num_matches_gt_80pct_difflib, num_matches_fuzzywuzzy




    





