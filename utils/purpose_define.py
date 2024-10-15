import pandas as pd 

def cat_duration(trip):
    purp_filt = trip.copy()
    dur_u15 = purp_filt.DURATION < 16
    dur_o15 = purp_filt.DURATION > 15
    dur_o60 = purp_filt.DURATION > 59
    dur_o180 = purp_filt.DURATION > 179

    purp_filt.loc[dur_u15, 'Dur'] = 'u15'
    purp_filt.loc[dur_o15, 'Dur'] = 'o15'
    purp_filt.loc[dur_o60, 'Dur'] = 'o60'
    purp_filt.loc[dur_o180, 'Dur'] = 'o180'
    return purp_filt
