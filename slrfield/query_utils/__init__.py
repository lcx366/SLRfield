'''
slrfield query_utils subpackage

This subpackage defines the following functions:

# ============================ query ========================= #

discos_buildin_filter - A subfunction dedicated to the function discos_query. It is used for upgrading the variable params(type of dictionary) in discos_query based on params and expr. 
If key 'filter' does not exist in params, then the upgraded params will become params['filter'] = expr; otherwise, the upgraded params will become params['filter'] += '&(' + expr + ')'

discos_query - Query space targets that meet the requirements by setting a series of specific parameters from the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database.

download_satcat - Download or update the satellites catalog file from www.celestrak.com

celestrak_query - Query space targets that meet the requirements by setting a series of specific parameters from the the [DISCOS](https://discosweb.esoc.esa.int)(Database and Information System Characterising Objects in Space) database and the [CELESTRAK](https://celestrak.com) database.

# ======================== tle_download ====================== #

tle_download - Download the TLE/3LE data from https://www.space-track.org

# ======================== visible_pass ====================== #

t_list - Generate a list of time moments based on start time, end time, and time step.

next_pass - Generate the space target passes in a time period.

visible_pass - Generate the visible passes of space targets in a time period.

'''