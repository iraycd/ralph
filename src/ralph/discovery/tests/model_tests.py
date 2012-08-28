# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from django.test import TestCase

from ralph.discovery.models import DeviceType, Device
from ralph.discovery.models_network import Network, NetworkTerminator, DataCenter
from ralph.business.models import Venture, VentureRole

class ModelsTest(TestCase):
    def test_device_create_empty(self):
        with self.assertRaises(ValueError):
            Device.create(model_name='xxx', model_type=DeviceType.unknown)

    def test_device_create_nomodel(self):
        with self.assertRaises(ValueError):
            Device.create(sn='xxx')

    def test_device_conflict(self):
        Device.create([('1', 'DEADBEEFCAFE', 0)],
                      model_name='xxx', model_type=DeviceType.rack_server)
        Device.create([('1', 'CAFEDEADBEEF', 0)],
                      model_name='xxx', model_type=DeviceType.rack_server)
        with self.assertRaises(ValueError):
            Device.create([('1', 'DEADBEEFCAFE', 0), ('2', 'CAFEDEADBEEF', 0)],
                          model_name='yyy', model_type=DeviceType.switch)

    def test_device_create_blacklist(self):
        ethernets = [
            ('1', 'DEADBEEFCAFE', 0),
            ('2', 'DEAD2CEFCAFE', 0),
        ]
        dev = Device.create(ethernets, sn='None',
                            model_name='xxx', model_type=DeviceType.unknown)

        self.assertEqual(dev.sn, None)
        macs = [e.mac for e in dev.ethernet_set.all()]
        self.assertEqual(macs, ['DEADBEEFCAFE'])

    def test_check_ip(self):
        terminator = NetworkTerminator(name='Test Terminator')
        terminator.save()

        data_center = DataCenter(name='Test date_center')
        data_center.save()
        
        network = Network(address='127.0.0.1',name='Test network', 
                          data_center=data_center)
        network.save()
        network.terminators = [terminator]
        network.save()
            
        main_venture = Venture(name='Main Venture')
        main_venture.save()
        main_venture.network = [network]
        main_venture.save()
        
        second_network = Network(address='127.0.0.2',name='Test secound_network', 
                          data_center=data_center)
        second_network.save()
        second_network.terminators = [terminator]
        second_network.save()
        
        child_venture = Venture(name='Child Venture', parent_id=main_venture.id)
        child_venture.save()
        child_venture.network = [second_network]
        child_venture.save()
        
        third_network = Network(address='127.0.0.3',name='Test third_network', 
                          data_center=data_center)
        third_network.save()
        third_network.terminators = [terminator]
        third_network.save()
        
        venture_role_main = VentureRole(name='Main Venture role', 
                                        venture=child_venture)
        venture_role_main.save()
        venture_role_main.network = [third_network]
        venture_role_main.save()
        
        fourth_network = Network(address='127.0.0.4',name='Test fourth_network', 
                          data_center=data_center)
        fourth_network.save()
        fourth_network.terminators = [terminator]
        fourth_network.save()
        
        venture_role_child = VentureRole(name='Child Venture role', 
                                         venture=child_venture, 
                                         parent=venture_role_main)
        venture_role_child.save()
        venture_role_child.network = [fourth_network]
        venture_role_child.save()
        
        self.assertEqual(Network.check_ip("127.0.0.1", venture_role_child), True)
        self.assertEqual(Network.check_ip("127.0.0.2", venture_role_child), True)
        self.assertEqual(Network.check_ip("127.0.0.3", venture_role_child), True)
        self.assertEqual(Network.check_ip("127.0.0.4", venture_role_child), True)
        self.assertEqual(Network.check_ip("127.0.0.5", venture_role_child), False)
        self.assertEqual(Network.check_ip("127.0.0.6", venture_role_child), False)