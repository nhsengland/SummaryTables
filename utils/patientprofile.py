from utils.connection import connection
from utils.queries import patient_profile,ons_data
import pandas as pd

def patient_profile_calculations(TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO,FYEAR):
    cnxn5 = connection() #connects to sqlAlchemy
    HR_patient_profile = pd.read_sql(patient_profile('HR',TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO), cnxn5)
    KR_patient_profile = pd.read_sql(patient_profile('KR',TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO), cnxn5)
    ons_demographics = pd.read_sql(ons_data(FYEAR),cnxn5)
    cnxn5.close()

    HRKR_Patient_profile = HR_patient_profile.merge(KR_patient_profile,how='outer', on = '_AGE_GROUP_5YR',suffixes=('_HR','_KR'))

    female_demographics = ons_demographics[ons_demographics['GENDER']=='F'].rename(columns={'Count':'Count_F'})[['AgeBand','Count_F']]
    profile_and_demographics = HRKR_Patient_profile.merge(female_demographics,left_on='_AGE_GROUP_5YR',right_on='AgeBand')
    profile_and_demographics['Female_HR'] = round((profile_and_demographics['Female_HR']/profile_and_demographics['Count_F'])*100000,1)
    profile_and_demographics['Female_KR'] = round((profile_and_demographics['Female_KR']/profile_and_demographics['Count_F'])*100000,1)

    male_demographics = ons_demographics[ons_demographics['GENDER']=='M'].rename(columns={'Count':'Count_M'})[['AgeBand','Count_M']]
    profile_and_demographics = profile_and_demographics.merge(male_demographics,on='AgeBand')
    profile_and_demographics['Male_HR'] = round((profile_and_demographics['Male_HR']/profile_and_demographics['Count_M'])*100000,1)
    profile_and_demographics['Male_KR'] = round((profile_and_demographics['Male_KR']/profile_and_demographics['Count_M'])*100000,1)


    profile = profile_and_demographics[['_AGE_GROUP_5YR','Female_HR','Male_HR','Female_KR','Male_KR']]
    HR_patient_profile = profile[['_AGE_GROUP_5YR','Female_HR','Male_HR']]
    KR_patient_profile = profile[['_AGE_GROUP_5YR','Female_KR','Male_KR']]

    HR_patient_profile = HR_patient_profile.rename(columns = {'_AGE_GROUP_5YR':'Age Gender','Female_HR':'Female','Male_HR':'Male'})
    KR_patient_profile = KR_patient_profile.rename(columns = {'_AGE_GROUP_5YR':'Age Gender','Female_KR':'Female','Male_KR':'Male'}) 

    return profile,HR_patient_profile,KR_patient_profile
