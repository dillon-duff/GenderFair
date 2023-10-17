import pandas as pd
import json
import os
import glob
import requests


# api_key = "38538c851bd3b555ef2cdd8eb8b907ff29f7f50baaa11d76314d1ef7640797d9"
# url_before_name = "https://gender-api.com/get?key=" + api_key + "&name="

url_before_name = "https://api.genderize.io?name="


def get_company_csv(company):
    path = os.getcwd()
    extension = 'csv'
    os.chdir(path)
    files = glob.glob('*.{}'.format(extension))
    for file in files:
        if company.lower() in file.lower():
            return file
    return None


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
        results = guess_gender(name.split()[0])
        gender = results['gender']
        genders.append(gender)
        accuracy = results['probability']
        accuracies.append(accuracy)

    genders = pd.Series(genders, name="gender")
    accuracies = pd.Series(accuracies, name="accuracy")

    df = pd.concat([names, genders, accuracies, totalComp], axis=1)
    return df


def generate_pay_gap_metric(company):

    csv_file_name = get_company_csv(company)
    df = pd.read_csv(csv_file_name)
    calibrated_df = format_gender_data_frame(df)

    avg_comp = calibrated_df.groupby('gender')['compensation'].mean()

    male_total_comp = avg_comp['male']
    male_count = len(calibrated_df[calibrated_df['gender'] == 'male'])
    female_total_comp = avg_comp['female']
    female_count = len(calibrated_df[calibrated_df['gender'] == 'female'])

    average_male_salary = male_total_comp/male_count
    average_female_salary = female_total_comp/female_count
    pay_gap = ((average_male_salary - average_female_salary) /
               average_male_salary)*100
    percent_male = male_count/(male_count+female_count)
    percent_female = female_count/(male_count+female_count)

    result = {'Average_Female_Salary': average_female_salary, "Average_Male_Salary": average_male_salary,
              "Pay_Gap": pay_gap, "percent_male": percent_male, "percent_female": percent_female}
    company_name = csv_file_name[csv_file_name.rindex(
        '_')+1:].removesuffix(".csv")
    print(f'{company_name} Gender Report:')
    print(
        f'Percent Male: {percent_male}, Percent Female: {percent_female}, Women are paid {pay_gap:.2f}% less')
    return result


# TODO: CHANGE TO AN AI AGENT SO WE DONT RUN OUT OF REQUESTS
def guess_gender(name):
    # print(name)
    url_after_name = url_before_name + name
    # print(url_after_name)
    req = requests.get(url_after_name)
    results = json.loads(req.text)
    print(results)
    return results

#!: RAN OUT OF REQUESTS


if __name__ == "__main__":
    # generate_pay_gap_metric("Dig")
    s = " "
    while len(s) > 0:
        s = str(input("\nEnter company name to get top earners from: "))
        if len(s) <= 0:
            break
        generate_pay_gap_metric(s)
