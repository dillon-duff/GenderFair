from xml_parsing import *
from main import *
import pandas as pd


def write_top_companies_from_report(report_filename, max_companies, dest_filename=None):
    """ Writes top max_companies, sorted by total_staff, companies with added revenue column to dest_filename
        or Candid-Demographics-Top-{max_companies}.csv by default

        Args: 
            string (report_filename): filename of the original demographic report
            int (max_companies): max number of companies to look at from original demographic report
            None | string (dest_filename): name of csv file to write new data to

        Example:
            write_top_companies_from_report('Candid-Demographics-Monthly-Report.xlsx', 10, 'top_companies.csv')
    """
    df = pd.read_excel(report_filename, sheet_name="Organizations")
    df = df.sort_values(by=['total_staff'], ascending=False)

    import pdb
    pdb.set_trace()
    if dest_filename is None:
        dest_filename = f"Candid-Demographics-Top-{max_companies}.csv"
    eins = df["ein"].values

    ein_to_revenue_dict = {}

    for ein in eins[:max_companies]:
        xml_url = get_xml_url_from_ein(ein.replace("-", ""))
        if xml_url == -1:
            continue
        try:
            resp = requests.get(xml_url)
        except:
            pass

        filename = '990.xml'
        with open(filename, "wb") as f:
            f.write(resp.content)

        tree = ET.parse(filename)
        root = tree.getroot()

        root = root[1]

        revenue_root = root.find(efile_string("IRS990"))
        if revenue_root is None:
            continue
        revenue = int(revenue_root.find(
            efile_string("CYTotalRevenueAmt")).text)

        if revenue is None:
            continue

        # TODO: Get more information here to save in the new CSV

        ein_to_revenue_dict[ein] = revenue

        with open("eins_and_revenue.csv", mode="a", newline="\n") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([ein, revenue])

    eins = pd.read_csv("eins_and_revenue.csv", names=["EIN", "Revenue"])

    def get_revenue(row):
        ein = row["ein"]
        revenue_match = eins[eins["EIN"] == ein]
        if revenue_match.empty:
            return None
        return int(revenue_match["Revenue"].values[0])

    df["total_revenue"] = df.apply(get_revenue, axis=1)
    df = df.dropna(subset=["total_revenue"])
    df.to_csv(dest_filename, index=False)


if __name__ == "__main__":
    write_top_companies_from_report(
        "Candid-Demographics-Monthly-Report (1).xlsx", 5000)
