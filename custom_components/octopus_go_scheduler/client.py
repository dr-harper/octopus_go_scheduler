"""Client."""
from datetime import datetime, timezone
import aiohttp
import logging
import numpy as np

from .const import INTENSITY
from .utils import get_index, format_datetimes_for_ha, json_to_df

_LOGGER = logging.getLogger(__name__)

class Client:
    """Carbon Intensity API Client"""

    def __init__(self, postcode):
        self.postcode = postcode
        self.headers = {"Accept": "application/json"}
        _LOGGER.debug(str(self))

    def __str__(self):
        return "{ postcode: %s, headers: %s }" % (self.postcode, self.headers)

    async def async_raw_get_data(self, from_time=None):
        if from_time is None:
            from_time = datetime.utcnow()
        request_url = (
            "https://api.carbonintensity.org.uk/regional/intensity/%s/fw48h/postcode/%s"
            % (from_time.strftime("%Y-%m-%dT%H:%MZ"), self.postcode)
        )
        _LOGGER.debug("Request: %s" % request_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_response = await resp.json()
                return json_response

    async def async_get_data(self, from_time=None, target='low'):
        raw_data = await self.async_raw_get_data(from_time)
        return generate_response(raw_data, target)

def generate_response(json_response, target='low'):
    response = {}
    data = json_response["data"]["data"]
    postcode = json_response["data"]["postcode"]

    # loadshifting parameters
    start_time = 1.5
    end_time = 6.5
    run_length = 1
    
    # sanitise input length
    if datetime.strptime(data[0]["to"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc) < datetime.utcnow().replace(tzinfo=timezone.utc):
        data.pop(0)
    if len(data) > 96:
        data = data[0:96]
    if len(data) < 48:
        return {"error": "malformed data"}
    if len(data) % 2 == 1:
        data.pop(-1)

    # calculate stats
    df = json_to_df(json_response)

    # --- optimal time period calculation
    # calculate forward looking average. Device needs at least run_length hours
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=2*run_length)
    df['intensity.forecast'] = df['intensity.forecast'].rolling(window=indexer, min_periods=1).mean()
    
    # filter to time period
    off_peak = df[(df['hour'] >= start_time) & (df['hour'] < (end_time - run_length))]

    # find lowest carbon intensity within the next 24 hours
    optimal_offpeak_24 = off_peak[off_peak['days_ahead'] < 2].sort_values('intensity.forecast').head(1)
    optimal_offpeak_48 = off_peak.sort_values('intensity.forecast').head(1)

    # extract first row
    current = df.iloc[0]
    current_co2 = current['intensity.forecast']
    
    # convert timestamp to string
    optimal_offpeak_24_time = format_datetimes_for_ha(optimal_offpeak_24['from'])
    optimal_offpeak_24_co2 = optimal_offpeak_24['intensity.forecast'].values[0]
    co2_saving_perc_24 = round((current_co2 - optimal_offpeak_24_co2)/current_co2, 2) * 100

    optimal_offpeak_48_time = format_datetimes_for_ha(optimal_offpeak_48['from'])
    optimal_offpeak_48_co2 = optimal_offpeak_48['intensity.forecast'].values[0]
    co2_saving_48 = round((current_co2 - optimal_offpeak_48_co2)/current_co2, 2) * 100

    response = {
        "data": {
            "current_co2": current_co2,
            "current_co2_index": get_index(current_co2),
            "optimal_offpeak_next_24_time": optimal_offpeak_24_time,
            "optimal_offpeak_next_24_co2": optimal_offpeak_24_co2,
            "optimal_offpeak_next_24_co2_saving": co2_saving_perc_24,
            "optimal_offpeak_nxext_48_time": optimal_offpeak_48_time,
            "optimal_offpeak_next_48_co2": optimal_offpeak_48_co2,
            "optimal_offpeak_next_48_co2_saving": co2_saving_48,
        }
    }
    return response

