import sbol3
import opil

sbol3.set_homespace('http://strateos.com/')

# Experimental parameters
inc_temp = opil.IntegerParameter('inc_temp')
inc_temp.name = 'Incubation Temperature'
media_well_strings = opil.StringParameter('media_well_strings')
media_well_strings.name = 'Media Wells'

# Define plate reader configuration
fluor_ex = opil.Measurement('fluor_ex')
fluor_ex.default_value = 588
# fluor_ex.measurement_type = sbol3.Measure(588, 'nm')

# Add parameters to protocol
time_series = opil.Protocol('time_series')
time_series.has_parameter = inc_temp
time_series.protocol_measurement_type = fluor_ex

# Serialize
doc = sbol3.Document()
doc.add(time_series)
doc.add(media_well_strings)
doc.write('time_series.xml', file_format='xml')
