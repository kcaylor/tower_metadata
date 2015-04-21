from metadata import Metadata
from __init__ import *


def find_dates(input_dir, datas):
    meta_list = []
    meta = None
    start = '2010-01-01'
    end = dt.datetime.utcnow()
    rng = pd.date_range(start, end, freq='D')
    for date in rng:
        y = date.year
        m = date.month
        d = date.dayofyear
        f = 'raw_MpalaTower_%i_%03d.nc' % (y, d)
        if any(f in os.listdir(join(input_dir, data)) for data in datas):
            meta = Metadata(
                    year=y,
                    month=m,
                    doy=d,
                    date=date
                    )
        if meta is not None:
            meta_list.append(meta)
            meta = None
    return meta_list