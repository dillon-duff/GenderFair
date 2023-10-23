import pandas as pd
import json
import os
import glob
import requests
import random

# api_key = "38538c851bd3b555ef2cdd8eb8b907ff29f7f50baaa11d76314d1ef7640797d9"
# url_before_name = "https://gender-api.com/get?key=" + api_key + "&name="

url_before_name = "https://api.genderize.io?name="


def get_names_from_dataFrame(dataFrame):
    names = dataFrame["PersonNm"]
    names.name = "name"
    return names


def get_total_compensation_from_data_frame(dataFrame):
    totalComp = dataFrame["TotalCompensationFilingOrgAmt"]
    def select_value(row): return row['TotalCompensationRltdOrgsAmt'] if row[
        'TotalCompensationFilingOrgAmt'] == 0 else row['TotalCompensationFilingOrgAmt']

    totalComp = dataFrame.apply(select_value, axis=1)
    totalComp.name = "compensation"
    return totalComp


def format_gender_data_frame(dataFrame):
    names = get_names_from_dataFrame(dataFrame)
    totalComp = get_total_compensation_from_data_frame(dataFrame)
    genders = []
    accuracies = []
    for name in names:
        if isinstance(name, str):
            results = guess_gender(name.split()[0])
        else:
            results = guess_gender("random")
        gender = results['gender']
        genders.append(gender)
        accuracy = results['probability']
        accuracies.append(accuracy)

    genders = pd.Series(genders, name="gender")
    accuracies = pd.Series(accuracies, name="accuracy")
    totalComp = pd.Series(totalComp, name="compensation")

    df = pd.concat([genders, accuracies, totalComp], axis=1)
    return df


def generate_pay_gap_metric(df):

    if 'PersonNm' not in df or 'TotalCompensationFilingOrgAmt' not in df:
        return -1

    calibrated_df = format_gender_data_frame(df)

    sum_comp = calibrated_df.groupby('gender')['compensation'].sum()

    if 'M' in sum_comp:
        male_total_comp = sum_comp['M']
        male_count = len(calibrated_df[calibrated_df['gender'] == 'M'])
    else:
        male_total_comp = 0
        male_count = 0

    if 'F' in sum_comp:
        female_total_comp = sum_comp['F']
        female_count = len(calibrated_df[calibrated_df['gender'] == 'F'])
    else:
        female_total_comp = 0
        female_count = 0

    average_male_salary = 0 if male_count == 0 else male_total_comp/male_count
    average_female_salary = 0 if female_count == 0 else female_total_comp/female_count

    pay_gap = -1 if average_male_salary == 0 else ((average_male_salary - average_female_salary) /
                                                   average_male_salary)*100
    percent_male = 0 if (
        male_count+female_count) == 0 else male_count/(male_count+female_count)
    percent_female = 0 if (
        male_count+female_count) == 0 else female_count/(male_count+female_count)

    result = {'average_female_salary': average_female_salary, "average_male_salary": average_male_salary,
              "pay_gap": pay_gap, "percent_male": percent_male, "percent_female": percent_female}
    # print(f'Gender Report:')
    # print(
    #     f'Percent Male: {percent_male}, Percent Female: {percent_female}, Women are paid {pay_gap:.2f}% less')

    return result


gender_df = pd.read_csv('name_gender_dataset.csv')
gender_df['Name'] = gender_df['Name'].str.lower()

# TODO: CHANGE TO AN AI AGENT SO WE DONT RUN OUT OF REQUESTS


def guess_gender(name):
    name = name.lower()
    if name not in gender_df['Name'].values:
        # print(f"Guessing for: {name}")
        return {'gender': random.choice(['M', 'F']), 'probability': 0.5}
    return {'gender': gender_df[gender_df['Name'] == name]['Gender'].values[0], 'probability': gender_df[gender_df['Name'] == name]['Probability'].values[0]}
    # url_after_name = url_before_name + name
    # req = requests.get(url_after_name)
    # results = json.loads(req.text)
    # print(results)
    # return results

#!: RAN OUT OF REQUESTS


if __name__ == "__main__":
    # generate_pay_gap_metric("Dig")
    s = " "
    while len(s) > 0:
        s = str(input("\nEnter company name to get top earners from: "))
        if len(s) <= 0:
            break
        generate_pay_gap_metric(s)
