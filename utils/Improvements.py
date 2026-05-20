
def improvements(data,data_previous_year,data_min2_years,FYEAR,PREVIOUS_FYEAR,FYEAR_MIN10,procedure):
    procdata = data[(data["Procedure"]==procedure) & (data["Organisation Type"]=="England")]
    procdata = procdata[["Measure","% Improved"]]
    procdata = procdata.rename(columns={'% Improved':FYEAR+'-'+str(int(FYEAR)+1)[2:]})

    procdata_min1 =  data_previous_year[(data_previous_year["Procedure"]==procedure) & (data_previous_year["Organisation Type"]=="England")]
    procdata_min1 = procdata_min1[["Measure","% Improved"]]
    procdata_min1 = procdata_min1.rename(columns={'% Improved':PREVIOUS_FYEAR+'-'+str(int(PREVIOUS_FYEAR)+1)[2:]})
    procdata = procdata_min1.set_index('Measure').join(procdata.set_index('Measure'),how='outer')
    procdata = procdata.reset_index()

    procdata_min10 =  data_min2_years[(data_min2_years["Procedure"]==procedure) & (data_min2_years["Organisation Type"]=="England")]
    procdata_min10 = procdata_min10[["Measure","% Improved"]]
    procdata_min10 = procdata_min10.rename(columns={'% Improved':FYEAR_MIN10+'-'+str(int(FYEAR_MIN10)+1)[2:]})
    procdata = procdata_min10.set_index('Measure').join(procdata.set_index('Measure'),how='outer')
    procdata = procdata.reset_index()
    return procdata

def improvements_prim_rev(data,procedure,prim_or_rev):
    procdata = data[(data["Procedure"]==procedure) & (data["Organisation Type"]=="England")]
    procdata = procdata[["Measure","% Improved"]]
    procdata = procdata.rename(columns={'% Improved':prim_or_rev})
    return procdata

def success_satisfaction(data,procedure,success_or_satisaction):
    data= data[(data['Procedure']==procedure) & (data['Breakdown']==success_or_satisaction)]
    data=data[['Answer','Percentage']]
    data = data.rename(columns={'Answer':success_or_satisaction})
    data['Percentage'] = [str(round(x,1))+'%' for x in data['Percentage']]
    return data