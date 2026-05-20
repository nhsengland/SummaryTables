from utils.connection import connection
import pandas as pd
from utils.queries import key_facts,successatisf,patient_profile,quarters,max_scores,complications,q2_returned,patient_engagement,severe_scores_hr,severe_scores_kr,patient_engagement_data,key_facts_min10
from utils.Improvements import improvements,improvements_prim_rev,success_satisfaction
from utils.scoredistribution import scoredistribution_formatting
import shutil
from utils.patientprofile import patient_profile_calculations

############ VARIABLES TO CHANGE
FYEAR='2018'
DATE_FROM = '2018-04-01'
DATE_TO='31-03-2019'
OTHER_FORMAT_DATE_TO = '2019-03-31'
TABLE='201912_V1_AR'
PREVIOUS_YEAR_TABLE = '201812_V1_AR'
TABLE_MIN10 = '201306_V2_AR'
SummaryTablesName = 'Summary Tables 2018-19.xlsx'


##### VARIABLES TO LEAVE AS BE
YEAR_STRING = f'{FYEAR}-{str(int(FYEAR)+1)[2:]} Final'
PREVIOUS_FYEAR = str(int(FYEAR)-1)
PREVIOUS_DATE_TO = DATE_TO[:-4]+str(int(DATE_TO[-4:])-1)
FYEAR_MIN10 = str(int(FYEAR)-11)
DATE_TO_MIN10 = DATE_TO[:-4]+str(int(DATE_TO[-4:])-11)

cnxn = connection() #connects to sqlAlchemy
data = pd.read_sql(key_facts(FYEAR,DATE_TO,TABLE), cnxn)
cnxn.close()
             
cnxn2 = connection() #connects to sqlAlchemy
data_previous_year = pd.read_sql(key_facts(PREVIOUS_FYEAR,PREVIOUS_DATE_TO,PREVIOUS_YEAR_TABLE), cnxn2)
cnxn2.close()

cnxn3 = connection() #connects to sqlAlchemy
data_min2_years = pd.read_sql(key_facts_min10(FYEAR_MIN10,DATE_TO_MIN10,TABLE_MIN10), cnxn3)
cnxn3.close()

HR_improvements = improvements(data,data_previous_year,data_min2_years,FYEAR,PREVIOUS_FYEAR,FYEAR_MIN10,'Hip Replacement')
HR_improvements = HR_improvements.replace('Oxford Hip Score','Oxford Score')

HR_improvements_primary = improvements_prim_rev(data,'Hip Replacement Primary','Primary')
HR_improvements_revision = improvements_prim_rev(data,'Hip Replacement Revision','Revision')

HR_Prim_rev = HR_improvements_primary.set_index('Measure').join(HR_improvements_revision.set_index('Measure')).reset_index()#
HR_Prim_rev = HR_Prim_rev.replace('Oxford Hip Score','Oxford Score')

KR_improvements = improvements(data,data_previous_year,data_min2_years,FYEAR,PREVIOUS_FYEAR,FYEAR_MIN10,'Knee Replacement')
KR_improvements = KR_improvements.replace('Oxford Knee Score','Oxford Score')

KR_improvements_primary = improvements_prim_rev(data,'Knee Replacement Primary','Primary')
KR_improvements_revision = improvements_prim_rev(data,'Knee Replacement Revision','Revision')
KR_Prim_rev = KR_improvements_primary.set_index('Measure').join(KR_improvements_revision.set_index('Measure')).reset_index()
KR_Prim_rev = KR_Prim_rev.replace('Oxford Knee Score','Oxford Score')

cnxn4 = connection() #connects to sqlAlchemy
successatisf_data = pd.read_sql(successatisf(YEAR_STRING,TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO), cnxn4)
cnxn4.close()

HR_Satisfaction = success_satisfaction(successatisf_data,'Hip Replacement','Satisfaction')
HR_Success = success_satisfaction(successatisf_data,'Hip Replacement','Success')

KR_Satisfaction = success_satisfaction(successatisf_data,'Knee Replacement','Satisfaction')
KR_Success = success_satisfaction(successatisf_data,'Knee Replacement','Success')

HRKR_Patient_profile,HR_patient_profile,KR_patient_profile = patient_profile_calculations(TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO,FYEAR)

cnxn6 = connection() #connects to sqlAlchemy
HR_max_scores = pd.read_sql(max_scores(DATE_FROM,OTHER_FORMAT_DATE_TO,TABLE,'HR'), cnxn6)
KR_max_scores = pd.read_sql(max_scores(DATE_FROM,OTHER_FORMAT_DATE_TO,TABLE,'KR'), cnxn6)
cnxn6.close()

HRKR_max_scores = HR_max_scores.merge(KR_max_scores,how='outer', on = 'Measure',suffixes=('_HR','_KR')).drop_duplicates()

cnxn7 = connection() #connects to sqlAlchemy
HR_complications = pd.read_sql(complications(TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO,'HR'), cnxn7)
KR_complications = pd.read_sql(complications(TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO,'KR'), cnxn7)
q2_returned_HR = pd.read_sql(q2_returned(DATE_FROM,OTHER_FORMAT_DATE_TO,TABLE,'HR'),cnxn7)
q2_returned_KR = pd.read_sql(q2_returned(DATE_FROM,OTHER_FORMAT_DATE_TO,TABLE,'KR'),cnxn7)

cnxn7.close()

At_least_1_HR=HR_complications[HR_complications['Symptom']=='At_Least_1']
At_least_1_KR=KR_complications[KR_complications['Symptom']=='At_Least_1']

HR_complications = HR_complications[HR_complications['Symptom']!='At_Least_1']
KR_complications = KR_complications[KR_complications['Symptom']!='At_Least_1']

cnxn8 = connection()
cursor = cnxn8.cursor()
cursor.execute(patient_engagement(DATE_FROM,OTHER_FORMAT_DATE_TO,TABLE,FYEAR))
cnxn8.commit()
patient_engagements = pd.read_sql(patient_engagement_data(FYEAR),cnxn8)
cnxn8.close()

cnxn9 = connection()
severe_hr = pd.read_sql(severe_scores_hr(TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO),cnxn9)
severe_kr = pd.read_sql(severe_scores_kr(TABLE,DATE_FROM,OTHER_FORMAT_DATE_TO),cnxn9)
cnxn9.close()

sd_oxford,sd_eqvas,sd_eq5d = scoredistribution_formatting(DATE_FROM,OTHER_FORMAT_DATE_TO,TABLE,connection)

with pd.ExcelWriter('HR_Improvements.xlsx',engine='openpyxl',mode='w') as writer:
    HR_improvements.to_excel(writer,sheet_name='HR_Improvements',index=False)
with pd.ExcelWriter('HR_PRIM_REV_Improvement.xlsx',engine='openpyxl',mode='w') as writer:
    HR_Prim_rev.to_excel(writer,sheet_name='HR_PRIM_REV_Improvements',index=False)
with pd.ExcelWriter('KR_Improvements.xlsx',engine='openpyxl',mode='w') as writer:
    KR_improvements.to_excel(writer,sheet_name='KR_Improvements',index=False)
with pd.ExcelWriter('KR_PRIM_REV_Improvement.xlsx',engine='openpyxl',mode='w') as writer:
    KR_Prim_rev.to_excel(writer,sheet_name='KR_PRIM_REV_Improvements',index=False)
with pd.ExcelWriter('HR_Satisfaction.xlsx',engine='openpyxl',mode='w') as writer:
    HR_Satisfaction.to_excel(writer,sheet_name='HR_Satisfaction',index=False)
with pd.ExcelWriter('HR_Success.xlsx',engine='openpyxl',mode='w') as writer:
    HR_Success.to_excel(writer,sheet_name='HR_Success',index=False)
with pd.ExcelWriter('KR_Satisfaction.xlsx',engine='openpyxl',mode='w') as writer:
    KR_Satisfaction.to_excel(writer,sheet_name='KR_Satisfaction',index=False)
with pd.ExcelWriter('KR_Success.xlsx',engine='openpyxl',mode='w') as writer:
    KR_Success.to_excel(writer,sheet_name='KR_Success',index=False)
with pd.ExcelWriter('HR_AgeGender.xlsx',engine='openpyxl',mode='w') as writer:
    HR_patient_profile.to_excel(writer,sheet_name='Sheet1',index=False,header=True,startrow=0)
with pd.ExcelWriter('KR_AgeGender.xlsx',engine='openpyxl',mode='w') as writer:
    KR_patient_profile.to_excel(writer,sheet_name='Sheet1',index=False,header=True,startrow=0)

with pd.ExcelWriter('HR_Engagement.xlsx',engine='openpyxl',mode='w') as writer:
    patient_engagements_HR = patient_engagements.rename(columns = {'EpisodesHR':'Episodes','Q1_RETURNED_HR':'Pre-operative questionnaires returned','Q2_RETURNED_HR':'Post-operative questionnaires returned'})
    patient_engagements_HR[['Year','Episodes','Pre-operative questionnaires returned','Post-operative questionnaires returned']].to_excel(writer,sheet_name='Sheet1',index=False,header=True)

with pd.ExcelWriter('KR_Engagement.xlsx',engine='openpyxl',mode='w') as writer:
    patient_engagements_KR = patient_engagements.rename(columns = {'EpisodesKR':'Episodes','Q1_Returned_KR':'Pre-operative questionnaires returned','Q2_Returned_KR':'Post-operative questionnaires returned'})
    patient_engagements_KR[['Year','Episodes','Pre-operative questionnaires returned','Post-operative questionnaires returned']].to_excel(writer,sheet_name='Sheet1',index=False,header=True)


shutil.copy("utils\\PROMs Summary Tables Empty.xlsx", SummaryTablesName)

with pd.ExcelWriter(SummaryTablesName,engine='openpyxl',mode='a', if_sheet_exists="overlay") as writer:
    HR_Prim_rev[['Measure','Primary','Revision']].to_excel(writer,sheet_name='Health Gain',index=False,startrow=17)
    KR_Prim_rev[['Primary','Revision']].to_excel(writer,sheet_name='Health Gain',index=False,startrow=17,startcol=3)

    HR_improvements[['Measure',FYEAR_MIN10+'-'+str(int(FYEAR_MIN10)+1)[2:],FYEAR+'-'+str(int(FYEAR)+1)[2:]]].to_excel(writer,sheet_name='Health Gain',index=False,startrow=7)
    KR_improvements[[FYEAR_MIN10+'-'+str(int(FYEAR_MIN10)+1)[2:],FYEAR+'-'+str(int(FYEAR)+1)[2:]]].to_excel(writer,sheet_name='Health Gain',index=False,startrow=7,startcol=3)

    HR_Success[['Success','Percentage']].to_excel(writer,sheet_name='Success & Satisfaction',index=False,header=False,startrow=7)
    KR_Success['Percentage'].to_excel(writer,sheet_name='Success & Satisfaction',index=False,header=False,startrow=7,startcol=2)

    HR_Satisfaction[['Satisfaction','Percentage']].to_excel(writer,sheet_name='Success & Satisfaction',index=False,header=False,startrow=16)
    KR_Satisfaction['Percentage'].to_excel(writer,sheet_name='Success & Satisfaction',index=False,header=False,startrow=16,startcol=2)

    HRKR_Patient_profile.to_excel(writer,sheet_name='Patient Profile',index=False,header=False,startrow=6)
    HRKR_max_scores[['Number_HR','Percentage_HR','Number_KR','Percentage_KR']].to_excel(writer,sheet_name='Maximum Value Scores',index=False,header=False,startrow=5,startcol=1)

    q2_returned_HR.to_excel(writer,sheet_name='Complications',startrow=5,startcol=1,index=False,header=False)
    q2_returned_KR.to_excel(writer,sheet_name='Complications',startrow=5,startcol=3,index=False,header=False)

    At_least_1_HR['Number'].to_excel(writer,sheet_name='Complications',startrow=7,startcol=1,index=False,header=False)
    At_least_1_KR['Number'].to_excel(writer,sheet_name='Complications',startrow=7,startcol=3,index=False,header=False)

    HR_complications['Number'].to_excel(writer,sheet_name='Complications',startrow=9,startcol=1,index=False,header=False)
    KR_complications['Number'].to_excel(writer,sheet_name='Complications',startrow=9,startcol=3,index=False,header=False)

    patient_engagements.to_excel(writer,sheet_name="Patient Engagement",startrow=5,startcol=0,index=False,header=False)

    severe_hr[['Pre-op','Post-Op']].to_excel(writer,sheet_name = "Most Severe Scores",startrow=6,startcol=1,index=False,header=False)
    severe_kr[['Pre-op','Post-Op']].to_excel(writer,sheet_name = "Most Severe Scores",startrow=22,startcol=1,index=False,header=False)

    sd_oxford[['HR Pre-op','HR Post-op','KR Pre-op','KR Post-op']].to_excel(writer, sheet_name = "Score Distributions",startrow=6,startcol=1,index=False,header=False)
    sd_eq5d[['HR Pre-op','HR Post-op','KR Pre-op','KR Post-op']].to_excel(writer, sheet_name = "Score Distributions",startrow=12,startcol=1,index=False,header=False)
    sd_eqvas[['HR Pre-op','HR Post-op','KR Pre-op','KR Post-op']].to_excel(writer, sheet_name = "Score Distributions",startrow=18,startcol=1,index=False,header=False)