'''
Mock-up examples to indicate functionality from an end-user perspective, that uses the
marker-repository (https://confluence.be.bayercropscience/display/IBI/Marker+Repository+API)
as an example

'''

# crestle is the mockup module
import crestle


conn = crestle.connect(host='http://vm-jbent-bgr-qa-1:8080/markerrepo',
                       user='bnlit001',
                       password = '*******',
                       content_type='application/json'
                       )

#-----------------------------------------------------------------------
# a simple get
# https://confluence.be.bayercropscience/display/IBI/Marker+Repository+API#MarkerRepositoryAPI-Getamarkerbyid
location = ['markers','mGOS00000042']
parameters = {}

try:
    response = conn.get(location=location, parameters=parameters)
except crestle.CrestleHttpBaseException:
    print('error')

marker_condition = response['markerCondition']
print(marker_condition)  # prints 'legacy'


#-----------------------------------------------------------------------
# more complex
# https://confluence.be.bayercropscience/display/IBI/Marker+Repository+API#MarkerRepositoryAPI-Getmarkersbycriteria:uidlike,aliaslike,availabletechnologyandcroparea

location = ['markers']
parameters = {'markerUID':'PARTIAL_UID',
              'taxonomy':'TAXONID',
              'alias':'PARTIAL_ALIAS',
              'sourceCategory':'SC_NAME',
              'technology':'TECHNOLOGY',
              'page':'PAGENO',
              'size':'PAGESIZE',
              'sort':'SORT_FIELD,SORT_DIR'}

response = conn.get(location=location, parameters=parameters)
marker_list = response['_embedded']['markers']

print(marker_list[0]['markerUID'])  # prints 'marker-mGOS00000010'