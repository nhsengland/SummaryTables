from utils.queries import quarters
import pandas as pd

def scoredistribution_formatting(DATE_FROM,OTHER_FORMAT_DATE_TO,TABLE,connection):
    cnxn12 = connection() #connects to sqlAlchemy
    sd_data = pd.read_sql(quarters(OTHER_FORMAT_DATE_TO,DATE_FROM,TABLE), cnxn12)
    cnxn12.close()

    Oxford = sd_data['Measure'] =='Oxford Score'
    sd_oxford = sd_data[Oxford]#&HR_data&preop]
    sd_oxford = sd_oxford.set_index('Questionnaire')[['Mean','Q1','Median','Q3']].transpose()
    sd_oxford.columns=['HR Post-op','HR Pre-op','KR Post-op','KR Pre-op']

    EQVAS = sd_data['Measure'] == 'EQ VAS'
    sd_eqvas = sd_data[EQVAS]
    sd_eqvas= sd_eqvas.set_index('Questionnaire')[['Mean','Q1','Median','Q3']].transpose()
    sd_eqvas.columns = ['HR Post-op','HR Pre-op','KR Post-op','KR Pre-op']

    eq5d = sd_data['Measure'] == 'EQ5D'
    sd_eq5d = sd_data[eq5d]
    sd_eq5d= sd_eq5d.set_index('Questionnaire')[['Mean','Q1','Median','Q3']].transpose()
    sd_eq5d.columns = ['HR Post-op','HR Pre-op','KR Post-op','KR Pre-op']

    return sd_oxford,sd_eqvas,sd_eq5d