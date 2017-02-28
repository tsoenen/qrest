'''
This example tries to be a simple ORM model for rest services that borrows some design ideas from Django.
It is rather incomplete and maybe inconsistent
'''

from crestle.models import CrestleDomain, CrestleTarget


class MarkerRepositoryQA(CrestleDomain):
    host='http://vm-jbent-bgr-qa-1:8080/markerrepo',
    content_type='application/json'
    
    class _GetMarkerByID(CrestleTarget):
        target_name = 'get_a_marker_by_id'
        target_url = ['markers/{markeruid}']
        required_url_parameters = {'markeruid':'markeruid'} # redundant to previous line, but not  easy to extract keys from format line
        required_option_parameters = {}                     # these must be present 
        optional_option_parameters = {}                     # these are there to validate if non paramters are added that make no sense for this target


    class _GetMarkerByCriteria(CrestleTarget):
        target_name = 'get_a_marker_by_id'
        target_url = ['markers']
        required_url_parameters = {} 
        required_option_parameters = {'taxonomy': 'taxonomy',}
        optional_option_parameters = { 'marker_uid':'markerUID',
                                       'alias':'alias',
                                       'source_category':'sourceCategory',
                                       'technology':'technology',
                                       'page':'page',
                                       'page_size':'size',
                                       'sort':'sort'}
        
        def to_python(self):
            # the payload is in the _embedded/markers part of the response
            return self._raw_response['_embedded']['markers']
        
        @property
        def page_info(self):
            # custom extension
            page_info = json.dumps(self._raw_response['page']) 
            return page_info


#--------------------------------------------------------------------------------------
# usage mock-up

# init connect, include a way to store passwd outside this file so the file can be shared. Using SSO would be nice, but not in scope ATM
markerrep = MarkerRepositoryQA(connection_file='~/.phoenixrc')

# list all targets
target_list = markerrep.list_targets
print(target_list)
# ['get_a_marker_by_id', 'get_markers_by_criteria', 'get_a_marker_instance_by_id', 'get_marker_instances_by_criteria', 'get_a_marker_source_category_by_name', 'get_all_marker_source_categories', 'get_a_marker_instance_source_category_by_name', 'get_all_marker_instance_source_categories', 'get_a_specific_upload_result_by_id', 'list_upload_results', 'list_update_results']

# some help
my_parm = markerrep.list_parameters('get_a_marker_by_id')
print(my_parm)  # prints {'required:['markeruid',],'optional:[]}

# get a marker
mymarker = markerrep.get_a_marker_by_id(markeruid='mGOS00000042')
print(mymarker['markerCondition']) # prints 'legacy'


# search
mylist = markerrep.get_markers_by_criteria()
# yields SyntaxError: parameter taxonomy is missing 

mylist = markerrep.get_markers_by_criteria(taxonomy=3633, page_size=10, page=0)
mymarker = mylist[0]['markerUID']
print(mymarker) # prints 'marker-mGOS00000010'
print(mymarker.page_info['totalPages'])  #prints 793



