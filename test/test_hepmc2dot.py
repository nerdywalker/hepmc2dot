import hepmc2dot

import unittest

import os
import tempfile
from math import sqrt


class Test_get_dot_particle(unittest.TestCase):

    def test_floatEnergy_expectEnergyRounding(self):
        actual_dot_particle = hepmc2dot._get_dot_particle(prod_vtx_barcode=123,
                                                          end_vtx_barcode=987,
                                                          particle_barcode=666,
                                                          particle_id=-111,
                                                          particle_energy=999.9)
        expected_dot_particle = '    V_123 -> V_987 [label="p #666\\nid=-111\\nE=1000"];\n'
        self.assertEqual(expected_dot_particle, actual_dot_particle)

    def test_finalStateParticle_expectDummyEndVertex(self):
        actual_dot_particle = hepmc2dot._get_dot_particle(prod_vtx_barcode=123,
                                                          end_vtx_barcode=None,
                                                          particle_barcode=666,
                                                          particle_id=-111,
                                                          particle_energy=888)
        expected_dot_particle = '    V_123 -> V_dummy_666 [label="p #666\\nid=-111\\nE=888"];\n'
        self.assertEqual(expected_dot_particle, actual_dot_particle)

    def test_stringArguments_expectAutomaticConversion(self):
        actual_dot_particle = hepmc2dot._get_dot_particle(prod_vtx_barcode='123',
                                                          end_vtx_barcode='987',
                                                          particle_barcode='666',
                                                          particle_id='-111',
                                                          particle_energy='888')
        expected_dot_particle = '    V_123 -> V_987 [label="p #666\\nid=-111\\nE=888"];\n'
        self.assertEqual(expected_dot_particle, actual_dot_particle)


class Test_get_node_name(unittest.TestCase):

    def test_positiveBarcode_expectPositiveNumInNodeName(self):
        actual_node_name = hepmc2dot._get_node_name(barcode=123)
        expected_node_name = 'V_123'
        self.assertEqual(actual_node_name, expected_node_name)

    def test_negativeBarcode_expectPositiveNumInNodeName(self):
        actual_node_name = hepmc2dot._get_node_name(barcode=-123)
        expected_node_name = 'V_123'
        self.assertEqual(actual_node_name, expected_node_name)

    def test_dummyVertex_expectDummyNodeName(self):
        actual_node_name = hepmc2dot._get_node_name(barcode=-123, is_dummy=True)
        expected_node_name = 'V_dummy_123'
        self.assertEqual(actual_node_name, expected_node_name)

    def test_strArguments_expectAutomaticConversion(self):
        actual_node_name = hepmc2dot._get_node_name(barcode='-123', is_dummy=True)
        expected_node_name = 'V_dummy_123'
        self.assertEqual(actual_node_name, expected_node_name)


class Test_get_dot_vertex(unittest.TestCase):

    def assert_get_vertex(self, expected_dot, *args, **kwargs):
        actual_dot = hepmc2dot._get_dot_vertex(*args, **kwargs)
        self.assertEqual(expected_dot, actual_dot)

    def test_nagativeVertexID_expectPositiveDotVertexNameAndNegativeIDInLabel(self):
        vtx_id = -1
        vtx_r = 2
        vtx_z = 3
        expected_dot = '    V_1 [label="vtx #-1\\nr=2.00,z=3.00",pos="3.000,2.000!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z)

    def test_positiveVertexID_expectPositiveDotVertexNameAndPositiveIDInLabel(self):
        vtx_id = 1
        vtx_r = 2
        vtx_z = 3
        expected_dot = '    V_1 [label="vtx #1\\nr=2.00,z=3.00",pos="3.000,2.000!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z)

    def test_dummyVertex_expectDummyVertexNameAndEmptyLabel(self):
        vtx_id = 1
        vtx_r = 2
        vtx_z = 3
        is_dummy = True
        expected_dot = '    V_dummy_1 [shape=none,label="",pos="3.000,2.000!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z, is_dummy)

    def test_dummyVertexNegativeID_expectDummyVertexNameAndEmptyLabel(self):
        vtx_id = -1
        vtx_r = 2
        vtx_z = 3
        is_dummy = True
        expected_dot = '    V_dummy_1 [shape=none,label="",pos="3.000,2.000!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z, is_dummy)

    def test_longFloatingPointRZ_expectRoundedRZ(self):
        vtx_id = -1
        vtx_r = 2.3456789
        vtx_z = 3.4567890
        expected_dot = '    V_1 [label="vtx #-1\\nr=2.35,z=3.46",pos="3.457,2.346!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z)

    def test_strVtxArguments_expectAutomaticConversion(self):
        vtx_id = '-1'
        vtx_r = '2.3456789'
        vtx_z = '3.4567890'
        expected_dot = '    V_1 [label="vtx #-1\\nr=2.35,z=3.46",pos="3.457,2.346!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z)

    def test_scaleProvided_expectScaledPosition(self):
        vtx_id = -1
        vtx_r = 2
        vtx_z = 3
        scale = 4

        expected_dot = '    V_1 [label="vtx #-1\\nr=2.00,z=3.00",pos="12.000,8.000!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z, scale=scale)

    def test_scaledDummy_expectScaledPosition(self):
        vtx_id = -1
        vtx_r = 2
        vtx_z = 3
        is_dummy = True
        scale = 4

        expected_dot = '    V_dummy_1 [shape=none,label="",pos="12.000,8.000!"];\n'
        self.assert_get_vertex(expected_dot, vtx_id, vtx_r, vtx_z, is_dummy=is_dummy, scale=scale)


class TestComponentHepMC2Dot(unittest.TestCase):

    def setUp(self):
        self.hepmc_file = tempfile.NamedTemporaryFile(delete=False, mode='w')

        self.dot_file = tempfile.NamedTemporaryFile(delete=False, mode='r')
        self.dot_file.close()

        # use common definition of particle and vertex DOT strings for test maintainability
        self.vtx_200334 = '    V_200334 [label="vtx #-200334\\nr=1027.68,z=1423.66",pos="1423.657,1027.677!"];\n'
        self.vtx_200648 = '    V_200648 [label="vtx #-200648\\nr=1091.08,z=-1881.66",pos="-1881.663,1091.080!"];\n'
        self.vtx_dummy_200386 = '    V_dummy_200386 [shape=none,label="",pos="-1943.048,1281.427!"];\n'
        self.vtx_dummy_200389 = '    V_dummy_200389 [shape=none,label="",pos="-1740.250,1232.510!"];\n'
        self.vtx_dummy_200391 = '    V_dummy_200391 [shape=none,label="",pos="-1913.914,1288.463!"];\n'
        self.vtx_dummy_200394 = '    V_dummy_200394 [shape=none,label="",pos="1548.247,1184.129!"];\n'
        self.p_200388 = '    V_200648 -> V_200334 [label="p #200388\\nid=211\\nE=356"];\n'
        self.p_200391 = '    V_200648 -> V_dummy_200391 [label="p #200391\\nid=2212\\nE=1042"];\n'
        self.p_200386 = '    V_200648 -> V_dummy_200386 [label="p #200386\\nid=2112\\nE=1087"];\n'
        self.p_200389 = '    V_200648 -> V_dummy_200389 [label="p #200389\\nid=-211\\nE=1077"];\n'
        self.p_200394 = '    V_200334 -> V_dummy_200394 [label="p #200394\\nid=2112\\nE=1017"];\n'

    def tearDown(self):
        self.hepmc_file.close()
        os.remove(self.hepmc_file.name)

        self.dot_file.close()
        os.remove(self.dot_file.name)

    def test_emptyHepMCFile_expectEmptyDotFile(self):
        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            expected_dot_contents = ""
            actual_dot_contents = result_file.read()
            self.assertEqual(expected_dot_contents, actual_dot_contents)


    def test_oneEmptyHepMCEvent_expectOneEmptyDotDigraph(self):
        self.hepmc_file.write("E 29 -1 -1.00000000e+00 -1.00000000e+00 -1.00000000e+00 1111230000 -243 534 1 2 0 3\n")
        self.hepmc_file.close()

        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            expected_dot_contents = "digraph event_29 {\n" \
                                    "}\n"
            actual_dot_contents = result_file.read()
            self.assertEqual(expected_dot_contents, actual_dot_contents)

    def test_eventWithOneHepMCVertex_expectOneEventWithOneVertexInDot(self):
        self.hepmc_file.write("E 29 -1 -1.00000000e+00 -1.00000000e+00 -1.00000000e+00 1111230000 -243 534 1 2 0 3\n")
        self.hepmc_file.write("V -200648 1121 9.51900940e+02 -5.33236511e+02 -1.88166296e+03 2.88058228e+03 0 1 1 2.00877000e+05\n")
        self.hepmc_file.close()

        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            actual_dot_contents = result_file.read()
        expected_dot_contents = 'digraph event_29 {\n' \
                                + self.vtx_200648 + \
                                '}\n'
        self.assertEqual(expected_dot_contents, actual_dot_contents)

    def test_oneVertexWithOutgoingParticleWithoutEndVertex_expectSameRepresentationInDot(self):
        self.hepmc_file.write("E 29 -1 -1.00000000e+00 -1.00000000e+00 -1.00000000e+00 1111230000 -243 534 1 2 0 3\n")
        self.hepmc_file.write("V -200648 1121 9.51900940e+02 -5.33236511e+02 -1.88166296e+03 2.88058228e+03 0 1 1 2.00877000e+05\n")
        self.hepmc_file.write("P 200386 2112 -2.51403702e+02 4.56170502e+02 -1.67972778e+02 1.08733311e+03 9.39565369e+02 1 0 0 0 0\n")
        self.hepmc_file.close()

        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            actual_dot_contents = result_file.read()
        expected_dot_contents = 'digraph event_29 {\n' \
                                + self.vtx_200648 \
                                + self.vtx_dummy_200386 \
                                + self.p_200386 \
                                + '}\n'
        self.assertEqual(expected_dot_contents, actual_dot_contents)

    def test_oneVertexTwoOutgoingParticlesWithoutEndVertices_expectSameRepresentationInDot(self):
        self.hepmc_file.write("E 29 -1 -1.00000000e+00 -1.00000000e+00 -1.00000000e+00 1111230000 -243 534 1 2 0 3\n")
        self.hepmc_file.write("V -200648 1121 9.51900940e+02 -5.33236511e+02 -1.88166296e+03 2.88058228e+03 0 1 1 2.00877000e+05\n")
        self.hepmc_file.write("P 200386 2112 -2.51403702e+02 4.56170502e+02 -1.67972778e+02 1.08733311e+03 9.39565369e+02 1 0 0 0 0\n")
        self.hepmc_file.write("P 200391 2212 -3.58282349e+02 -2.69635498e+02 -7.32659836e+01 1.04249310e+03 9.38272034e+02 1 0 0 0 0\n")
        self.hepmc_file.close()

        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            actual_dot_contents = result_file.read()
        expected_dot_contents = 'digraph event_29 {\n' \
                                + self.vtx_200648 \
                                + self.vtx_dummy_200386 \
                                + self.p_200386 \
                                + self.vtx_dummy_200391 \
                                + self.p_200391 \
                                + '}\n'
        self.assertEqual(expected_dot_contents, actual_dot_contents)

    def test_eventTwoVerticesWithOneConnectingParticle_expectSameRepresentationInDot(self):
        self.hepmc_file.write("E 29 -1 -1.00000000e+00 -1.00000000e+00 -1.00000000e+00 1111230000 -243 534 1 2 0 3\n")
        self.hepmc_file.write("V -200648 1121 9.51900940e+02 -5.33236511e+02 -1.88166296e+03 2.88058228e+03 0 1 1 2.00877000e+05\n")
        self.hepmc_file.write("P 200388 211 -2.08521011e+02 2.27627213e+02 1.08288109e+02 3.55670194e+02 1.39570099e+02 1 0 0 -200334 0\n")
        self.hepmc_file.write("V -200334 1121 -7.28379395e+02 7.24970886e+02 1.42365698e+03 2.04311096e+03 0 2 1 2.00388000e+05\n")
        self.hepmc_file.close()

        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            actual_dot_contents = result_file.read()
        expected_dot_contents = 'digraph event_29 {\n' \
                                + self.vtx_200648 \
                                + self.p_200388 \
                                + self.vtx_200334 \
                                + '}\n'
        self.assertEqual(expected_dot_contents, actual_dot_contents)

    def test_eventTwoVerticesWithOneConnectingParticleAndOneParticleWithoutEndVertex_expectSameRepresentationInDot(self):
        self.hepmc_file.write("E 29 -1 -1.00000000e+00 -1.00000000e+00 -1.00000000e+00 1111230000 -243 534 1 2 0 3\n")
        self.hepmc_file.write("V -200648 1121 9.51900940e+02 -5.33236511e+02 -1.88166296e+03 2.88058228e+03 0 1 1 2.00877000e+05\n")
        self.hepmc_file.write("P 200388 211 -2.08521011e+02 2.27627213e+02 1.08288109e+02 3.55670194e+02 1.39570099e+02 1 0 0 -200334 0\n")
        self.hepmc_file.write("P 200389 -211 -5.99197632e+02 -4.59768372e+02 7.55172729e+02 1.07712136e+03 1.39570099e+02 1 0 0 0 0\n")
        self.hepmc_file.write("V -200334 1121 -7.28379395e+02 7.24970886e+02 1.42365698e+03 2.04311096e+03 0 2 1 2.00388000e+05\n")
        self.hepmc_file.close()

        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            actual_dot_contents = result_file.read()
        expected_dot_contents = 'digraph event_29 {\n' \
                                + self.vtx_200648 \
                                + self.p_200388 \
                                + self.vtx_dummy_200389 \
                                + self.p_200389 \
                                + self.vtx_200334 \
                                + '}\n'
        self.assertEqual(expected_dot_contents, actual_dot_contents)

    def test_eventTwoVerticesWithOneConnectingParticleAndTwoParticlesWithoutEndVertices_expectSameRepresentationInDot(self):
        self.hepmc_file.write("E 29 -1 -1.00000000e+00 -1.00000000e+00 -1.00000000e+00 1111230000 -243 534 1 2 0 3\n")
        self.hepmc_file.write("V -200648 1121 9.51900940e+02 -5.33236511e+02 -1.88166296e+03 2.88058228e+03 0 1 1 2.00877000e+05\n")
        self.hepmc_file.write("P 200388 211 -2.08521011e+02 2.27627213e+02 1.08288109e+02 3.55670194e+02 1.39570099e+02 1 0 0 -200334 0\n")
        self.hepmc_file.write("P 200389 -211 -5.99197632e+02 -4.59768372e+02 7.55172729e+02 1.07712136e+03 1.39570099e+02 1 0 0 0 0\n")
        self.hepmc_file.write("V -200334 1121 -7.28379395e+02 7.24970886e+02 1.42365698e+03 2.04311096e+03 0 2 1 2.00388000e+05\n")
        self.hepmc_file.write("P 200394 2112 -1.85434677e+02 -2.42430649e+02 2.43059982e+02 1.01735927e+03 9.39565369e+02 1 0 0 0 0\n")
        self.hepmc_file.close()

        hepmc2dot.main(self.hepmc_file.name, self.dot_file.name)

        with open(self.dot_file.name, 'r') as result_file:
            actual_dot_contents = result_file.read()
        expected_dot_contents = 'digraph event_29 {\n' \
                                + self.vtx_200648 \
                                + self.p_200388 \
                                + self.vtx_dummy_200389 \
                                + self.p_200389 \
                                + self.vtx_200334 \
                                + self.vtx_dummy_200394 \
                                + self.p_200394 \
                                + '}\n'
        self.assertEqual(expected_dot_contents, actual_dot_contents)
