"""compile

"Compile" JSON settings for the HGC ROC into their page/register values
written to a CSV.

I'm using JSON insteam of YAML because JSON comes with Python.

Each parameter is given specific bits in (one or more) registers across
a page. (TO BE CHECKED, pretty sure no settings go across two pages)
The parameters are encoded into the register values IN ORDER so that
general defaults can be set first and then exceptions can be made.

The JSON file has a two-tier structure:
  {
    'Page_Name' : {
      'Parameter1' : val1,
      'Parameter2' : val2
    },
    'Other_page' : {
    }
  }

Following the terminology in the ASIC_parameters_HGCROC_for_SiPM document.
"""

class BitSpec :
    """This class holds the bit specification of a parameter.

    It is designed so that the user can more easily copy the specifications
    from the documenation of the HGC ROC v2. 

    Parameters
    ----------
    i_register : int or list[int]
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

    def __init__(self, i_register, min_bit, n_bits) :
        if not isinstance(i_register,list) :
            i_register = [i_register]
        for val in i_register :
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
        if not (len(n_bits) == len(min_bit) == len(i_register)) :
            raise TypeError(f'BitSpec: Length of specifications don\'t match.')

        self.i_register = i_register
        self.min_bit = min_bit
        self.n_bits = n_bits
        self.mask = [((1 << n) - 1) for n in self.n_bits]
        self.clear = [(mask << min_bit) ^ 0b11111111 for mask, min_bit in zip(self.mask,self.min_bit)]

class CompiledSettings :
    """Structure holding the compiled settings

    The __init__ constructor is what does the compilation of the input
    settings into register values across pages.

    Parameters
    ----------
    parameter_settings : list[dict] 
        This input has a very specific format
        Each entry in the list has a two-tiered dictionary.
        The first level gives the name of a page and the second gives the
        name of a setting within that page.

    Exceptions
    ----------
    KeyError : thrown if a page or parameter name is not recognized
    """

    num_pages = 300 # 0 -> 299
    num_registers_per_page = 16
    value_print_type = 'bin' #'dec' or 'hex'

    global_analog_lut = {
        'ON_dac_trim' : BitSpec(0,0,1),
        'ON_input_dac' : BitSpec(0,1,1),
        'ON_conv' : BitSpec(0,2,1),
        'ON_pa' : BitSpec(0,3,1),
        'Gain_conv' : BitSpec(0,4,4)
        }
    
    reference_voltage_lut = {
        'Tot_vref' : BitSpec([1,2],[6,0],[2,8])
        }
    
    # docs give us the page name to numbers
    name_lut = {
        'Global_Analog_0' : (297, global_analog_lut),
        'Global_Analog_1' : (41,  global_analog_lut),
        'Reference_Voltage_0' : (296, reference_voltage_lut)
        }

    def __init__(self, named_settings) :
        self.compiled_settings = {}
        for iteration, settings in enumerate(named_settings) :
            print(f'Staring iteration {iteration}')
            for page_name, page_params in settings.items() :
                print(f'Compiling page {page_name}')
                page_id, name_to_bits = CompiledSettings.name_lut[page_name]
                
                self.init_registers(page_id)
        
                # go through parameters and insert them into their registers
                for param_name, param_val in page_params.items() :
                    print(f'{param_name} set to {param_val}')
                    bit_spec = name_to_bits[param_name]
                    self.compile_param(page_id, param_name, param_val, bit_spec)
    
    def init_registers(self, page_id) :
        if page_id not in self.compiled_settings :
            self.compiled_settings[page_id] = [
                None for i_reg in range(CompiledSettings.num_registers_per_page)]

    def compile_param(self, page_id, name, val, bit_spec) :
        value_curr_min_bit = 0
        for i_spec in range(len(bit_spec.i_register)) :
            # 1. get sub-value from parameter (next n_bits)
            sub_val = ((val >> value_curr_min_bit) & bit_spec.mask[i_spec])
            value_curr_min_bit += bit_spec.n_bits[i_spec]

            # 2. initialize register
            if self.compiled_settings[page_id][bit_spec.i_register[i_spec]] is None :
                # initialize unset register
                self.compiled_settings[page_id][bit_spec.i_register[i_spec]] = 0
            else :
                # clear old setting
                self.compiled_settings[page_id][bit_spec.i_register[i_spec]] &= (
                    bit_spec.clear[i_spec]
                    )
            # 3. put sub-value into register
            self.compiled_settings[page_id][bit_spec.i_register[i_spec]] += (
                (sub_val & bit_spec.mask[i_spec]) << bit_spec.min_bit[i_spec]
                )

    def __str__(self) :
        # print compiled settings
        msg = ''
        for page, registers in self.compiled_settings.items() :
            for i_reg, val in enumerate(registers) :
                if val is not None :
                    msg += f'{page},{i_reg},'
                    if CompiledSettings.value_print_type == 'bin' :
                        msg += f'0b{val:08b}'
                    elif CompiledSettings.value_print_type == 'hex' :
                        msg += f'0x{val:02x}'
                    elif CompiledSettings.value_print_type == 'dec' :
                        msg += f'{val}'
                    msg += '\n'
                    
        return msg

        
if __name__ == '__main__' :
    print(CompiledSettings([{
      'Global_Analog_0' : {
        'ON_pa' : 1,
        'Gain_conv' : 0b0100
       },
      'Reference_Voltage_0' : {
        'Tot_vref' : 0b1100111101
      }},
      {'Global_Analog_0' : {
        'ON_pa' : 0
       }}
      ]))
