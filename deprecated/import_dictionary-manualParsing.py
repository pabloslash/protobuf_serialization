# Load the .pickle containing the dictionary for the protobuf message
# Read dictionary from pickle and create protobuf metadata-message

import pickle
import metadata_pb2
from datetime import datetime
import pytz
import json
import pickle
from operator import attrgetter
from google.protobuf.json_format import MessageToDict

class ProtobufMetadata:

    def __init__(self):
        # Create SESSION protobuff metadata
        self.sess = metadata_pb2.Session()
        # string: e.g. 2021-03-10
        self.sess.date = str(datetime.now(pytz.timezone('US/Pacific')).date())
        # string: e.g. 14:42:01.754603 (microseconds precision)
        self.sess.time = str(datetime.now(pytz.timezone('US/Pacific')).time())
        self.default_bird_metadata()

    '''Functions to load metadata from file'''
    '''TODO: Add options to read from json file'''

    # Load all metadata from metadata file
    def load_file(self, file_name):
        if file_name.endswith('.pickle'):
            with open(file_name, 'rb') as f:
                session_dict = pickle.load(f)
        elif file_name.endswith('.json'):
            with open(file_name) as f:
                session_dict = json.load(f)    
                print('.json file loaded correctly')
        else: return
        return session_dict
    
    def load_metadata_from_file(self, file_name):
        session_dict = self.load_file(file_name)
        
        # Read bird metadata
        self.read_bird_metadata(session_dict)
        # Read acquisitions metadata
        if 'acquisitions' in session_dict:
            for acquisition_dict in session_dict['acquisitions']:
                self.add_acquisition_metadata(acquisition_dict)

    # Load BIRD metadata from metadata file
    def load_bird_metadata_from_file(self, file_name):
        bird_dict = self.load_file(file_name)
        self.read_bird_metadata(bird_dict)
        
    # Load ACQUISITION metadata from metadata file
    def load_acquisition_from_file(self, file_name):
        acquisition_dict = self.load_file(file_name)
        # Read acquisitions metadata
        self.add_acquisition_metadata(acquisition_dict)

    # Load ACQUISITION(s) metadata from metadata file
    def load_acquisitions_from_file(self, file_name):
        acquisitions_dict = self.load_file(file_name)
        # Read acquisitions metadata
        if 'acquisitions' in acquisitions_dict:
            for acq in acquisitions_dict['acquisitions']:
                self.add_acquisition_metadata(acq)

    '''Functions to read metadata from a dictionary'''
    
    def read_bird_metadata(self, bird_dict):
        if 'bird_type' in bird_dict:  # UNKNOWN_BIRDTYPE(0), ZEBRA(1), STARLING(2), BENGALESE(3)
            if bird_dict['bird_type'] == 'STARLING':
                self.sess.bird_type = self.sess.BirdType.STARLING
            elif bird_dict['bird_type'] == 'ZEBRA':
                self.sess.bird_type = self.sess.BirdType.ZEBRA
            elif bird_dict['bird_type'] == 'BENGALESE':
                self.sess.bird_type = self.sess.BirdType.BENGALESE
            else:
                self.sess.bird_type = self.sess.BirdType.UNKNOWN_BIRDTYPE  # Also if user input is unrecognized

        if 'bird_sex' in bird_dict:  # UNKNOWN_BIRDSEX(0), MALE(1), FEMALE(2)
            if bird_dict['bird_sex'] == 'MALE':
                self.sess.bird_sex = self.sess.BirdSex.MALE
            elif bird_dict['bird_sex'] == 'FEMALE':
                self.sess.bird_sex = self.sess.BirdSex.FEMALE
            else:
                self.sess.bird_sex = self.sess.BirdSex.UNKNOWN_BIRDSEX  # Also if user input is unrecognized
        if 'condition' in bird_dict:  # UNKNOWN_CONDITION(0), HABITUATION(1), CHRONIC(2), ACUTE(3)
            if bird_dict['condition'] == 'HABITUATION':
                self.sess.condition = self.sess.Condition.HABITUATION
            elif bird_dict['condition'] == 'CHRONIC':
                self.sess.condition = self.sess.Condition.CHRONIC
            elif bird_dict['condition'] == 'ACUTE':
                self.sess.condition = self.sess.Condition.ACUTE
            else:
                self.sess.condition = self.sess.Condition.UNKNOWN_CONDITION  # Also if user input is unrecognized

        if 'bird_uid' in bird_dict: self.sess.bird_uid = bird_dict['bird_uid']  # string e.g. z_m10g8_20
        if 'weight_grams' in bird_dict: self.sess.weight_grams = bird_dict['weight_grams']  # float
        if 'testosterone' in bird_dict: self.sess.testosterone = bird_dict['testosterone']  # bool: True / False
        if 'testosterone_date' in bird_dict: self.sess.testosterone_date = bird_dict[
            'testosterone_date']  # string: e.g. 2021-03-10
        if 'dummy_weight' in bird_dict: self.sess.dummy_weight = bird_dict[
            'dummy_weight']  # bool: True / False
        if 'dummy_weight_grams' in bird_dict: self.sess.dummy_weight_grams = bird_dict[
            'dummy_weight_grams']  # bool: True / False
        if 'dummy_weight_date' in bird_dict: self.sess.dummy_weight_date = bird_dict[
            'dummy_weight_date']  # string: e.g. 2021-03-10
        if 'dummy_tether' in bird_dict: self.sess.dummy_tether = bird_dict[
            'dummy_tether']  # bool: True / False
        if 'dummy_tether_date' in bird_dict: self.sess.dummy_tether_date = bird_dict[
            'dummy_tether_date']  # string: e.g. 2021-03-10
        if 'box' in bird_dict: self.sess.box = bird_dict['box']  # string: e.g. passaro1, cuervecito3, shoox
        if 'details' in bird_dict:
            for det in bird_dict['details']: self.sess.details.append(det)  # repeated string: (Any additional info)

        self.sess.sess_uid = self.sess.Condition.keys()[
                                 self.sess.condition] + '-' + self.sess.bird_uid + '-' + datetime.now(
            pytz.timezone('US/Pacific')).strftime("%Y%m%d-%H:%M:%S")  # string: e.g. habituation_birdID_date_time

    def add_acquisition_metadata(self, acquisition_dict):
        acquisition = self.sess.acquisitions.add()
        if 'acquisition_hardware' in acquisition_dict: acquisition.acquisition_hardware = acquisition_dict[
            'acquisition_hardware']  # openephys, intan, spikeglx, uma8, raspi, any custom amp
        if 'acquisition_software' in acquisition_dict: acquisition.acquisition_software = acquisition_dict[
            'acquisition_software']  # openephys, openephys++, spikeglx, alsa, vlc
        # Iterate over Sensors
        if 'sensors' in acquisition_dict:
            for sensor_dict in acquisition_dict['sensors']:
                sensor = acquisition.sensors.add()
                if 'acquisition_signal' in sensor_dict: sensor.acquisition_signal = sensor_dict[
                    'acquisition_signal']  # audio, audio, pressure, sync, emg, video
                if 'manufacturer' in sensor_dict: sensor.manufacturer = sensor_dict[
                    'manufacturer']  # miniDSP, earthworks, fujikura, inhouse, inhouse
                if 'model' in sensor_dict: sensor.model = sensor_dict[
                    'model']  # uma8, m30, fhm-20, uma8_sync, emg_amp_inhouse
                if 'serial_number' in sensor_dict: sensor.serial_number = sensor_dict[
                    'serial_number']  # '', '', '', uma_syn_001, emg_amp_001
                if 'signal_name' in sensor_dict: sensor.signal_name = sensor_dict[
                    'signal_name']  # uma_syn_001, pressure, syn_uma8, emg, syn_stim, stim, etc.
                if 'headstage' in sensor_dict: sensor.headstage = sensor_dict[
                    'headstage']  # '', '', intan32, ", intan32
                if 'channel_group' in sensor_dict: sensor.channel_group = sensor_dict[
                    'channel_group']  # '', AIN, port_0, DIN, port_1
                if 'channels' in sensor_dict: sensor.channels = sensor_dict[
                    'channels']  # '', [0], [aux_0], [0], [aux_0, aux_1]
                if 'locations' in sensor_dict: sensor.locations = sensor_dict[
                    'locations']  # left, right, tracheal rings, muscles...
                if 'details' in sensor_dict:
                    for det in sensor_dict['details']: sensor.details.append(det)  # repeated string

        # Iterate over Neural probes
        if 'neuralprobes' in acquisition_dict:
            for neural_probe_dict in acquisition_dict['neuralprobes']:
                neural_probe = acquisition.neuralprobes.add()
                if 'acquisition_signal' in neural_probe_dict: neural_probe.acquisition_signal = neural_probe_dict[
                    'acquisition_signal']  # string: e.g. neural
                if 'manufacturer' in neural_probe_dict: neural_probe.manufacturer = neural_probe_dict[
                    'manufacturer']  # string: neuronexus, neuropixel, masmanidis, inhouse
                if 'model' in neural_probe_dict: neural_probe.model = neural_probe_dict[
                    'model']  # string: buzsaki32, neuropixels_1
                if 'serial_number' in neural_probe_dict: neural_probe.serial_number = neural_probe_dict[
                    'serial_number']  # string: U656
                if 'num_channels' in neural_probe_dict: neural_probe.num_channels = neural_probe_dict[
                    'num_channels']  # int32: 16, 32, 64, 384
                if 'tip_depth_microns' in neural_probe_dict: neural_probe.tip_depth_microns = neural_probe_dict[
                    'tip_depth_microns']  # float: depth of the tip of the probe
                if 'implant_coordinates_microns' in neural_probe_dict: neural_probe.implant_coordinates_microns = \
                    neural_probe_dict['implant_coordinates_microns']  # string: A/P, M/L, D/V
                if 'hemisphere' in neural_probe_dict: neural_probe.hemisphere = neural_probe_dict[
                    'hemisphere']  # string: left, right
                if 'brain_nucleus' in neural_probe_dict:
                    for bn in neural_probe_dict['brain_nucleus']: neural_probe.brain_nucleus.append(
                        bn)  # repeated string [hvc], [hvc,ra], area_X
                if 'headstage' in neural_probe_dict: neural_probe.headstage = neural_probe_dict[
                    'headstage']  # string: e.g. H32
                if 'channel_group' in neural_probe_dict: neural_probe.channel_group = neural_probe_dict[
                    'channel_group']  # string: port_0, imec_0
                if 'channels' in neural_probe_dict: neural_probe.channels = neural_probe_dict[
                    'channels']  # string: e.g. 1-64,
                if 'details' in neural_probe_dict:
                    for det in neural_probe_dict['details']: neural_probe.details.append(det)  # repeated string

        # Iterate over Stimuli
        if 'stimuli' in acquisition_dict:
            for stimulus_dict in acquisition_dict['stimuli']:
                stimulus = acquisition.stimuli.add()
                if 'stimulus_signal' in stimulus_dict: stimulus.stimulus_signal = stimulus_dict[
                    'stimulus_signal']  # string: female, video, song_replay, neural_stim
                if 'manufacturer' in stimulus_dict: stimulus.manufacturer = stimulus_dict[
                    'manufacturer']  # string: '', inhouse, inhouse, neuronexus
                if 'model' in stimulus_dict: stimulus.model = stimulus_dict[
                    'model']  # string: '', '', '3 females in cage, buzsaki32
                if 'serial_number' in stimulus_dict: stimulus.serial_number = stimulus_dict['serial_number']  #
                if 'signal_name' in stimulus_dict: stimulus.signal_name = stimulus_dict['signal_name']
                if 'channel_gropup' in stimulus_dict: stimulus.channel_gropup = stimulus_dict[
                    'channel_gropup']  # string: AIN, port_0, DIN, port_1
                if 'channels' in stimulus_dict: stimulus.channels = stimulus_dict[
                    'channels']  # string: [0], [aux_0], [0], [aux_0, aux_1]
                if 'details' in stimulus_dict:
                    for det in stimulus_dict['details']: stimulus.details.append(det)  # repeated string
                        
    def add_aquisitions_metadata(self, acquisitions_dict):
        # Iterate over ACQUISITIONS
        if 'acquisitions' in acquisitions_dict:
            for acquisition_dict in session_dict['acquisitions']:
                self.add_acquisition_metadata(acquisition_dict)

    def read_aquisitions_metadata(self, acquisition_metadata_file):
        with open(acquisition_metadata_file, 'rb') as file:
            session_dict = pickle.load(file)

        # Iterate over ACQUISITIONS
        if 'acquisitions' in session_dict:
            for acquisition_dict in session_dict['acquisitions']:
                self.add_acquisition_metadata(acquisition_dict)

        
    '''Saving Functions'''
    
    def save_metadata_json(self, metadata_dict, file_name):
        json_obj = MessageToDict(metadata_dict, including_default_value_fields=False, preserving_proto_field_name=False, use_integers_for_enums=False, descriptor_pool=None, float_precision=None)

        with open(file_name, 'w') as fj:
            json.dump(json_obj, fj, indent=5)
        fj.close()

    def save_metadata_pickle(self, metadata_dict, file_name):
        with open(file_name, 'wb') as fp:
            pickle.dump(metadata_dict, fp, protocol=pickle.HIGHEST_PROTOCOL)
        fp.close()
        
        
    '''Set Defaults Functions'''
    
    def default_bird_metadata(self):
        self.sess.bird_type = self.sess.BirdType.UNKNOWN_BIRDTYPE
        self.sess.bird_sex = self.sess.BirdSex.MALE
        self.sess.Condition.UNKNOWN_CONDITION
        self.sess.bird_uid = 'x_x00x00_00'
        self.sess.testosterone = False
        self.sess.testosterone_date = 'YYYY-MM-DD'
        self.sess.dummy_weight = False
        self.sess.dummy_weight_grams = 0
        self.sess.dummy_weight_date = 'YYYY-MM-DD'
        self.sess.dummy_tether = False
        self.sess.dummy_tether_date = 'YYYY-MM-DD'
        self.sess.box = ''
        self.sess.sess_uid = self.sess.Condition.keys()[
                                 self.sess.condition] + '-' + self.sess.bird_uid + '-' + datetime.now(
            pytz.timezone('US/Pacific')).strftime("%Y%m%d-%H:%M:%S")  # string: e.g. habituation_birdID_date_time
        
        
    #     def delete_attribute(self, metadata_object, attribute_name):
        
#         attribute_getter = attrgetter(attribute_name)
#         for atribute in attribute_getter(metadata_object):
#             del(attribute)


