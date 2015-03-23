from redcap import Project
import redcap_credentials as rcp
import pandas as pd
import re
from datetime import datetime,timedelta

### Connect to redcap project using the API TOKEN
## The API TOKEN Is included in the redcap_credentials.py file
## which has the format as
##


try:
	cur_project = Project(rcp.API_URL, rcp.API_TOKEN)
except:
	print "Unable to access project... check API Token and URL"
	quit


print "Accessing Project"
print rcp.SAMPLE_FILE

## project dd by name is a reformat of the project data dictionary where i have keyed it by field_name

import re
from datetime import datetime,timedelta
def reformat_pt_record( record_dict, project_dd_by_name):
	"""Given a project data dictionary and a patient_record that I am trying to import, it will reformat
    fields such as converting enumerations into values, and fixing dates...."""
	months_to_num = { 'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05',
        'jun': '06', 'jul': '07', 'aug' : '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12' }


	ignore_enum_case = True ### going to lower case all the variables I add to an enumerated list so that True and true are the same..

	fields_with_dates = [ field for field in project_dd_by_name.keys() if project_dd_by_name[field]['text_validation_type_or_show_slider_number'] == u'date_mdy']
    #print fields_with_dates,'are date fields..'
	fields_with_enumerations = [ field for field in project_dd_by_name.keys() if ( project_dd_by_name[field]['field_type'] == u'dropdown' or project_dd_by_name[field]['field_type'] == 'radio' )]
    #print fields_with_enumerations,"are enumerations"
    ### need to figure out multiselect...
	debug = False


	## need to map yes/no fields to 1 and 0 there are other types I need to do this for as well...
	#boolean_fields u'field_type': u'yesno'
	boolean_fields = [ field for field in project_dd_by_name.keys() if project_dd_by_name[field]['field_type'] == u'yesno' ]
	if debug: print boolean_fields,'are yes no fields!'
	
	boolean_enum_map =  {'yes':1,'no':0, False:0, True:0, 'Yes':1, 'No':0}


	enumeration_map = {}
	combined_enum_map = {}  #contains a dict keyed by field for each enumeratable field
#	print record_dict


	for field in fields_with_enumerations:
        ##enumeration_map[field] = 
		enum_values = project_dd_by_name[field]['select_choices_or_calculations']
		enum_list = enum_values.split(' | ')
		enum_dict = {}
		#print enum_values,field
		enum_dict = dict([ x.split(', ') for x in enum_list])
		if ignore_enum_case:
			enum_rvs_dict = {v.lower():k for k,v in enum_dict.iteritems()}
		else:
			enum_rvs_dict = {v:k for k,v in enum_dict.iteritems()}
#		enum_rvs_dict = {v:k for k,v in enum_dict.iteritems()}

		combined_enum_map[field] = enum_rvs_dict
        #print enum_dict

	for field in record_dict:
		if field in fields_with_dates:
			value_to_fix = record_dict[field]
			if debug: print "need to fix",value_to_fix,'for',field
			valid_date = re.compile('/d+-/d+-/d+')
            ##need to maek sure there is a DOB or this fails
			if debug: print value_to_fix,type(value_to_fix)
			


			if not value_to_fix:
				pass
			elif isinstance(value_to_fix,datetime):
				date_format_string = project_dd_by_name[field]['text_validation_type_or_show_slider_number']
				if isinstance(value_to_fix, pd.tslib.NaTType):
					record_dict[field] = ''
					## Replacing pandas NaT aka notatime with ''
					pass
				elif date_format_string == 'date_mdy':
					if debug: print "FIXED THE DATE TO",value_to_fix,'to',
					value_to_fix = value_to_fix.strftime("%Y-%m-%d")
					record_dict[field] = value_to_fix
					if debug: print value_to_fix

			elif  valid_date.match(value_to_fix):
                #print "Date is already in the correct format"
				pass
			elif not value_to_fix:
				pass
			else:
				value_to_fix = value_to_fix.lower()
                #print "still need to fix",value_to_fix
                ## need to make this into its own function, for now im doing it crudely
				print value_to_fix	
				if( '-' in value_to_fix):
					try:
						parts = value_to_fix.split('-', 2)
	    	            # Explicit is better than implicit
						parts[2] = '19{}'.format(parts[2])  
						better_date_string = '-'.join(parts)
						dt = datetime.strptime(better_date_string, '%d-%b-%Y')
						value_to_fix = dt.strftime("%Y-%m-%d")
						record_dict[field] = value_to_fix
					except:
						print "data wasn't parsed properly"                

		elif field in fields_with_enumerations:
			
			value_to_fix = record_dict[field]
			if value_to_fix:
				value_to_fix = record_dict[field].lower()
            #print "need to fix",value_to_fix,"for",field
			## ADDING IN LOWER CASE FIX
			lc_combined_enum_map = [ x.lower() for x in combined_enum_map[field].keys() ]
			if value_to_fix in lc_combined_enum_map:
				enumerated_value = combined_enum_map[field][value_to_fix]
				record_dict[field] = enumerated_value

		elif field in boolean_fields:
			value_to_fix = record_dict[field]
			if value_to_fix in boolean_enum_map.keys():
				enumerated_value = boolean_enum_map[value_to_fix]
				record_dict[field] = enumerated_value



	return record_dict
        
