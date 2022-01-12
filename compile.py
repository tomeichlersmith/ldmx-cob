"""Compile JSON settings for the HGC ROC into their page/register values
written to a CSV.

I'm using JSON instead of YAML because JSON comes with Python.

Each parameter is given specific bits in (one or more) registers across
a page. (TO BE CHECKED, pretty sure no settings go across two pages)
The parameters are encoded into the register values IN ORDER so that
general defaults can be set first and then exceptions can be made.

The JSON settings have a two-tier structure:
```json
{
  "Page_Name" : {
    "Parameter1" : val1,
    "Parameter2" : val2
  },
  "Other_page" : {
  }
}
```

The names of the pages and parameters are copied from the documentation
of the ASIC parameters.

The "Page_Name" strings can be regular expressions to match several
different pages. For example, if you wish to apply the same parameter
settings to all channels, you would use the following JSON snippet.
```json
{
  "Channel_*" : {
    "SameForAllChannels" : value
  }
}
```

Each JSON file holding JSON settings can have one of the JSON settings objects 
or multiple in an ordered list. This second option would be helpful
for applying general rules and then exceptions.
```json
[
  {
    "Channel_*" : {
      "SameForAllChannels" : value
    }
  },
  {
    "Channel_42" : {
      "Except42" : value2
    }
  }
]
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

    def __init__(self, register, min_bit, n_bits) :
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
        Key: name of parameter, Val: BitSpc for that parameter
    reference_voltage_lut : dict
        LUT for the Reference Voltage pages
        Key: name of parameter, Val: BitSpc for that parameter
    name_lut : dict
        LUT for all supported pages
        Key: name of page, Val: tuple(<page number>,<page_lut>)
    defaults : dict
        Values for all parameters as specified by the documentation
    """

    num_pages = 300 # 0 -> 299
    num_registers_per_page = 16

    global_analog_lut = {
        'ON_dac_trim' : BitSpec(0,0,1),
        'ON_input_dac' : BitSpec(0,1,1),
        'ON_conv' : BitSpec(0,2,1),
        'ON_pa' : BitSpec(0,3,1),
        'Gain_conv' : BitSpec(0,4,4)
        }
    
    reference_voltage_lut = {
        'Tot_vref' : BitSpec([1,2],[6,0],[2,8]),
        }
    
    # docs give us the page name to numbers
    name_lut = {
        'Global_Analog_0' : (297, global_analog_lut),
        'Global_Analog_1' : (41,  global_analog_lut),
        'Reference_Voltage_0' : (296, reference_voltage_lut),
        'Reference_Voltage_1' : (40, reference_voltage_lut),
        }

    defaults = {
        'Global_Analog_*' : {
            'ON_dac_trim' : 1,
            'ON_input_dac' : 1,
            'ON_conv' : 1,
            'ON_pa' : 1,
            'Gain_conv' : 0b0100
        },
        'Reference_Voltage_*' : {
            'Tot_vref' : 432 #0b0110110000
        },
    }

    def __init__(self, named_settings, prepend_defaults = True) :
        self.compiled_settings = {}

        if prepend_defaults :
            named_settings.insert(0, CompiledSettings.defaults)

        for iteration, settings in enumerate(named_settings) :
            print(f'Staring iteration {iteration}')
            for page_regex, page_params in settings.items() :
                print(f' Compiling pages matching {page_regex}')
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
    import json

    parser = argparse.ArgumentParser(
            description="Compile one or more JSON setting objects into a single CSV settings file.",
            formatter_class = argparse.RawTextHelpFormatter
            )

    class FullHelpAction(argparse.Action):
        def __init__(self, nargs = 0, **kwargs):
            super().__init__(nargs = nargs, **kwargs)

        def __call__(self, parser, args, values, option_string=None):
            print(sys.modules[__name__].__doc__)
            sys.exit(0)
            return FullHelpAction

    parser.add_argument('--full_help', action=FullHelpAction,
            help="Print an extended help message.")
    parser.add_argument('setting_file', type=str, nargs='+', 
            help='One (or more, in order) JSON setting files to compile.')
    parser.add_argument('--output','-o', type=str,
            help='Path to output file to write compiled settings to.')
    parser.add_argument('--no_defaults', action='store_true', 
            help='(optional) Don\'t include defaults from documentation in compilation.')

    arg = parser.parse_args()

    if arg.output is None :
        arg.output = arg.setting_file[0].replace('json','csv')

    settings_in_memory = []
    for file_name in arg.setting_file :
        with open(file_name) as f :
            sim = json.load(f)

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

