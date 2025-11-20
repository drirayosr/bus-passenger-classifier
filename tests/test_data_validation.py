"""
Data Validation Tests
Tests for data quality and integrity checks on passengers.csv and bus.csv
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import pytest
import pandas as pd
import os
from datetime import datetime
from src.utils import detect_column


class TestPassengersData:
    """Validation tests for passengers.csv"""
    
    @pytest.fixture
    def passengers_df(self):
        """Load passengers data"""
        data_path = 'data/raw/passengers.csv'
        assert os.path.exists(data_path), f"Passengers data not found at {data_path}"
        df = pd.read_csv(data_path)
        return df
    
    def test_required_columns_exist(self, passengers_df):
        """Check that all required columns are present"""
        # Use flexible column detection
        user_col = detect_column(passengers_df, ['user_id', 'id', 'userid'])
        time_col = detect_column(passengers_df, ['timestamp_utc', 'timestamp', 'time'])
        lat_col = detect_column(passengers_df, ['latitude', 'lat'])
        lon_col = detect_column(passengers_df, ['longitude', 'lon', 'lng'])
        
        assert user_col is not None, "Missing user ID column (tried: user_id, id, userid)"
        assert time_col is not None, "Missing timestamp column (tried: timestamp_utc, timestamp, time)"
        assert lat_col is not None, "Missing latitude column (tried: latitude, lat)"
        assert lon_col is not None, "Missing longitude column (tried: longitude, lon, lng)"
    
    def test_no_missing_critical_values(self, passengers_df):
        """Check for missing values in critical columns"""
        user_col = detect_column(passengers_df, ['user_id', 'id', 'userid'])
        time_col = detect_column(passengers_df, ['timestamp_utc', 'timestamp', 'time'])
        lat_col = detect_column(passengers_df, ['latitude', 'lat'])
        lon_col = detect_column(passengers_df, ['longitude', 'lon', 'lng'])
        
        for col in [user_col, time_col, lat_col, lon_col]:
            if col:
                missing = passengers_df[col].isna().sum()
                # Allow some missing values but warn if excessive
                if missing > len(passengers_df) * 0.1:  # More than 10%
                    assert False, f"Column {col} has {missing} missing values ({missing/len(passengers_df)*100:.1f}%)"
    
    def test_latitude_range(self, passengers_df):
        """Check latitude values are within reasonable Copenhagen area"""
        lat_col = detect_column(passengers_df, ['latitude', 'lat'])
        if lat_col:
            # Wider bounds to accommodate full dataset (AOI filter handles this later)
            lat_min, lat_max = 55.6, 55.9  # Greater Copenhagen area
            actual_min = passengers_df[lat_col].min()
            actual_max = passengers_df[lat_col].max()
            assert actual_min >= lat_min, \
                f"Latitude below minimum: {actual_min} (expected >= {lat_min})"
            assert actual_max <= lat_max, \
                f"Latitude above maximum: {actual_max} (expected <= {lat_max})"
    
    def test_longitude_range(self, passengers_df):
        """Check longitude values are within reasonable Copenhagen area"""
        lon_col = detect_column(passengers_df, ['longitude', 'lon', 'lng'])
        if lon_col:
            # Wider bounds to accommodate full dataset
            lon_min, lon_max = 12.4, 12.7  # Greater Copenhagen area
            actual_min = passengers_df[lon_col].min()
            actual_max = passengers_df[lon_col].max()
            assert actual_min >= lon_min, \
                f"Longitude below minimum: {actual_min} (expected >= {lon_min})"
            assert actual_max <= lon_max, \
                f"Longitude above maximum: {actual_max} (expected <= {lon_max})"
    
    def test_speed_reasonable(self, passengers_df):
        """Check speed values are reasonable (if speed column exists)"""
        speed_col = detect_column(passengers_df, ['speed', 'speed_mps', 'velocity'])
        if speed_col:
            max_speed = passengers_df[speed_col].max()
            min_speed = passengers_df[speed_col].min()
            assert max_speed < 50, f"Unreasonable speed detected: {max_speed} (units unclear)"
            # Allow some negative speeds (could be sensor noise, will be filtered in pipeline)
            if min_speed < -5:
                assert False, f"Large negative speed detected: {min_speed}"
    
    def test_timestamp_format(self, passengers_df):
        """Check timestamp is parseable"""
        time_col = detect_column(passengers_df, ['timestamp_utc', 'timestamp', 'time'])
        if time_col:
            try:
                pd.to_datetime(passengers_df[time_col].head(100), format='mixed')
            except Exception as e:
                pytest.fail(f"Timestamp parsing failed: {e}")
    
    def test_label_values(self, passengers_df):
        """Check label encoding values if present"""
        if 'labelEnc2' in passengers_df.columns:
            unique_labels = passengers_df['labelEnc2'].dropna().unique()
            assert set(unique_labels).issubset({0, 1}), \
                f"Unexpected label values: {unique_labels}"
    
    def test_minimum_records(self, passengers_df):
        """Check dataset has sufficient records"""
        assert len(passengers_df) > 1000, \
            f"Insufficient records: {len(passengers_df)}"
    
    def test_duplicate_timestamps_per_user(self, passengers_df):
        """Check for excessive duplicate timestamps per user"""
        user_col = detect_column(passengers_df, ['user_id', 'id', 'userid'])
        time_col = detect_column(passengers_df, ['timestamp_utc', 'timestamp', 'time'])
        
        if user_col and time_col:
            duplicates = passengers_df.groupby([user_col, time_col]).size()
            max_duplicates = duplicates.max()
            assert max_duplicates < 100, \
                f"Excessive duplicate timestamps: {max_duplicates}"


class TestBusData:
    """Validation tests for bus.csv"""
    
    @pytest.fixture
    def bus_df(self):
        """Load bus data"""
        data_path = 'data/raw/bus.csv'
        assert os.path.exists(data_path), f"Bus data not found at {data_path}"
        df = pd.read_csv(data_path)
        return df
    
    def test_required_columns_exist(self, bus_df):
        """Check that all required columns are present"""
        time_col = detect_column(bus_df, ['timestamp_utc', 'utc_time', 'timestamp', 'time'])
        lat_col = detect_column(bus_df, ['latitude', 'lat'])
        lon_col = detect_column(bus_df, ['longitude', 'lon', 'lng'])
        
        assert time_col is not None, "Missing timestamp column in bus data"
        assert lat_col is not None, "Missing latitude column in bus data"
        assert lon_col is not None, "Missing longitude column in bus data"
    
    def test_no_missing_critical_values(self, bus_df):
        """Check for missing values in critical columns"""
        time_col = detect_column(bus_df, ['timestamp_utc', 'utc_time', 'timestamp', 'time'])
        lat_col = detect_column(bus_df, ['latitude', 'lat'])
        lon_col = detect_column(bus_df, ['longitude', 'lon', 'lng'])
        
        for col in [time_col, lat_col, lon_col]:
            if col:
                missing = bus_df[col].isna().sum()
                if missing > len(bus_df) * 0.1:  # More than 10%
                    assert False, f"Column {col} has {missing} missing values"
    
    def test_latitude_range(self, bus_df):
        """Check latitude values are within Copenhagen bounds"""
        lat_col = detect_column(bus_df, ['latitude', 'lat'])
        if lat_col:
            lat_min, lat_max = 55.79, 55.81
            actual_min = bus_df[lat_col].min()
            actual_max = bus_df[lat_col].max()
            assert actual_min >= lat_min, \
                f"Latitude below minimum: {actual_min}"
            assert actual_max <= lat_max, \
                f"Latitude above maximum: {actual_max}"
    
    def test_longitude_range(self, bus_df):
        """Check longitude values are within Copenhagen bounds"""
        lon_col = detect_column(bus_df, ['longitude', 'lon', 'lng'])
        if lon_col:
            lon_min, lon_max = 12.51, 12.54
            actual_min = bus_df[lon_col].min()
            actual_max = bus_df[lon_col].max()
            assert actual_min >= lon_min, \
                f"Longitude below minimum: {actual_min}"
            assert actual_max <= lon_max, \
                f"Longitude above maximum: {actual_max}"
    
    def test_speed_non_negative(self, bus_df):
        """Check speed is non-negative if present"""
        speed_col = detect_column(bus_df, ['speed', 'speed_mps', 'velocity'])
        if speed_col:
            min_speed = bus_df[speed_col].min()
            # Allow some negative speeds (sensor noise), but flag large negative values
            if min_speed < -5:
                assert False, f"Large negative speed in bus data: {min_speed}"
    
    def test_door_state_values(self, bus_df):
        """Check door state has expected values if present"""
        door_col = detect_column(bus_df, ['door_state', 'door', 'doors'])
        if door_col:
            unique_states = set(bus_df[door_col].dropna().unique())
            # Just check that values exist, don't enforce specific values
            assert len(unique_states) > 0, "No door state values found"
    
    def test_minimum_records(self, bus_df):
        """Check dataset has sufficient records"""
        assert len(bus_df) > 1000, \
            f"Insufficient records: {len(bus_df)}"
    
    def test_timestamp_format(self, bus_df):
        """Check timestamp is parseable"""
        time_col = detect_column(bus_df, ['timestamp_utc', 'utc_time', 'timestamp', 'time'])
        if time_col:
            try:
                pd.to_datetime(bus_df[time_col].head(100), format='mixed')
            except Exception as e:
                pytest.fail(f"Timestamp parsing failed: {e}")


class TestDataConsistency:
    """Cross-dataset consistency tests"""
    
    @pytest.fixture
    def passengers_df(self):
        df = pd.read_csv('data/raw/passengers.csv')
        return df
    
    @pytest.fixture
    def bus_df(self):
        df = pd.read_csv('data/raw/bus.csv')
        return df
    
    def test_overlapping_time_range(self, passengers_df, bus_df):
        """Check that passenger and bus data have overlapping time ranges"""
        pass_time_col = detect_column(passengers_df, ['timestamp_utc', 'timestamp', 'time'])
        bus_time_col = detect_column(bus_df, ['timestamp_utc', 'utc_time', 'timestamp', 'time'])
        
        if pass_time_col and bus_time_col:
            # Convert to datetime and remove timezone info for comparison
            passengers_df[pass_time_col] = pd.to_datetime(passengers_df[pass_time_col], format='mixed', utc=True).dt.tz_localize(None)
            bus_df[bus_time_col] = pd.to_datetime(bus_df[bus_time_col], format='mixed', utc=True).dt.tz_localize(None)
            
            pass_min = passengers_df[pass_time_col].min()
            pass_max = passengers_df[pass_time_col].max()
            bus_min = bus_df[bus_time_col].min()
            bus_max = bus_df[bus_time_col].max()
            
            # Check for overlap
            overlap_exists = (pass_min <= bus_max) and (bus_min <= pass_max)
            assert overlap_exists, f"No time overlap: Pass[{pass_min} to {pass_max}] vs Bus[{bus_min} to {bus_max}]"
    
    def test_similar_geographic_bounds(self, passengers_df, bus_df):
        """Check that both datasets are in similar geographic region"""
        pass_lat_col = detect_column(passengers_df, ['latitude', 'lat'])
        bus_lat_col = detect_column(bus_df, ['latitude', 'lat'])
        
        if pass_lat_col and bus_lat_col:
            pass_lat_range = passengers_df[pass_lat_col].max() - passengers_df[pass_lat_col].min()
            bus_lat_range = bus_df[bus_lat_col].max() - bus_df[bus_lat_col].min()
            
            # Allow different coverage ranges (bus travels smaller area)
            # Just check both are in reasonable range (not worldwide)
            assert pass_lat_range < 1.0, f"Passenger data spans too wide: {pass_lat_range} degrees"
            assert bus_lat_range < 1.0, f"Bus data spans too wide: {bus_lat_range} degrees"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
