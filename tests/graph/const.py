from live_line_builder.domain.line_graph.audio_patch import EquipmentID, PortID

EQ_VO = EquipmentID("eq_vo")
EQ_LG = EquipmentID("eq_lg")
EQ_LG_MIC = EquipmentID("eq_lg_mic")
EQ_SB = EquipmentID("eq_sb")
EQ_MIX = EquipmentID("eq_mix")


VO_OUT = PortID("vo_out")
LG_OUT = PortID("lg_out")
LG_MIC_IN = PortID("lg_mic_in")
LG_MIC_OUT = PortID("lg_mic_out")
SB_IN1 = PortID("sb_in1")
SB_OUT1 = PortID("sb_out1")
SB_IN2 = PortID("sb_in2")
SB_OUT2 = PortID("sb_out2")
MIX_IN1 = PortID("mix_in1")
MIX_IN2 = PortID("mix_in2")
MIX_AUX1_OUT = PortID("mix_out")
