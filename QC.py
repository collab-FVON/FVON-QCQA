import pandas as pd
import numpy as np
from datetime import datetime, timezone
# library to check if it's land or not
# from global_land_mask import globe
# library to calculate the speed
import pyproj
import os
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic
import warnings

warnings.filterwarnings('ignore')


class GenericQC(object):
    """
    Generic Quality Control class for basic QC checks on oceanographic data.

    This class performs fundamental quality control tests including date validation,
    location validation, land position checking, and sensor calibration checks.

    Args:
        df (pd.DataFrame): DataFrame containing oceanographic observation data with columns:
            - datetime: Timestamp of observations
            - latitude: Latitude coordinates
            - longitude: Longitude coordinates
            - calibration_date: Sensor calibration date

    Attributes:
        df (pd.DataFrame): The input DataFrame with added QC flag columns
    """
    def __init__(self, df):
        self.df = df
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        self.df['flag'] = 1
        self.impossible_date()
        self.impossible_location()
        self.calibration_date()
        # self.position_on_land()

    # 4. Impossible date test
    # The date of the profile can be no earlier than 01/01/2010 and no later than current date in UTC

    def impossible_date(self):
        """
        Flag data with impossible dates (before 01/01/2010 or after current UTC date).

        Sets flag_date to 4 (bad data) for impossible dates, 1 (pass) otherwise.
        Also updates the main 'flag' column to reflect failures.
        """
        self.df['flag_date'] = 1
        currdate = datetime.now(timezone.utc).replace(tzinfo=None)
        mindate = datetime(2010, 1, 1)
        self.df.loc[((self.df['datetime'] > currdate) | (self.df['datetime'] < mindate)), ['flag_date', 'flag']] = 4

    # 5. Impossible location test
    # Requires the observation latitude and longitude to be sensible

    def impossible_location(self):
        """
        Flag data with impossible geographic coordinates.

        Checks that latitude is within [-90, 90] and longitude within [-180, 180].
        Sets flag_location to 4 (bad data) for out-of-range coordinates, 1 (pass) otherwise.
        """
        self.df['flag_location'] = 1
        latrange = [-90, 90]
        lonrange = [-180, 180]
        self.df.loc[((self.df['latitude'] < latrange[0]) | (self.df['latitude'] > latrange[1]) | (
                self.df['longitude'] < lonrange[0]) | (self.df['longitude'] > lonrange[1])), ['flag_location',
                                                                                              'flag']] = 4

    # 6. Position on land test
    # Tests if the observation longitude and latitude from a profile is located in an ocean, based on ETOPO5.

    def position_on_land(self):
        self.df['flag_land'] = 1

        def on_land_check():
            points = gpd.GeoDataFrame(self.df,
                                      geometry=[Point(xy) for xy in zip(self.df["longitude"], self.df["latitude"])],
                                      crs="EPSG:4326")
            shapefile_path = os.path.dirname(os.path.abspath(__file__)).replace("\\",
                                                                                "/") + '/QC_land/WB_countries_Admin0_10m.shp'
            land = gpd.read_file(shapefile_path)
            land.crs = pyproj.CRS("EPSG:4326")
            results = points.sjoin(land, how="left", predicate="intersects")
            on_land = ~results['index_right'].isna()
            self.df['flag_land'] = np.where(on_land, 4, 1)
            self.df.loc[self.df['flag_land'] == 4, ['flag_land', 'flag']] = 4

        on_land_check()
        # self.df.loc[(globe.is_land(self.df['latitude'], self.df['longitude'])), ['flag_land', 'flag']] = 4

    # 19. Out of calibration

    def calibration_date(self):
        self.df['flag_calibration_date'] = 1
        self.df['calibration_date'] = pd.to_datetime(self.df['calibration_date'])
        try:
            self.df['gap_cal'] = (self.df['datetime'].dt.date - self.df['calibration_date'].dt.date)
            # # Convert the 'gap_cal' to timedelta
            self.df['gap_cal'] = pd.to_timedelta(self.df['gap_cal'])

            # Convert timedelta to days
            self.df['gap_cal'] = self.df['gap_cal'].dt.total_seconds() / 3600 / 24 / 365
            self.df.loc[(self.df['gap_cal'] > 2) & (self.df['sensor_type'] == 'ZEBRATECH'), 'flag_calibration_date'] = 3
            self.df.loc[self.df['gap_cal'].isna(), 'flag_calibration_date'] = 2

            self.df = self.df.drop(columns=['gap_cal'])
        except:
            if 'gap_cal' in self.df.columns:
                self.df = self.df.drop(columns=['gap_cal'])
            self.df['flag_calibration_date'] = 2


class QC(object):
    """
    Quality Control class for comprehensive oceanographic data validation.

    Performs advanced QC tests for CTD/TD data from fishing vessel platforms including
    vessel region validation, gear type checks, speed tests, range checks, spike detection,
    stuck values, rate of change, climatology, drift, mud contamination, response time,
    and cold surface effects.

    Args:
        df (pd.DataFrame): DataFrame containing profile data
        gear_type (str): Type of fishing gear ('FIXED', 'MOBILE', or 'OTHER')
        zone (str): Geographic zone name (e.g., 'Atlantic', 'North Sea', 'Mediterranean Sea')
        sensor_type (str): Sensor model ('NKE', 'ZEBRATECH', 'MOANA', 'LOWELL', 'MARPORT', 'HOBO', 'VEMCO')
        time_col (str): Name of datetime column (default: 'datetime')
        pressure_col (str): Name of pressure column (default: 'pressure')
        temperature_col (str): Name of temperature column (default: 'temperature')
        salinity_col (str): Name of salinity column (default: 'salinity')

    Attributes:
        df (pd.DataFrame): The input DataFrame with multiple QC flag columns added
        gear (str): Normalized gear type
        zone (str): Geographic zone
        sensor_type (str): Sensor model
    """
    def __init__(self, df, gear_type, zone, sensor_type, time_col='datetime', pressure_col='pressure',
                 temperature_col='temperature', salinity_col='salinity'):
        self.df = df
        self.gear = gear_type.upper()
        self.zone = zone
        self.sensor_type = sensor_type
        self.time_col = time_col
        self.pressure_col = pressure_col
        self.temperature_col = temperature_col
        self.salinity_col = salinity_col
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        self.df['flag'] = 1
        self.regions()
        self.gear_type()
        self.impossible_speed()
        self.global_range()
        self.spike()
        self.rollover()
        self.stuck()
        self.rate_of_change()
        # self.timing_gap()
        self.climatology(zone)
        self.drift()
        self.mud()
        self.response_time()
        self.cold_surface()

    # 1. Platform identification, from line 93 load_cloud.py

    # 2. Vessel ID control
    # d represent a dictionary where the keys are the vessels and the values represent the pertinent region
    def regions(self):
        self.df['flag_vessel_region'] = 1
        region = ['Unknown']
        max_lat = self.df['latitude'].max()
        min_lat = self.df['latitude'].min()
        max_lon = self.df['longitude'].max()
        min_lon = self.df['longitude'].min()

        if -60 <= max_lon <= -15 and 55 <= max_lat <= 90 and -60 <= min_lon <= -15 and 55 <= min_lat <= 90:
            region += ['Greenland']
        if -15 <= max_lon <= 30 and 45 <= max_lat <= 60 and -15 <= min_lon <= 30 and 45 <= min_lat:
            region += ['North Sea']
        if -75 <= max_lon <= 30 and 0 <= max_lat <= 90 and -75 <= min_lon <= 30 and 0 <= min_lat <= 90:
            region += ['Atlantic']
        if (160 <= max_lon <= 180 or 0 <= max_lon <= 5) and -50 <= max_lat <= -30 and (
                160 <= min_lon <= 180 or 0 <= min_lon <= 5) and -50 <= min_lat <= -30:
            region += ['New Zealand']
        if 30 <= max_lon <= 45 and 10 <= max_lat <= 45 and 30 <= min_lon <= 45 and 10 <= min_lat <= 45:
            region += ['Red Sea']
        if -5 <= max_lon <= 40 and 25 <= max_lat <= 45 and -5 <= min_lon <= 40 and 25 <= min_lat <= 45:
            region += ['Mediterranean Sea']
        if -180 <= max_lon <= -125 and 45 <= max_lat <= 90 and -180 <= min_lon <= -125 and 45 <= min_lat <= 90:
            region += ['Alaska', 'Canada']
        if -180 <= max_lon <= -70 and 0 <= max_lat <= 60 and -180 <= min_lon <= -70 and 0 <= min_lat <= 60:
            region += ['Pacific']
        if -100 <= max_lon <= -70 and 15 <= max_lat <= 35 and -100 <= min_lon <= -70 and 15 <= min_lat <= 35:
            region += ['Gulf of Mexico']
        # elif -180 <= max_lon <= -125 and 45 <= max_lat <= 90 and -180 <= min_lon <= -125 and 45 <= min_lat <= 90:
        #     region = ['South West Shelves']
        # elif -180 <= max_lon <= -125 and 45 <= max_lat <= 90 and -180 <= min_lon <= -125 and 45 <= min_lat <= 90:
        #     region = ['Artic Sea']

        if self.zone not in region and self.zone != 'All':
            self.df['flag_vessel_region'] = 3
            self.df['flag'] = 3

    # 3. Gear type control
    # Still some thoughts need to be applied
    def gear_type(self):
        self.df['flag_gear_type'] = 1
        if self.gear == 'OTHER': return
        if 'SEINE' in self.df['vessel_gear_type'].max() or 'HANDLINE' in self.df['vessel_gear_type'].max():
            start_time = self.df['datetime'].min()
            end_time = self.df['datetime'].max()
            duration_hr = (end_time - start_time).total_seconds() / 3600.0

            try:
                coords_1 = self.df['raw_lat'].iloc[0], self.df['raw_lon'].iloc[0]
                coords_2 = self.df['raw_lat'].iloc[-1], self.df['raw_lon'].iloc[-1]
                distance_km = geodesic(coords_1, coords_2).km

                if duration_hr == 0 or distance_km / duration_hr > 10:
                    self.df[['flag_gear_type', 'flag']] = 3
            except:
                return
            return

        # Get the start and end coordinates
        raw_lat_start = self.df['raw_lat'].iloc[0]
        raw_lat_end = self.df['raw_lat'].iloc[-1]

        if len(self.df[self.df['latitude'].notnull()]) == 0:
            self.df[['flag_gear_type', 'flag']] = 4
            return

        if pd.isna(raw_lat_start) and pd.isna(raw_lat_end):
            self.df[['flag_gear_type', 'flag']] = 4
            return

        elif pd.isna(raw_lat_start) and not pd.isna(raw_lat_end) and self.gear == 'MOBILE':
            self.df[['flag_gear_type', 'flag']] = 3
            return

        elif not pd.isna(raw_lat_start) and pd.isna(raw_lat_end) and self.gear == 'MOBILE':
            self.df[['flag_gear_type', 'flag']] = 3
            return

        coords_1 = self.df['raw_lat'].iloc[0], self.df['raw_lon'].iloc[0]
        coords_2 = self.df['raw_lat'].iloc[-1], self.df['raw_lon'].iloc[-1]

        d = 0 if pd.isna(coords_1[0]) or pd.isna(coords_1[1]) or pd.isna(coords_2[0]) or pd.isna(
            coords_2[1]) else geodesic(coords_1, coords_2).m

        gt = 1 if d > 200 else 0

        if (gt == 1 and self.gear == 'FIXED') or (gt == 0 and self.gear == 'MOBILE'):
            track_coords = self.df[['raw_lat', 'raw_lon']].dropna().values
            total_distance = 0
            for i in range(1, len(track_coords)):
                coord1 = tuple(track_coords[i - 1])
                coord2 = tuple(track_coords[i])
                total_distance += geodesic(coord1, coord2).m

            start_time = self.df['datetime'].min()
            end_time = self.df['datetime'].max()
            duration_hr = (end_time - start_time).total_seconds() / 3600.0

            if duration_hr == 0:
                self.df[['flag_gear_type', 'flag']] = 3
                return

            if self.gear == 'MOBILE':
                if d < 200 and total_distance / 1000 / duration_hr > 10:
                    self.df[['flag_gear_type', 'flag']] = 3
                    return
            else:
                if duration_hr > 24 and d > 500:
                    self.df[['flag_gear_type', 'flag']] = 3
                elif duration_hr <= 24:
                    self.df[['flag_gear_type', 'flag']] = 3

    # 7. Impossible speed test
    # Drift speeds calculated given the positions and times of the floats, can't exceed 4.12m/s

    def impossible_speed(self):
        self.df['flag_speed'] = 1

        if self.gear == 'FIXED':
            return

        self.df['is_duplicated'] = self.df.duplicated(subset=['raw_lat', 'raw_lon'], keep='first')
        self.df.loc[self.df['is_duplicated'], ['raw_lat', 'raw_lon']] = np.nan
        self.df.drop(columns=['is_duplicated'], inplace=True)

        valid_indices = self.df.dropna(subset=['raw_lat', 'raw_lon']).index

        self.df['distance'] = np.nan  # Initialize column
        self.df['time_diff'] = np.nan
        for i in range(len(valid_indices) - 1):
            idx1, idx2 = valid_indices[i], valid_indices[i + 1]

            if pd.isna(self.df.loc[idx1, 'latitude']) or pd.isna(self.df.loc[idx2, 'latitude']): continue
            self.df.loc[idx2, 'distance'] = geodesic(
                (self.df.loc[idx1, 'latitude'], self.df.loc[idx1, 'longitude']),
                (self.df.loc[idx2, 'latitude'], self.df.loc[idx2, 'longitude'])
            ).meters

            self.df.loc[idx2, 'time_diff'] = (
                        self.df.loc[idx2, 'datetime'] - self.df.loc[idx1, 'datetime']).total_seconds()

        self.df['speed'] = self.df['distance'] / self.df['time_diff']
        self.df['speed'] = self.df['speed'].bfill()
        self.df['raw_lat'] = self.df['raw_lat'].bfill()
        self.df['raw_lon'] = self.df['raw_lon'].bfill()

        self.df.reset_index(drop=True, inplace=True)
        if len(self.df) != 0:
            self.df.loc[(self.df['speed'] > 4.12), ['flag_speed', 'flag']] = 4
            # self.df = self.df[self.df['flag_speed'] == 1]
            self.df = self.df.drop(columns=['speed', 'time_diff', 'distance'])

    # 8. Global range test
    # Gross filter on the observed values of pressure, temperature and salinity

    def global_range(self):
        max_press, min_temp, max_temp, min_sal, max_sal = None, None, None, None, None
        if self.sensor_type == 'NKE':
            min_temp, max_temp = -2, 35
            max_press = 1000 * 1.1
            if self.salinity_col in self.df.columns:
                min_sal, max_sal = 0.2, 4.2
                max_press = 300 * 1.1
        elif self.sensor_type in ['MOANA', 'ZEBRATECH']:
            min_temp, max_temp = -2, 35
            max_press = 1000 * 1.1
        elif self.sensor_type == 'LOWELL':
            min_temp, max_temp = -5, 50
            max_press = 1000 * 1.5

        self.df['flag_global_range'] = 1
        self.df.loc[
            (self.df[self.pressure_col] >= -5) & (self.df[self.pressure_col] < 0), ['flag_global_range', 'flag']] = 3
        self.df.loc[self.df[self.pressure_col] > max_press, ['flag_global_range', 'flag']] = 3
        self.df.loc[(self.df[self.pressure_col] < -5), ['flag_global_range', 'flag']] = 4
        self.df.loc[((self.df[self.temperature_col] < min_temp) | (self.df[self.temperature_col] > max_temp)), [
            'flag_global_range', 'flag']] = 4
        if self.salinity_col in self.df.columns:
            self.df.loc[
                ((self.df[self.salinity_col] < min_sal) | (self.df[self.salinity_col] > max_sal)), ['flag_global_range',
                                                                                                    'flag']] = 4

    # 9. Spike test
    def spike(self):
        self.df['flag_temp_spike'] = 1
        self.df['prev_temp'] = self.df[self.temperature_col].shift(1)
        self.df['post_temp'] = self.df[self.temperature_col].shift(-1)
        self.df['val'] = abs(self.df[self.temperature_col] - (self.df['post_temp'] + self.df['prev_temp']) / 2) - abs(
            (self.df['post_temp'] - self.df['prev_temp']) / 2)
        self.df.loc[(((self.df[self.pressure_col] < 500) & (self.df['val'] > 6)) | (
                (self.df[self.pressure_col] >= 500) & (self.df['val'] > 2))), ['flag_temp_spike', 'flag']] = 4
        self.df = self.df.drop(columns=['prev_temp', 'post_temp', 'val'])

        if self.salinity_col in self.df.columns:
            self.df['flag_sal_spike'] = 1
            self.df['prev_sal'] = self.df[self.salinity_col].shift(1)
            self.df['post_sal'] = self.df[self.salinity_col].shift(-1)
            self.df['val'] = abs(self.df[self.salinity_col] - (self.df['post_sal'] + self.df['prev_sal']) / 2) - abs(
                (self.df['post_sal'] - self.df['prev_sal']) / 2)
            self.df.loc[(((self.df[self.pressure_col] < 500) & (self.df['val'] > 0.09)) | (
                    (self.df[self.pressure_col] >= 500) & (self.df['val'] > 0.03))), ['flag_sal_spike', 'flag']] = 4
            self.df = self.df.drop(columns=['prev_sal', 'post_sal', 'val'])

    # 10. Digit rollover test adapted to:
    # Bottom Spike test
    # This is a special version of the spike test, which
    # compares the measurements at the end of the
    # profile to the adjacent measurement. temperature
    # at the bottom should not differ from the adjacent
    # measurement by more than 1.0°C

    def rollover(self):
        self.df['flag_rollover'] = 1
        self.df['prev_temp'] = self.df[self.temperature_col].shift(1)
        self.df.loc[(abs(self.df[self.temperature_col] - self.df['prev_temp']) > 1.0) & (
                    self.df['segment_type'] == 'Fishing'), ['flag_rollover', 'flag']] = 3
        self.df = self.df.drop(columns=['prev_temp'])

    # 11. Stuck value test
    # Looks if there are temperature or salinity measurements identical
    ## temperature

    def stuck(self):
        self.df['flag_temp_stuck'] = 1
        self.df['prev_temp_1'] = self.df[self.temperature_col].shift(1)
        self.df['prev_temp_2'] = self.df[self.temperature_col].shift(2)
        self.df['post_temp_1'] = self.df[self.temperature_col].shift(-1)
        self.df['post_temp_2'] = self.df[self.temperature_col].shift(-2)
        self.df.loc[((self.df['prev_temp_1'] == self.df[self.temperature_col]) & (
                self.df['post_temp_1'] == self.df[self.temperature_col]) & (self.df['segment_type'] != 'Fishing')), [
            'flag_temp_stuck',
            'flag']] = 3
        self.df.loc[((self.df['prev_temp_1'] == self.df[self.temperature_col]) & (
                self.df['post_temp_1'] == self.df[self.temperature_col]) & (
                             self.df['prev_temp_2'] == self.df[self.temperature_col]) & (
                             self.df['post_temp_2'] == self.df[self.temperature_col]) & (
                                 self.df['segment_type'] != 'Fishing')), [
            'flag_temp_stuck', 'flag']] = 4
        self.df = self.df.drop(columns=['prev_temp_1', 'post_temp_1', 'prev_temp_2', 'post_temp_2'])

        if self.salinity_col in self.df.columns:
            self.df['flag_sal_stuck'] = 1
            self.df['prev_sal_1'] = self.df[self.salinity_col].shift(1)
            self.df['prev_sal_2'] = self.df[self.salinity_col].shift(2)
            self.df['post_sal_1'] = self.df[self.salinity_col].shift(-1)
            self.df['post_sal_2'] = self.df[self.salinity_col].shift(-2)
            self.df.loc[
                ((self.df['prev_sal_1'] == self.df[self.salinity_col]) & (
                            self.df['post_sal_1'] == self.df[self.salinity_col]) & (
                         self.df['segment_type'] != 'Fishing')), ['flag_sal_stuck', 'flag']] = 3
            self.df.loc[((self.df['prev_sal_1'] == self.df[self.salinity_col]) & (
                    self.df['post_sal_1'] == self.df[self.salinity_col]) & (
                                     self.df['prev_sal_2'] == self.df[self.salinity_col]) & (
                                 self.df['post_sal_2'] == self.df[self.salinity_col]) & (
                                 self.df['segment_type'] != 'Fishing')), ['flag_sal_stuck', 'flag']] = 4
            self.df = self.df.drop(columns=['prev_sal_1', 'post_sal_1', 'prev_sal_2', 'post_sal_2'])

        try:
            self.df = self.df.drop(columns=['vel', 'vel_smooth', 'delta_time'])
        except:
            pass

    # 12. Rate of change test
    # Excessive rise/fall test.
    # This test inspects the time series for a time rate of change that exceeds a threshold value identified by the
    # operator. T, SP, C, P values can change substantially over short periods in some locations, hindering the value of
    # this test. A balance must be found between a threshold set too low, which triggers too many false alarms, and one
    # set too high, making the test ineffective. Determining the excessive rate of change is left to the local operator.
    # The following shows two different examples of ways to select the thresholds provided by QARTOD VI participants.
    # Implementation of this test can be challenging. Upon failure, it is unknown which of the points is bad. Further, upon
    # failing a data point, it remains to be determined how the next iteration can be handled.
    # This test should be applied with different SDs for Up & Down and Bottom.
    # No flag fail (4) for this test, only suspect marking

    def rate_of_change(self):
        self.df['flag_RoC'] = 1

        sd_temp_down = self.df[self.df['segment_type'] == 'Profiling Down'][self.temperature_col].std()
        sd_temp_bottom = self.df[self.df['segment_type'] == 'Fishing'][self.temperature_col].std()
        sd_temp_up = self.df[self.df['segment_type'] == 'Profiling Up'][self.temperature_col].std()

        n_dev = 3

        self.df['prev_temp'] = self.df[self.temperature_col].shift(1)

        self.df.loc[(abs(self.df[self.temperature_col] - self.df['prev_temp']) > (n_dev * sd_temp_down)) & (
                    self.df['segment_type'] == 'Profiling Down'), ['flag_RoC', 'flag']] = 3
        self.df.loc[(abs(self.df[self.temperature_col] - self.df['prev_temp']) > (n_dev * sd_temp_bottom)) & (
                    self.df['segment_type'] == 'Fishing'), ['flag_RoC', 'flag']] = 3
        self.df.loc[(abs(self.df[self.temperature_col] - self.df['prev_temp']) > (n_dev * sd_temp_up)) & (
                    self.df['segment_type'] == 'Profiling Up'), ['flag_RoC', 'flag']] = 3

        if self.salinity_col in self.df.columns:
            sd_sal_down = self.df[self.df['segment_type'] == 'Profiling Down'][self.salinity_col].std()
            sd_sal_bottom = self.df[self.df['segment_type'] == 'Fishing'][self.salinity_col].std()
            sd_sal_up = self.df[self.df['segment_type'] == 'Profiling Up'][self.salinity_col].std()

            self.df['prev_sal'] = self.df[self.salinity_col].shift(1)

            self.df.loc[(abs(self.df[self.salinity_col] - self.df['prev_sal']) > (n_dev * sd_sal_down)) & (
                        self.df['segment_type'] == 'Profiling Down'), ['flag_RoC', 'flag']] = 3
            self.df.loc[(abs(self.df[self.salinity_col] - self.df['prev_sal']) > (n_dev * sd_sal_bottom)) & (
                        self.df['segment_type'] == 'Fishing'), ['flag_RoC', 'flag']] = 3
            self.df.loc[(abs(self.df[self.salinity_col] - self.df['prev_sal']) > (n_dev * sd_sal_up)) & (
                        self.df['segment_type'] == 'Profiling Up'), ['flag_RoC', 'flag']] = 3

            self.df = self.df.drop(columns=['prev_sal'])

        self.df = self.df.drop(columns=['prev_temp'])

    # 13. Timing/gap test
    # Check for the arrival of data: Test determines that the most recent data point has been measured and received within the expected time
    # window (TIM_INC) and has the correct time stamp (TIM_STMP).

    def timing_gap(self):
        self.df['flag_timing_gap'] = 1
        currdate = datetime.now(timezone.utc).replace(tzinfo=None)
        tim_inc = 24  # hours
        time_gap = currdate - self.df['datetime'].iloc[-1]
        if time_gap.total_seconds() / 3600 > tim_inc:
            self.df['flag_timing_gap'] = 3
            self.df['flag'] = 3

    # 14. Climatology test
    # Test that data point falls within seasonal expectations.
    # This test is a variation on the gross range check, where the thresholds T_Season_MAX and T_Season_MIN are
    # adjusted monthly, seasonally, or at some other operator-selected time period (TIM_TST). Expertise of the operator
    # is required to determine reasonable seasonal averages. Longer time series permit more refined identification of
    # appropriate thresholds. The ranges should also vary with water depth, if the measurements are taken at sites that
    # cover significant vertical extent and if climatological ranges are meaningfully different at different depths (e.g.,
    # narrower ranges at greater depth).
    # Because of the dynamic nature of T and S in some
    # locations, no fail flag is identified for this test.
    # Set limits for all areas, preferably also changing according to season.
    # In the mean time just take min and max of temp and sal of all measurements from our vessels in DB.

    def climatology(self, zone):
        d = {'Red Sea': [(21.7, 40), (2, 41)], 'Mediterranean Sea': [(10, 40), (2, 40)],
             'North Western Shelves': [(-2, 24), (0, 37)], 'South West Shelves': [(-2, 30), (0, 38)],
             'Artic Sea': [(-1.92, 25), (2, 40)], 'Atlantic': [(2, 40), (2, 38)], 'North Sea': [(2, 40), (2, 38)],
             'Alaska': [(-1.92, 25), (0, 40)], 'Pacific': [(2, 40), (2, 38)], 'Gulf of Mexico': [(2, 40), (2, 38)],
             'Canada': [(-1.92, 25), (0, 40)], 'All': [(-1.92, 35), (2, 41)]}

        self.df['flag_clima'] = 1
        self.df.loc[((self.df[self.temperature_col] < d[zone][0][0]) | (
                    self.df[self.temperature_col] > d[zone][0][1])), 'flag_clima'] = 3

        if self.salinity_col in self.df.columns:
            self.df.loc[((self.df[self.salinity_col] < d[zone][1][0]) | (
                        self.df[self.salinity_col] > d[zone][1][1])), 'flag_clima'] = 3

    # 15. Drift test
    # Evaluates whether parameters show substantial variations when the sensor is near the sea floor.
    def drift(self):
        self.df['flag_drift'] = 1

        df_bottom = self.df[self.df['segment_type'] == 'Fishing'].reset_index(drop=True)
        if len(df_bottom) != 0:
            temp1 = df_bottom[self.temperature_col].iloc[0]
            temp2 = df_bottom[self.temperature_col].iloc[-1]
            if ((df_bottom[self.time_col].max() - df_bottom[self.time_col].min()).total_seconds() / 3600) < 24:
                if abs(temp1 - temp2) > 3:
                    self.df.loc[:, ['flag_drift', 'flag']] = 3
                if self.salinity_col in self.df.columns:
                    sal1 = df_bottom[self.salinity_col].iloc[0]
                    sal2 = df_bottom[self.salinity_col].iloc[-1]
                    if abs(sal1 - sal2) > 8:
                        self.df.loc[:, ['flag_drift', 'flag']] = 3

    # 16. Mud test
    # Identifies instances where the temperature sensor remains constant during the profiling up phase, potentially due to mud or other particles obstructing the sensor.
    def mud(self):
        self.df['flag_mud'] = 1

        self.df['TEMP_diff'] = self.df[self.temperature_col] - self.df[self.temperature_col].shift(1)

        df2 = self.df[self.df['segment_type'] == 'Profiling Down']
        df1 = self.df[self.df['segment_type'] == 'Profiling Up']

        # if self.df[self.pressure_col].max() < 100:
        #     self.df = self.df.drop(columns=['TEMP_diff'])
        #     return

        df1n = df1[df1[self.pressure_col] > (df1[self.pressure_col].max() / 2)]
        df2n = df2[df2[self.pressure_col] > (df2[self.pressure_col].max() / 2)]

        df1n.loc[:, 'rolled_temp'] = df1n['TEMP_diff'].rolling(10, center=True, min_periods=1).mean()
        df2n.loc[:, 'rolled_temp'] = df2n['TEMP_diff'].rolling(10, center=True, min_periods=1).mean()

        if len(df1n[abs(df1n['rolled_temp']) < 0.005]):
            if len(df2n[abs(df2n['rolled_temp']) < 0.005]) < 4 and len(df1n[abs(df1n['rolled_temp']) < 0.005]) > 10:
                if len(df1n[abs(df1n['rolled_temp']) < 0.005]) / len(df1n) > 0.9:
                    self.df.loc[self.df['segment_type'] == 'Profiling Up', 'flag_mud'] = 3
                    return

                df1_flagged = df1n[abs(df1n['rolled_temp']) < 0.005]
                df1_no_flag = df1[df1.index > df1_flagged.index[-1] + 1]
                df2_comp = df2[df2[self.pressure_col] < df1_no_flag[self.pressure_col].max()]

                inter_point = 0
                for (idx_down, row_down), (idx_up, row_up) in zip(df2_comp[::-1].iterrows(), df1_no_flag.iterrows()):
                    if row_down[self.temperature_col] <= row_up[self.temperature_col]:
                        inter_point = idx_up
                        break

                self.df.loc[
                    (self.df.index < inter_point) & (self.df.index >= df1.index.min()), ['flag_mud', 'flag']] = 3

        self.df = self.df.drop(columns=['TEMP_diff'])

    # 17. Response time test
    # Checks sensor response time in the profiling down and up
    def response_time(self):
        self.df['flag_response_time'] = 1

        # Calculate speed as absolute rate of pressure change over time
        self.df['speed'] = abs((self.df[self.pressure_col] - self.df[self.pressure_col].shift(1)) /
                               (self.df[self.time_col] - self.df[self.time_col].shift(1)).dt.total_seconds())
        self.df['speed'] = self.df['speed'].fillna(0)

        # Calculate mean speed for Profiling Down segment where pressure < 10
        down = self.df[self.df['segment_type'] == 'Profiling Down']
        up = self.df[self.df['segment_type'] == 'Profiling Up']

        # Assign flags based on response time threshold
        self.df.loc[down[down['speed'] > 2].index, ['flag_response_time', 'flag']] = 4
        self.df.loc[down[(down['speed'] > 1) & (down['speed'] <= 2)].index, ['flag_response_time', 'flag']] = 3
        self.df.loc[up[up['speed'] > 2].index, ['flag_response_time', 'flag']] = 4
        self.df.loc[up[(up['speed'] > 1) & (up['speed'] <= 2)].index, ['flag_response_time', 'flag']] = 3

        self.df = self.df.drop(columns=['speed'])

    # . Cold surface
    # Checks sensor temperature response when there is a bit of ice clogging the thermistor region

    def cold_surface(self):
        self.df['flag_cold_surface'] = 1

        self.df['diff_temp'] = self.df['temperature'] - self.df['temperature'].shift(1)
        self.df['diff_temp'] = self.df['diff_temp'].shift(-1)

        self.df.loc[(self.df['segment_type'] == 'Profiling Down') & (self.df['diff_temp'] > 0.5) & (
                    self.df['pressure'] < 10), 'flag_cold_surface'] = 3
        last_3_index = self.df[self.df['flag_cold_surface'] == 3].index.max()

        if last_3_index is not None:
            self.df.loc[self.df.index <= last_3_index + 1, 'flag_cold_surface'] = 3

        self.df = self.df.drop(columns=['diff_temp'])
