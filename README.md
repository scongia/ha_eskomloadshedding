# eskomloadshedding

[![GitHub Release][releases-shield]][releases]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Dependency][dependency-shield]][load_shedding_api]

**Beta Testing**
This is a component designed for [Home Assistant](https://www.home-assistant.io) and intended for South African users.

The EskomLoadshedding integration component reports the current load shedding stage from Eskom (South African national utility provider) and provides a 7 day view of the corresponding load shedding schedule for a configured area.

Calendar View              | Lovelace
:-------------------------:|:-------------------------:
![Lovelace](/assets/lovelace_view.jpg) |  ![Calendar](/assets/calendar_view.jpg)

Configure Province         | Configure Suburb
:-------------------------:|:-------------------------:
![Lovelace](/assets/configure_province.jpg) |  ![Calendar](/assets/configure_suburb.jpg)

<div align="center">

  <a href="https://www.buymeacoffee.com/scongia">![example1](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge)</a>

</div>

If a province and suburb are configured, the component provides the calendar sensor containing the corresponding load shedding schedule for that area, and an additional sensor reporting when the next outage will be (should this be required for any automations). 

The Province and Suburb can be configured using the configuration wizard accessible for the integrations page.

## Download

### HACS
This component has not yet been added to the HACS inventory of repos (still to be tested). For now it can be installed as a custom repository. To do this do the following:
1. Select HACS from the side menu
2. Click on the 3 dots at the top right corner and select `Custom repositories`
3. Enter `https://github.com/scongia/ha_eskomloadshedding` into the Repository field and choose Category `Integration`
4. Click `Add` to add the component to your list of custom repositories
5. Scroll down and select `Eskom Load Shedding Utility`
6. Click on `Download the repository with HACS`
7. Select the most recent version and click `Download`
8. Restart Home Assistant

### Manual
Locate the config folder on your home assistant installation (where the `configuration.yaml` file is located), and do the following:
1. Create a folder called `custom_components` if one does not already exist.
2. Download the latest release of the eskomloadshedding integrtaion from the [releases](https://github.com/scongia/ha_eskomloadshedding/releases) page.
3. Unzip and copy the `eskomloadshedding` folder to the `custom_components` folder
4. Restart Home Assistant

## Installation
Once you have downloaded the component, you can install integration as follows:
1. Navigate to Settings > Devices & Services
2. Select `Add Integration` and search for Eskom Load Shedding
3. Select `Eskom Load Shedding` and click `Submit` to start the installation.

## Configuration

1. Once added, navigate to the integration and click on `Configure`
2. Set the desired poll interval using `scan interval`
3. To proceed to area configuration, select the option `Continue to location config` and click `Submit`
4. Select your `Province` from the dropdown 
5. Enter part of `suburb name` to search form and click `Submit`
6. Select the `suburb` from the list and click `Finish`

<!---->
[releases-shield]: https://img.shields.io/github/v/release/scongia/ha_eskomloadshedding?style=for-the-badge
[releases]: https://github.com/scongia/ha_eskomloadshedding/releases

[maintenance-shield]: https://img.shields.io/badge/maintainer-%40scongia-blue.svg?style=for-the-badge
[user_profile]: https://github.com/scongia

[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/scongia

[dependency-shield]: https://img.shields.io/badge/Dependency-load--shedding_v0.4.0-blue?logo=gitlab&style=for-the-badge
[load_shedding_api]: https://pypi.org/project/load-shedding

