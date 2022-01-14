"""Compile YAML settings for the HGC ROC into their page/register values
written to a CSV.

Each parameter is given specific bits in (one or more) registers across
a page. (TO BE CHECKED, pretty sure no settings go across two pages)
The parameters are encoded into the register values IN ORDER so that
general defaults can be set first and then exceptions can be made.

The YAML settings have a two-tier structure:
```yaml
Page_Name:
  Parameter1: val1
  Parameter2: val2
Other_page:
  Parameter3: val3
```

The names of the pages and parameters are copied from the documentation
of the ASIC parameters.

The "Page_Name" strings can be regular expressions to match several
different pages. For example, if you wish to apply the same parameter
settings to all channels, you would use the following YAML snippet.
```yaml
Channel_*:
  SameForAllChannels: value
```

If you want multiple rounds of compilation in one file, you will need
to list them including an extra <tab>.
```yaml
-
  Channel_*:
    Parameter: default_value
-
  Channel_42:
    Parameter: value_for_42_only
```
"""

import re

class BitSpec :
    """This class holds the bit specification of a parameter.

    It is designed so that the user can more easily copy the specifications
    from the documenation of the HGC ROC v2. If (in the rare occasion),
    a parameter spans multiple registers, each input to this __init__
    should be a list of the same length giving the bit specification of
    the parameter value FROM THE LSB to the MSB.

    Parameters
    ----------
    register : int or list[int]
        the register number within the page (0-15)
    min_bit : int or list[int]
        the minimum bit that the parameter starts on (0-7)
    n_bits : int or list[int]
        number of bits the parameter spans within this register (1-8)
    default : int
        Default value for the parameter as given in the documentation

    Attributes
    ----------
    mask : list[int]
        From the number of bits, this mask is generated to be applied
        to the lowest n_bits of a parameter value
    clear : list[int]
        From the mask and min_bit, this new mask is generated to be 
        applied to the register value to clear any old parameter values
        before adding the new one.
    """

    def __init__(self, register, min_bit, n_bits, default = 0) :
        if not isinstance(register,list) :
            register = [register]
        for val in register :
            if val < 0 or val > 15 :
                raise TypeError(f'BitSpec: {val} is not a valid register number.')

        if not isinstance(min_bit,list) :
            min_bit = [min_bit]
        for val in min_bit :
            if val < 0 or val > 7 :
                raise TypeError(f'BitSpec: {min_bit} is not a valid minimum bit in a register.')

        if not isinstance(n_bits,list) :
            n_bits = [n_bits]
        for val in n_bits :
            if val < 1 or val > 8 :
                raise TypeError(f'BitSpec: {n_bits} is not a valid number of bits in a register.')

        if not (len(n_bits) == len(min_bit) == len(register)) :
            raise TypeError(f'BitSpec: Length of specifications don\'t match.')

        self.register = register
        self.min_bit = min_bit
        self.n_bits = n_bits
        self.mask = [((1 << n) - 1) for n in self.n_bits]
        self.clear = [(mask << min_bit) ^ 0b11111111 
                for mask, min_bit in zip(self.mask,self.min_bit)]
        self.default = default

    def __iter__(self) :
        """We are our own iterator"""
        self.__index = 0
        return self

    def __next__(self) :
        """Go to the next specification in this BitSpec

        The order of the entries in the returned tuple should
        exactly match the order of the variables in the 'for'
        loop so that the correct assignments are made.
        """
        if self.__index < len(self.register) :
            # still another register to write to
            ret_val = (self.register[self.__index],
                    self.min_bit[self.__index],
                    self.n_bits[self.__index],
                    self.mask[self.__index],
                    self.clear[self.__index]
                    )
            self.__index += 1
            return ret_val

        raise StopIteration

class CompiledSettings :
    """Structure holding the compiled settings

    The __init__ constructor is what does the compilation of the input
    settings into register values across pages.

    LUT == Look Up Table

    Parameters
    ----------
    parameter_settings : list[dict] 
        This input has a very specific format
        Each entry in the list has a two-tiered dictionary.
        The first level gives a simple regex matching one or more page names
        and the second gives the name of a setting within that page (or pages)
    prepend_defaults : bool, optional
        True if we want the default values to be set first

    Exceptions
    ----------
    KeyError : thrown if a page or parameter name is not recognized

    Class Attributes
    ----------
    num_pages : int
        Number of pages of settings on the HGC ROC (300)
    num_registers_per_page : int
        Number of registers per page on the HGC ROC (16)
    global_analog_lut : dict
        LUT for the Global Analog pages
        Key: name of parameter, Val: BitSpec for that parameter
    reference_voltage_lut : dict
        LUT for the Reference Voltage pages
        Key: name of parameter, Val: BitSpec for that parameter
    master_tdc_lut : dict
        LUT for the Master TDC pages
        Key: name of parameter, Val: BitSpec for that parameter
    digital_half_lut : dict
        LUT for the Digital Half pages
        Key: name of parameter, Val: BitSpec for that parameter
    top_lut : dict
        LUT for the Top page
        Key: name of parameter, Val: BitSpec for that parameter
    channel_wise_lut : dict
        LUT for the Channel (including calib and common) pages
        Key: name of parameter, Val: BitSpec for that parameter
    name_lut : dict
        LUT for all supported pages
        Key: name of page, Val: tuple(<page number>,<page_lut>)
    defaults : dict
        Values for all parameters as specified by the documentation
    """

    num_pages = 300 # 0 -> 299
    num_registers_per_page = 16

    global_analog_lut = {
        'ON_dac_trim' : BitSpec(0,0,1,1),
        'ON_input_dac' : BitSpec(0,1,1,1),
        'ON_conv' : BitSpec(0,2,1,1),
        'ON_pa' : BitSpec(0,3,1,1),
        'Gain_conv' : BitSpec(0,4,4,0b0100),
        'ON_rtr' : BitSpec(1,0,1,1),
        'Sw_super_conv' : BitSpec(1,1,1,1),
        'Dacb_vb_conv' : BitSpec(1,2,6,0b110011),
        'ON_toa' : BitSpec(2,0,1,1),
        'ON_tot' : BitSpec(2,1,1,1),
        'Dacb_vbi_pa' : BitSpec(2,2,6,0b011111),
        'Ibi_sk' : BitSpec(3,0,2,0),
        'Ibo_sk' : BitSpec(3,2,6,0b001010),
        'Ibi_inv' : BitSpec(4,0,2,0),
        'Ibo_inv' : BitSpec(4,2,6,0b001010),
        'Ibi_noinv' : BitSpec(5,0,2,0),
        'Ib0_noinv' : BitSpec(5,2,6,0b001010),
        'Ibi_inv_buf' : BitSpec(6,0,2,0b11),
        'Ibo_inv_buf' : BitSpec(6,2,6,0b100110),
        'Ibi_noinv_buf' : BitSpec(7,0,2,0b11),
        'Ibo_noinv_buf' : BitSpec(7,2,6,0b100110),
        'Sw_cd' : BitSpec(8,0,3,0b111),
        'En_hyst_tot' : BitSpec(8,3,1,0),
        'Sw_Cf_comp' : BitSpec(8,4,4,0b1010),
        'Sw_Cf' : BitSpec(9,0,4,0b1010),
        'Sw_Rf' : BitSpec(9,4,4,0b1000),
        'Clr_ShaperTail' : BitSpec(10,1,1,0),
        'SelRisingEdge' : BitSpec(10,2,1,1),
        'SelExtADC' : BitSpec(10,3,1,0),
        'Clr_ADC' : BitSpec(10,4,1,0),
        'S_sk' : BitSpec(10,5,3,0b010),
        'S_inv' : BitSpec(11,2,3,0b010),
        'S_noinv' : BitSpec(11,5,3,0b010),
        'S_inv_buf' : BitSpec(12,2,3,0b110),
        'S_noinv_buf' : BitSpec(12,5,3,0b110),
        'Ref_adc' : BitSpec(13,0,2,0),
        'Delay40' : BitSpec(13,2,3,0),
        'Delay65' : BitSpec(13,5,3,0),
        'ON_ref_adc' : BitSpec(14,0,1,1),
        'Pol_adc' : BitSpec(14,1,1,1),
        'Delay87' : BitSpec(14,2,3,0),
        'Delay9' : BitSpec(14,5,3,0),
        }
    
    reference_voltage_lut = {
        'Probe_vref_pa' : BitSpec(0,0,1,0),
        'Probe_vref_time' : BitSpec(0,1,1,0),
        'Refi' : BitSpec(0,2,2,0b11),
        'Vbg_1v' : BitSpec(0,4,3,0b111),
        'ON_dac' : BitSpec(0,7,1,1),
        'Noinv_vref' : BitSpec([1,5],[0,0],[2,8],0b0100111100),
        'Inv_vref' : BitSpec([1,4],[2,0],[2,8],0b0110000000),
        'Toa_vref' : BitSpec([1,3],[4,0],[2,8],0b0001110000),
        'Tot_vref' : BitSpec([1,2],[6,0],[2,8],0b0110110000),
        'Calib_dac' : BitSpec([6,7],[0,0],[8,4],0),
        'IntCtest' : BitSpec(7,6,1,0),
        'ExtCtest' : BitSpec(7,7,1,0),
        'Probe_dc' : BitSpec(8,0,8,0),
        }

    master_tdc_lut = {
        'GLOBAL_TA_SELECT_GAIN_TOA' : BitSpec(0,0,4,0b0011),
        'GLOBAL_TA_SELECT_GAIN_TOT' : BitSpec(0,4,4,0b0011),
        'GLOBAL_MODE_NO_TOT_SUB' : BitSpec(1,0,1,0),
        'GLOBAL_LATENCY_TIME' : BitSpec(1,1,4,0b1010),
        'GLOBAL_MODE_FTDC_TOA_S0' : BitSpec(1,5,1,0),
        'GLOBAL_MODE_FTDC_TOA_S1' : BitSpec(1,6,1,1),
        'GLOBAL_SEU_TIME_OUT' : BitSpec(1,7,1,1),
        'BIAS_FOLLOWER_CAL_P_D' : BitSpec(2,0,4,0),
        'BIAS_FOLLOWER_CAL_P_EN' : BitSpec(2,4,1,0),
        'INV_FRONT_40MHZ' : BitSpec(2,5,1,0),
        'START_COUNTER' : BitSpec(2,6,1,1),
        'CALIB_CHANNEL_DLL' : BitSpec(2,7,1,0),
        'VD_CTDC_P_D' : BitSpec(3,0,5,0),
        'VD_CTDC_P_DAC_EN' : BitSpec(3,5,1,0),
        'EN_MASTER_CTDC_VOUT_INIT' : BitSpec(3,6,1,0),
        'EN_MASTER_CTDC_DLL' : BitSpec(3,7,1,1),
        'BIAS_CAL_DAC_CTDC_P_D' : BitSpec([4,7],[0,6],[2,2],0b0000),
        'CTDC_CALIB_FREQUENCY' : BitSpec(4,2,6,0b000010),
        'GLOBAL_MODE_TOA_DIRECT_OUTPUT' : BitSpec(5,0,1,0),
        'BIAS_I_CTDC_D' : BitSpec(5,1,6,0b011000),
        'FOLLOWER_CTDC_EN' : BitSpec(5,7,1,1),
        'GLOBAL_EN_BUFFER_CTDC' : BitSpec(6,0,1,0),
        'VD_CTDC_N_FORCE_MAX' : BitSpec(6,1,1,1),
        'VD_CTDC_N_D' : BitSpec(6,2,5,0),
        'VD_CTDC_N_DAC_EN' : BitSpec(6,7,1,0),
        'CTRL_IN_REF_CTDC_P_D' : BitSpec(7,0,5,0),
        'CTRL_IN_REF_CTDC_P_EN' : BitSpec(7,5,1,0),
        'CTRL_IN_SIG_CTDC_P_D' : BitSpec(8,0,5,0),
        'CTRL_IN_SIG_CTDC_P_EN' : BitSpec(8,5,1,0),
        'GLOBAL_INIT_DAC_B_CTDC' : BitSpec(8,6,1,0),
        'BIAS_CAL_DAC_CTDC_P_EN' : BitSpec(8,7,1,0),
        'VD_FTDC_P_D' : BitSpec(9,0,5,0),
        'VD_FTDC_P_DAC_EN' : BitSpec(9,5,1,0),
        'EN_MASTER_FTDC_VOUT_INIT' : BitSpec(9,6,1,0),
        'EN_MASTER_FTDC_DLL' : BitSpec(9,7,1,1),
        'BIAS_CAL_DAC_FTDC_P_D' : BitSpec([10,14],[0,6],[2,2],0b0000),
        'FTDC_CALIB_FREQUENCY' : BitSpec(10,2,6,0b000010),
        'EN_REF_BG' : BitSpec(11,0,1,1),
        'BIAS_I_FTDC_D' : BitSpec(11,1,6,0b011000),
        'FOLLOWER_FTDC_EN' : BitSpec(11,7,1,1),
        'GLOBAL_EN_BUFFER_FTDC' : BitSpec(12,0,1,0),
        'VD_FTDC_N_FORCE_MAX' : BitSpec(12,1,1,1),
        'VD_FTDC_N_D' : BitSpec(12,2,5,0),
        'VD_FTDC_N_DAC_EN' : BitSpec(12,7,1,0),
        'CTRL_IN_SIG_FTDC_P_D' : BitSpec(13,0,5,0),
        'CTRL_IN_SIG_FTDC_P_EN' : BitSpec(13,5,1,0),
        'GLOBAL_INIT_DAC_B_FTDC' : BitSpec(13,6,1,0),
        'BIAS_CAL_DAC_FTDC_P_EN' : BitSpec(13,7,1,0),
        'CTRL_IN_REF_FTDC_P_D' : BitSpec(14,0,5,0),
        'CTRL_IN_REF_FTDC_P_EN' : BitSpec(14,5,1,0),
        'GLOBAL_DISABLE_TOT_LIMIT' : BitSpec(15,0,1,0),
        'GLOBAL_FORCE_EN_CLK' : BitSpec(15,1,1,0),
        'GLOBAL_FORCE_EN_OUTPUT_DATA' : BitSpec(15,2,1,0),
        'GLOBAL_FORCE_EN_TOT' : BitSpec(15,3,1,0),
        }

    digital_half_lut = {}

    channel_wise_lut = {
        'Inputdac' : BitSpec(0,0,6,0b011111),
        'Dacb' : BitSpec([2,1,0],[6,6,6],[2,2,2],0b111111),
        'Sign_dac' : BitSpec(1,0,1,0),
        'Ref_dac_toa' : BitSpec(1,1,5,0),
        'Probe_noinv' : BitSpec(2,0,1,0),
        'Ref_dac_tot' : BitSpec(2,1,5,0),
        'Mask_toa' : BitSpec(3,0,1,0),
        'Ref_dac_inv' : BitSpec(3,1,5,0),
        'Sel_trigger_toa' : BitSpec(3,6,1,0),
        'Probe_inv' : BitSpec(3,7,1,0),
        'Probe_pa' : BitSpec(4,0,1,0),
        'LowRange' : BitSpec(4,1,1,0),
        'HighRange' : BitSpec(4,2,1,0),
        'Channel_off' : BitSpec(4,3,1,0),
        'Sel_trigger_tot' : BitSpec(4,4,1,0),
        'Mask_tot' : BitSpec(4,5,1,0),
        'Probe_tot' : BitSpec(4,6,1,0),
        'Probe_toa' : BitSpec(4,7,1,0),
        'DAC_CAL_FTDC_TOA' : BitSpec(5,0,6,0),
        'Mask_adc' : BitSpec(5,7,1,0),
        'DAC_CAL_CTDC_TOA' : BitSpec(6,0,6,0),
        'DAC_CAL_FTDC_TOT' : BitSpec(7,0,6,0),
        'DAC_CAL_CTDC_TOT' : BitSpec(8,0,6,0),
        'IN_FTDC_ENCODER_TOA' : BitSpec(9,0,6,0),
        'IN_FTDC_ENCODER_TOT' : BitSpec(10,0,6,0),
        'DIS_TDC' : BitSpec(10,7,1,0),
        'ExtData' : BitSpec([13,11],[0,0],[8,2],0),
        'Mask_AlignBuffer' : BitSpec(11,7,1,0),
        'Adc_pedestal' : BitSpec(12,0,8,0),
        }

    top_lut = {}
    
    # docs give us the page name to numbers
    name_lut = {
        'Reference_Voltage_0' : (296, reference_voltage_lut),
        'Global_Analog_0' : (297, global_analog_lut),
        'Master_TDC_0' : (298, master_tdc_lut),
        #'Digital_Half_0' : (299, digital_half_lut),
        'Reference_Voltage_1' : (40, reference_voltage_lut),
        'Global_Analog_1' : (41, global_analog_lut),
        'Master_TDC_1' : (42, master_tdc_lut),
        #'Digital_Half_1' : (43, digital_half_lut),
        #'Top' : (44,top_lut),
        'Channel_0' : (261, channel_wise_lut),
        'Channel_1' : (260, channel_wise_lut),
        'Channel_2' : (259, channel_wise_lut),
        'Channel_3' : (258, channel_wise_lut),
        'Channel_4' : (265, channel_wise_lut),
        'Channel_5' : (264, channel_wise_lut),
        'Channel_6' : (263, channel_wise_lut),
        'Channel_7' : (262, channel_wise_lut),
        'Channel_8' : (269, channel_wise_lut),
        'Channel_9' : (268, channel_wise_lut),
        'Channel_10' : (267, channel_wise_lut),
        'Channel_11' : (266, channel_wise_lut),
        'Channel_12' : (273, channel_wise_lut),
        'Channel_13' : (272, channel_wise_lut),
        'Channel_14' : (271, channel_wise_lut),
        'Channel_15' : (270, channel_wise_lut),
        'Channel_16' : (294, channel_wise_lut),
        'Channel_17' : (256, channel_wise_lut),
        'Channel_18' : (277, channel_wise_lut),
        'Channel_19' : (295, channel_wise_lut),
        'Channel_20' : (278, channel_wise_lut),
        'Channel_21' : (279, channel_wise_lut),
        'Channel_22' : (280, channel_wise_lut),
        'Channel_23' : (281, channel_wise_lut),
        'Channel_24' : (282, channel_wise_lut),
        'Channel_25' : (283, channel_wise_lut),
        'Channel_26' : (284, channel_wise_lut),
        'Channel_27' : (285, channel_wise_lut),
        'Channel_28' : (286, channel_wise_lut),
        'Channel_29' : (287, channel_wise_lut),
        'Channel_30' : (288, channel_wise_lut),
        'Channel_31' : (289, channel_wise_lut),
        'Channel_32' : (290, channel_wise_lut),
        'Channel_33' : (291, channel_wise_lut),
        'Channel_34' : (292, channel_wise_lut),
        'Channel_35' : (293, channel_wise_lut),
        'Channel_36' : (5, channel_wise_lut),
        'Channel_37' : (4, channel_wise_lut),
        'Channel_38' : (3, channel_wise_lut),
        'Channel_39' : (2, channel_wise_lut),
        'Channel_40' : (9, channel_wise_lut),
        'Channel_41' : (8, channel_wise_lut),
        'Channel_42' : (7, channel_wise_lut),
        'Channel_43' : (6, channel_wise_lut),
        'Channel_44' : (13, channel_wise_lut),
        'Channel_45' : (12, channel_wise_lut),
        'Channel_46' : (11, channel_wise_lut),
        'Channel_47' : (10, channel_wise_lut),
        'Channel_48' : (17, channel_wise_lut),
        'Channel_49' : (16, channel_wise_lut),
        'Channel_50' : (15, channel_wise_lut),
        'Channel_51' : (14, channel_wise_lut),
        'Channel_52' : (38, channel_wise_lut),
        'Channel_53' : (0, channel_wise_lut),
        'Channel_54' : (21, channel_wise_lut),
        'Channel_55' : (39, channel_wise_lut),
        'Channel_56' : (22, channel_wise_lut),
        'Channel_57' : (23, channel_wise_lut),
        'Channel_58' : (24, channel_wise_lut),
        'Channel_59' : (25, channel_wise_lut),
        'Channel_60' : (26, channel_wise_lut),
        'Channel_61' : (27, channel_wise_lut),
        'Channel_62' : (28, channel_wise_lut),
        'Channel_63' : (29, channel_wise_lut),
        'Channel_64' : (30, channel_wise_lut),
        'Channel_65' : (31, channel_wise_lut),
        'Channel_66' : (32, channel_wise_lut),
        'Channel_67' : (33, channel_wise_lut),
        'Channel_68' : (34, channel_wise_lut),
        'Channel_69' : (35, channel_wise_lut),
        'Channel_70' : (36, channel_wise_lut),
        'Channel_71' : (37, channel_wise_lut),
        #'CM0' : (275, channel_wise_lut),
        #'CM1' : (276, channel_wise_lut),
        #'CALIB0' : (274, channel_wise_lut),
        #'CM2' : (19, channel_wise_lut),
        #'CM3' : (20, channel_wise_lut),
        #'CALIB1' : (18, channel_wise_lut),


    }

    def __init__(self, named_settings, prepend_defaults = True) :
        self.compiled_settings = {}

        if prepend_defaults :
            defaults = {}
            for page_name, (page,lut) in CompiledSettings.name_lut.items() :
                defaults[page_name] = { param : spec.default for param, spec in lut.items() }
            named_settings.insert(0, defaults)

        for iteration, settings in enumerate(named_settings) :
            print(f'Staring iteration {iteration}')
            for page_regex, page_params in settings.items() :
                page_names = [n for n in CompiledSettings.name_lut.keys() 
                        if re.match(page_regex,n)]

                if len(page_names) == 0 :
                    raise KeyError(f'No page names match {page_regex}')

                for page_name in page_names :
                    print(f' Compiling page {page_name}')
                    page, name_to_bits = CompiledSettings.name_lut[page_name]
                    
                    # initiliaze page
                    if page not in self.compiled_settings :
                        self.compiled_settings[page] = [
                                None for r in range(CompiledSettings.num_registers_per_page)]
            
                    # go through parameters and insert them into their registers
                    for param_name, param_val in page_params.items() :
                        print(f'  {param_name} set to {param_val}')
                        bit_spec = name_to_bits[param_name]
                        value_curr_min_bit = 0
                        for reg, min_bit, n_bits, mask, clear in bit_spec :
                            # 1. get sub-value from parameter (next n_bits)
                            sub_val = ((param_val >> value_curr_min_bit) & mask)
                            value_curr_min_bit += n_bits
                            # 2. initialize register
                            if self.compiled_settings[page][reg] is None :
                                self.compiled_settings[page][reg] = 0
                            else :
                                self.compiled_settings[page][reg] &= clear;
    
                            # 3. insert value into register
                            self.compiled_settings[page][reg] += ((sub_val & mask) << min_bit)

    def __str__(self) :
        """Full string representation prints the compiled settings as a CSV string

        the columns are page,register,value (in hex)
        """

        msg = ''
        for page, registers in self.compiled_settings.items() :
            for reg, val in enumerate(registers) :
                if val is not None :
                    #msg += f'{page},{reg},0b{val:08b}\n'
                    msg += f'{page},{reg},0x{val:02x}\n'
        return msg

if __name__ == '__main__' :
    import argparse
    import sys
    import os
    # try to load C-bindings to be faster if possible
    from yaml import load, dump
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    parser = argparse.ArgumentParser(
            description="Compile one or more YAML setting objects into a single CSV settings file.",
            formatter_class = argparse.RawTextHelpFormatter
            )

    def run_then_exit(func) :
        class RunThenExitAction(argparse.Action):
            def __init__(self, nargs = 0, **kwargs):
                super().__init__(nargs = nargs, **kwargs)
    
            def __call__(self, parser, args, values, option_string=None):
                func()
                sys.exit(0)

        return RunThenExitAction

    def full_help() :
        print(sys.modules[__name__].__doc__)

    def print_example() :
        example = { 'Global_Analog_0' : { 'ON_pa' : 0 }}
        with open('example.yaml','w') as f :
            dump(example,f, Dumper=Dumper)    

    parser.add_argument('setting_file', type=str, nargs='+', 
            help='One (or more, in order) YAML setting files to compile.')
    parser.add_argument('--output', type=str,
            help='Path to output file to write compiled settings to,\n'
                  'default uses the name of the last YAML input file.')
    parser.add_argument('--no_defaults', action='store_true', 
            help='Don\'t include defaults from documentation in compilation.')
    parser.add_argument('--full_help', action=run_then_exit(full_help),
            help="Print an extended help message and exit.")
    parser.add_argument('--print_example', action=run_then_exit(print_example),
            help="Print an example YAML file and exit.")

    arg = parser.parse_args()

    if arg.output is None :
        arg.output = arg.setting_file[-1].replace('yaml','csv')

    settings_in_memory = []
    for file_name in arg.setting_file :
        with open(file_name) as f :
            sim = load(f,Loader=Loader)

        if isinstance(sim,list) :
            # assume that list of several iterations
            settings_in_memory.extend(sim)
        else :
            # assume single iteration of settings
            settings_in_memory.append(sim)

    compiled = CompiledSettings(settings_in_memory,
            prepend_defaults = (not arg.no_defaults))

    with open(arg.output,'w') as f :
        f.write(str(compiled))

