class Config:
    INDEX_FOLDER = "indexes"
    ARCHIVE_FOLDER = "990_xml_archive"
    START_YEAR = 2021
    END_YEAR = 2023
    CANDID_DEMOGRAPHICS_URL = "https://info.candid.org/candid-demographics"
    IRS_BASE_URL = "https://www.irs.gov/pub/irs-soi/"
    IRS_FILE_NAMES = ["eo1.csv", "eo2.csv", "eo3.csv", "eo4.csv"]
    GENDER_CSV_PATH = "first_name_gender_probabilities.csv"
    LOG_FILE = "npo_rankings_pipeline.log"
    RESULTS_FOLDER = "results"