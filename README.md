<div align="justify">

# FVON-QCQA: Fishing Vessel Ocean Observing Network - QA/QC Guidelines

This repository provides tools, workflows, and guidelines for automated near real-time Quality Control (QC) of fishing vessel ocean observing data. 

---

## Acknowledgement

This work builds on the QA/QC frameworks provided by [BDC_qc](https://github.com/BerringDC/BDC_qc), developed by the Ocean Data Network (ODN) and [moana-qc](https://github.com/metocean/moana-qc/blob/master/docs/moana_sensor_qc.md), developed by the moana project. Addtitional input from the AdriFOOS program at [CNR-IRBIM](https://www.irbim.cnr.it/en/). We extend their work and adapt it for FVON's specific needs.

---

## Updates and Contributions

This README and the QA/QC workflows will be updated collaboratively by the FVON team. Contributions are welcome! Please submit a pull request for any additions or improvements.

---

# FVON_QC
Collection of manuals and scripts to assist in automated quality assurance and quality control for oceanographic subsurface profile data collected via fishing gear as a platform. These QC tests apply to both fixed and mobile gears.

<br>

## Table of contents

<!--ts-->

* [Introduction](#introduction)
* [Flags](#flags)
* [General Quality Control Tests](#general-quality-control-tests)
* [Real-time Quality control](#real-time-quality-control)
	* [Fisheries quality control tests](#fisheries-quality-control-tests)
		* [Platform identification (under development)](#platform-identification-under-development)
		* [Vessel ID control test](#vessel-id-control-test)
		* [Gear type control test](#gear-type-control-test)
	* [Quality control tests CTD](#quality-control-tests-ctd)
		* [Impossible date test](#impossible-date-test)
		* [Impossible location test](#impossible-location-test)
		* [Position on land test](#position-on-land-test)
		* [Impossible speed test](#impossible-speed-test)
		* [Global range test](#global-range-test)
		* [Spike test](#spike-test)
		* [Digit rollover test](#digit-rollover-test)
		* [Stuck value / flat line test](#stuck-value-flat-line-test)
		* [Rate of change test](#rate-of-change-test)
		* [Mud test](#mud-test)
		* [Timing/gap test](#timinggap-test)
		* [Climatology test](#climatology-test)
        * [Sensor calibration date test](#sensor-calibration-date-test)
* [References](#references)

<!--te-->

<br>

## Introduction

This document describes the implementation of the automated checks that are performed on CTD (Conductivity, Temperature, Depth) or TD (Temperature, Depth) data that are collected via fishing gear as a platform for sensors. Trajectory data describe the positions and time of the fishing vessel.

<div align="center">

<img width="450" src="https://user-images.githubusercontent.com/70140203/100598077-88045780-32fe-11eb-935d-c67de78713d9.png">

<sub> Figure 1. A fishing vessel as a data collection platform. </sub>

</div>

<br>

## Flags

The data collected by fishing vessels of opportunity, i.e. with sensors attached to fishing gear, is aimed to be interoperable and used by different users with different requirements. In order to maximize (re)usability, the data is quality controlled and flagged to characterize data. Flags are always included in the data delivery, to optimize data reliability and consistency.

Quality checks are mainly based on the tests described by IOOS QARTOD (U.S. Integrated Ocean Observing System, 2020), EuroGOOS (EuroGOOS DATA-/MEQ working group, 2010), the Glider network (U.S. Integrated Ocean Observing System, 2016) and the Argo network (Wong et al., 2020).

The flags used to indicate QC status are based on existing standards defined by other programs and datasets for oceanographic observations. Flags are indicated in Table 1.

<div align="center">

| **Code** | **Meaning** |
| :---: | :---: |
| 0/NA | No QC was performed |
| 1 | Good data |
| 3 | Suspect data |
| 4 | Bad data |
| 5 | Corrected data |
| 9 | Missing value |

<sub> Table 1. Quality flags. </sub>

</div>

- Data flagged as (0) are not quality controlled, and therefore recommended not to be used without QC performed by the user.
- Data flagged as (1) have been quality controlled, and can be used safely.
- Data flagged as (3) have been quality controlled, and marked as suspect. These data can&#39;t be used directly, but have the potential to be corrected in delayed mode.
- Data flagged as (4) have been quality controlled and should be rejected.
- Data flagged as (5) have been corrected.
- Data flagged as (9) are missing.

<br>

## General Quality Control Tests

| Test Name                 | Method Name               | Flag Name              | Variable QC Flag | Recommended | Flag Values |
|---------------------------|---------------------------|------------------------|------------------|-------------|-------------|
| Impossible Date           | impossible_date           | flag_impossible_date   | DATETIME_QC      | yes         | 1, 4         |
| Impossible Location       | impossible_location       | flag_impossible_loc    | LOCATION_QC      | yes         | 1, 4 |
| Remove Reference Location | remove_ref_location       | flag_ref_loc           | LOCATION_QC      | yes         | 1, 4 |
| Timing Gap                | timing_gap                | flag_timing_gap        | DATETIME_QC      | yes         | 1, 4 |
| Datetime Increasing       | datetime_increasing       | flag_datetime_inc      | DATETIME_QC      | yes         | 1, 4 |
| Position on Land          | position_on_land          | flag_land              | LOCATION_QC      | no          | 1, 3 |
| Temperature Global Range  | global_range              | flag_global_range_temp | TEMPERATURE_QC   | yes         | 1, 3 |
| Pressure Global Range     | global_range              | flag_global_range_pres | PRESSURE_QC      | yes         | 1, 3, 4 |
| Temperature Spike         | spike                     | flag_spike_temp        | TEMPERATURE_QC   | yes         | 1, 3 |
| Pressure Spike            | spike                     | flag_spike_pres        | PRESSURE_QC      | yes         | 1, 3 |
| Temperature Stuck Value   | stuck_value               | flag_stuck_value_temp  | TEMPERATURE_QC   | yes         | 1, 3 |
| Pressure Stuck Value      | stuck_value               | flag_stuck_value_pres  | PRESSURE_QC      | yes         | 1, 3 |
| Rate of Change            | rate_of_change_test       | flag_roc               | PRESSURE_QC      | yes         | 1, 3 |
| Temperature Drift         | temp_drift                | flag_temp_drift        | TEMPERATURE_QC   | yes         | 1, 3 |
| Climatology               | climatology_test          | flag_clima             | TEMPERATURE_QC   | no          | 1, 3 |

## Fishing Specific and/or Moana Specific Tests
| Test Name                 | Method Name               | Flag Name             | Variable QC Flag | Recommended | Flag Values |
|---------------------------|---------------------------|-----------------------|------------------|-------------|-------------|
| Stationary Position Check | stationary_position_check | flag_surf_loc         | LOCATION_QC      | yes         | 1, 2, 3     |
| Start End Distance Check  | start_end_dist_check      | flag_dist             | LOCATION_QC      | yes         | 1, 2, 3     |
| Sensor Reset              |                           | flag_dist             | LOCATION_QC      | yes         | 1, 4        |
| Sensor Calibration Date   |                           | flag_calibration_date | DATETIME_QC      | yes         | 1, 3        |


## Real-time Quality control

<div align="center">

<img width="650" src="https://user-images.githubusercontent.com/70140203/100599274-175e3a80-3300-11eb-927c-fc7ebc2ca4f6.png">

<sub>Figure 2. Schematic of the data flow applied to oceanographic data from fishing vessels.</sub>

</div>

<br>

### Fisheries quality control tests

#### Platform identification (under development)

Check if there is an unknown sensor ID/Vessel ID

<br>

#### Vessel ID control test

Check if the vessel is operating in an expected region, defined by the operator. Action: Values that fail the test should be flagged as suspect data (3).

<div align="center">

| **Region** | **Longitude min (º)** | **Longitude max(º)** | **Latitude min(º)** | **Latitude max(º)** |
| :---: | :---: | :---: | :---: | :---: |
| **Greenland** | -60 | -15 | 55 | 90 |
| **North Sea and Baltic** | -15 | 30 | 45 | 60 |
| **Atlantic** | -75 | 30 | 55 | 90 |
| **New Zealand** | 160 | 175 | -50 | -30 |
| **Alaska** | -180 | -125 | 45 | 90 |

<sub> Table 2. Region location. </sub>

</div>

<br>

#### Gear type control test

Check if the gear type assigned is correct.

Gear types are either defined as fixed gear (Fixed) or mobile gear (Mobile). A profile measured by a sensor on fixed gear is assigned to one single GPS point. A profile by a sensor on mobile gear follows the trajectory from the fishing vessel. 

The distance travelled by the sensor during the profile is calculated between the first and last data locations. Action: Values that fail the test should be flagged as suspect data (3).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Suspect (3) | _Gear type: <br><br> Fixed: distance &gt; 200 meters <br> Mobile: distance &lt;= 200 meters_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 3. Gear type flags. </sub>

</div>

<br>

### Quality control tests CTD

#### Impossible date test

The date of the profile can be no earlier than 01/01/2010 and no later than current date in UTC. Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Impossible date: <br><br> 01/01/2010 &lt; Date &gt; UTC_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Tablel 4. Impossible date flags. </sub>

</div>

<br>

#### Impossible location test

This test controls whether the geographic location is reasonable, based on the global limits for longitude and latitude. Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Impossible location: <br><br> -180º &lt; longitude &gt; 180º <br> -90º &lt; latitude &gt; 90º_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 5. Impossible location flags. </sub>

</div>

<br>

#### Position on land test

This test requires that the observation latitude and longitude from a float profile be located in an ocean. Here we use a 5 minutes bathymetry file (ETOPO5/TerrainBase) downloaded from [http://www.ngdc.noaa.gov/mgg/global/etopo5.html](http://www.ngdc.noaa.gov/mgg/global/etopo5.html). Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Measurement is on land._ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 6. Position on land flags. </sub>

</div>

<br>

#### Impossible speed test

This test is only applied to profiles coming from mobile gear. It controls whether there are no erroneous locations provided. The speed of the vessels are generated given the positions and times of the vessel. Vessel speed is expected not to exceed 3 ms−1. Otherwise, it means either the positions or times are bad data, or a vessel is sailing full speed rather than fishing.

This test is helpful for determining if there is an error in merging the sensor and GPS data, often due to setting a sensor to a time zone other than UTC. Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Speed is too high for mobile gear fishing. <br><br> Vessel speed &gt; 4.12 ms−1 (8 knots)_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 7. Impossible speed flags. </sub>

</div>

<br>

#### Global range test

Gross filter on the observed values of pressure, temperature and salinity based on the sensor ranges (NKE TD, NKE CTD and ZebraTech Moana TD).

- [Zebra-Tech](https://zebra-tech.co.nz/moana)
- [NKE CTD](https://nke-instrumentation.com/produit/wisens-ctd/)
- [NKE TD](https://nke-instrumentation.com/produit/wisens-td/)
- [Hobo](https://www.onsetcomp.com)
- [Vemco_minilog](https://www.vemco.com)
- [Marport](http://www.marport.com)
- [Lowell TD](https://lowellinstruments.com)


This test applies a gross filter on the observed values of pressure, temperature and salinity. Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Measurement outside sensor operating range <br><br> <b> NKE sensors </b> <br> -5 dbar &lt; Pressure <br> -2 &lt; Temperature &gt; 35 °C <br> 2 &lt; Salinity &gt; 42 PSU <br> <br> <b> ZebraTech sensors </b> <br> -5 dbar &lt; Pressure <br> -2 &lt; Temperature &gt; 35 °C <br> <br> <b> Lowell sensors </b> <br> -5 dbar &lt; Pressure <br> -5 &lt; Temperature &gt; 50 °C <br> <br> <b> Marport sensors </b> <br> -5 dbar &lt; Pressure <br> -5 &lt; Temperature &gt; 25 °C <br> <br> <b> Hobo/Vemco sensors </b> <br> -5 dbar &lt; Pressure <br> -20 &lt; Temperature &gt; 50 °C_ |
| Suspect (3) | -5 &lt;= Pressure &lt; 0 dbar <br> Pressure &gt; Max sensor depth + 10% or 50% (ZebraTech) |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 8. Global range flags. </sub>

</div>

<br>

#### Spike test

The spike tests checks whether there is a significant difference between sequential measurements, by comparing a measurement to its adjacent ones. The test does not consider differences in pressure, and rather assumes measurements that adequately reproduce changes in temperature and salinity with pressure.

Here, V2 is the tested value, and V1 and V3 are the values before and after. Spikes consisting of more than one data point are difficult to capture, but their onset may be flagged by the rate of change test.

Cut-off values are based on (Wong et al., 2020), and V2 will be flagged based on the following values. Action: Values that fail the test should be flagged as bad data (4). 

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Measurement differs significantly from its neighbours <br><br> Pressure &lt; 500 dbar:<br> Test value T &gt; 6.0 °C <br> Test value S &gt; 0.9 PSU <br><br> Pressure &gt; = 500 dbar: <br> Test value T &gt; 2.0°C <br>Test value S &gt; 0.3 PSU_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 9. Spike flags. </sub>

</div>

<br>

#### Digit rollover test

Here we compare the measurements at the end of the profile to the adjacent measurement. Temperature at the bottom should not differ from the adjacent measurement by more than 1°C. Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Measurement differs significantly from its neighbours <br><br> T2 - T1 &gt; 1.0 °C_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 10. Digit rollover flags. </sub>

</div>

<br>

#### Stuck value/ flat line test

It is possible that, when sensors fail, continuously repeated observations of the same value are produced. In this test, the present observation is compared to several previous observations. The present observation is flagged if the present observation is the same as all previous observations, calculating in a tolerance value. Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _The five most recent observations are equal <br><br> Tolerance values: <br> Temperature: 0.05 °C <br> Salinity: 0.05 PSU <br> Pressure: 0.5 dbar_ |
| Suspect (3) | _The three most recent observations are equal_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 11. Flat line flags. </sub>

</div>

<br>

#### Rate of change test

This test is applied per segment (Up-Down-Bottom), and inspects the segments on a rate of change exceeding a threshold defined by the operator. In this case the thresholds are based on the IOOS examples (U.S. Integrated Ocean Observing System, 2020), where the rate of change between measurement Tn-1 and Tn must be less than three standard deviations (3\*SD). The SD of the T time series is computed over the full segment.

This test needs to find a balance between setting a threshold too low, triggering too many false alarms, and setting a threshold too high, triggering too little alarms. Action: Values that fail the test should be flagged as suspect data (3).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Suspect (3) | _The rate of change exceeds the selected threshold._ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 12. Rate of change flags. </sub>

</div>

<br>

#### Mud test

This test is applied only in the Up segment. Controls whether the temperature sensor has some mud biasing the measurements once hauled. Values are rolled by 10 measurements and observations are flagged if rolled temperature is lower than 0.005ºC.	Action: Values that fail the test should be flagged as bad data (4).

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Fail (4) | _Invariant measurement <br> Rolled temperature < 0.005 °C_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 13. Mud flags. </sub>

</div>

<br>

#### Timing/gap test

<div align="center">

This test controls whether the most recent measurement has been received within the expected time period. Action: Values that fail the test should be flagged as suspect data (3).

| **Flags** | **Description** |
| :---: | :---: |
| Suspect (3) | _Check for the arrival of data <br><br> Data didn&#39;t come in as expected: NOW – TIM\_STMP &gt; TIM\_INC_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 14. Timing flags. </sub>

</div>

<br>

#### Climatology test

Test that data point falls within seasonal expectations according to different regions.

This test is a variation on the gross range check, where the thresholds T\_Season\_MAX and T\_Season\_MIN are adjusted monthly, seasonally, or at some other operator-selected time period (TIM\_TST) in a specific region. Because of the dynamic nature of T and S in some locations, no fail flag is identified for this test and measurements will only be marked as &#39;suspect&#39; (3).

Regional ranges are defined based on (EuroGOOS DATA-MEQ working group, 2010) and (Wong et al., 2020), see also Figure 3.

<div align="center">

![clima](https://user-images.githubusercontent.com/70140203/100601137-8341a280-3302-11eb-83da-4dd1b9ada1a9.jpg)

<sub> Figure 3. Regions used for the climatology test. </sub>

</div>

Red Sea (from 10 N to 32 N and 30 E to 45 E)

- Temperature in range 21.7°C to 40.0°C
- Salinity in range 2.0 to 41.0

Mediterranean Sea (from 30 N to 45 N and 6 W to 30 E)

- Temperature in range 10.0°C to 40.0°C
- Salinity in range 2.0 to 40.0

North Western Shelves (from 50 N to 60 N and 20 W to 10 E)

- Temperature in range –2.0°C to 24.0°C
- Salinity in range 0.0 to 37.0

South West Shelves (From 25 N to 50 N and 30 W to 0 W)

- Temperature in range –2.0°C to 30.0°C
- Salinity in range 0.0 to 38.0

Arctic Sea (above 60N)

- Temperature in range –1.92°C to 25.0°C
- Salinity in range 2.0 to 40.0

Seasonal limits per area still have to be defined, in the meantime we take min and max of temp and sal of all measurements from our vessels in DB.

<div align="center">

| **Flags** | **Description** |
| :---: | :---: |
| Suspect (3) | _Measurement outside climatology range <br><br> Seas\_min\_T &lt; Temperature&gt; Seas\_max\_T <br> Seas\_min\_S &lt; Salinity &gt; Seas\_max\_S_ |
| Pass (1) | _Applies for test pass condition._ |

<sub> Table 15. Climatology flags. </sub>

</div>

<br>

#### Sensor calibration date test

<div align="center">

This test verifies whether the most recent measurement falls within the expected time range of calibration. Action: Values that fail the test should be flagged as suspect data (3).

|  **Flags**  |            **Description**             |
|:-----------:|:--------------------------------------:|
| Suspect (3) | _Measurement out of calibration date._ |
|  Pass (1)   |   _Applies for test pass condition._   |

<sub> Table 16. Sensor calibration date test flags. </sub>

</div>

<br>


## References

Annie Wong, Robert Keeley, Thierry Carval and the Argo Data Management Team (2020).

Argo Quality Control Manual for CTD and Trajectory Data. [http://dx.doi.org/10.13155/33951](http://dx.doi.org/10.13155/33951)

EuroGOOS DATA-MEQ working group (2010). Recommendations for in-situ data Near Real Time Quality Control. https://doi.org/10.13155/36230

IMOS Fishing Vessels as Ships of Opportunity (FishSOOP), Real-time Quality Assurance and Quality Control Practice Manual, Version 1.0. [https:doi.org/10.26198/sp0r-p448](https://repository.oceanbestpractices.org/handle/11329/2629)

U.S. Integrated Ocean Observing System, 2020. Manual for Real-Time Quality Control of In-situ Temperature and Salinity Data Version 2.1: A Guide to Quality Control and Quality Assurance of In-situ Temperature and Salinity Observations. 50 pp. [https://doi.org/10.25923/x02m-m555](https://doi.org/10.25923/x02m-m555)

U.S. Integrated Ocean Observing System (2016) Manual for Quality Control of Temperature and Salinity Data Observations from Gliders. Version 1.0. Silver Spring, MD, U.S. Department of Commerce, National Oceanic and Atmospheric Administration, National Ocean Service, Integrated Ocean Observing System, 23pp. & Appendices. http://hdl.handle.net/11329/289

</div>
