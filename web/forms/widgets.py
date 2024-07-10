

from django.forms import RadioSelect

class ColoredRadioSelect(RadioSelect):
    template_name = 'widgets/color_radio/radio.html'
    option_template_name = 'widgets/color_radio/radio_option.html'